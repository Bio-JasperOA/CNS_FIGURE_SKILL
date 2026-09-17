---
name: singlecell-spatial-figures
description: "Render reviewed single-cell, spatial and multimodal biological results with explicit scales, reproducible layouts, export audits and human scientific review. / 将已审核的单细胞、空间与多模态生物学结果转换为具有明确尺度、可复现布局、导出审核和人工科学复核的图形。"
---

# Single-cell & Spatial Figure Skill · 单细胞与空间科学绘图 Skill

This Skill converts **reviewed analysis outputs** into traceable scientific figures. It does not rerun upstream biological/statistical models and does not automatically certify biological conclusions or journal readiness.

本 Skill 将**已经审核的分析结果**转换为可追溯的科学图形。它不会重新运行上游生物学/统计模型，也不会自动认证生物学结论或期刊发表资格。

## 1. Choose the smallest route · 选择最小执行路线

Use the route that matches the actual task. / 根据真实任务选择对应入口：

- `plot-single` — render one reviewed table with `style_gallery/render.py`. / 使用 `style_gallery/render.py` 绘制单个已审核结果表。
- `plot-pipeline` — render the figure set for one registered analysis module with `pipeline_tree/run_pipeline.py`. / 使用 `pipeline_tree/run_pipeline.py` 为一个注册分析模块生成配套图组。
- `figure-audit` — render or audit a strict FigureSpec figure, exported PDF or final carrier. / 渲染或审核严格 FigureSpec、导出 PDF 或最终载体。

Do not start a new research plan when the request is only to redraw an existing result. Do not rerun analysis when the task is only figure generation.

如果用户只要求重绘现有结果，不要重新启动研究设计；如果任务只是绘图，不要重新运行分析。

## 2. Scientific invariants · 科学不变量

Every figure must preserve the numerical and inferential meaning of its input.

每张图都必须保持输入结果原有的数值与推断含义。

Required rules / 必须遵守：

- Never invent missing significance, confidence intervals, trajectories, boundaries, neighborhoods, probabilities or uncertainty. / 不得补造缺失的显著性、置信区间、轨迹、边界、邻域、概率或不确定性。
- Missing values are not zeros. / 缺失值不等于零。
- A top-k list is not a composition denominator. / top-k 列表不等于组成比例的完整分母。
- Pseudotime is not proven lineage. / pseudotime 不等于已证明的真实谱系。
- OT coupling is not automatically a row-wise transition probability. / OT coupling 不自动等同于逐行转移概率。
- Dissociated data alone do not prove a spatial mechanism. / 解离数据本身不能单独证明空间机制。
- Synthetic fixtures are software examples, never biological evidence. / 合成 fixture 仅用于软件示例，不能作为生物学证据。

## 3. Visual policy · 视觉规范

All public plotting routes follow the same visual policy.

所有公开绘图路线统一遵守以下视觉规范：

- **No subtitle. / 不使用 subtitle。**
- Keep essential axis labels, units, legends and provenance. / 保留必要的坐标名称、单位、图例和来源记录。
- Keep explanatory microcopy off the plotting canvas; put interpretation in captions/provenance. / 不在画布上堆叠说明性小字，解释放入 caption/provenance。
- Stable biological identities should reuse stable named colors across related panels. / 相同生物学类别在相关 panel 中尽量复用固定命名颜色。
- Palette selection and numerical normalization are independent decisions. / 色板选择与数值归一化相互独立。
- `advanced` must expose a real scientific dimension already supported by the input. / `advanced` 必须展示输入中真实存在的额外科学维度。
- Decoration alone never qualifies as an advanced view. / 仅增加颜色、边框、阴影或装饰不构成 advanced 图。

Examples of valid advanced dimensions include condition comparison, uncertainty, pairing, hierarchy, spatial context, temporal/lineage structure, transitions, multimodal evidence and prediction error.

有效的 advanced 维度包括条件比较、不确定性、配对结构、层级、空间背景、时间/谱系结构、转变、多模态证据与预测误差。

## 4. Input contract · 输入约定

Before rendering, explicitly identify the following when relevant:

绘图前应根据任务明确：

```text
unique IDs / 唯一 ID
sample or section / 样本或切片
assay/layer / assay 或 layer
matrix/table orientation / 矩阵或表格方向
units and transformations / 单位与变换
comparison denominator / 比较分母
independent biological unit / 独立生物学重复单位
category order / 类别顺序
shared scales / 需要共享的尺度
provenance / 来源记录
```

Unknown scales, duplicate primary keys, ambiguous coordinates or unsupported renderers should fail explicitly rather than be guessed.

尺度未知、主键重复、坐标含义不清或 renderer 不支持时，应明确报错，而不是猜测处理。

## 5. Single-figure route · 单图路线

Read `style_gallery/README.md` and its machine-readable catalogue before using a plot family.

使用单图路线前，先读取 `style_gallery/README.md` 与对应机器可读 catalogue。

```bash
cd singlecell-spatial-figures/style_gallery
python render.py plot \
  --kind heatmap \
  --input reviewed.csv \
  --config reviewed.json \
  --mode advanced \
  --out results/Fig1
```

`minimal` is the smallest scientifically complete view. `advanced` may add only information already present in the reviewed input.

`minimal` 是最小科学完整视图；`advanced` 只能增加已审核输入中真实存在的信息。

## 6. Pipeline-aware route · 流程配套图组

Locate the module in `pipeline_tree/IMPLEMENTED_MODULES.json`, then align every named input to `pipeline_tree/RESULT_CONTRACTS.json`.

先在 `pipeline_tree/IMPLEMENTED_MODULES.json` 中定位模块，再根据 `pipeline_tree/RESULT_CONTRACTS.json` 对齐每个具名输入。

```bash
cd singlecell-spatial-figures
python pipeline_tree/run_pipeline.py \
  --module scrna.annotation \
  --input markers=results/markers.csv \
  --input embedding=results/embedding.csv \
  --config project/annotation.json \
  --out build/annotation
```

The plotting layer does not rerun Seurat, Scanpy, CellRank, scVelo, CellChat, LIANA, Milo, scCODA, Squidpy, cell2location, Tangram, scVI or model fitting.

绘图层不重新运行 Seurat、Scanpy、CellRank、scVelo、CellChat、LIANA、Milo、scCODA、Squidpy、cell2location、Tangram、scVI 或模型拟合。

The generated `manifest.json` is the authoritative record of what was rendered and what was skipped.

生成的 `manifest.json` 是该次运行实际生成与跳过内容的权威记录。

Validate the registry when module definitions change / 修改模块定义后执行：

```bash
python pipeline_tree/validate_registry.py validate
python -m pytest pipeline_tree/tests -q
```

## 7. Strict FigureSpec and audit route · 严格 FigureSpec 与审核路线

Use the strict route for manuscript-level layout, scale, vector export and final-carrier checks.

论文级布局、尺度、矢量导出与最终载体检查使用严格审核路线。

```bash
python scripts/render_v3.py render project/figure.yaml \
  --root project \
  --out build/Fig1

python scripts/render_v3.py review build/Fig1
```

A new render is not automatically approved. Human review remains pending until the generated artifact is inspected and explicitly reviewed.

新生成的图不会自动获得批准。必须查看实际产物并进行人工复核后，审核状态才可改变。

For final PDF placement / 检查最终 PDF 中的真实放置：

```bash
python scripts/render_v3.py carrier \
  build/Fig1/Fig1.pdf \
  final_report.pdf \
  placement.json \
  --out build/Fig1/carrier_audit.json
```

Use real page indices and placement coordinates from the final layout. If the carrier has rasterized or outlined text and verification is impossible, report that limitation instead of claiming success.

页码与放置坐标必须来自真实最终排版。如果载体已经栅格化或文字转曲而无法验证，应明确报告限制，不能冒称通过。

## 8. Scales and legends · 色阶与图例

Continuous scales must explicitly define scientifically meaningful limits, normalization and out-of-range behavior. Supported normalization families include linear, diverging/two-slope, log, symlog, power and boundary-style mappings where implemented.

连续尺度必须显式定义具有科学意义的范围、归一化与越界处理。实现支持时可使用 linear、diverging/two-slope、log、symlog、power 与 boundary 等映射。

Shared legends are valid only when panels truly share the same scale semantics. Marker size, color and other channels must have interpretable guides when they encode quantitative information.

只有 panel 真正共享相同尺度语义时才能共享图例。点大小、颜色等通道用于编码定量信息时必须具有可解释的 guide。

## 9. Layout and readability · 布局与可读性

Measure actual titles, labels, legends and annotations before compressing the data region. Preserve spatial aspect ratio where scientifically meaningful.

压缩数据区域前应先测量实际标题、标签、图例与注释。空间几何具有科学意义时必须保留合理长宽比。

If content cannot fit at the minimum readable size, enlarge the figure, split the panel, reduce only scientifically justified content, or choose a different plot type. Do not silently remove labels or distort scales to make the figure fit.

内容在最低可读字号下无法容纳时，应扩大画布、拆分 panel、仅减少经过科学论证的内容，或更换图型；不得为了“塞下”而静默删除标签或扭曲尺度。

## 10. Output and provenance · 输出与可追溯性

Publication candidates should preserve vector output when appropriate. PNG files are useful for preview; PDF/SVG are preferred when vector structure is retained.

在合适场景应保留矢量输出。PNG 适合预览；能保持矢量结构时优先使用 PDF/SVG。

A valid output should retain enough provenance to identify source tables, configuration, transformations and relevant hashes. File extensions alone are not proof of vector quality, embedded fonts or scientific validity.

有效输出应保留足够 provenance，以识别来源表、配置、变换与相关哈希。文件后缀本身不能证明矢量质量、字体嵌入或科学有效性。

## 11. Review boundary · 审核边界

Automated checks may identify structural problems, export failures, missing mappings and layout warnings. They do not replace visual inspection, biological interpretation or scientific responsibility.

自动检查可以发现结构问题、导出失败、映射缺失与布局警告，但不能替代视觉检查、生物学解释与科学责任。

Never automatically sign off a scientific conclusion. / 不自动签署任何科学结论。
