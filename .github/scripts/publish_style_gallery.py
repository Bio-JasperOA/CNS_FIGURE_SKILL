"""Install and verify the scientific style gallery without publishing CI process artifacts.
安装并校验科学图库，但不把 CI、本地测试或发布过程报告写入公开仓库。
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import io
import json
import os
import tarfile

ROOT = Path.cwd().resolve()
SKILL = ROOT / "singlecell-spatial-figures"
GALLERY = SKILL / "style_gallery"
DELIVERY = ROOT / ".delivery/style-gallery-v32-26"
STATE = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "cns-style-publish-state.json"
DIGEST = "98cbc446b1daa3c237847a88265c1842e40996a9e519b60f2fa4f751b884b874"


def digest(path: Path) -> str:
    """Return SHA-256 for one file. / 返回单个文件的 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected() -> dict[str, str]:
    """Hash protected runtime assets. / 计算受保护运行资产哈希。"""
    paths = list((SKILL / "assets").rglob("*")) + list((SKILL / "scripts").rglob("*"))
    return {
        path.relative_to(ROOT).as_posix(): digest(path)
        for path in sorted(paths)
        if path.is_file() and "__pycache__" not in path.parts
    }


def install() -> None:
    """Install the checked gallery source bundle when present. / 安装经过校验的图库源码包。"""
    caps = json.loads((SKILL / "CAPABILITIES.json").read_text(encoding="utf-8"))
    state = {
        "protected": protected(),
        "capabilities": {key: value for key, value in caps.items() if key not in ("version", "style_gallery")},
        "source_sha256": {},
    }

    if DELIVERY.exists():
        paths = [DELIVERY / f"chunk_{i:02d}.xz" for i in range(19)]
        raw = b"".join(path.read_bytes() for path in paths)
        assert len(raw) == 41616 and hashlib.sha256(raw).hexdigest() == DIGEST, "Delivery checksum mismatch"
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:xz") as archive:
            members = archive.getmembers()
            assert len(members) == 20 and sum(member.size for member in members) == 144602
            assert len({member.name for member in members}) == len(members), "Repeated source path"
            staged = []
            for member in members:
                rel = PurePosixPath(member.name)
                assert member.isfile() and not rel.is_absolute() and ".." not in rel.parts
                assert rel.parts[:2] == ("singlecell-spatial-figures", "style_gallery")
                target = ROOT / str(rel)
                assert target.resolve().is_relative_to(ROOT)
                assert not any(path.is_symlink() for path in [target, *target.parents] if path != ROOT)
                data = archive.extractfile(member).read()
                assert len(data) == member.size
                staged.append((target, data))
            for target, data in staged:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                state["source_sha256"][target.relative_to(ROOT).as_posix()] = hashlib.sha256(data).hexdigest()
        for path in paths:
            path.unlink()
        DELIVERY.rmdir()
    else:
        assert (GALLERY / "catalogue_v32.json").is_file(), "Gallery sources are not installed"

    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print("Gallery source delivery verified")


def verify() -> None:
    """Verify generated examples without writing public QA reports. / 校验示例，但不生成公开 QA 报告。"""
    import fitz
    import pandas as pd

    state = json.loads(STATE.read_text(encoding="utf-8"))
    assert state["protected"] == protected(), "Protected palette, schema or script changed"

    caps = json.loads((SKILL / "CAPABILITIES.json").read_text(encoding="utf-8"))
    current = {key: value for key, value in caps.items() if key not in ("version", "style_gallery")}
    assert state["capabilities"] == current
    assert len(caps["style_gallery"]["kinds"]) == 26

    for rel, sha in state["source_sha256"].items():
        assert digest(ROOT / rel) == sha, "Delivered source modified: " + rel

    root = GALLERY / "examples"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["pairs"]) == 26

    prefixes = [
        root / "figures" / f"{row['kind']}_{mode}"
        for row in manifest["pairs"]
        for mode in ("minimal", "advanced")
    ]
    prefixes += [root / "figures" / f"embedding_100_{mode}" for mode in ("minimal", "advanced")]

    for prefix in prefixes:
        qa = json.loads(prefix.with_suffix(".qa.json").read_text(encoding="utf-8"))
        assert qa["subtitle_count"] == 0 and not qa["outside_canvas"], prefix.name
        for ext in ("png", "pdf", "svg"):
            path = prefix.with_suffix("." + ext)
            assert path.stat().st_size > 1000
            assert digest(path) == qa["outputs"][ext], "Output hash mismatch: " + path.name
        assert "<text" in prefix.with_suffix(".svg").read_text(encoding="utf-8")
        with fitz.open(prefix.with_suffix(".pdf")) as doc:
            assert len(doc) == 1
            assert abs(doc[0].rect.width * 25.4 / 72 - qa["width_mm"]) < 0.03
            assert abs(doc[0].rect.height * 25.4 / 72 - qa["height_mm"]) < 0.03
            text = doc[0].get_text()
            assert "SYNTHETIC EXAMPLE" in text and "SUBTITLE" not in text

    with fitz.open(root / "paired_gallery.pdf") as doc:
        assert len(doc) == 26

    for mode in ("minimal", "advanced"):
        key = pd.read_csv(root / "figures" / f"embedding_100_{mode}.colors.csv")
        assert len(key) == 100 and key.color.nunique() == 100

    for row in manifest["pairs"]:
        csv_path = root / "source_data" / (row["kind"] + ".csv")
        assert digest(csv_path) == row["data_sha256"]
        assert digest(csv_path.with_suffix(".json")) == row["config_sha256"]

    print("Gallery verification passed: 26 chart families, no subtitles, export hashes valid")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["install", "verify"])
    args = parser.parse_args()
    {"install": install, "verify": verify}[args.command]()
