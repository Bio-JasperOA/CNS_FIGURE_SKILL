# Agent Routing Guide · Agent 路由指南

This file defines how Codex/agents should enter the repository. Read the root `README.md` and `STRATEGY_ROUTES.json` first. Repository-local `task_mode` values are routing labels, not shell commands.

本文件定义 Codex/Agent 如何进入仓库。首先读取根目录 `README.md` 与 `STRATEGY_ROUTES.json`。仓库中的 `task_mode` 是路由标签，不是 shell 命令。

## Task routing · 任务路由

| Task mode | English | 中文 |
|---|---|---|
| `research-design` | Read `research_logic/SKILL.md`; define the question, provisional claims and evidence chain. | 读取 `research_logic/SKILL.md`；定义问题、暂定主张与证据链。 |
| `analysis-plan` | Read `research_logic/ANALYSIS_SKILL.md`; choose the smallest defensible analysis strategy. | 读取 `research_logic/ANALYSIS_SKILL.md`；选择最小且可辩护的分析策略。 |
| `analysis-code` | Read `research_logic/ANALYSIS_EXECUTION.md`; write project-specific R/Python code from an approved plan. | 读取 `research_logic/ANALYSIS_EXECUTION.md`；根据已审核方案编写项目级 R/Python 代码。 |
| `results-interpret` | Read `result_interpretation/SKILL.md`; interpret actual source-linked results. | 读取 `result_interpretation/SKILL.md`；解读可追溯的真实结果。 |
| `plot-single` | Read `style_gallery/README.md`; render one reviewed result table. | 读取 `style_gallery/README.md`；绘制单个已审核结果表。 |
| `plot-pipeline` | Read `pipeline_tree/README.md`; render figures for one registered analysis module. | 读取 `pipeline_tree/README.md`；为一个注册分析模块生成配套图组。 |
| `figure-audit` | Read `singlecell-spatial-figures/SKILL.md`; perform strict figure and carrier checks. | 读取 `singlecell-spatial-figures/SKILL.md`；执行严格图形与载体审核。 |
| `end-to-end` | Follow the scientific sequence below. | 按下方科研顺序推进。 |

Honor an explicit task mode. If no mode is given, select the smallest route that directly answers the request. Do not invent route IDs, module IDs, CLI flags, missing data or claimed capabilities.

用户明确指定 `task_mode` 时必须遵循；未指定时选择能够直接完成任务的最小路线。不得虚构 route ID、module ID、CLI 参数、缺失数据或不存在的能力。

## Execution semantics · 执行语义

- `plan_only` — planning or read-only interpretation; no new analysis execution. / 仅规划或只读解读，不执行新的分析。
- `write_code` — write source code, configuration and run instructions. / 编写代码、配置与运行说明。
- `run_approved` — execute the explicitly requested scope when data, dependencies and compute are available. / 在数据、依赖与计算环境满足时执行用户明确指定的范围。

Never report unexecuted code as completed analysis.

不得将“已写代码”描述为“已完成分析”。

## Research-design rules · 研究设计规则

Start from the biological gap, answerable question, provisional claim, alternatives and claim-evidence graph rather than from software or attractive figures.

从生物学空白、可回答问题、暂定主张、替代解释和主张—证据图出发，而不是从软件或好看的图出发。

For foundation-model work, explicitly consider biological utility, baseline quality, OOD axes, specimen-level independence and leakage. For developmental and spatial work, distinguish measured time/space from inferred geometry.

基础模型研究必须明确考虑生物学效用、基线质量、OOD 维度、样本级独立性与数据泄漏。发育和空间研究必须区分真实测量的时间/空间与推断得到的几何关系。

Do not treat pseudotime as proven lineage or dissociated data as proof of a spatial mechanism.

不得将 pseudotime 直接等同于真实谱系，也不得用解离单细胞数据单独证明空间机制。

## Analysis-strategy rules · 分析策略规则

Choose the smallest defensible chain. Each analysis step should have:

选择最小且可辩护的分析链。每一步都应明确：

```text
question / 问题
→ input / 输入
→ independence unit / 独立重复单位
→ method reason / 方法选择理由
→ output / 输出
→ diagnostic / 诊断
→ limitation / 局限
→ validation / 验证
→ figure handoff or justified skip / 绘图交接或合理跳过
```

Do not add communication, trajectory, velocity, regulons, niches, deconvolution or other advanced analyses only because they are available.

不要因为“可以做”就自动增加通讯、轨迹、velocity、regulon、niche、去卷积等高级分析。

## Figure-generation rules · 绘图规则

Plotting consumes reviewed results. It must not refit biological/statistical models or manufacture missing significance, intervals, boundaries, trajectories, neighborhoods, probabilities or conclusions.

绘图只消费已审核结果，不得重新拟合生物学/统计模型，也不得补造显著性、区间、边界、轨迹、邻域、概率或结论。

Global visual rules / 全局视觉规则：

- no subtitle / 不使用 subtitle；
- stable named colors for stable biological identities / 稳定生物学类别尽量保持固定命名颜色；
- palette and normalization are independent / 色板与归一化独立；
- explanatory microcopy stays off the canvas / 不在画布上堆叠说明性小字；
- synthetic fixtures remain explicitly synthetic / 合成数据必须明确标注为 synthetic。

## Result-interpretation rules · 结果解读规则

For every material result, separate observation, biological meaning, explanation, alternatives and claim boundary. Preserve relevant negative and contradictory evidence.

对每个关键结果，区分观察、生物学含义、解释、替代解释与主张边界，并保留重要阴性和矛盾证据。

Literature provides context; it must not be used to fabricate project-specific observations. Human scientific review remains required.

文献用于提供背景，不能用于补造本项目不存在的观察结果。最终科学判断仍需人工审核。

## End-to-end sequence · 端到端顺序

```text
research-design
→ analysis-plan
→ analysis-code
→ actual execution when requested and feasible
→ diagnostics
→ results-interpret
→ plot-single or plot-pipeline
→ figure-audit when required
```

Keep stage status explicit: planned, code written, executed, checked or skipped.

每个阶段必须明确标记 planned、code written、executed、checked 或 skipped。
