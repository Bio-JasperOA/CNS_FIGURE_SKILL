# CNS Figure Skill · v3

Publication-oriented figure infrastructure for **single-cell RNA-seq, spatial transcriptomics, cross-modal biology, developmental/embryo studies, and biological foundation-model evaluation**.

The repository keeps the **v3 major version** and **FigureSpec 3.0**, with a complete pipeline-first visualization runtime layered on the original strict figure-audit system.

> The Skill renders reviewed upstream results. It does not rerun biological/statistical analyses and does not claim that a figure is automatically “CNS-approved”.

## Current status

The pipeline runtime covers **36/36 registered analysis modules**:

- scRNA-seq: **13**
- spatial transcriptomics: **11**
- cross-modal analysis: **4**
- development / embryo: **4**
- foundation-model evaluation: **4**

The registry contains **141 required figure assignments**, **107 advanced figure assignments**, and **240 unique plot targets** across **23 canonical result contracts**.

The complete pipeline runtime is CI-tested, and the style gallery publication workflow currently verifies **26 minimal/advanced figure families**, **54 standalone no-subtitle exports**, and a **26-page paired gallery PDF**.

All figures follow the repository-wide rule: **no subtitle renderer**.

## Modern Editorial color system

The default automatic color policy is now **`modern_editorial`**: light-background, low-saturation palettes designed to avoid the dark, high-chroma “analysis software screenshot” look.

New default palette layer:

- **E01–E12** — low-saturation categorical palettes for cell types, clusters and conditions;
- **L01–L06** — light sequential palettes for expression, abundance, probability, score, pseudotime and related scalar values;
- **V01–V04** — restrained diverging palettes for signed effects, residuals, correlations and centered activity scores.

Typical routing:

```text
2–6 categories    → E01
7–8 categories    → E02
9–10 categories   → E04
11–12 categories  → E06
13–16 categories  → E08
17–20 categories  → E09
>20 categories    → restrained high-capacity legacy palette

expression        → L01
activation/score  → L02
pseudotime/latent → L03
abundance/prob.   → L04
signed effect     → V01
correlation/z     → V02
residual/delta    → V03
pathway activity  → V04
```

The new continuous palettes deliberately avoid black endpoints. Existing palette assets are retained for compatibility and high-capacity use; they are no longer the preferred automatic defaults.

Use the modern policy explicitly:

```json
{"palette_policy": "modern_editorial"}
```

Use legacy automatic behavior when necessary:

```json
{"palette_policy": "legacy"}
```

Or lock a specific legacy palette:

```json
{"categorical_preset": "C19", "palette_lock": true}
```

Real-data projects that provide an explicit biological identity → color mapping keep that mapping by default. The automatic editorial router is primarily responsible for cases where Codex/the plotting runtime would otherwise choose a palette itself.

[Modern palette definitions](singlecell-spatial-figures/style_gallery/modern_palette_presets_v32.json) · [Style gallery documentation](singlecell-spatial-figures/style_gallery/README.md)

## Architecture

```text
Reviewed upstream analysis result
        │
        ▼
Canonical result contract
        │
        ▼
Pipeline module
        │
        ├── required figures
        ├── advanced figures
        └── publication/review panels
        │
        ▼
PNG / PDF / SVG + manifest.json + input hashes
```

The plotting layer does not rerun Seurat, Scanpy, CellRank, scVelo, CellChat, LIANA, Milo, scCODA, Squidpy, cell2location, Tangram, scVI, or related scientific methods. Missing significance, confidence intervals, trajectories, segmentation boundaries, neighborhood definitions, transition probabilities, mapping confidence, or uncertainty are never invented for visual completeness.

## Start here

- [Skill entry](singlecell-spatial-figures/SKILL.md)
- [Pipeline-first runtime](singlecell-spatial-figures/pipeline_tree/README.md)
- [Complete analysis → figure tree](singlecell-spatial-figures/pipeline_tree/PIPELINE_TREE.md)
- [Executable module registry](singlecell-spatial-figures/pipeline_tree/IMPLEMENTED_MODULES.json)
- [Canonical result contracts](singlecell-spatial-figures/pipeline_tree/RESULT_CONTRACTS.json)
- [Capability registry](singlecell-spatial-figures/CAPABILITIES.json)
- [Runtime notes](singlecell-spatial-figures/pipeline_tree/RUNTIME.md)
- [26-family style gallery](singlecell-spatial-figures/style_gallery/examples/README.md)
- [Generated figure files](singlecell-spatial-figures/style_gallery/examples/figures/)

## Pipeline-first usage

Example: render a reviewed single-cell annotation result.

```bash
cd singlecell-spatial-figures

python pipeline_tree/run_pipeline.py \
  --module scrna.annotation \
  --input markers=results/markers.csv \
  --input embedding=results/embedding.csv \
  --config project/annotation.json \
  --out build/annotation
```

Each run writes the generated figures plus `manifest.json`, including input hashes, generated targets, palette policy, and explicit reasons for any conditional advanced targets that were skipped.

To exercise the complete runtime with deterministic synthetic fixtures:

```bash
python pipeline_tree/build_gallery.py --out build/pipeline_gallery
```

Synthetic fixtures validate software execution and layout behavior; they are not biological results.

## Analysis coverage

**scRNA-seq** — QC, normalization/HVG, integration, clustering, annotation, marker/DE, composition and differential abundance, pathway activity, trajectory, velocity/fate, communication, regulon/module analysis, perturbation/prediction.

**Spatial transcriptomics** — spatial QC, normalization/embedding, domains, expression, mapping/deconvolution, SVG/autocorrelation, neighborhood/niche, spatial communication, spatial gradient/trajectory, multi-section analysis, histology/morphology integration.

**Cross-modal** — reference mapping, marker validation, niche validation, communication validation.

**Development / embryo** — stage composition, lineage progression, spatial developmental gradients, virtual-embryo prediction.

**Foundation models** — latent-space evaluation, reconstruction/prediction, benchmarking, ablation/scaling.

## Figure design system

The reusable style gallery contains **26 figure families**, each with minimal and advanced variants. Advanced means adding a scientifically supported dimension such as comparison, uncertainty, hierarchy, matched structure, spatial context, lineage, transition structure, multimodal evidence, or prediction error—not merely more decoration.

[Browse the style gallery](singlecell-spatial-figures/style_gallery/README.md) · [Minimal / advanced examples](singlecell-spatial-figures/style_gallery/examples/README.md) · [Generated PNG/PDF/SVG files](singlecell-spatial-figures/style_gallery/examples/figures/) · [Design guide](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md)

Core visual rules:

- no subtitles;
- white/light background by default;
- low-saturation editorial automatic palettes;
- palette and numeric normalization are separate decisions;
- stable named colors should be reused for biological identities across figures;
- missing evidence is reported, not fabricated;
- standalone PDF/SVG outputs are publication candidates;
- raster contact sheets are review/navigation artifacts;
- advanced figures must add scientific information, not decorative complexity.

## Palette compatibility layer

The original palette library is retained for compatibility, source-authentic recipes, and high-capacity categorical use. Categorical mappings never silently cycle or interpolate when capacity is exceeded. Continuous palettes remain separate from `linear`, `two_slope`, `log`, `symlog`, `power`, and `boundary` normalization choices.

[Legacy palette index and usage](singlecell-spatial-figures/assets/palettes/README.md) · [Legacy palette preview](singlecell-spatial-figures/assets/palettes/preview.svg)

## Strict FigureSpec / final-carrier audit

The original v3 FigureSpec path remains available for strict scale, layout, PDF, carrier-placement, stale-review, and human-review checks.

```bash
cd singlecell-spatial-figures
python -m pip install -r requirements-v3.txt
python scripts/render_v3.py render examples/v3_software_qa/figure.yaml \
  --root examples/v3_software_qa \
  --out build/software_qa
python scripts/render_v3.py review build/software_qa
```

A successful render is still a draft. Final scientific interpretation, narrative hierarchy, and acceptance remain human responsibilities.

## Validation boundary

Current Python pipeline/runtime execution and the modern editorial style-gallery routing are CI-tested. The R bridge remains a shared-output wrapper and is **not** claimed to have native feature parity with the Python runtime. The synthetic gallery validates software behavior, not real-data biological validity or universal journal compliance.

No paper PDFs, user experiments, model weights, or font files are distributed with this repository.

## v3.2 publication gallery

**[26 类最简／高级图库](docs/GALLERY.md)** · [并排对照 PDF](singlecell-spatial-figures/style_gallery/examples/paired_gallery.pdf) · [直接查看生成图](singlecell-spatial-figures/style_gallery/examples/figures/)

![Advanced figure overview](docs/preview.png)

<!-- V3_2_PUBLICATION_NAV -->

## v3.2 publication gallery

**[26 类最简／高级图库](docs/GALLERY.md)** · [并排对照 PDF](singlecell-spatial-figures/style_gallery/examples/paired_gallery.pdf)

![Advanced figure overview](docs/preview.png)

<!-- STYLE_GALLERY_V3_2:START -->
## v3.2 · 26 类无副标题图形

[最简 / 高级实图对照](singlecell-spatial-figures/style_gallery/examples/README.md) · [设计与来源](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [验证](singlecell-spatial-figures/style_gallery/QA_REPORT.md)

原入口升级为 26 类图；高级版补充数据支持的比较、分层、空间轮廓和质量结构，不只是额外标签。所有图无 subtitle。附 52 张常规范例、100 类别的两版图与完整色键；附带数据全部是合成测试。保留 v3 大版本、schema 3.0 和已有 52 色卡家族。本地更新不等于 GitHub 已推送；远端状态另查提交。
<!-- STYLE_GALLERY_V3_2:END -->
