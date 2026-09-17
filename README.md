# CNS Figure Skill · v3

Research design, question-driven bioinformatics strategy, and publication-oriented figures for **single-cell / single-nucleus RNA-seq, spatial transcriptomics, cross-modal biology, development / embryos, and biological foundation models**.

The repository keeps **Skill major version 3** and **FigureSpec 3.0**. Planning instructions and executable plotting programs are different capabilities: an analysis strategy selects an approach; a renderer draws reviewed results; neither automatically proves a biological conclusion.

<!-- RESULT_INTERPRETATION:START -->
## Result interpretation · 结果解读

`task_mode: results-interpret` 用于解读已经产生的实验/生信结果，不是重新制定整个课题，也不只是润色 Results。入口：[Result Interpretation Skill](singlecell-spatial-figures/result_interpretation/SKILL.md)。

```text
读取 AGENTS.md、STRATEGY_ROUTES.json 和结果解读 Skill。
task_mode: results-interpret
interpretation_depth: full
response_language: zh
execution: plan_only
inputs:
  question: project/research_question.md
  results: project/results/
  sample_metadata: project/samples.csv
  analysis_log: project/logs/
  data_profile: project/profile.json   # 已有时复用；不是必需文件
output_dir: project/interpretation
先读取实际结果，区分观察、解释、机制假设和已验证结论。
逐项核对比较方向、效应、区间、分母、独立重复和来源。
按问题组织证据，保留阴性/矛盾结果，并提出最能区分替代解释的下一步。
不要用文献常识补造我的实验结果，不要为了叙事添加未完成的验证。
```

这些项目路径需替换为真实文件。`quick` 产生重点解读；`full` 增加逐结果解释、证据链、主张与矛盾记录；`manuscript` 再输出相互独立的 Results 和 Discussion 草稿。在此路线中 `plan_only` 表示只读解读和报告，不运行新生信分析；不会阻止输出解读文本。

如已有数据自适应模块，复用其 profile、字段语义和输入绑定；没有时本模块仍可从实际结果及元数据开始。支持单细胞/空间/轨迹/通讯/模型结果，以及 qPCR、蛋白、成像、流式、功能、扰动和救援实验。针对实际测量和研究设计解释，不把所有读数都升级成“机制”。

结构化证据记录可用独立 CLI 校验（从仓库根目录运行）：

```bash
python -m pip install 'jsonschema>=4.18,<5'
python singlecell-spatial-figures/result_interpretation/review_results.py packet \
  project/interpretation/result_bundle.json \
  --root project --verify-files --out project/interpretation/checked
```

`review_results.py` 校验 schema、声明的证据关系、文件哈希和显式 CSV/TSV 数值绑定，输出 `audit.json` 与 `review_packet.md`；它不自动阅读所有 assay、不拟合模型、不验证自由文本的全部生物学含义，也不自动签署科学结论。真正的解读由 agent 按 Skill 读取材料后完成，人工审核保持 pending。

[Assay-aware playbook](singlecell-spatial-figures/result_interpretation/ASSAY_PLAYBOOK.md) · [Narrative patterns](singlecell-spatial-figures/result_interpretation/NARRATIVE_PLAYBOOK.md) · [Literature and read scope](singlecell-spatial-figures/result_interpretation/LITERATURE_LOGIC.md) · [Synthetic worked example](singlecell-spatial-figures/result_interpretation/examples/synthetic_multimodal.json)
<!-- RESULT_INTERPRETATION:END -->

## Invocation

**先按任务选择入口，再提供输入。** 以下 `task_mode` 是本仓库定义的 agent 任务标签，**不是 shell 命令，也不是自动安装的 slash command**。在能读取本仓库的 Codex / agent 工作目录中粘贴提示词，并要求先读取 `AGENTS.md` 和 `STRATEGY_ROUTES.json`。只给一个 GitHub 链接，不等于执行环境已获得仓库文件。

[机器可读调用定义](STRATEGY_ROUTES.json) · [Agent 路由规则](AGENTS.md)

| `task_mode` | 什么时候使用 | 主要入口 | 产出与能力边界 |
|---|---|---|---|
| `research-design` | 选题、拆解论文逻辑、评价研究证据链 | [Research Logic Skill](singlecell-spatial-figures/research_logic/SKILL.md) | 研究问题、候选主张、证据链、验证与失败条件；不执行分析 |
| `analysis-plan` | 已有科学问题，选择单细胞 / 空间生信分析路线 | [Analysis Strategy Skill](singlecell-spatial-figures/research_logic/ANALYSIS_SKILL.md) | 最小主线、可选模块、输入输出、诊断和不推荐的分析；不运行算法 |
| `analysis-code` | 把已审阅分析计划落成 R / Python 代码 | [Analysis Execution Contract](singlecell-spatial-figures/research_logic/ANALYSIS_EXECUTION.md) | 由 agent 编写项目脚本、环境、检查及绘图结果表导出；不是预置的一键生信流水线 |
| `results-interpret` | 解读实际实验/生信结果，构建证据链，处理阴性/矛盾结果 | [Result Interpretation Skill](singlecell-spatial-figures/result_interpretation/SKILL.md) | 解读报告与可追溯叙事；不自动证明机制或运行新分析 |
| `plot-single` | 已有结果表，只画一种图 | [Style Gallery](singlecell-spatial-figures/style_gallery/README.md) | `render.py plot`：一种图的 `minimal` 或 `advanced` 版本 |
| `plot-pipeline` | 已有某个分析过程的全部结果，生成配套图组 | [Pipeline Runtime](singlecell-spatial-figures/pipeline_tree/README.md) | `run_pipeline.py --module ...`：模块图片、manifest 与跳过原因；不执行同名分析 |
| `figure-audit` | 严格组图、尺度 / 布局 / 导出 / 最终载体检查 | [FigureSpec / Audit Skill](singlecell-spatial-figures/SKILL.md) | `render_v3.py`：FigureSpec 渲染或 PDF / carrier / review 检查；人工验收仍必需 |
| `end-to-end` | 从研究设计依次推进到分析、结果审核和绘图 | [AGENTS.md](AGENTS.md) | 分阶段编排以上入口；默认先产计划，不是一个端到端算法命令 |

### 最简调用模板

把下面整段作为提示词，不是在终端执行：

```text
先读取本仓库 AGENTS.md 和 STRATEGY_ROUTES.json，按指定 task_mode 调用对应入口。
task_mode: analysis-plan
language: R
execution: plan_only
inputs:
  brief: project/research_question.md
  data_inventory: project/data_inventory.md
  sample_sheet: project/samples.csv
output_dir: project/plan
目标：为我的 scRNA-seq + 空间转录组课题制定可检验的分析主线。
逐步说明问题、输入、独立重复单位、方法选择理由、结果、诊断、验证和配套图。
不要自动增加与研究问题无关的 CellChat、轨迹或其他高级分析。
```

`inputs` 中的项目路径是示例，使用前替换成真实文件。已有充分的研究计划时直接进入下游，不重复要求用户重新定义课题。输入不足时列明缺口；不能用合成数据补齐真实研究。

`execution` 的定义是：`plan_only` 只规划；`write_code` 编写代码和运行说明；`run_approved` 执行用户明确指定且前提已满足的步骤。只有实际执行并检查过，才能报告分析完成。直接调用下文绘图 CLI 会立即运行渲染，不受提示词字段控制。

### 1. 调用研究逻辑：research-design

```text
读取 AGENTS.md 和 STRATEGY_ROUTES.json。
task_mode: research-design
execution: plan_only
study_pattern: development_embryo
inputs: project/brief.md, project/data_inventory.md
output_dir: project/research_plan
基于 Research Logic Skill 拆解问题，提出待检验主张、替代解释、证据链和验证设计。
输出研究计划与 figure story；需要 JSON 时符合 RESEARCH_PLAN_SCHEMA.json。
先区分文献事实、我的现有证据和待验证假设，不把计划写成已证实结论。
```

可选 `study_pattern` 使用现有研究计划 schema 中的枚举：`atlas_discovery`、`development_embryo`、`spatial_ecology`、`foundation_model`、`perturbation_causal`、`multimodal_bridge`、`hybrid`。它们是研究设计类型，不是分析执行命令；`hybrid` 只在确实需要组合路径时使用。聚焦的小问题可以先输出 Markdown，不强行填满完整论文 schema。

文献入口：[CNS anchors](singlecell-spatial-figures/research_logic/CNS_ANCHORS.md) · [Paper Logic Library](singlecell-spatial-figures/research_logic/PAPER_LOGIC_LIBRARY.md)。引用具体结论时回到实际原文核查，不将案例库当成原文的替代。

### 2. 调用生信分析策略：analysis-plan

```text
读取 AGENTS.md 和 STRATEGY_ROUTES.json。
task_mode: analysis-plan
language: R
execution: plan_only
inputs: project/research_plan.md, project/data_inventory.md, project/samples.csv
analysis_modules: [sc.annotation, sc.composition_da, sc.de, spatial.mapping_deconvolution, spatial.niche]
output_dir: project/analysis_plan
按 ANALYSIS_SKILL.md 和 ANALYSIS_STRATEGY_CATALOG.json 审查上述候选模块。
区分必需主线、条件触发的可选分析和应排除的分析；不要求候选模块全部执行。
对每步写清输入 → 方法家族 → 结果 → 支持的主张 → 诊断 → 验证 → 绘图交接。
```

[Analysis Strategy Library](singlecell-spatial-figures/research_logic/ANALYSIS_STRATEGY_LIBRARY.md) 解释路线；[Analysis Catalog](singlecell-spatial-figures/research_logic/ANALYSIS_STRATEGY_CATALOG.json) 定义合法策略 ID、最低输入和推断边界。`analysis_modules` 可省略，让 agent 根据问题选择，而不是默认运行所有模块。

### 3. 生成或执行分析代码：analysis-code

```text
读取 AGENTS.md 和 STRATEGY_ROUTES.json。
task_mode: analysis-code
language: R
execution: write_code
inputs: project/analysis_plan.md, project/data_inventory.md, project/samples.csv
output_dir: project/analysis
按 ANALYSIS_EXECUTION.md 编写可复用分析脚本、配置、环境声明、输入检查和 RUN.md。
先检查实际 assay/layer、样本配对与独立重复单位；不要改变已审阅的比较设计。
每步导出配套诊断结果，并为后续绘图生成符合 RESULT_CONTRACTS.json 的结果表。
本次只写代码，不报告分析已经运行；未验证的依赖和步骤必须标明。
```

需要实际执行时，把 `execution` 改为 `run_approved` 并提供可访问的数据、已明确的执行范围和计算资源。R / Python / mixed 是分析实现偏好；方法是否可用须检查环境。当前没有一个接收原始数据并自动运行全部 Seurat / Scanpy / CellChat / CellRank 等方法的统一 CLI。

### 4. 单图：plot-single

```text
读取 AGENTS.md 和 STRATEGY_ROUTES.json。
task_mode: plot-single
plot_kind: heatmap
plot_mode: advanced
inputs: results/reviewed_heatmap.csv, project/heatmap.json
output_dir: build/heatmap
使用 style_gallery/render.py，只绘制已审核数值；保持现有配色和无 subtitle 规则。
不要重新做差异分析或补造区间，导出 PNG/PDF/SVG 及 QA。
```

`plot_kind` 从 [26-family catalogue](singlecell-spatial-figures/style_gallery/catalogue_v32.json) 选择，例如 `embedding`、`dotplot`、`heatmap`、`composition`、`volcano`、`forest`、`spatial`、`network`、`trajectory`、`trajectory_heatmap`。`plot_mode` 只有 `minimal` / `advanced`；**`panel` 不是这个 CLI 的合法模式**。Advanced 使用额外的真实输入信息，不是装饰性升级。

### 5. 分析配套图组：plot-pipeline

```text
读取 AGENTS.md 和 STRATEGY_ROUTES.json。
task_mode: plot-pipeline
plot_module: scrna.annotation
inputs:
  markers: results/markers.csv
  embedding: results/embedding.csv
  config: project/annotation.json
output_dir: build/annotation
按 IMPLEMENTED_MODULES.json 检查所有 named inputs，再调用 run_pipeline.py。
生成当前模块支持的图片和 manifest；缺少高级图所需字段时记录原因，不伪造数据。
```

每个模块的输入键不同。上例必须是 `markers=...` 与 `embedding=...`，不能一律写成 `main=...`。见 [Executable Module Registry](singlecell-spatial-figures/pipeline_tree/IMPLEMENTED_MODULES.json) 和 [Result Contracts](singlecell-spatial-figures/pipeline_tree/RESULT_CONTRACTS.json)。`required_targets` 是映射目标，是否实际生成仍受输入条件和实现边界约束；检查 manifest，不把目标清单当作全部生成的证明。

### 6. 严格组图 / 载体审核：figure-audit

```text
读取 AGENTS.md 和 STRATEGY_ROUTES.json。
task_mode: figure-audit
inputs: project/figure.yaml, results/, final/report.pdf, project/placement.json
output_dir: build/Fig1
根据已提供文件选择 FigureSpec 渲染、PDF 检查或载体检查，不能假设所有文件都存在。
区分自动检查和人工审阅，保留未通过项，不自动签署科学结论或修改数据。
```

FigureSpec 支持的 renderer 与 26 类单图不是同一个注册表，不得把任意 `plot_kind` 填成 FigureSpec renderer。也不能把 style-gallery 的 `.qa.json` 当成完整 FigureSpec review 工程。

### 7. 整体项目：end-to-end

```text
读取 AGENTS.md 和 STRATEGY_ROUTES.json。
task_mode: end-to-end
language: mixed
execution: plan_only
inputs: project/brief.md, project/data_inventory.md, project/samples.csv
output_dir: project/work
依次使用 research-design → analysis-plan → analysis-code → 结果审核 → 绘图 → figure-audit。
本次先输出分阶段计划、缺失输入和交付清单；不提前生成研究结果。
已有且通过检查的阶段直接复用，不为凑流程重复执行。
```

## Analysis strategy IDs versus plotting IDs

**分析策略 ID 不等于绘图模块 ID。** 两者的完整候选交接关系定义在 [STRATEGY_ROUTES.json](STRATEGY_ROUTES.json) 的 `analysis_to_plot` 中，覆盖当前 20 个分析策略。映射只表示“哪些图可能接收这类分析的结果”，不表示已实现分析算法，也不进行自动字段转换。

| 分析策略 | 绘图模块举例 | 使用条件 |
|---|---|---|
| `sc.de` | `scrna.markers_de` | 模块需要 `markers` 和 `de`；只有 DE 表时可改用单图，不补造 marker 数据 |
| `sc.pathway` | `scrna.pathway_activity` | 分别检查 activity、enrichment、GSEA 输入 |
| `sc.trajectory` | `scrna.trajectory` | 需要 trajectory 和 embedding 表；拟合趋势 / 区间来自上游 |
| `spatial.svg` | `spatial.svg_autocorrelation` | 需要 effects、moran、spatial 三类输入 |
| `spatial.niche` | `spatial.neighborhood_niche` | 需要 spatial 和 interaction，不能仅凭坐标伪造 niche |
| `crossmodal.sc_to_spatial` | `cross_modal.reference_mapping` | 需要 reference 和 spatial；验证图另查对应模块输入 |

目录里尚未定义的分析先按 `analysis-plan` 说明问题、前提和输出，必要时扩展 catalog / handoff / tests；不要发明不存在的 module ID 或自动冒称有 renderer。绘图 runtime 覆盖面大于当前策略 catalog，两者不要求数量一致。

## Terminal quick start

**以下命令全部从仓库根目录运行**。项目路径需要先准备；只有标为 synthetic smoke test 的命令直接使用随库测试数据。提示词中的 `task_mode` 等字段不是这些脚本的参数。

Python 环境可参考 CI 使用的 Python 3.13；不要将未实际测试的环境称为已验证。仅浏览策略文档不需要安装绘图依赖。

```bash
# Linux/macOS: isolated Python environment for rendering and validation
python -m venv .venv
source .venv/bin/activate
python -m pip install -r singlecell-spatial-figures/requirements-v3.txt \
  -r singlecell-spatial-figures/style_gallery/requirements-tested.txt

# Inspect supported CLI arguments and module choices
python singlecell-spatial-figures/style_gallery/render.py plot --help
python singlecell-spatial-figures/pipeline_tree/run_pipeline.py --help
```

### Validate a plan, rather than execute its analyses

```bash
# Synthetic/example research-plan contract check
python singlecell-spatial-figures/research_logic/validate_research_plan.py \
  singlecell-spatial-figures/research_logic/templates/research_plan.example.json

# A real project plan, after it has been authored
python singlecell-spatial-figures/research_logic/validate_research_plan.py \
  project/research_plan.json
```

This validator checks schema and selected explicit consistency rules. It does not read datasets, detect every confounder, prove absence of leakage, or certify the reasoning.

### Render a single chart

```bash
# Runnable synthetic smoke test; writes to build/, not repository examples/
python singlecell-spatial-figures/style_gallery/render.py plot \
  --kind heatmap \
  --input singlecell-spatial-figures/style_gallery/examples/source_data/heatmap.csv \
  --config singlecell-spatial-figures/style_gallery/examples/source_data/heatmap.json \
  --mode advanced --out build/smoke/heatmap

# Real reviewed data: prepare both input files first
python singlecell-spatial-figures/style_gallery/render.py plot \
  --kind heatmap --input results/reviewed_heatmap.csv \
  --config project/heatmap.json --mode advanced --out build/Fig1
```

Real-data configs use `demo: false` and a nonempty, accurate `provenance`, with explicit units, limits, ordering and value definitions where required. Example configs retain synthetic-data status and must not be reused unchanged for real results.

### Render analysis-module results

```bash
# Annotation
python singlecell-spatial-figures/pipeline_tree/run_pipeline.py \
  --module scrna.annotation \
  --input markers=results/markers.csv --input embedding=results/embedding.csv \
  --config project/annotation.json --out build/annotation

# Trajectory: both named inputs are required
python singlecell-spatial-figures/pipeline_tree/run_pipeline.py \
  --module scrna.trajectory \
  --input main=results/trajectory.csv --input embedding=results/embedding.csv \
  --config project/trajectory.json --out build/trajectory

# Spatial niche: these tables are reviewed upstream results, not raw inputs
python singlecell-spatial-figures/pipeline_tree/run_pipeline.py \
  --module spatial.neighborhood_niche \
  --input spatial=results/spatial_points.csv --input interaction=results/niche_interactions.csv \
  --config project/niche.json --out build/niche

# Entire deterministic synthetic pipeline gallery
python singlecell-spatial-figures/pipeline_tree/build_gallery.py --out build/pipeline_gallery
```

Each module writes figures and a `manifest.json` with input hashes, generated targets and skip reasons. A rendered communication or trajectory figure does not mean this command estimated communication or trajectories.

### FigureSpec and final-carrier checks

```bash
# Runnable synthetic FigureSpec example
python singlecell-spatial-figures/scripts/render_v3.py render \
  singlecell-spatial-figures/examples/v3_software_qa/figure.yaml \
  --root singlecell-spatial-figures/examples/v3_software_qa --out build/software_qa

# Review requires a genuine completed human-review record; initially it should fail
python singlecell-spatial-figures/scripts/render_v3.py review build/software_qa

# Independent inspection of an exported PDF
python singlecell-spatial-figures/scripts/render_v3.py inspect-pdf \
  build/Fig1.pdf --out build/Fig1_pdf_audit.json

# Real placement metadata is required; do not guess page or millimetre coordinates
python singlecell-spatial-figures/scripts/render_v3.py carrier \
  build/Fig1.pdf final/report.pdf project/placement.json --out build/carrier_audit.json
```

Use [the main Skill](singlecell-spatial-figures/SKILL.md) for binding export/carrier reports to a FigureSpec project and handling stale reviews. Standalone gallery figures can be inspected as PDFs; a full review gate requires its own valid FigureSpec project artifacts.

## R and Python boundaries

Research and analysis strategies are language-independent. `analysis-code` can request native R, Python or mixed project scripts. Current gallery and pipeline rendering CLIs are Python. The existing R bridge shares prepared Python outputs and is not a native equivalent of all 36 modules or 26 gallery families. Read the [main Skill](singlecell-spatial-figures/SKILL.md) before using the R bridge; passing Python tests does not establish R test coverage.

## Current coverage

The plotting runtime registers **36 modules**: scRNA-seq 13, spatial 11, cross-modal 4, development / embryo 4, and foundation models 4. The pipeline map contains **141 required figure assignments**, **107 advanced assignments**, **240 unique plot targets**, and **23 canonical result contracts**. These are inventory counts, not a guarantee that every target is implemented or generated for every input.

The style gallery contains **26 minimal/advanced families**, **54 standalone examples** including the high-category examples, and a **26-page paired PDF**. The analysis-strategy catalog currently defines **20 selection modules**. See the live registries and reports for implemented, conditional and skipped behavior.

[Pipeline tree](singlecell-spatial-figures/pipeline_tree/PIPELINE_TREE.md) · [Runtime notes](singlecell-spatial-figures/pipeline_tree/RUNTIME.md) · [Capabilities](singlecell-spatial-figures/CAPABILITIES.json) · [Research Logic overview](singlecell-spatial-figures/research_logic/README.md)

## Visual defaults — unchanged by this documentation update

Keep the existing **no-subtitle** rule, white background, low-saturation `modern_editorial` policy, aligned legends and no explanatory microcopy on the canvas. Essential axis labels, units, legend labels, scientific annotations and synthetic-data identification remain distinct from explanatory footnotes. Preserve interpretation details in captions and provenance.

The default palette layer is **E01–E12** categorical, **L01–L06** sequential and **V01–V04** diverging. Typical category routing is E01 for 2–6, E02 for 7–8, E04 for 9–10, E06 for 11–12, E08 for 13–16 and E09 for 17–20; higher category counts use the existing high-capacity fallback rather than recycling colors. Scalar choices depend on the value's meaning and are separate from numeric normalization.

```json
{"palette_policy": "modern_editorial"}
```

Legacy behavior remains explicitly selectable with `{"palette_policy":"legacy"}` or a locked preset such as `{"categorical_preset":"C19","palette_lock":true}`. Preserve real-data named identity-color maps where supplied. Gallery auto-routing is not a promise that the separate FigureSpec scale resolver uses identical preset IDs: define its supported scales explicitly.

[Modern palette definitions](singlecell-spatial-figures/style_gallery/modern_palette_presets_v32.json) · [Design guide](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [Legacy palette library](singlecell-spatial-figures/assets/palettes/README.md)

## Validate invocation definitions

```bash
# Standard-library-only route/link/ID checks plus negative regression cases
python .github/scripts/validate_strategy_routes.py --self-test
```

Research-logic CI checks these route definitions, referenced files, analysis-to-plot IDs and README coverage. This is documentation/contract validation, not a new biological-analysis benchmark. Original plotting code, palette definitions and example image assets are unchanged by this update.

## Validation boundary

The pipeline consumes reviewed result tables. It never invents missing significance, intervals, spatial boundaries, niche labels, fitted trajectories, fate probabilities or model uncertainty. Strategy prompts guide decisions; authored analysis code needs its own execution and scientific checks. Synthetic tests establish software behavior, not biological validity or journal approval. Raster review panels are not substitutes for standalone vector outputs.

No paper PDFs, private experiments, model weights or font files are distributed with this repository.

<!-- V3_2_PUBLICATION_NAV -->
## v3.2 publication gallery

[26 类最简 / 高级图库](docs/GALLERY.md) · [配对示例 PDF](singlecell-spatial-figures/style_gallery/examples/paired_gallery.pdf) · [全部生成图](singlecell-spatial-figures/style_gallery/examples/figures/)

![Advanced figure overview](docs/preview.png)

<!-- STYLE_GALLERY_V3_2:START -->
## v3.2 · 26 类无副标题图形

[最简 / 高级实图对照](singlecell-spatial-figures/style_gallery/examples/README.md) · [设计与来源](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [验证](singlecell-spatial-figures/style_gallery/QA_REPORT.md)

保留 v3 大版本与 FigureSpec 3.0。图库测试数据为合成示例；真实研究始终先审阅结果，再调用绘图层。
<!-- STYLE_GALLERY_V3_2:END -->
