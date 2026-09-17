# Result Interpretation

**Source-linked interpretation of actual computational and experimental results.**  
**面向真实计算与实验结果的可追溯解读层。**

Use `task_mode: results-interpret` for single-cell, spatial, developmental, model-evaluation and wet-lab results. Start with [`SKILL.md`](SKILL.md), then use the relevant assay and narrative guidance.

对单细胞、空间组学、发育、模型评估及湿实验结果使用 `task_mode: results-interpret`。先读取 [`SKILL.md`](SKILL.md)，再根据实际结果选择 assay 与 narrative 指南。

## Interpretation logic · 解读逻辑

```text
Observed result / 观察结果
        ↓
Biological meaning / 生物学含义
        ↓
Plausible explanation / 可能解释
        ↓
Alternative explanations / 替代解释
        ↓
Evidence strength and boundary / 证据强度与边界
        ↓
Discriminating validation / 可区分解释的验证
```

Observation, interpretation, mechanism hypothesis and validated conclusion must remain separate. Negative and contradictory results are retained when they materially affect the claim.

观察、解释、机制假设与已验证结论必须分开。对主张有实质影响的阴性结果和矛盾结果必须保留。

## Invocation · 调用

```text
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
```

Replace example paths with real project files. In this route, `plan_only` means read-only interpretation and reporting; it does not suppress the interpretation output.

示例路径必须替换为真实项目文件。在本路线中，`plan_only` 表示只读解读与报告，不表示停止输出解读结果。

`interpretation_depth` values / 解读深度：

- `quick` — key findings and major caveats / 核心发现与主要限制
- `full` — result-by-result interpretation and evidence chain / 逐结果解读与证据链
- `manuscript` — structured Results/Discussion handoff while preserving claim boundaries / 在保持主张边界的前提下形成 Results/Discussion 交接材料

## Structured evidence check · 结构化证据检查

```bash
python -m pip install 'jsonschema>=4.18,<5'
python singlecell-spatial-figures/result_interpretation/review_results.py packet \
  project/interpretation/result_bundle.json \
  --root project \
  --verify-files \
  --out project/interpretation/checked
```

The helper validates declared evidence relationships, metadata consistency, source hashes and explicit numeric bindings where supported. It does not independently establish biological truth or causal mechanism.

辅助程序用于检查声明的证据关系、元数据一致性、来源哈希以及支持格式中的显式数值绑定；它不会独立证明生物学事实或因果机制。

## Main documents · 主要文档

- [`ASSAY_PLAYBOOK.md`](ASSAY_PLAYBOOK.md) — assay-aware interpretation / 按实验类型解读
- [`ASSAY_RULES.json`](ASSAY_RULES.json) — machine-readable interpretation constraints / 机器可读解读约束
- [`NARRATIVE_PLAYBOOK.md`](NARRATIVE_PLAYBOOK.md) — evidence-to-narrative patterns / 证据到叙事的组织方式
- [`LITERATURE_LOGIC.md`](LITERATURE_LOGIC.md) — literature-use boundaries / 文献使用边界
- [`RESULT_BUNDLE_SCHEMA.json`](RESULT_BUNDLE_SCHEMA.json) — structured evidence contract / 结构化证据约定
- [`review_results.py`](review_results.py) — evidence packet validator / 证据包校验工具

## Scientific boundary · 科学边界

Literature may explain context, expected biology or alternative mechanisms, but it must not be used to invent project-specific measurements. A successful schema or software validation is not equivalent to a validated biological conclusion.

文献可以用于解释背景、预期生物学与替代机制，但不能用于补造本项目不存在的测量结果。Schema 或软件校验通过，不等于生物学结论已经得到验证。
