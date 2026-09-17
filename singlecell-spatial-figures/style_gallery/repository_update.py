"""Synchronize machine-readable gallery metadata without rewriting public documentation.
同步机器可读的图库元数据，但不改写公开 README、Skill 文档或生成开发过程报告。
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent


def update() -> None:
    """Refresh capability metadata only. / 仅刷新能力元数据。"""
    rows = json.loads((HERE / "catalogue_v32.json").read_text(encoding="utf-8"))
    path = SKILL / "CAPABILITIES.json"
    capabilities = json.loads(path.read_text(encoding="utf-8"))

    # Keep the machine compatibility version while avoiding release-note prose.
    # 保留机器兼容版本字段，但不向公开文档写入版本发布说明。
    if str(capabilities["version"]).split(".")[0] != "3":
        raise ValueError("Unsupported capability major version")
    if tuple(int(value) for value in capabilities["version"].split(".")) < (3, 2, 0):
        capabilities["version"] = "3.2.0"

    capabilities["style_gallery"] = {
        "version": "3.2.0",
        "path": "style_gallery/README.md",
        "kinds": [row["kind"] for row in rows],
        "implementation": "style_gallery/render.py",
        "modules": ["style_gallery/chart_core.py", "style_gallery/chart_types.py"],
        "test": "style_gallery/tests/test_gallery.py",
        "catalogue": "style_gallery/catalogue_v32.json",
        "gallery": "style_gallery/examples/README.md",
        "examples": "paired minimal/advanced synthetic software examples",
        "subtitle_policy": "forbidden",
        "status": "implemented",
        "R": "Python wrapper; native R parity is not claimed",
        "limits": [
            "Upstream biological and statistical models are not rerun by the renderer",
            "Synthetic examples are not biological results",
            "No universal visual, scientific or journal-readiness certification",
        ],
    }
    path.write_text(json.dumps(capabilities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Capability metadata synchronized")


def presets() -> None:
    """Verify palette snapshots against installed presets. / 校验色板快照与已安装 preset。"""
    sys.path.insert(0, str(SKILL / "scripts"))
    from palette_presets import palette_colors

    snapshots = json.loads((HERE / "palette_snapshots_v32.json").read_text(encoding="utf-8"))
    for preset_id, item in snapshots.items():
        expected = [color.upper() for color in palette_colors(preset_id)]
        if expected != item["colors"]:
            raise ValueError("Preset snapshot mismatch: " + preset_id)
    print("Palette snapshots verified")


def manifest() -> None:
    """Rebuild the repository file manifest. / 重建文件哈希清单。"""
    rows = []
    excluded = {"__pycache__", ".pytest_cache", ".git", ".venv"}
    for path in sorted(SKILL.rglob("*")):
        relative = path.relative_to(SKILL)
        if path.is_file() and path.name != "MANIFEST.sha256" and not (excluded & set(relative.parts)):
            rows.append(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + relative.as_posix())
    (SKILL / "MANIFEST.sha256").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("Manifest rebuilt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["metadata", "presets", "manifest"])
    args = parser.parse_args()
    {"metadata": update, "presets": presets, "manifest": manifest}[args.command]()
