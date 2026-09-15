---
name: singlecell-spatial-figures
description: "Render reviewed single-cell and spatial transcriptomics results with explicit visual scales, measured layouts, independent guides, export audits and artifact-bound human review. Use Python's tested v3 pipeline or the explicitly unverified R bridge; do not treat scientific conclusions or journal approval as automated capabilities."
---

<!-- STYLE_GALLERY_V3_2:START -->
## 图形样式执行规则 · v3.2

**所有绘图均不显示 subtitle。** 不将副标题搬成主标题下的另一行说明，也不保留副标题空白。主标题、坐标名称、单位、图例和必要的真实/合成标识是不同概念，不得为删副标题而删掉数值语义。

先读 `style_gallery/examples/README.md` 选择 26 类之一，再读 `style_gallery/DESIGN_GUIDE.md`。同一个 `style_gallery/render.py` 的 minimal/advanced 入口已更新，不另建平行绘图路线。原 FigureSpec schema 3.0、四类 renderer、52 个色卡家族保留。

高级版必须有输入支持的结构性新增：真实条件对照、共索引注释轨道、配对差值、多阶段质量、空间轮廓、给定区间或错误结构。只增加标签/边框不算高级。缺少数据列时不要伪造，必要时退回最简版并解释缺口。图型与对应数据字段见 `style_gallery/catalogue_v32.json`；范例 CSV 只是合成测试，不得代替实验结果。

```bash
python style_gallery/render.py plot --kind heatmap --input reviewed.csv --config reviewed.json --mode advanced --out results/Fig1
python -m pytest style_gallery/tests -q
```

必须检查数值、共同分母、变换与不确定性；高级版如改画配对差值/行比例，轴与图例必须同步改名。每次导出保存输入哈希与语义图层记录。旧版最终 PDF/载体审核仍使用 `scripts/render_v3.py inspect-pdf` / `bind-report`，不把新增 Canvas 检查称为全自动科学审阅。R 仅为共享 Python 引擎的 wrapper，未声明原生 R 等价。
<!-- STYLE_GALLERY_V3_2:END -->

# Single-cell / Spatial Figures · v3

## 1. 定位与能力边界

本 Skill 的核心任务是：**把已经审核的分析结果转换为可追溯、可阅读、经过最终载体检查的图。** 不在绘图时重做细胞注释、差异检验、轨迹模型或因果解释。科学叙事只做设计讨论与人工验收，不冒称已被代码判定正确。

先看 `CAPABILITIES.json`，当前能力只以它和 `QA_REPORT.md` 为准。`references/` 中旧版资料是文献或历史实现，不会因文件存在就成为 v3 已连接的功能。

Python v3 已连接四种 renderer：`embedding`、`spatial`、`marker_dot`、`annotated_heatmap`。其他图先使用已审阅的项目脚本或旧版原子函数，再做导出审核；不得假装已接入新流水线。R 的 `render_v3.R` 是共用规划产物的实现初稿，未在本次环境运行；不能把 Python 测试算成 R 测试。

## 2. 先选择执行路径

**局部修改**：输入、数值映射和布局已明确时，只改指定字段。仍需检查改动后的输出、字体、源数据与依赖影响。不强制创建新的分析工程。

**新图或整图重构**：使用 `spec_version: '3.0'` 和 `scripts/render_v3.py`。从 `examples/v3_software_qa/figure.yaml` 复制结构，换成真实来源、真实字段和经审阅的尺度。这个例子是人工软件测试，绝不能混入研究结果。

**复杂项目扩展**：先确认缺的是 adapter、renderer 还是人工设计决策。只扩展明确的缺口，增加输入/尺度/版式/导出测试后更新能力登记；不为一个 dotplot 安装整套模型生态。v2 模板不是已实现 v3 renderer 的清单。

## 3. 输入与数值：不可破坏的约束

必须声明唯一 ID、样本/切片、矩阵或表格方向、实际 assay/layer、量纲、转换、分母和独立样本单位。绘图函数只处理副本。缺失不等于零；top-k 成员不等于组成比例；OT coupling 不等于逐行转移概率；预测轨迹不等于物理运动。

AnnData/Seurat/SpatialExperiment 在上游明确选层并对齐 ID；v3 使用 CSV/TSV 交换表，不对全图谱稠密化。未知数据/尺度、重复主键、未声明坐标单位、越界 panel 或未实现 renderer 应报错，不降级猜测。

## 4. 把设计问题转成可检查的选择

先写一句**可被图中实际比较回答的问题**，再指出回答它的 marks、对照、分母和不确定性。不要先写阳性结论再安排图。

为整图指定 `visual.lead_panel` 和 `visual.reading_order`。对主比较优先使用可直接比较的位置/长度，空间或嵌入图保留真实几何；热图的颜色适合结构筛选，不代替精确效应比较。先看最终尺寸的标签是否可读，再决定增加面板面积、拆矩阵、变更图型或减少经过科学论证的展示范围。

`design_audit` 会提示主次面积、几何阅读顺序和过大的矩阵单元，但它是**审阅提示**，不是审美或科学评分。具体设计决策、失败例和重构顺序见 `references/v3_playbook.md`。

## 5. 色阶与图例必须一起定义

连续量在 `scales` 中配置 `limits`、`norm`、`out_of_range`、`invalid` 和 `bad/under/over`。支持 `linear`、`two_slope`、`log`、`symlog`、`power`、`boundary`。中心值、阈值与截断来自实际问题，不能为突出效果而自动挑选。图例刻度用原始单位，缺失单独显示，越界/非法值数量写入 QA。

图例在根级 `guides` 独立定义：owner、panels、channel、scale_id、位置、方向、刻度/标签、列数、字号、长度和厚度。共享图例只允许共享同一个尺度 ID；marker 点面积必须有比例图例。不允许通过隐藏分类或无声缩字让图例“放得下”。

明度、背景对比、近似 CIELAB 距离及三类 severity-100 CVD 筛查均需阅读。筛查阈值是可调政策，不是可访问性认证；最终仍要确认关键区别不是只靠颜色。不要将 deltaE76 写成 deltaE2000 或人类辨色保证。

## 6. 按内容测量，不按固定百分比挤压

布局先测量实际字体下的标题、标签、图例及热图注释，再试右侧/底部方案。设置最小数据区域，保留切片长宽比。标题可用 `panels[].title`；非数值大小编码的散点可用 `marks.area_pt2`，它是渲染尺寸而非真实 spot 直径。

换行保留完整标识符，数学式不随意断开。超过容纳能力时抛出 `LayoutFailure`，改整体尺寸或分区，不删除标签、篡改尺度或缩到最小字号以下。它是有边界的布局搜索，不是任意论文的全局最优排版器。

## 7. 执行和输出

在 Skill 目录运行：

```bash
python scripts/render_v3.py render project/figure.yaml --root project --out build/Fig1
python scripts/render_v3.py review build/Fig1
```

第一次 `review` 应失败，因为审阅记录仍是 pending。渲染输出包含 PDF/SVG/PNG、source CSV、provenance、`preflight.json`、`qa.json`、`render_plan_v3.json`、`snapshot.json`、`review.json` 及修订记录。不把文件后缀当作矢量或嵌入字体证明。

R 路径：

```bash
Rscript scripts/render_v3.R build/Fig1/render_plan_v3.json build/Fig1/figure_R.pdf
python scripts/render_v3.py inspect-pdf build/Fig1/figure_R.pdf --out build/Fig1/R_pdf_audit.json
python scripts/render_v3.py bind-report build/Fig1 build/Fig1/R_pdf_audit.json --kind export
```

R 使用上一步 Python 生成的几何和颜色，不是独立的等价布局引擎。TeX 数学文本和负值注释轨道不由此 R bridge 自动翻译；使用已验证的原生 R adapter。绑定新产物后旧 review 必须重做。

## 8. 最终载体不是导出文件的别名

图放入组图、报告或幻灯片后，检查**真正交付的 PDF**。声明其 0-based 页码和毫米坐标；用原图与载体中的真实文字锚点核对位置、缩放、裁切和显示字号：

```bash
python scripts/render_v3.py carrier build/Fig1/Fig1.pdf final_report.pdf placement.json --out build/Fig1/carrier_audit.json
python scripts/render_v3.py bind-report build/Fig1 build/Fig1/carrier_audit.json --kind carrier
```

`placement.json` 为 `{"page_index":0,"box_mm":[20,30,150,90]}`，数值必须来自实际排版。该检查支持未旋转、保留文字的 PDF 插入；栅格化、描边文字或锚点不足应报告无法验证，不能冒称通过。未实现直接读取 DOCX/PPTX 的最终排版；先从目标软件导出实际 PDF。

## 9. 修改、升级与验收

颜色/尺度修改复核所有使用该尺度的 panel；字体、全局布局或渲染代码修改保守地复核整图。输入、依赖、共享图例和实际文件哈希通过 `snapshot` / `impact` 追踪，旧审阅不能移用到新产物。

同类缺陷连续两轮未解决、局部修改涉及多 panel、需要低于最小字号或发生跨 panel 侵入时，停止微调，转为重排。查看 `repair_decision.json`；重构要重新检查整图，而不只看改动处。两轮是可改项目阈值，不是期刊规定。

人工验收逐项记录 reviewer、含时区时间、具体证据、失败条件、warning ID 的处理理由，以及 standalone/placed 载体。`review_pending.json` 是绑定新报告后新生成的待审模板；重新审阅后用它更新 `review.json`，不要仅复制一个新哈希来绕过复核。

不自动签署科学结论。自动硬错误不能用说明文字豁免；警告可以在查看实际输出后以具体理由处理。字形替换、数学字体、最终字号和包围盒有程序检查；光学字距、全部数据遮挡和科学解释仍须人工检查。

## 10. 交付与维护

交付实际图、真实脚本、源数据、配置、QA、snapshot 和完整审阅记录。对未跑的 R/设备/生物学项目明确标注。

任何新能力必须同步修改 `CAPABILITIES.json`、对应测试及当前 `QA_REPORT.md`；历史审计保留但不重复承担当前能力说明。硬约束保护数值、身份、几何和来源；字号、色差、留白、列宽、修复轮次等默认值允许有记录地调整。不要将这些默认值称为 Nature/Cell/Science 的通用官方标准。

## Palette presets · v3.0.1（兼容扩充）

保留 `spec_version: '3.0'`。本次增加 52 个可选色卡家族，原有默认色和六种 norm 不变。使用前读 [色卡索引与调用规则](assets/palettes/README.md)。类别尺度可写 `preset: C19` 加固定 `order`；连续尺度可写 `preset: M02`，中心发散可用 `preset: D03` 加 `norm: {type: two_slope, center: 0}`。`preset` 不可与显式 colors/cmap 混用。C06 必须选具体变体；C21 是衍生试选，不标为论文原色。

`render_v3.py` 自动编译预设并保留 `palette_bindings.json`、原始配置及色卡依赖哈希。类别颜色不足时停止，不循环或插值；只筛选群组时重用已保存的命名颜色字典。R 的 `scripts/palette_presets.R` 读取同一 RGB8 表，但当前未运行原生 R 测试，不能扩张为跨后端等价验证。
