# Research Logic

**Question-first research design for single-cell, spatial, developmental and biological foundation-model studies.**  
**面向单细胞、空间组学、发育生物学与生物学基础模型研究的问题驱动型研究设计层。**

The core rule is simple: start from the biological gap and an answerable question, then build claims, evidence and validation before choosing analyses or figures.

核心规则是：先从生物学空白与可回答的问题出发，建立主张、证据与验证逻辑，再选择分析方法和图形。

## Research flow · 研究流程

```text
Biological gap / 生物学空白
        ↓
Answerable question / 可回答问题
        ↓
Provisional central claim / 暂定核心主张
        ↓
Subclaims + alternatives / 子主张与替代解释
        ↓
Claim-specific evidence / 对应证据
        ↓
Analysis strategy / 分析策略
        ↓
Diagnostics + validation / 诊断与验证
        ↓
Failure modes / 失败条件
        ↓
Figure story / 图形叙事
```

Analysis methods are not a checklist. QC, integration, annotation, differential abundance, DE, trajectory, velocity, communication, deconvolution, spatial domains, SVGs, niches, gradients or multimodal integration should be selected only when they answer a defined question or protect inference quality.

分析方法不是固定清单。QC、整合、注释、差异丰度、DE、轨迹、velocity、通讯、去卷积、空间域、SVG、niche、gradient 与多模态整合，只有在能够回答明确问题或保护推断质量时才应使用。

## Main documents · 主要文档

- `SKILL.md` — research-design operating rules / 研究设计操作规则
- `ANALYSIS_SKILL.md` — analysis-planning rules / 分析规划规则
- `ANALYSIS_EXECUTION.md` — code-authoring and execution contract / 代码编写与执行约定
- `ANALYSIS_STRATEGY_LIBRARY.md` — reusable strategy patterns / 可复用分析策略
- `ANALYSIS_STRATEGY_CATALOG.json` — machine-readable strategy catalogue / 机器可读策略目录
- `CNS_ANCHORS.md` — literature navigation anchors / 文献导航锚点
- `PAPER_LOGIC_LIBRARY.md` — representative paper logic library / 代表性论文逻辑库
- `RESEARCH_PLAN_SCHEMA.json` — structured research-plan contract / 结构化研究计划约定

## Validation · 校验

```bash
python research_logic/validate_research_plan.py \
  research_logic/templates/research_plan.example.json
```

A structurally valid plan is not a scientific certification. Specific literature claims must still be checked against the original source, and biological conclusions remain subject to experimental evidence and human scientific judgment.

结构上合法的研究计划并不等于科学结论已经成立。具体文献结论仍需回到原文核查，生物学结论仍必须由实际证据与人工科学判断支持。

## Scope · 适用范围

Designed for / 适用于：

- single-cell atlases and cohort studies / 单细胞图谱与队列研究
- spatial transcriptomics and tissue ecology / 空间转录组与组织生态
- developmental and embryo biology / 发育与胚胎生物学
- cross-modal reference mapping / 跨模态参考映射
- perturbation biology / 扰动生物学
- biological foundation models and virtual cell/embryo studies / 生物学基础模型与虚拟细胞/虚拟胚胎研究
