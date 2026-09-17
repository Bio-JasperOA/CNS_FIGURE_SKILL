# CNS Figure Skill — Usage Scenarios & Examples

# CNS Figure Skill — 使用场景与调用示例

This document explains **when to use CNS Figure Skill, which module to call, what information to provide, and what output to expect**. It is intended as a framework-level guide for researchers and AI agents rather than a complete API reference.

本文用于说明 **CNS Figure Skill 在什么场景下使用、应该调用哪个模块、需要提供什么信息，以及预期得到什么结果**。它是一份面向科研用户与 AI Agent 的框架性使用指南，而不是底层 API 手册。

> Repository-level `task_mode` values are routing labels for an AI agent/Codex workflow. They are not shell commands. Direct plotting and pipeline rendering additionally provide executable Python CLIs.
>
> 仓库中的 `task_mode` 是供 AI Agent/Codex 选择工作路线的任务标签，并不是终端命令。直接绘图和 pipeline 图组另外提供可执行的 Python CLI。

---

## 1. What problem does this Skill solve? · 这个 Skill 解决什么问题？

CNS Figure Skill is designed for projects in which the following stages must remain connected but distinguishable:

CNS Figure Skill 适用于需要把以下阶段保持关联、同时又明确区分的科研项目：

```text
Biological question / 生物学问题
        ↓
Research design / 研究设计
        ↓
Analysis strategy / 分析策略
        ↓
Analysis implementation / 分析实现
        ↓
Result interpretation / 结果解读
        ↓
Scientific figures / 科学绘图
        ↓
Final figure audit / 最终图形审核
```

The Skill does not assume that every project must run every module. The correct route is the **smallest route that answers the current research task**.

本 Skill 不要求每个项目都运行全部模块。正确的使用方式是选择 **能够回答当前科研任务的最小工作路线**。

---

## 2. Choose a route by scenario · 按使用场景选择模块

| Research scenario / 使用场景 | Recommended route / 推荐模块 | Typical output / 典型输出 |
|---|---|---|
| I have an idea but the biological question is still vague. / 有研究想法，但科学问题还不清楚。 | `research-design` | Research question, candidate claims, alternatives, evidence chain, validation logic. / 科学问题、候选主张、替代解释、证据链与验证逻辑。 |
| I already know the question and need to decide what analyses are necessary. / 已明确问题，需要确定应该做哪些分析。 | `analysis-plan` | Minimal defensible analysis chain, diagnostics, inputs/outputs, optional analyses. / 最小可辩护分析主线、诊断、输入输出及条件性高级分析。 |
| I already have an approved analysis plan and need executable R/Python code. / 已有分析方案，需要生成可执行 R/Python 代码。 | `analysis-code` | Project scripts, environment, input checks, result-table exports and run instructions. / 项目脚本、环境、输入检查、结果表输出及运行说明。 |
| I already have analysis or experimental results and need to understand what they mean. / 已有实验或生信结果，需要系统解读。 | `results-interpret` | Observation → interpretation → alternatives → claim boundary → next validation. / 观察 → 解读 → 替代解释 → 结论边界 → 下一步验证。 |
| I have one reviewed table and only need one publication-style plot. / 已有一个审核后的结果表，只需要画一张图。 | `plot-single` | PNG/PDF/SVG plus QA metadata. / PNG/PDF/SVG 与 QA 信息。 |
| I completed one analysis module and want the complete associated figure set. / 已完成某个分析模块，希望生成整套配套图。 | `plot-pipeline` | Required + advanced figures, manifest and skipped reasons. / 必需图 + 高级图、manifest 与跳过原因。 |
| I already have a final figure or report and need layout/export checking. / 已有最终 Figure 或报告，需要检查版式和导出。 | `figure-audit` | Scale/layout/export/carrier audit and review records. / 尺度、布局、导出和最终载体审核。 |
| I want an agent to coordinate the entire project from question to figures. / 希望 Agent 从科学问题一路组织到最终绘图。 | `end-to-end` | Staged workflow with explicit status for each step. / 分阶段科研工作流，并记录每一步状态。 |

---

## 3. General agent invocation pattern · 通用 Agent 调用框架

For most tasks, begin with the following structure:

大多数任务可以从以下框架开始：

```text
Read AGENTS.md and STRATEGY_ROUTES.json first.
先读取 AGENTS.md 和 STRATEGY_ROUTES.json。

task_mode: <route>
execution: <plan_only | write_code | run_approved>
language: <R | Python | mixed>          # when relevant / 需要时填写
inputs:
  <real project files>
output_dir: <project output directory>

Research objective / 研究目标:
<state the actual scientific question or task>

Constraints / 约束:
- use actual project data only
- do not fabricate missing statistics or biological evidence
- separate observation from interpretation
- keep plotting downstream of reviewed results
```

The three `execution` modes mean:

三个 `execution` 模式分别表示：

- `plan_only` — planning or read-only interpretation; no analysis execution. / 仅规划或只读结果解读，不执行分析。
- `write_code` — write project-specific code and run instructions, but do not claim it has been executed. / 编写项目代码和运行说明，但不声称已经执行。
- `run_approved` — execute the explicitly requested scope when actual files and dependencies are available. / 在真实文件和依赖满足时执行用户明确授权的范围。

---

# 4. Module examples · 各模块使用示例

## 4.1 `research-design` — from idea to a testable research question

## 4.1 `research-design` — 从研究想法到可检验科学问题

Use this route when the project is still being designed. The goal is not to list methods; it is to define what biological claim the project could actually test.

当项目仍处于设计阶段时使用。重点不是堆叠方法，而是明确项目真正能够检验什么生物学主张。

### Example scenario · 示例场景

You have scRNA-seq and spatial transcriptomics data from multiple embryo stages and want to study a developmental transition, but you have not yet decided the central claim.

你拥有多个胚胎时期的 scRNA-seq 与空间转录组数据，希望研究一个发育转变过程，但还没有明确中心科学主张。

### Agent prompt · Agent 调用示例

```text
Read AGENTS.md and STRATEGY_ROUTES.json.
task_mode: research-design
execution: plan_only
study_pattern: development_embryo
inputs:
  brief: project/brief.md
  data_inventory: project/data_inventory.md
output_dir: project/research_plan

Define one answerable biological question around a developmental transition.
Separate measured developmental time from inferred pseudotime.
Construct candidate claims, alternative explanations, required evidence,
validation experiments and a figure-level story.
Do not select methods before the biological question is defined.
```

### Expected result · 预期结果

```text
Biological gap
→ central question
→ provisional central claim
→ 3–5 subclaims
→ evidence required for each claim
→ alternative explanations
→ validation/failure criteria
→ candidate figure story
```

---

## 4.2 `analysis-plan` — choose the smallest defensible analysis chain

## 4.2 `analysis-plan` — 选择最小可辩护分析主线

Use this route after the scientific question is sufficiently clear but before writing analysis code.

当科学问题已经明确，但还没有开始正式编写分析代码时使用。

### Example scenario · 示例场景

You want to test whether a treatment changes a specific cell state and its spatial localization.

你希望检验某种处理是否改变特定细胞状态及其空间定位。

```text
Read AGENTS.md and STRATEGY_ROUTES.json.
task_mode: analysis-plan
execution: plan_only
language: R
inputs:
  research_plan: project/research_plan.md
  data_inventory: project/data_inventory.md
  sample_sheet: project/samples.csv
analysis_modules:
  - sc.annotation
  - sc.composition_da
  - sc.de
  - spatial.mapping_deconvolution
  - spatial.niche
output_dir: project/analysis_plan

For each candidate module, decide whether it is required, optional or unnecessary.
For each retained step specify:
question → input → independence unit → method family → output → diagnostic
→ validation → limitation → plotting handoff.
Do not add trajectory or cell-cell communication unless the research question requires them.
```

### Key principle · 核心原则

A long pipeline is not automatically a stronger study. Every analysis should have a scientific or technical reason to exist.

分析流程越长并不代表研究越强。每一个分析步骤都必须有明确的科学问题或技术质量控制理由。

---

## 4.3 `analysis-code` — convert a reviewed plan into reproducible code

## 4.3 `analysis-code` — 将已审核分析方案落实为可复现代码

Use this route only after the comparison design, biological unit and analysis strategy have been reviewed.

只有在比较设计、独立生物学单位和分析路线已经审核后，才进入这一模块。

```text
Read AGENTS.md and STRATEGY_ROUTES.json.
task_mode: analysis-code
execution: write_code
language: R
inputs:
  analysis_plan: project/analysis_plan.md
  data_inventory: project/data_inventory.md
  sample_sheet: project/samples.csv
output_dir: project/analysis

Generate reusable project-specific analysis scripts.
Include:
- dependency/environment declaration
- input validation
- assay/layer checks
- sample and replicate checks
- analysis scripts
- diagnostic outputs
- reviewed result-table exports for downstream plotting
- RUN.md

Do not change the approved comparison design.
Do not claim that code has been executed when execution: write_code.
```

A typical project directory may look like:

典型项目目录可以是：

```text
project/analysis/
├── config/
├── scripts/
├── diagnostics/
├── results/
├── figures_input/
├── environment/
└── RUN.md
```

---

## 4.4 `results-interpret` — interpret actual results without overclaiming

## 4.4 `results-interpret` — 解读真实结果而不过度推断

Use this route when actual analysis or experimental outputs already exist.

当真实实验或生信结果已经产生时使用。

```text
Read AGENTS.md and STRATEGY_ROUTES.json.
task_mode: results-interpret
interpretation_depth: full
response_language: zh
execution: plan_only
inputs:
  question: project/research_question.md
  results: project/results/
  sample_metadata: project/samples.csv
  analysis_log: project/logs/
output_dir: project/interpretation

Interpret the actual results.
For each major result separate:
1. observation
2. biological meaning
3. plausible explanation
4. alternative explanations
5. evidence supporting or contradicting the explanation
6. conclusion boundary
7. discriminating next experiment or reanalysis

Retain important negative and contradictory results.
Do not use literature to invent measurements that are absent from this project.
```

The preferred reasoning structure is:

推荐的解读结构是：

```text
Observed result / 观察到什么
        ↓
What it supports / 能支持什么
        ↓
What it does NOT prove / 不能证明什么
        ↓
Alternative explanation / 替代解释
        ↓
Orthogonal or intervention evidence / 正交或干预证据
        ↓
Current claim boundary / 当前结论边界
```

---

## 4.5 `plot-single` — render one reviewed result table

## 4.5 `plot-single` — 将单个审核结果表绘制成发表级图形

Use this route when the upstream analysis is already complete and only one figure is needed.

当上游分析已经完成，只需要绘制一个结果图时使用。

### Agent-level request · Agent 层调用

```text
Read AGENTS.md and STRATEGY_ROUTES.json.
task_mode: plot-single
plot_kind: heatmap
plot_mode: advanced
inputs:
  table: results/reviewed_heatmap.csv
  config: project/heatmap.json
output_dir: build/heatmap

Render only the reviewed values.
Do not rerun differential analysis.
Do not fabricate missing intervals, significance or annotations.
Keep the no-subtitle policy.
```

### Direct CLI · 直接命令行

```bash
cd singlecell-spatial-figures/style_gallery
python render.py plot \
  --kind heatmap \
  --input reviewed_heatmap.csv \
  --config heatmap.json \
  --mode advanced \
  --out results/Fig1
```

`minimal` is the smallest scientifically complete version. `advanced` is allowed only when the input contains additional real scientific structure such as comparison, uncertainty, hierarchy, pairing or spatial context.

`minimal` 是最小科学完整版本；只有当输入中存在额外的真实科学信息，例如比较、不确定性、层级、配对或空间背景时，才应使用 `advanced`。

Common plot families include:

常用图形类型包括：

```text
embedding
spatial
dotplot
heatmap
composition
volcano
forest
upset
ridge
ecdf
hexbin
roc
precision_recall
calibration
confusion
gsea
network
trajectory
trajectory_heatmap
spatial_composition
```

See `singlecell-spatial-figures/style_gallery/catalogue_v32.json` for the registered catalogue.

完整注册图形类型见 `singlecell-spatial-figures/style_gallery/catalogue_v32.json`。

---

## 4.6 `plot-pipeline` — generate the figure set for one analysis module

## 4.6 `plot-pipeline` — 为一个分析模块生成完整配套图组

Use this route when an upstream analysis module has already produced all reviewed result tables required by a registered plotting module.

当某个上游分析模块已经产生了注册绘图模块所需的审核结果表时使用。

### Example: cell-type annotation · 示例：细胞类型注释

```text
Read AGENTS.md and STRATEGY_ROUTES.json.
task_mode: plot-pipeline
plot_module: scrna.annotation
inputs:
  markers: results/markers.csv
  embedding: results/embedding.csv
  config: project/annotation.json
output_dir: build/annotation

Validate the named inputs against IMPLEMENTED_MODULES.json and RESULT_CONTRACTS.json.
Render all supported required and advanced figures.
If an optional advanced figure lacks the required evidence, record it as skipped.
```

Direct CLI:

```bash
cd singlecell-spatial-figures
python pipeline_tree/run_pipeline.py \
  --module scrna.annotation \
  --input markers=results/markers.csv \
  --input embedding=results/embedding.csv \
  --config project/annotation.json \
  --out build/annotation
```

Other example registered modules include:

其他可调用模块示例包括：

```text
scrna.qc
scrna.integration
scrna.clustering
scrna.annotation
scrna.markers_de
scrna.composition_da
scrna.trajectory
scrna.velocity_fate
scrna.communication
scrna.regulon_module

spatial.qc
spatial.domains
spatial.expression
spatial.mapping_deconvolution
spatial.neighborhood_niche
spatial.communication
spatial.gradient_trajectory
spatial.multisection
spatial.histology_morphology

cross_modal.reference_mapping
cross_modal.marker_validation
cross_modal.niche_validation
cross_modal.communication_validation

development.stage_composition
development.lineage_progression
development.spatial_gradient
development.virtual_embryo_prediction

fm.latent_embedding
fm.reconstruction_prediction
fm.benchmark
fm.ablation_scaling
```

The definitive executable registry is:

最终以机器注册表为准：

- `singlecell-spatial-figures/pipeline_tree/IMPLEMENTED_MODULES.json`
- `singlecell-spatial-figures/pipeline_tree/RESULT_CONTRACTS.json`

---

## 4.7 `figure-audit` — audit final figures and placed outputs

## 4.7 `figure-audit` — 审核最终 Figure 与实际排版载体

Use this route when a figure has already been rendered and must be checked at publication size or after placement into a final PDF/report.

当 Figure 已经绘制完成，需要在最终尺寸或放入 PDF/报告后进行检查时使用。

```text
Read AGENTS.md and STRATEGY_ROUTES.json.
task_mode: figure-audit
inputs:
  figure_spec: project/figure.yaml
  results: results/
  final_pdf: final/report.pdf
  placement: project/placement.json
output_dir: build/Fig1

Check scale definitions, layout, legends, export properties and final placement.
Separate automated checks from human scientific review.
Do not modify data to make a figure pass visual inspection.
```

Typical executable checks include:

典型可执行检查包括：

```bash
python singlecell-spatial-figures/scripts/render_v3.py render \
  project/figure.yaml \
  --root project \
  --out build/Fig1

python singlecell-spatial-figures/scripts/render_v3.py review build/Fig1
```

For a figure already placed in a final PDF, use the carrier/bind-report workflow described in `singlecell-spatial-figures/SKILL.md`.

如果 Figure 已经放入最终 PDF，应使用 `singlecell-spatial-figures/SKILL.md` 中定义的 carrier/bind-report 流程检查实际载体。

---

## 4.8 `end-to-end` — coordinate a complete research workflow

## 4.8 `end-to-end` — 串联完整科研工作流

Use this mode when an agent is expected to coordinate multiple stages. It should not collapse all stages into one opaque pipeline.

当希望 Agent 协调多个科研阶段时使用。它不应该把所有步骤压缩成一个无法审查的黑箱流程。

```text
Read AGENTS.md and STRATEGY_ROUTES.json.
task_mode: end-to-end
execution: plan_only
inputs:
  brief: project/brief.md
  data_inventory: project/data_inventory.md
  sample_sheet: project/samples.csv
output_dir: project/workflow

Coordinate the project in this order:
research-design
→ analysis-plan
→ analysis-code
→ execution only when explicitly approved
→ diagnostics
→ results-interpret
→ plot-single or plot-pipeline
→ figure-audit when required.

For every stage report one status:
planned / code_written / executed / checked / skipped.
Do not treat a downstream figure as proof that an upstream analysis was executed correctly.
```

---

# 5. Typical combined use cases · 典型组合使用场景

## Case A — Starting a new scRNA-seq + spatial project

## 场景 A — 从零开始一个 scRNA-seq + 空间项目

```text
research-design
→ analysis-plan
→ analysis-code
→ run approved analysis
→ results-interpret
→ plot-pipeline
→ figure-audit
```

Use this when both the scientific question and analysis strategy need to be built systematically.

适用于需要同时系统建立科学问题与分析路线的新项目。

---

## Case B — Analysis is already finished; figures are poor

## 场景 B — 分析已经完成，但图不好看

```text
review existing result tables
→ plot-single or plot-pipeline
→ figure-audit
```

Do **not** restart research design or rerun statistics unless the existing result tables are scientifically insufficient.

除非现有结果本身存在科学问题，否则 **不需要** 重新做研究设计，也不应该为了绘图而重新进行统计分析。

---

## Case C — Results exist but the biological story is unclear

## 场景 C — 已有结果，但不知道应该如何解释

```text
results-interpret
↔ targeted analysis-plan / analysis-code only when needed
→ plotting
```

Interpretation may identify a missing discriminating analysis, but that new analysis should return through the analysis route rather than being silently performed during interpretation.

结果解读可以发现需要补做的关键分析，但新的分析应该重新进入 analysis 路线，而不是在“解读”过程中偷偷执行。

---

## Case D — Foundation-model / virtual embryo project

## 场景 D — Foundation Model / Virtual Embryo 项目

A typical route is:

典型路线可以是：

```text
research-design
  focus: biological utility, OOD definition, leakage, independent specimens
        ↓
analysis-plan
  benchmark + reconstruction/prediction + latent representation + ablation/scaling
        ↓
analysis-code
        ↓
results-interpret
        ↓
plot-pipeline
  fm.latent_embedding
  fm.reconstruction_prediction
  fm.benchmark
  fm.ablation_scaling
        ↓
figure-audit
```

The Skill should distinguish model performance from biological validity. A strong benchmark score alone does not establish developmental mechanism.

本 Skill 应明确区分模型性能与生物学有效性。较高的 benchmark 分数本身不能证明发育机制。

---

# 6. What the Skill should not do · 不应该如何使用

Do not use CNS Figure Skill as a mechanism for turning missing evidence into a visually complete figure.

不要把 CNS Figure Skill 当作“把缺失证据补成完整图”的工具。

The following are explicit anti-patterns:

以下属于明确禁止的使用方式：

```text
missing confidence interval → invent an interval
missing significance → calculate or display an undocumented p-value
missing trajectory → draw a smooth lineage curve
missing spatial boundary → infer a visually convenient region
missing biological replicate → treat cells/spots as independent specimens
correlation → label as mechanism or causality
pseudotime → label as measured developmental time
embedding geometry → label as physical movement
synthetic example → present as biological evidence
```

When an input is missing, the correct behavior is to report the missing requirement, downgrade the requested visualization, skip the unsupported view, or return to the appropriate upstream analysis route.

当关键输入缺失时，正确行为应是说明缺失条件、降低图形层级、跳过无法支持的高级视图，或返回相应的上游分析模块。

---

# 7. Minimal decision rule · 最简选择原则

When unsure which route to use, ask one question:

如果不知道应该选择哪个模块，只需要问一个问题：

> **What is the next scientific object I actually need to produce?**  
> **我现在真正需要产出的下一个科研对象是什么？**

```text
A testable question?        → research-design
An analysis strategy?       → analysis-plan
Executable project code?    → analysis-code
Meaning of actual results?  → results-interpret
One figure?                 → plot-single
A module-level figure set?  → plot-pipeline
Final figure QA?            → figure-audit
Whole staged workflow?      → end-to-end
```

This keeps the workflow modular, traceable and scientifically auditable.

这样可以让整个工作流保持模块化、可追溯，并能够进行科学审查。

---

## 8. Related documentation · 相关文档

- [`README.md`](README.md) — project overview / 项目总览
- [`AGENTS.md`](AGENTS.md) — agent routing rules / Agent 路由规则
- [`STRATEGY_ROUTES.json`](STRATEGY_ROUTES.json) — machine-readable route registry / 机器可读路由表
- [`singlecell-spatial-figures/research_logic/`](singlecell-spatial-figures/research_logic/) — research design and analysis strategy / 研究设计与分析策略
- [`singlecell-spatial-figures/result_interpretation/`](singlecell-spatial-figures/result_interpretation/) — result interpretation / 结果解读
- [`singlecell-spatial-figures/style_gallery/`](singlecell-spatial-figures/style_gallery/) — reusable figure families / 通用科学图形库
- [`singlecell-spatial-figures/pipeline_tree/`](singlecell-spatial-figures/pipeline_tree/) — registered analysis-to-figure modules / 注册分析模块到图形的映射
- [`singlecell-spatial-figures/SKILL.md`](singlecell-spatial-figures/SKILL.md) — strict figure rendering and audit rules / 严格绘图与最终审核规范
