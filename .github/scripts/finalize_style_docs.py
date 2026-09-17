#!/usr/bin/env python3
"""Build public gallery navigation after successful rendering.
成功渲染后生成面向公众的图库导航与预览，不写入维护过程或版本说明。
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "singlecell-spatial-figures"


def load_rows(examples: Path) -> list[dict]:
    """Load and validate the public chart catalogue. / 读取并校验公开图形目录。"""
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


def write_gallery(rows: list[dict], docs: Path) -> None:
    """Write the bilingual public gallery index. / 写入中英双语公开图库索引。"""
    lines = [
        "# CNS Figure Gallery · CNS 科学图库",
        "",
        "Publication-oriented minimal and advanced examples. All bundled numerical values are synthetic software fixtures.",
        "面向论文发表的 minimal 与 advanced 示例。所有随附数值均为合成软件示例。",
        "",
        "[Skill / 使用规范](../singlecell-spatial-figures/SKILL.md) · [Design guide / 设计指南](../singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [Examples / 完整示例](../singlecell-spatial-figures/style_gallery/examples/README.md)",
        "",
        "![Advanced overview](preview.png)",
        "",
        "| Figure family / 图形类型 | Minimal | Advanced |",
        "|---|---|---|",
    ]
    for row in rows:
        kind = row.get("chart", row.get("kind", ""))
        title = row.get("name", row.get("title", kind))
        base = f"../singlecell-spatial-figures/style_gallery/examples/figures/{kind}"
        lines.append(
            f"| {title} | [PNG]({base}_minimal.png) · [PDF]({base}_minimal.pdf) | "
            f"[PNG]({base}_advanced.png) · [PDF]({base}_advanced.pdf) |"
        )
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "GALLERY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_preview(rows: list[dict], examples: Path, target: Path, columns: int = 3) -> None:
    """Build a compact public preview sheet. / 生成紧凑的公开预览图。"""
    if not isinstance(columns, int) or columns < 1:
        raise ValueError("columns must be a positive integer")
    preferred = [
        "heatmap", "dotplot", "distribution", "network", "flow", "forest",
        "upset", "spatial_composition", "trajectory_heatmap", "spatial_pies",
        "lineage_heatmap",
    ]
    by_kind = {row.get("chart", row.get("kind")): row for row in rows}
    chosen = [kind for kind in preferred if kind in by_kind][:9] or list(by_kind)[:9]
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
            image = source.convert("RGB")
            image.thumbnail((tile_w, tile_h - 35), Image.Resampling.LANCZOS)
            x = gap + (i % columns) * (tile_w + gap)
            y = gap + (i // columns) * (tile_h + gap)
            canvas.paste(image, (x + (tile_w - image.width) // 2, y + 35))
            draw.text((x, y), kind.replace("_", " "), fill="#333333", font=font)

    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target)


def main() -> None:
    """Refresh public gallery artifacts only. / 仅刷新公开图库产物。"""
    examples = SKILL / "style_gallery" / "examples"
    rows = load_rows(examples)
    docs = ROOT / "docs"
    write_gallery(rows, docs)
    build_preview(rows, examples, docs / "preview.png", columns=3)


if __name__ == "__main__":
    main()
