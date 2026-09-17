# From Biological Question to Analysis with an LLM

# 从生物学问题到分析：如何使用 LLM 辅助完成科研设计与执行

This guide shows how to start from a **biological observation or vague research idea**, convert it into a **testable biological question**, and then use an LLM together with CNS Figure Skill to move through research design, analysis planning, code generation, result interpretation and figure production.

本文说明如何从一个**生物学观察、现象或模糊研究想法**出发，把它转化为一个**可检验的生物学问题**，再结合 LLM 与 CNS Figure Skill，逐步完成研究设计、分析规划、代码实现、结果解读和科学绘图。

The central principle is:

核心原则是：

```text
Do not ask the LLM what analyses look impressive.
Ask what biological question is being tested,
what evidence would distinguish competing explanations,
and only then decide which analyses are necessary.

不要先问 LLM“还能做什么高级分析”。
先明确要检验什么生物学问题、
什么证据能够区分不同解释，
然后再决定需要哪些分析。
```

---

## 1. Start from biology, not software · 从生物学出发，而不是从软件出发

A weak project often starts like this:

一个较弱的课题通常这样开始：

> I have scRNA-seq data. What analyses can I do?  
> 我有单细胞数据，可以做哪些分析？

This invites a checklist of UMAP, markers, CellChat, trajectory, enrichment and other methods without a clear inferential purpose.

这种提问很容易变成 UMAP、marker、CellChat、轨迹、富集分析等方法的堆叠，但没有明确的推断目的。

A stronger starting point is:

更好的起点是：

> I observe biological phenomenon X under condition Y. I want to know whether process A, cell state B, or spatial relationship C explains this change, and what evidence would distinguish these possibilities.  
> 我观察到条件 Y 下出现生物学现象 X。我希望判断过程 A、细胞状态 B 或空间关系 C 是否能够解释这一变化，以及什么证据能够区分这些可能性。

The LLM should help **structure and challenge the question**, not manufacture a biological story around whatever analyses are available.

LLM 的作用应该是帮助**结构化并挑战这个问题**，而不是围绕已有分析工具拼出一个生物学故事。

---

## 2. A biological question has six parts · 一个好的生物学问题至少包含六个部分

Before using any analysis module, write down the following six elements.

在调用任何分析模块之前，先写清以下六项。

| Element / 要素 | Question / 要回答的问题 | Example / 示例 |
|---|---|---|
| Biological system / 生物系统 | What organism, tissue, developmental stage or disease context? / 什么物种、组织、发育阶段或疾病背景？ | Human fetal tissue / 人胚胎组织 |
| Biological unit / 生物学单位 | What changes: cell type, state, lineage, niche, tissue region or molecular program? / 谁在变化：细胞类型、状态、谱系、生态位、组织区域还是分子程序？ | A progenitor population / 一个祖细胞群 |
| Process / 生物过程 | What process are you trying to explain? / 想解释什么过程？ | Lineage commitment / 谱系决定 |
| Contrast / 比较关系 | What comparison makes the question testable? / 哪个比较使问题可检验？ | Earlier vs later stage / 早期 vs 晚期阶段 |
| Observable evidence / 可观测证据 | What measurements would support or contradict the hypothesis? / 哪些测量能够支持或反驳假设？ | State abundance, gene program, spatial localization / 状态比例、基因程序、空间定位 |
| Alternative explanation / 替代解释 | What else could produce the same observation? / 还有什么可能产生相同现象？ | Sampling composition, batch, maturation rather than lineage choice / 样本组成、批次、成熟而非谱系选择 |

A useful biological question normally contains a **system + process + comparison + measurable evidence + alternative explanation**.

一个真正可分析的问题通常至少包含：**研究系统 + 生物过程 + 比较关系 + 可测证据 + 替代解释**。

---

## 3. Turn a vague idea into a testable question · 将模糊想法转化为可检验问题

### Vague idea · 模糊想法

```text
I want to study embryo development with single-cell and spatial data.
我想用单细胞和空间组学研究胚胎发育。
```

This defines a field, not a research question.

这只是研究领域，不是科学问题。

### Better question · 更好的问题

```text
Which transcriptional states change during early development,
and where are these states located in tissue space?

早期发育过程中哪些转录状态发生变化，
这些状态在组织空间中位于哪里？
```

This is answerable, but still mostly descriptive.

这个问题可以回答，但主要仍是描述性的。

### Stronger, claim-oriented question · 更强的、面向主张的问题

```text
Does the emergence of a spatially localized progenitor state precede
and predict a later lineage bifurcation during early development?

在早期发育过程中，某个具有特定空间定位的祖细胞状态是否先于
并能够预测后续的谱系分化？
```

Now the question implies several separable claims:

这个问题已经隐含了几个可以分别检验的主张：

```text
Claim 1: the progenitor state exists reproducibly.
主张 1：该祖细胞状态可重复识别。

Claim 2: its abundance or molecular program changes before bifurcation.
主张 2：其丰度或分子程序在谱系分叉前发生变化。

Claim 3: it has a reproducible spatial localization.
主张 3：它具有可重复的空间定位。

Claim 4: the state is associated with later lineage outcome.
主张 4：该状态与后续谱系结果相关。

Claim 5: this relationship is not explained solely by stage, batch,
sampling composition or generic maturation.
主张 5：这一关系不能仅由阶段、批次、采样组成或普遍成熟过程解释。
```

Each claim requires different evidence. This is where analysis planning begins.

不同主张需要不同证据。分析规划应从这里开始。

---

## 4. First LLM step: ask it to structure the question · 第一步：让 LLM 帮你结构化科学问题

Do not initially ask for code. Ask the LLM to act as a critical research-design assistant.

第一轮不要直接让 LLM 写代码，而是让它作为研究设计助手审查问题。

### Recommended prompt · 推荐提示词

```text
Read AGENTS.md and STRATEGY_ROUTES.json first.
先读取 AGENTS.md 和 STRATEGY_ROUTES.json。

task_mode: research-design
execution: plan_only

My initial biological idea / 我的初始研究想法:
During early development, I suspect that a transient progenitor state
appears in a specific spatial niche before lineage bifurcation.

Available data / 已有数据:
- scRNA-seq from multiple developmental stages
- spatial transcriptomics from matched or comparable stages
- sample-level metadata

Please do not start from methods.
请不要从分析方法出发。

Help me:
1. define one primary biological question;
2. formulate a falsifiable central hypothesis;
3. identify 3–5 subclaims;
4. list alternative explanations for each major claim;
5. specify the minimum evidence needed to support or reject each claim;
6. identify which questions cannot be answered with the current data;
7. propose a figure-level evidence story without selecting decorative analyses.

Distinguish observation, hypothesis and validated conclusion.
区分观察、假设和已验证结论。
```

### What the LLM should produce · LLM 应该产出什么

The output should resemble a research logic map rather than a software list:

输出应该更像“研究逻辑图”，而不是软件清单：

```text
Biological gap
    ↓
Primary question
    ↓
Central hypothesis
    ↓
Claim 1 ─ evidence ─ alternative explanation
Claim 2 ─ evidence ─ alternative explanation
Claim 3 ─ evidence ─ alternative explanation
    ↓
Validation / falsification conditions
    ↓
Candidate figure story
```

If the answer is dominated by software names, ask the LLM to rewrite it around claims and evidence.

如果输出主要由软件名称组成，应要求 LLM 重新按“主张—证据”组织。

---

## 5. Check whether the question is actually answerable · 判断这个问题是否真的能被现有数据回答

Before analysis planning, ask the LLM to perform a **data–question fit check**.

在制定分析方案之前，让 LLM 先做一次**问题—数据匹配检查**。

For each claim, check:

对每个主张检查：

```text
What is the biological unit?
生物学单位是什么？

What is the independent replicate?
独立重复是什么？

What is directly measured?
什么是直接测量的？

What is inferred?
什么是推断出来的？

What comparison is required?
需要什么比较？

Does the dataset contain that comparison?
数据是否真的包含这个比较？

What confounders could mimic the signal?
什么混杂因素可能产生类似信号？

What claim would remain unsupported even if the analysis is statistically significant?
即使统计显著，哪些结论仍然无法成立？
```

Examples of important boundaries:

几个常见边界：

- pseudotime does not by itself prove a true developmental lineage; / pseudotime 本身不能证明真实谱系；
- dissociated scRNA-seq does not establish spatial interaction; / 解离的 scRNA-seq 不能直接证明空间相互作用；
- ligand–receptor scores do not prove physical signaling; / 配体–受体评分不能证明真实信号传递；
- cell-state correlation does not establish causal transition; / 细胞状态相关不能证明因果转变；
- a model embedding does not automatically represent a biologically meaningful axis. / 模型 embedding 并不自动代表有生物学意义的轴。

---

## 6. Second LLM step: convert claims into an analysis plan · 第二步：把主张转化为分析方案

Once the biological question and claims are stable, move to `analysis-plan`.

当生物学问题和主张已经稳定后，再进入 `analysis-plan`。

### Example prompt · 示例提示词

```text
Read AGENTS.md and STRATEGY_ROUTES.json first.

task_mode: analysis-plan
execution: plan_only
language: R

inputs:
  research_plan: project/research_plan.md
  data_inventory: project/data_inventory.md
  sample_sheet: project/samples.csv

Primary biological question:
Does a spatially localized progenitor state emerge before and associate
with later lineage bifurcation during early development?

For each proposed analysis step, provide:
- biological question being tested;
- claim supported or challenged;
- required input;
- independent biological unit;
- recommended method family;
- why this method is appropriate;
- expected output table;
- diagnostic or failure condition;
- alternative explanation;
- validation strategy;
- downstream figure handoff.

Classify every analysis as:
1. required main analysis;
2. conditional advanced analysis;
3. unnecessary for the current question.

Do not add trajectory, communication, regulons, spatial niches or
foundation-model analyses unless they answer a defined claim.
```

### Example reasoning structure · 示例分析逻辑结构

A defensible plan might look like this:

一个可辩护的分析计划可能是：

```text
Question A: Is the proposed progenitor state reproducible?
    ↓
QC → integration diagnostics → annotation/state definition
    ↓
marker consistency + sample-level recurrence

Question B: Does this state change before lineage bifurcation?
    ↓
sample-aware composition analysis
+ state-specific differential expression / program analysis

Question C: Is the state spatially localized?
    ↓
cell-state mapping/deconvolution
+ spatial localization / neighborhood analysis

Question D: Is the state associated with later lineage outcome?
    ↓
trajectory/fate analysis only if temporal and biological assumptions hold
+ independent stage/specimen validation

Question E: Could the pattern be explained by confounding?
    ↓
batch/stage/sample diagnostics
+ alternative state definitions
+ robustness analysis
```

Notice that `CellChat`, velocity, regulons, foundation models or other advanced analyses are not automatically required.

注意，这里并不会默认要求 CellChat、velocity、regulon 或 foundation model 等高级分析。

---

## 7. Analysis should be organized as claim → test → output · 分析应按“主张 → 检验 → 输出”组织

Avoid organizing the project only by software:

不要只按软件组织项目：

```text
Seurat
CellChat
Monocle
GSVA
...
```

Instead use:

更推荐：

```text
Claim 1 — Cell state identity
    analysis
    diagnostics
    output table
    figure

Claim 2 — Temporal change
    analysis
    diagnostics
    output table
    figure

Claim 3 — Spatial localization
    analysis
    diagnostics
    output table
    figure

Claim 4 — Association with lineage outcome
    analysis
    diagnostics
    output table
    figure
```

This prevents the final manuscript from becoming a sequence of unrelated methods.

这样可以避免论文最后变成互不相关的方法堆叠。

---

## 8. Third LLM step: generate project-specific analysis code · 第三步：让 LLM 生成项目级分析代码

Only after reviewing the analysis plan should you ask for code.

只有在人工审查分析方案之后，才建议让 LLM 编写代码。

```text
Read AGENTS.md and STRATEGY_ROUTES.json first.

task_mode: analysis-code
execution: write_code
language: R

inputs:
  analysis_plan: project/analysis_plan.md
  data_inventory: project/data_inventory.md
  sample_sheet: project/samples.csv

output_dir: project/analysis

Generate project-specific reusable scripts.

Requirements:
- validate sample IDs and assay/layer names before analysis;
- preserve specimen-level independence;
- do not change the approved biological contrasts;
- create one script or clearly separated stage per analysis objective;
- export intermediate diagnostics;
- export reviewed result tables for downstream plotting;
- record package versions and random seeds where relevant;
- fail explicitly when required input is missing;
- do not report a result as completed unless the code was actually executed.
```

A useful project structure is:

推荐项目结构：

```text
project/
├── question/
│   └── research_plan.md
├── metadata/
│   ├── samples.csv
│   └── data_inventory.md
├── analysis_plan/
│   └── analysis_plan.md
├── analysis/
│   ├── 01_qc.R
│   ├── 02_state_definition.R
│   ├── 03_composition.R
│   ├── 04_state_programs.R
│   ├── 05_spatial_mapping.R
│   ├── 06_spatial_niche.R
│   ├── 07_lineage_analysis.R
│   └── RUN.md
├── results/
│   ├── diagnostics/
│   ├── reviewed_tables/
│   └── manifests/
├── interpretation/
└── figures/
```

The exact file names are project-specific; the important idea is to keep raw data, analysis logic, reviewed tables and figures separable.

具体文件名可以变化，关键是让原始数据、分析逻辑、审核后的结果表和最终图片彼此分离。

---

## 9. The LLM must inspect diagnostics before interpreting biology · LLM 在解释生物学之前必须先检查诊断结果

A statistically significant result is not automatically a biological result.

统计显著不等于生物学结论成立。

Before interpretation, the LLM should check at least:

在结果解读之前，LLM 至少应检查：

- number of independent specimens; / 独立样本数；
- group balance and pairing; / 分组平衡与配对关系；
- batch/stage confounding; / 批次与阶段混杂；
- QC distribution across groups; / 不同组 QC 分布；
- whether the effect is driven by one specimen; / 是否由单个样本驱动；
- whether normalization/integration changes the conclusion; / 归一化或整合是否改变结论；
- effect size and uncertainty, not only p-values; / 效应量和不确定性，而非只看 P 值；
- whether cell-level tests incorrectly treat cells as independent biological replicates. / 是否错误地把细胞当作独立生物学重复。

If diagnostics fail, the correct next step is often reanalysis rather than interpretation or figure polishing.

如果诊断不通过，正确的下一步通常是重新分析，而不是继续讲故事或美化图片。

---

## 10. Fourth LLM step: interpret actual results · 第四步：让 LLM 解读真实结果

After analysis and diagnostics, use `results-interpret`.

完成分析和诊断后，再使用 `results-interpret`。

```text
Read AGENTS.md and STRATEGY_ROUTES.json first.

task_mode: results-interpret
interpretation_depth: full
execution: plan_only
response_language: zh

inputs:
  question: project/question/research_plan.md
  results: project/results/reviewed_tables/
  diagnostics: project/results/diagnostics/
  sample_metadata: project/metadata/samples.csv
  analysis_log: project/analysis/RUN.md

output_dir: project/interpretation

For each main result:
1. state the direct observation;
2. state what biological interpretation is supported;
3. identify what is not supported;
4. list plausible alternative explanations;
5. connect it to the predefined claim;
6. retain negative or contradictory evidence;
7. recommend the most discriminating next validation.

Do not use literature to invent project-specific results.
Do not convert association into mechanism or causality without evidence.
```

The interpretation should follow:

结果解读应遵循：

```text
Observed result
观察结果
    ↓
Supported interpretation
可支持的解释
    ↓
Alternative explanations
替代解释
    ↓
Evidence strength / limitation
证据强度与局限
    ↓
Claim status
主张状态
    ↓
Next discriminating experiment or analysis
最能区分解释的下一步实验或分析
```

---

## 11. Fifth LLM step: decide what should be plotted · 第五步：决定哪些结果值得画成 Figure

Figures should correspond to scientific claims, not to every analysis that was run.

Figure 应对应科学主张，而不是“做过一个分析就必须画一张图”。

A useful mapping is:

推荐映射：

```text
Figure 1 — Define the biological system and reproducible cell states
Figure 1 — 定义研究系统和可重复细胞状态

Figure 2 — Show the temporal/condition-associated state change
Figure 2 — 展示时间或条件相关的状态变化

Figure 3 — Establish spatial localization or niche structure
Figure 3 — 建立空间定位或生态位证据

Figure 4 — Test developmental/lineage association
Figure 4 — 检验发育或谱系关联

Figure 5 — Orthogonal validation and alternative-explanation tests
Figure 5 — 正交验证与替代解释检验
```

Diagnostic figures may remain supplementary even when they are scientifically essential.

诊断图即使非常重要，也可以放在 Supplementary，而不必强行进入主 Figure。

---

## 12. Use `plot-single` when the result table is already final · 结果表已经确定时使用 `plot-single`

Example Agent instruction:

Agent 示例：

```text
task_mode: plot-single
plot_kind: forest
plot_mode: advanced
inputs:
  table: project/results/reviewed_tables/state_effects.csv
  config: project/figures/state_effects.json
output_dir: project/figures/Fig2B

Render only the reviewed effect estimates and intervals.
Do not rerun differential analysis.
Do not infer missing confidence intervals.
Use no subtitle.
```

Direct CLI:

```bash
cd singlecell-spatial-figures/style_gallery
python render.py plot \
  --kind forest \
  --input ../../project/results/reviewed_tables/state_effects.csv \
  --config ../../project/figures/state_effects.json \
  --mode advanced \
  --out ../../project/figures/Fig2B
```

---

## 13. Use `plot-pipeline` when one analysis module needs its full figure set · 一个分析模块需要整套配图时使用 `plot-pipeline`

For example, after cell annotation:

例如，在细胞注释完成后：

```text
task_mode: plot-pipeline
plot_module: scrna.annotation
inputs:
  markers: project/results/reviewed_tables/markers.csv
  embedding: project/results/reviewed_tables/embedding.csv
  config: project/figures/annotation.json
output_dir: project/figures/annotation
```

The pipeline renderer should produce the supported required and advanced views and record missing optional evidence as `skipped`.

Pipeline renderer 应生成当前支持的 required / advanced 图，并把缺失的可选证据记录为 `skipped`，而不是补造数据。

---

## 14. Full worked example · 完整框架示例

### Step A — Initial observation · 初始观察

```text
In preliminary data, one progenitor-like population appears transiently
at an intermediate developmental stage and seems enriched in one tissue region.

初步数据中，一个祖细胞样群体在中间发育阶段短暂出现，
并且似乎富集于某个组织区域。
```

### Step B — Primary question · 主问题

```text
Does a transient spatially localized progenitor state emerge before
lineage bifurcation and associate with subsequent lineage outcome?

一个短暂出现且具有空间定位的祖细胞状态，是否先于谱系分叉出现，
并与后续谱系结果相关？
```

### Step C — Hypothesis · 假设

```text
A transient progenitor program arises in a defined spatial niche before
lineage bifurcation, and cells expressing this program are preferentially
associated with one later lineage state.

在谱系分叉之前，一个短暂祖细胞程序在特定空间生态位中出现；
表达该程序的细胞更倾向于与后续某一谱系状态相关。
```

### Step D — Alternative explanations · 替代解释

```text
- the state is a batch-specific cluster;
- the apparent increase reflects specimen composition;
- the program reflects general maturation rather than lineage commitment;
- spatial enrichment is caused by tissue sampling geometry;
- inferred lineage association is driven by stage ordering.
```

```text
- 该状态只是批次特异 cluster；
- 表面上的增加来自样本组成差异；
- 该程序反映的是普遍成熟，而非谱系决定；
- 空间富集来自组织取样几何差异；
- 推断的谱系关联只是由阶段排序造成。
```

### Step E — Minimum analysis chain · 最小分析主线

```text
1. QC and specimen-level diagnostics
2. reproducible state definition across samples
3. sample-aware state composition analysis
4. state-specific program analysis
5. spatial mapping and localization validation
6. lineage/fate association only if assumptions are satisfied
7. sensitivity analysis for stage, batch and alternative state definitions
```

```text
1. QC 与样本级诊断
2. 跨样本可重复的状态定义
3. 基于样本的状态组成分析
4. 状态特异分子程序分析
5. 空间映射与定位验证
6. 仅在假设满足时进行谱系/命运关联分析
7. 对阶段、批次和状态定义进行敏感性分析
```

### Step F — Evidence story · 证据故事

```text
State exists reproducibly
        ↓
State changes before bifurcation
        ↓
State occupies a reproducible spatial niche
        ↓
State is associated with later lineage outcome
        ↓
Alternative explanations are weakened by robustness/validation
```

### Step G — Figure story · Figure 逻辑

```text
Fig. 1  Data quality + atlas + state definition
Fig. 2  Stage-dependent state abundance/program change
Fig. 3  Spatial localization and niche context
Fig. 4  Lineage/fate association
Fig. 5  Validation and alternative-explanation tests
```

This sequence is not mandatory. It is an example of how to make the figure structure follow the evidence chain.

这个顺序并不是固定模板，而是示范如何让 Figure 结构服从证据链。

---

## 15. A reusable prompt for a new biological project · 可复用的新课题提示词

The following prompt can be adapted to most single-cell/spatial biological projects.

下面这段可以作为大多数单细胞/空间课题的起始模板。

```text
Read AGENTS.md and STRATEGY_ROUTES.json first.

I want to develop a biological research project with LLM assistance.
Do not begin by recommending software or advanced analyses.

My observation / 我的观察:
<describe the biological phenomenon>

Biological system / 研究系统:
<organism, tissue, disease, developmental stage>

Available data / 已有数据:
<scRNA-seq, snRNA-seq, spatial, imaging, perturbation, metadata, etc.>

Known comparison / 已知比较:
<condition, stage, treatment, genotype, region, outcome>

What I currently suspect / 当前假设:
<optional hypothesis>

Please first use task_mode: research-design and:
1. convert this into one answerable primary biological question;
2. define a falsifiable central hypothesis;
3. split it into 3–5 claims;
4. identify alternative explanations;
5. define the minimum evidence required for each claim;
6. identify what the current data cannot establish;
7. propose the smallest defensible analysis chain;
8. distinguish required analyses from conditional advanced analyses;
9. map each analysis to a reviewed result table and candidate figure;
10. identify stop conditions that would invalidate the current story.

Do not fabricate missing measurements.
Do not infer causality from association.
Do not recommend an analysis solely because it is fashionable.
```

---

## 16. How to use the LLM correctly · 如何正确使用 LLM

The LLM is most useful for:

LLM 最适合：

- converting vague ideas into explicit questions; / 把模糊想法转成明确问题；
- exposing hidden assumptions; / 暴露隐含假设；
- identifying alternative explanations; / 提出替代解释；
- mapping claims to evidence; / 建立主张与证据映射；
- checking whether data can answer the question; / 判断数据能否回答问题；
- drafting analysis plans and reusable code; / 生成分析计划与可复用代码；
- interpreting results while preserving uncertainty; / 在保留不确定性的前提下解读结果；
- organizing figures around scientific claims. / 围绕科学主张组织 Figure。

The LLM should not be treated as:

不应把 LLM 当作：

- an automatic source of biological truth; / 自动产生生物学真理的工具；
- a substitute for experimental controls; / 实验对照的替代品；
- a justification for an unsupported causal claim; / 无证据因果结论的辩护工具；
- a reason to run every available analysis; / 把所有高级分析都跑一遍的理由；
- a replacement for checking source data and primary literature. / 检查原始数据和原始文献的替代品。

---

## 17. Stop and revise when the evidence chain breaks · 当证据链断裂时，应停止并修改问题

Do not force the original hypothesis to survive every analysis.

不要强迫最初的假设在所有分析后仍然成立。

Revise the question when:

出现以下情况时应修改问题：

- the proposed state cannot be reproduced across specimens; / 状态无法跨样本重复；
- the effect disappears after specimen-aware analysis; / 采用样本级分析后效应消失；
- spatial evidence contradicts dissociated data; / 空间证据与解离数据矛盾；
- trajectory results are unstable to reasonable parameter choices; / 轨迹结果对合理参数高度不稳定；
- orthogonal validation fails; / 正交验证失败；
- a simpler alternative explanation accounts for the observations. / 更简单的替代解释已经可以解释观察结果。

A negative result can refine the biological question and often improves the final study.

阴性结果可以帮助重新定义科学问题，并不等于课题失败。

---

## 18. Recommended complete workflow · 推荐完整工作流

```text
Observation / 现象
    ↓
Biological question / 生物学问题
    ↓
research-design
    ↓
Question–data fit check / 问题–数据匹配
    ↓
analysis-plan
    ↓
Human review of design / 人工审查设计
    ↓
analysis-code
    ↓
Execution + diagnostics / 实际运行与诊断
    ↓
results-interpret
    ↓
Claim status update / 更新主张状态
    ↓
plot-single or plot-pipeline
    ↓
figure-audit
    ↓
Manuscript-level evidence story / 论文级证据链
```

At every transition, ask one question:

在每个阶段转换时，都问一句：

> What biological claim does the next step test, and what result would make us change our mind?  
> 下一步到底在检验哪个生物学主张？出现什么结果时，我们应该改变原来的解释？

If that question cannot be answered, the next analysis is probably not yet justified.

如果这句话无法回答，那么下一步分析通常还没有被充分论证。
