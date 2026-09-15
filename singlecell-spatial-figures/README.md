# Single-cell / Spatial Figures · v3

入口为 [SKILL.md](SKILL.md)。当前能力边界见 [CAPABILITIES.json](CAPABILITIES.json)，pipeline-first 运行层见 [pipeline_tree/README.md](pipeline_tree/README.md)，执行与验证记录见 [pipeline_tree/RUNTIME.md](pipeline_tree/RUNTIME.md) 和 [QA_REPORT.md](QA_REPORT.md)。

当前 Skill 保持 **v3 / FigureSpec 3.0**，同时提供两层可复用能力：

1. 原 v3 FigureSpec 审核/载体层，用于严格的尺度、布局、导出、PDF carrier 与人工签署；
2. pipeline-first 科研绘图层，用于把已经审核的 scRNA-seq、空间转录组、跨模态、胚胎发育和 foundation-model 分析结果映射到必产图、高级图和 panel。

## Pipeline-first runtime

当前 `pipeline_tree/` 已覆盖 **36/36 注册模块**：

- scRNA-seq：13
- spatial transcriptomics：11
- cross-modal：4
- development / embryo：4
- foundation-model evaluation：4

机器注册表包含 141 个 required figure assignments、107 个 advanced figure assignments 和 240 个 unique plot targets。最新完整 GitHub Actions 验证为 **60 tests passed**，随后实际渲染 **36 个模块 / 286 个 synthetic figure records**。

统一入口：

```bash
python pipeline_tree/run_pipeline.py \
  --module scrna.annotation \
  --input markers=results/markers.csv \
  --input embedding=results/embedding.csv \
  --config project/annotation.json \
  --out build/annotation
```

每个模块的字段约束见 `pipeline_tree/RESULT_CONTRACTS.json`；完整分析树见 `pipeline_tree/PIPELINE_TREE.md`；当前可执行边界见 `pipeline_tree/IMPLEMENTED_MODULES.json`。

绘图 runtime 不重新执行 Seurat、Scanpy、CellRank、scVelo、CellChat、LIANA、Milo、scCODA、Squidpy、cell2location 等上游分析，也不制造缺失的统计显著性、区间、轨迹、分割边界、邻域、概率或不确定性。缺少高级图所需输入时，会在 `manifest.json` 中明确记录 `skipped` 原因。

## 图形与视觉规范

所有图统一执行：

- **禁止 subtitle**；
- palette 与 normalization 分离；
- 同一生物类别尽量使用固定命名颜色；
- `advanced` 必须增加真实科学维度，而非只增加装饰；
- standalone PDF/SVG 是矢量发表候选，review contact sheet 只用于检查和导航；
- synthetic fixtures 永远不能当作生物学结果。

26 类通用绘图 primitive 和 minimal/advanced 范例位于 [style_gallery](style_gallery/README.md)。52 个色卡家族位于 [assets/palettes](assets/palettes/README.md)。

## 原 v3 FigureSpec / 最终载体审核

严格 FigureSpec 路径仍保留，用于最终论文图与载体检查：

```bash
python -m pip install -r requirements-v3.txt
python scripts/render_v3.py render examples/v3_software_qa/figure.yaml --root examples/v3_software_qa --out build/software_qa
python scripts/render_v3.py review build/software_qa
```

需要检查最终报告/组图 PDF 时继续使用 `inspect-pdf`、`carrier` 和 `bind-report` 路线。pipeline runtime 的成功不替代最终 carrier audit 或人工科学审阅。

## 色卡

保留 `spec_version: '3.0'` 和既有 52 个色卡家族。类别颜色不足时停止，不循环或插值；筛选群组时继续复用固定命名颜色。连续尺度的 palette 与 normalization 独立配置。

R bridge 仍未声明与 Python runtime 原生等价；只有实际执行并加入测试后才能扩张该能力声明。
