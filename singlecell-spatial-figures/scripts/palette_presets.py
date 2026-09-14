"""Version-3 palette presets. Offline RGB8 tables; never infer category identities."""
from __future__ import annotations
import argparse
import base64
import gzip
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Mapping, Sequence

ASSETS = Path(__file__).resolve().parents[1] / "assets" / "palettes"
INDEX = ASSETS / "index.json"
PREFIX = "cns_"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory():
    """Return an independent metadata copy. Loading makes no network requests."""
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    data["sources"] = json.loads((ASSETS / "sources.json").read_text(encoding="utf-8"))
    return data


def _entry(palette_id):
    if not isinstance(palette_id, str) or not re.fullmatch(r"[CMSDY][0-9]{2}(?:\.[a-z]+)?", palette_id):
        raise ValueError("Use a palette ID such as C19, C06.green, M02 or D03.")
    data = inventory()
    matches = [p for p in data["presets"] if p["id"] == palette_id.split(".")[0]]
    if len(matches) != 1:
        raise ValueError(f"Unknown preset: {palette_id}")
    p = deepcopy(matches[0])
    if "variants" in p:
        variants = [v for v in p["variants"] if v["id"] == palette_id]
        if len(variants) != 1:
            raise ValueError("Select one comparison variant: " + ", ".join(v["id"] for v in p["variants"]))
        p.update(variants[0])
    elif p["id"] != palette_id:
        raise ValueError(f"Preset has no variant: {palette_id}")
    path = ASSETS / p["file"]
    if path.resolve().parent != ASSETS.resolve():
        raise ValueError("Palette file must stay inside the bundled assets directory.")
    packed = json.loads(path.read_text(encoding="utf-8"))[palette_id]
    if packed.startswith("gz-delta8:"):
        try:
            delta = gzip.decompress(base64.b64decode(packed[len("gz-delta8:"):], validate=True))
            if len(delta) != 3 * p["n_colors"]:
                raise ValueError("Wrong decoded palette length.")
            rgb = bytearray(delta)
            for i in range(3, len(rgb)):
                rgb[i] = (rgb[i] + rgb[i - 3]) % 256
            packed = rgb.hex().upper()
        except Exception as error:
            raise ValueError(f"Malformed compressed RGB8 table: {palette_id}") from error
    if not re.fullmatch(r"(?:[0-9A-F]{6})+", packed) or len(packed) != 6 * p["n_colors"]:
        raise ValueError(f"Invalid RGB8 table: {palette_id}")
    if hashlib.sha256(packed.encode()).hexdigest() != p["sha256"]:
        raise ValueError(f"Palette checksum mismatch: {palette_id}")
    colors = ["#" + packed[i:i + 6] for i in range(0, len(packed), 6)]
    if p["family"] == "categorical" and len(set(colors)) != len(colors):
        raise ValueError("Repeated colors in a categorical preset.")
    p["source"] = data["sources"][p["source_id"]]
    return p, colors


def palette_colors(palette_id: str, n: int | None = None) -> list[str]:
    """Category: prefix, never interpolation. Scalar: endpoint-safe LUT sampling."""
    p, colors = _entry(palette_id)
    if n is None:
        return colors
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer.")
    if p["family"] == "categorical":
        if n > len(colors):
            raise ValueError(f"{palette_id}: capacity {len(colors)}, requested {n}; colors are not recycled.")
        return colors[:n]
    if n < 2:
        raise ValueError("A scalar palette needs at least two sample positions.")
    return [colors[min(len(colors) - 1, (i * len(colors)) // (n - 1))] for i in range(n)]


def _levels(values: Sequence[str]) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise ValueError("Pass a sequence of complete category names, not one string.")
    values = list(values)
    if not values or any(not isinstance(x, str) or not x.strip() for x in values) or len(set(values)) != len(values):
        raise ValueError("Reference levels must be unique nonempty strings.")
    return values


def categorical_map(palette_id: str, reference_levels: Sequence[str],
                    existing: Mapping[str, str] | None = None) -> dict[str, str]:
    """Extend a saved identity map without recoloring existing or absent categories."""
    p, colors = _entry(palette_id)
    if p["family"] != "categorical":
        raise ValueError("Continuous or cyclic palettes are not category palettes.")
    levels = _levels(reference_levels)
    result = dict(existing or {})
    if result:
        _levels(list(result))
        if any(not isinstance(c, str) or c.upper() not in colors for c in result.values()):
            raise ValueError("Existing colors must belong to the selected preset.")
        if len({c.upper() for c in result.values()}) != len(result):
            raise ValueError("Existing identity map repeats colors.")
    available = [c for c in colors if c not in {v.upper() for v in result.values()}]
    new = [x for x in levels if x not in result]
    if len(new) > len(available):
        raise ValueError(f"{palette_id}: insufficient unused colors; no cycling or interpolation.")
    result.update(zip(new, available))
    return result


def palette_colormap(palette_id: str):
    """Return a new Matplotlib ListedColormap; original RGB8 lookup order is fixed."""
    from matplotlib.colors import ListedColormap
    p, colors = _entry(palette_id)
    if p["family"] == "categorical":
        raise ValueError("Category palettes must be assigned by label, not scalar interpolation.")
    return ListedColormap(colors, name=PREFIX + palette_id + "_" + p["sha256"][:12])


def _register(palette_id):
    import matplotlib as mpl
    import numpy as np
    cmap = palette_colormap(palette_id)
    if cmap.name not in mpl.colormaps:
        mpl.colormaps.register(cmap)
    else:
        old = mpl.colormaps[cmap.name]
        if old.N != cmap.N or not np.array_equal(old(np.arange(old.N)), cmap(np.arange(cmap.N))):
            raise ValueError("Registered preset name contains different colors.")
    return cmap.name


def resolve_presets(spec):
    """Compile opt-in preset fields to an ordinary v3 spec plus source bindings."""
    resolved = deepcopy(spec)
    bindings = {}
    for sid, scale in resolved.get("scales", {}).items():
        if not isinstance(scale, dict):
            continue  # The existing schema validator will explain malformed input.
        pid = scale.pop("preset", None)
        if pid is None:
            name = scale.get("cmap", "")
            if not isinstance(name, str) or not name.startswith(PREFIX):
                continue
            match = re.fullmatch(r"cns_([MSDY][0-9]{2})_[0-9a-f]{12}", name)
            if not match or _register(match[1]) != name:
                raise ValueError("Saved preset name/checksum no longer matches the bundled table.")
            pid = match[1]
        elif scale.get("kind") == "categorical":
            if "colors" in scale:
                raise ValueError("Choose preset + order OR an explicit saved colors map, not both.")
            scale["colors"] = categorical_map(pid, scale.get("order", []))
        elif scale.get("kind") == "continuous":
            if "cmap" in scale:
                raise ValueError("Choose preset OR cmap, not both.")
            scale["cmap"] = _register(pid)
        else:
            raise ValueError("Preset scales need kind: categorical or continuous.")
        p, _ = _entry(pid)
        if scale.get("kind") == "continuous":
            role = "diverging" if p["family"] == "diverging" else ("qualitative" if p["family"] == "cyclic" else "sequential")
            scale.setdefault("palette_role", role)
        bindings[sid] = {k: p[k] for k in ("id", "name", "family", "grade", "source", "sha256", "n_colors")}
        bindings[sid]["storage"] = "RGB8; scalar float samples rounded to the reviewed HEX values"
        bindings[sid]["index_sha256"] = digest(INDEX)
        bindings[sid]["file"] = p["file"]
        bindings[sid]["file_sha256"] = digest(ASSETS / p["file"])
    return resolved, bindings


def dependency_paths(bindings):
    return sorted({INDEX, ASSETS / "sources.json", *(ASSETS / p["file"] for p in bindings.values())}) if bindings else []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("palette_id", nargs="?")
    parser.add_argument("--n", type=int)
    parser.add_argument("--levels", nargs="+")
    args = parser.parse_args()
    if args.palette_id is None:
        result = inventory()["presets"]
    elif args.levels:
        result = categorical_map(args.palette_id, args.levels)
    else:
        result = palette_colors(args.palette_id, args.n)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
