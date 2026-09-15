#!/usr/bin/env python3
"""Prepare v3.2 gallery navigation after successful rendering."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "singlecell-spatial-figures"


def load_rows(examples: Path) -> list[dict]:
    raw = json.loads((examples / "catalogue.json").read_text(encoding="utf-8"))
    if isinstance(raw, list):
        rows = raw
    elif isinstance(raw, dict):
        rows = raw.get("plots", raw.get("entries", raw.get("catalogue", [])))
    else:
        raise ValueError("Catalogue must be a list or a supported wrapper object")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Catalogue has no chart rows")
    kinds = [row.get("chart", row.get("kind", "")) for row in rows if isinstance(row, dict)]
    if len(kinds) != len(rows) or any(not k for k in kinds) or len(set(kinds)) != len(kinds):
        raise ValueError("Catalogue chart IDs must be present and unique")
    return rows


def write_readme(rows: list[dict], docs: Path) -> None:
    lines = [
        "# CNS Figure Skill · v3.2", "",
        f"{len(rows)} families, minimal and advanced examples, no subtitles. All bundled numbers are synthetic style fixtures.", "",
        "[Skill](../singlecell-spatial-figures/SKILL.md) · [Design guide](../singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [Full examples](../singlecell-spatial-figures/style_gallery/examples/README.md)", "",
        "![Advanced overview](preview.png)", "",
        "| Figure family | Minimal | Advanced |", "|---|---|---|",
    ]
    for row in rows:
        kind = row.get("chart", row.get("kind", ""))
        title = row.get("name", row.get("title", kind))
        base = f"../singlecell-spatial-figures/style_gallery/examples/figures/{kind}"
        lines.append(f"| {title} | [PNG]({base}_minimal.png) · [PDF]({base}_minimal.pdf) | [PNG]({base}_advanced.png) · [PDF]({base}_advanced.pdf) |")
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "GALLERY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_preview(rows, examples, target, columns=3):
    # Image is imported once at module scope. A local import below its first
    # use caused UnboundLocalError and prevented the successful build publishing.
    if not isinstance(columns, int) or columns < 1:
        raise ValueError("columns must be a positive integer")
    chosen = ["heatmap", "dotplot", "distribution", "network", "flow", "forest", "upset", "spatial_composition", "trajectory_heatmap", "spatial_pies", "lineage_heatmap"]
    by_kind = {r.get("chart", r.get("kind")): r for r in rows}
    chosen = [x for x in chosen if x in by_kind][:9]
    if not chosen:
        chosen = list(by_kind)[:9]
    if not chosen:
        raise ValueError("No charts to preview")
    examples = Path(examples)
    figures = examples / "figures" if (examples / "figures").is_dir() else examples
    paths = [figures / f"{kind}_advanced.png" for kind in chosen]
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"Missing rendered preview: {path}")
    tile_w, tile_h, gap = 720, 520, 22
    nrows = (len(chosen) + columns - 1) // columns
    size = (columns * tile_w + (columns + 1) * gap, nrows * tile_h + (nrows + 1) * gap)
    canvas = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    for i, (kind, path) in enumerate(zip(chosen, paths)):
        with Image.open(path) as source:
            img = source.convert("RGB")
            img.thumbnail((tile_w, tile_h - 35), Image.Resampling.LANCZOS)
            x = gap + (i % columns) * (tile_w + gap)
            y = gap + (i // columns) * (tile_h + gap)
            canvas.paste(img, (x + (tile_w - img.width) // 2, y + 35))
            draw.text((x, y), kind.replace("_", " "), fill="#333333", font=font)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target)


def main():
    examples = SKILL / "style_gallery" / "examples"
    rows = load_rows(examples)
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    write_readme(rows, docs)
    build_preview(rows, examples, docs / "preview.png", columns=3)
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "<!-- V3_2_PUBLICATION_NAV -->"
    if marker not in text:
        text += "\n\n" + marker + "\n\n## v3.2 publication gallery\n\n"
        text += "**[26 类最简／高级图库](docs/GALLERY.md)** · [并排对照 PDF](singlecell-spatial-figures/style_gallery/examples/paired_gallery.pdf)\n\n"
        text += "![Advanced figure overview](docs/preview.png)\n"
    readme.write_text(text, encoding="utf-8")
    (ROOT / "README_MAINTAINER.md").write_text(
        "# Maintainer notes\n\nThe Skill remains major version 3 and `spec_version: '3.0'`. "
        "v3.2 adds 26-family table-driven style rendering without changing the existing palette IDs. "
        "All demo data must remain marked synthetic. No subtitle is rendered.\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
