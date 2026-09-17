# Single-cell & Spatial Figure System

**Reusable scientific figure generation for single-cell, spatial, developmental and foundation-model research.**  
**面向单细胞、空间组学、发育生物学与基础模型研究的可复用科学绘图系统。**

The entry document for strict figure generation and audit is [`SKILL.md`](SKILL.md). Machine-readable capability boundaries are defined in [`CAPABILITIES.json`](CAPABILITIES.json).

严格绘图与审核入口见 [`SKILL.md`](SKILL.md)，机器可读的能力边界见 [`CAPABILITIES.json`](CAPABILITIES.json)。

## Architecture · 架构

The system is organized into five public components:

系统由五个公开组件构成：

1. **Research logic / 研究逻辑** — biological question, evidence chain and analysis strategy.
2. **Result interpretation / 结果解读** — source-linked interpretation of actual outputs.
3. **Style gallery / 图形库** — reusable plot families with `minimal` and `advanced` modes.
4. **Pipeline tree / 流程图树** — analysis-module to figure-set mapping.
5. **Figure audit / 图形审核** — layout, scale, export and final-carrier checks.

## Supported research domains · 支持领域

- scRNA-seq and snRNA-seq / 单细胞与单核 RNA 测序
- spatial transcriptomics / 空间转录组
- cross-modal and multimodal biology / 跨模态与多模态生物学
- development and embryo research / 发育与胚胎研究
- biological foundation-model evaluation / 生物学基础模型评估

## Figure principles · 绘图原则

- No subtitles. / 不使用 subtitle。
- `advanced` must add real scientific information. / `advanced` 必须增加真实科学信息。
- Do not refit statistical or biological models while plotting. / 绘图阶段不重新拟合统计或生物学模型。
- Do not invent significance, uncertainty, trajectories, boundaries, neighborhoods or probabilities. / 不补造显著性、不确定性、轨迹、边界、邻域或概率。
- Keep biological identities color-stable across related panels when possible. / 相同生物类别在相关 panel 中尽量保持颜色一致。
- Continuous normalization and palette choice are separate decisions. / 连续变量归一化与色板选择分开处理。
- Synthetic fixtures are software examples only. / 合成数据仅用于软件示例。

## Single-figure rendering · 单图绘制

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

The style gallery currently exposes supported scientific plot families through a common rendering interface. See [`style_gallery/README.md`](style_gallery/README.md).

通用图形通过统一渲染接口调用，详见 [`style_gallery/README.md`](style_gallery/README.md)。

## Pipeline-aware rendering · 流程配套绘图

```bash
python pipeline_tree/run_pipeline.py \
  --module scrna.annotation \
  --input markers=results/markers.csv \
  --input embedding=results/embedding.csv \
  --config project/annotation.json \
  --out build/annotation
```

The pipeline renderer consumes reviewed upstream result tables. It does not rerun Seurat, Scanpy, CellRank, scVelo, CellChat, LIANA, Milo, scCODA, Squidpy, cell2location, Tangram or model fitting.

Pipeline renderer 只消费已审核的上游结果表，不重新执行 Seurat、Scanpy、CellRank、scVelo、CellChat、LIANA、Milo、scCODA、Squidpy、cell2location、Tangram 或模型训练。

Input definitions / 输入定义：

- [`pipeline_tree/IMPLEMENTED_MODULES.json`](pipeline_tree/IMPLEMENTED_MODULES.json)
- [`pipeline_tree/RESULT_CONTRACTS.json`](pipeline_tree/RESULT_CONTRACTS.json)
- [`pipeline_tree/PIPELINE_TREE.md`](pipeline_tree/PIPELINE_TREE.md)

## Research and interpretation routes · 研究与解读入口

- [`research_logic/SKILL.md`](research_logic/SKILL.md) — research design / 研究设计
- [`research_logic/ANALYSIS_SKILL.md`](research_logic/ANALYSIS_SKILL.md) — analysis planning / 分析规划
- [`research_logic/ANALYSIS_EXECUTION.md`](research_logic/ANALYSIS_EXECUTION.md) — code authoring contract / 代码实现约定
- [`result_interpretation/SKILL.md`](result_interpretation/SKILL.md) — actual-result interpretation / 真实结果解读

## Final figure audit · 最终图形审核

For manuscript figures, use the strict audit route in [`SKILL.md`](SKILL.md) to check scale, panel layout, vector export, PDF carriers and review status.

论文正式组图应使用 [`SKILL.md`](SKILL.md) 中的严格审核路线检查尺度、panel 布局、矢量导出、PDF 载体与审核状态。
