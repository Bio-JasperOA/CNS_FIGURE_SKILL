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

<!-- STYLE_GALLERY_V3_2:START -->
## v3.2 · 26 类无副标题图形

[最简 / 高级实图对照](singlecell-spatial-figures/style_gallery/examples/README.md) · [设计与来源](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [验证](singlecell-spatial-figures/style_gallery/QA_REPORT.md)

原入口升级为 26 类图；高级版补充数据支持的比较、分层、空间轮廓和质量结构，不只是额外标签。所有图无 subtitle。附 52 张常规范例、100 类别的两版图与完整色键；附带数据全部是合成测试。保留 v3 大版本、schema 3.0 和已有 52 色卡家族。本地更新不等于 GitHub 已推送；远端状态另查提交。
<!-- STYLE_GALLERY_V3_2:END -->


<!-- V3_2_PUBLICATION_NAV -->

## v3.2 publication gallery

**[26 类最简／高级图库](docs/GALLERY.md)** · [并排对照 PDF](singlecell-spatial-figures/style_gallery/examples/paired_gallery.pdf)

![Advanced figure overview](docs/preview.png)
