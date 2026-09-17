# CNS Figure Skill

**Publication-oriented analysis planning, result interpretation, and scientific figure generation for single-cell, spatial, developmental and AI-for-life-science research.**  
**面向单细胞、空间组学、发育生物学与 AI for Life Science 的科研分析规划、结果解读与发表级科学绘图工具集。**

CNS Figure Skill is designed for research workflows in which scientific reasoning, statistical outputs and figure rendering must remain traceable and separate. It does not replace upstream biological or statistical analysis; it converts reviewed inputs into reproducible plans, interpretations and figures.

CNS Figure Skill 面向需要保持“科学问题—分析结果—图形证据”可追溯关系的科研工作流。它不会替代上游生物学或统计分析，而是将已经审核的输入转化为可复现的分析规划、结果解读与发表级图形。

## Start here · 从这里开始

**New users should first read [`USAGE_EXAMPLES.md`](USAGE_EXAMPLES.md).** It explains the main usage scenarios, how to choose among the eight task routes, how to call each module from an Agent/Codex workflow, and how direct plotting/pipeline CLIs fit into the overall research workflow.

**If you are starting from a biological idea rather than an existing analysis, read [`BIOLOGICAL_QUESTION_TO_ANALYSIS.md`](BIOLOGICAL_QUESTION_TO_ANALYSIS.md).** It shows how to formulate a testable biological question, use an LLM to construct claims and alternatives, check whether the available data can answer the question, and then move through analysis planning, code generation, diagnostics, interpretation and figure design.

**首次使用建议先阅读 [`USAGE_EXAMPLES.md`](USAGE_EXAMPLES.md)。** 其中以“使用场景 → 模块选择 → 调用模板 → 预期输出”的方式说明八类任务路线，并提供 Agent/Codex 调用框架、直接绘图命令和典型组合使用实例。

**如果你是从一个生物学想法而不是已有分析开始，建议继续阅读 [`BIOLOGICAL_QUESTION_TO_ANALYSIS.md`](BIOLOGICAL_QUESTION_TO_ANALYSIS.md)。** 该指南说明如何提出可检验的生物学问题、利用 LLM 建立主张与替代解释、判断数据能否回答问题，并进一步进入分析规划、代码生成、诊断、结果解读和 Figure 设计。

Quick references / 快速入口：

- [`USAGE_EXAMPLES.md`](USAGE_EXAMPLES.md) — usage scenarios and module examples / 使用场景与模块调用示例
- [`BIOLOGICAL_QUESTION_TO_ANALYSIS.md`](BIOLOGICAL_QUESTION_TO_ANALYSIS.md) — biological question → LLM → analysis workflow / 生物学问题 → LLM → 分析完整流程
- [`AGENTS.md`](AGENTS.md) — agent routing rules / Agent 路由规则
- [`STRATEGY_ROUTES.json`](STRATEGY_ROUTES.json) — machine-readable route registry / 机器可读路由表
- [`singlecell-spatial-figures/README.md`](singlecell-spatial-figures/README.md) — scientific figure system / 科学绘图系统

## Core capabilities · 核心能力

| Route | English | 中文 |
|---|---|---|
| `research-design` | Define the biological question, candidate claims, alternatives and evidence chain. | 明确生物学问题、候选主张、替代解释与证据链。 |
| `analysis-plan` | Select the smallest defensible single-cell/spatial analysis strategy and diagnostics. | 选择最小且可辩护的单细胞/空间分析路线与诊断。 |
| `analysis-code` | Turn an approved plan into project-specific R/Python code. | 将已审核分析方案落实为项目级 R/Python 代码。 |
| `results-interpret` | Interpret actual outputs while separating observation, explanation and mechanism. | 解读真实结果，并区分观察、解释、机制假设与验证结论。 |
| `plot-single` | Render one reviewed result table with a supported plot family. | 将单个已审核结果表绘制为支持的图形类型。 |
| `plot-pipeline` | Render the complete figure set associated with one registered analysis module. | 为一个注册分析模块生成对应的完整配套图组。 |
| `figure-audit` | Audit scale, layout, export and final figure carriers. | 审核尺度、布局、导出格式与最终组图载体。 |
| `end-to-end` | Coordinate the routes above in scientific order. | 按科研逻辑串联上述流程。 |

Machine-readable routing: [`STRATEGY_ROUTES.json`](STRATEGY_ROUTES.json)  
Agent instructions / Agent 路由说明: [`AGENTS.md`](AGENTS.md)

## Recommended workflow · 推荐工作流

```text
Biological question / 生物学问题
        ↓
Research design / 研究设计
        ↓
Analysis plan / 分析规划
        ↓
Analysis code + diagnostics / 分析代码与诊断
        ↓
Result interpretation / 结果解读
        ↓
Single figure or pipeline figures / 单图或流程图组
        ↓
Figure audit / 最终图形审核
```

Each stage keeps its own status: planned, code written, executed, checked or skipped. A plotting command never implies that an upstream biological analysis was performed.

每个阶段分别记录 planned、code written、executed、checked 或 skipped 状态。执行绘图命令不代表已经完成上游生物学分析。

## Quick start · 快速开始

For an agent/Codex workflow, provide a task mode and real project inputs:

在 Agent/Codex 工作流中，指定任务模式并提供真实项目输入：

```text
Read AGENTS.md and STRATEGY_ROUTES.json first.
先读取 AGENTS.md 与 STRATEGY_ROUTES.json。

task_mode: analysis-plan
language: R
execution: plan_only
inputs:
  brief: project/research_question.md
  data_inventory: project/data_inventory.md
  sample_sheet: project/samples.csv
output_dir: project/analysis_plan

Design the smallest defensible scRNA-seq + spatial analysis chain.
为该 scRNA-seq + 空间项目设计最小且可辩护的分析主线。
```

`execution` semantics / `execution` 定义：

- `plan_only`: planning or read-only interpretation only / 仅规划或只读结果解读；
- `write_code`: write reusable code and run instructions / 编写可复用代码与运行说明；
- `run_approved`: execute the explicitly requested scope when data and environment are available / 在数据与环境满足时执行用户明确指定的范围。

## Scientific figure system · 科学绘图系统

The figure system covers single-cell RNA-seq, single-nucleus RNA-seq, spatial transcriptomics, cross-modal biology, development/embryo studies and biological foundation-model evaluation.

绘图系统覆盖 scRNA-seq、snRNA-seq、空间转录组、跨模态生物学、胚胎/发育研究与生物学基础模型评估。

Main entry points / 主要入口：

- [`singlecell-spatial-figures/README.md`](singlecell-spatial-figures/README.md) — capability overview / 能力总览
- [`singlecell-spatial-figures/research_logic/`](singlecell-spatial-figures/research_logic/) — research design and analysis strategy / 研究设计与分析策略
- [`singlecell-spatial-figures/result_interpretation/`](singlecell-spatial-figures/result_interpretation/) — result interpretation / 结果解读
- [`singlecell-spatial-figures/style_gallery/`](singlecell-spatial-figures/style_gallery/) — reusable plot families / 通用图形库
- [`singlecell-spatial-figures/pipeline_tree/`](singlecell-spatial-figures/pipeline_tree/) — analysis-to-figure mapping / 分析流程到图形的映射

### Visual rules · 视觉规则

- No subtitle in scientific figures. / 科学图形不使用 subtitle。
- Advanced figures must add a real scientific dimension, not decoration. / Advanced 图必须增加真实科学信息，而不是装饰。
- Palette selection and numerical normalization are independent. / 配色选择与数值归一化相互独立。
- Stable biological identities should keep stable named colors. / 相同生物学类别应尽量保持稳定命名颜色。
- Missing uncertainty, trajectories, boundaries, probabilities or significance are never fabricated. / 不补造缺失的不确定性、轨迹、边界、概率或显著性。
- Synthetic examples are software demonstrations, never biological evidence. / 合成示例仅用于软件演示，不能作为生物学证据。
- Figure interpretation belongs in captions and provenance, not decorative microcopy on the canvas. / 图形解释应放在 caption 与 provenance 中，不在画布上堆叠说明性小字。

## Direct plotting · 直接绘图

```bash
cd singlecell-spatial-figures/style_gallery
python -m pip install -r requirements-tested.txt
python render.py plot \
  --kind heatmap \
  --input reviewed.csv \
  --config reviewed.json \
  --mode advanced \
  --out results/Fig1
```

`minimal` provides the smallest scientifically complete view. `advanced` may add comparison, uncertainty, hierarchy, pairing, spatial context or other information that is already present in the input.

`minimal` 提供最小科学完整视图；`advanced` 可以增加输入中真实存在的比较、不确定性、层级、配对结构、空间背景等信息。

## Pipeline figures · 分析配套图组

```bash
cd singlecell-spatial-figures
python pipeline_tree/run_pipeline.py \
  --module scrna.annotation \
  --input markers=results/markers.csv \
  --input embedding=results/embedding.csv \
  --config project/annotation.json \
  --out build/annotation
```

Module inputs are defined in [`IMPLEMENTED_MODULES.json`](singlecell-spatial-figures/pipeline_tree/IMPLEMENTED_MODULES.json), and table fields are defined in [`RESULT_CONTRACTS.json`](singlecell-spatial-figures/pipeline_tree/RESULT_CONTRACTS.json). Missing optional evidence is recorded as skipped rather than fabricated.

模块输入由 [`IMPLEMENTED_MODULES.json`](singlecell-spatial-figures/pipeline_tree/IMPLEMENTED_MODULES.json) 定义，结果表字段由 [`RESULT_CONTRACTS.json`](singlecell-spatial-figures/pipeline_tree/RESULT_CONTRACTS.json) 定义。缺少可选证据时应记录 skipped，而不是伪造数据。

## Result interpretation · 结果解读

Use `results-interpret` for actual experimental or computational outputs. The interpretation layer separates:

对真实实验或生信结果使用 `results-interpret`，解读层明确区分：

```text
Observation / 观察
→ biological meaning / 生物学含义
→ plausible explanation / 可能解释
→ alternatives / 替代解释
→ validation boundary / 验证边界
```

Relevant negative or contradictory results must be retained. Literature can provide context, but it must not be used to invent project-specific measurements or conclusions.

重要阴性结果与矛盾结果必须保留。文献可以提供背景，但不能用于补造本项目不存在的测量结果或结论。

## Public documentation · 公开文档

This repository is maintained as a public research tool. User-facing documentation describes current interfaces, capabilities, scientific constraints and reproducible usage. Internal development history, temporary release notes and local test logs are intentionally excluded from the public documentation surface.

本仓库按面向公众的科研工具维护。公开文档只描述当前接口、能力、科学边界与可复现用法；内部开发过程、临时版本说明和本地测试日志不作为公开使用文档的一部分。