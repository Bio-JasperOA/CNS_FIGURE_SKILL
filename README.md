# CNS Figure Skill · v3

**Render reviewed single-cell/spatial results, make visual decisions explicit, and audit the final artifact.** This is not an automated scientific-analysis or “CNS-approved design” system.

Start with [`singlecell-spatial-figures/SKILL.md`](singlecell-spatial-figures/SKILL.md). Preserve that complete directory.

## What changed

The v3 pipeline adds six explicit scalar mappings, measured labels and independent guides, lightness/contrast/CVD screening, text and PDF geometry checks, actual final-PDF placement verification, artifact-bound human review, repair escalation, and dependency-aware re-review. Unsupported renderer names fail preflight instead of being advertised as working features.

Python has four connected v3 renderers: embedding, spatial scalar map, marker dotplot, and annotated heatmap. The R bridge consumes the same compiled geometry and colors but **has not been executed in the authoring environment**. Shared post-export PDF checks do not prove Python/R pixel parity. Legacy v1/v2 numerical helpers and tests are retained separately.

## Read only what is needed

- [Skill entry](singlecell-spatial-figures/SKILL.md): decisions, commands and stop conditions.
- [Capability registry](singlecell-spatial-figures/CAPABILITIES.json): current implementation/test/manual boundaries, including all 17 reported issues.
- [Operational playbook](singlecell-spatial-figures/references/v3_playbook.md): visual hierarchy, density, guide design, concrete failure criteria and version migration.
- [Current QA record](singlecell-spatial-figures/QA_REPORT.md): actual tests and limitations, not historical claims.
- [Run a clearly artificial example](singlecell-spatial-figures/examples/v3_software_qa/README.md).

```bash
cd singlecell-spatial-figures
# Use an isolated environment; review pins before changing an existing research project.
python -m pip install -r requirements-v3.txt
python scripts/render_v3.py render examples/v3_software_qa/figure.yaml   --root examples/v3_software_qa --out build/software_qa
python -m pytest -q
```

A successful render produces **a draft**, not an approved scientific figure. Complete `review.json` against the actual output; a later input/config/code/export change makes that review stale. Use `render_v3.py --help` and the playbook for final placement and native-R audits.

No fonts, user experiments, paper PDFs or author model weights are distributed. The paper/code audit is inherited; v3 does not claim additional paper reproduction. Journal dimensions and contrast thresholds are project defaults, not universal publication rules. No new license is assigned by this update.

## v3.0.1 · Palette presets

已加入 52 个可选色卡家族（含 21 个类别家族及 20–102 色的高容量方案）；保留 v3 大版本和 `spec_version: '3.0'`，不更换现有图的默认配色。

[色卡浏览与调用说明](singlecell-spatial-figures/assets/palettes/README.md) · [预览图](singlecell-spatial-figures/assets/palettes/preview.svg) · [当前测试记录](singlecell-spatial-figures/QA_REPORT.md)

```yaml
# 某个 categorical scale 内：
preset: C19
order: [T_cell, B_cell, Myeloid]
# 某个 continuous scale 内则使用 preset: M02，limits 与 norm 仍显式定义。
```

<!-- STYLE_GALLERY_V3_1:START -->
## v3.1 · 图形样式与实例

**[浏览14类最简版 / 高级版](singlecell-spatial-figures/style_gallery/examples/README.md)** · [设计手册](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [运行代码](singlecell-spatial-figures/style_gallery/README.md) · [新增测试记录](singlecell-spatial-figures/style_gallery/QA_REPORT.md)

每类含同一输入的两版图、PNG/PDF/SVG、源表和配置，以及CNS及子刊论文具体panel的设计对照。另有100类别嵌入图与完整色键。所有实例均为合成样式测试，不是生物学结果或论文数值复现。保留v3大版本、schema 3.0及52个色卡家族；不覆盖现有分析流程。
<!-- STYLE_GALLERY_V3_1:END -->
