# 复杂图形：从数据结构到绘制代码

本文件是原创建议，不是任何论文源码的逐行拷贝。Pxx 指论文；Cxx 指已经检查的代码，见 `evidence_catalogue.md`。没有代码证据的工具明确列为工程推荐。所有例子都要求真实、经过核对的输入；不得用模拟数据代替论文或用户的结果。

## 1. 先把分析结果变成可审计的绘图数据

推荐的五层结构：

```text
分析对象 → 有 ID 的结果表/矩阵/图 → 视觉编码 → 图层与布局 → 导出与核查
```

不要把标准化、统计检验、配色、坐标翻转和文件导出藏在一个长函数里。分析函数负责数值，绘图函数消费已经确定的数值并返回 Axes / ggplot / Heatmap。临时修改坐标或归一化的行为必须能从 provenance 看出来。

每幅图的最小数据协议：记录输入版本、细胞/基因 ID、sample_id、section_id、细胞类型顺序、数值单位、变换、筛选、缺失值策略和随机种子。`sample_id` 是生物学重复；`section_id` 是组织切片。它们不能互换。

## 2. Marker dot plot：两个矩阵、两个编码

对于群组 g、基因 k：

```text
fraction[g,k] = count(raw_detection[cell,k] > 0) / n_cells_in_group[g]
mean[g,k]     = sum(declared_expression[cell,k]) / n_cells_in_group[g]
area[g,k]     = maximum_area × fraction[g,k]
```

分母包括零表达细胞；没有观测到的群组是 NA，而不是零。原始 counts 用来判定检测，归一化表达用来描述平均水平，integrated residuals 不能当检测矩阵。

特别注意：`mean(log1p(x))` 不等于 `log1p(mean(x))`。本包的 `marker_summary` 计算“传入矩阵的算术均值”，**不承诺自动与 Seurat/Scanpy 某个版本 DotPlot 的默认聚合完全一致**。跨 R/Python 比较时，先明确双方输入层和数学定义，再用共同小矩阵检查；不要只比较函数名字。

如果需要按基因 z-score，本包使用群组间总体标准差（ddof=0）；R 的 `scale()` 默认约定可能不同。保留未截断值，另生成展示值。点的面积而非半径与比例成正比；Python scatter 的 s 是 pt²，R 用 `scale_size_area()`。独立解释点面积和颜色图例。零检测与未观测群组都可能没有点，因此对未观测群组另作 NA 标识。

实现：两版 `marker_summary`、`gene_zscore`、`plot_marker_dot`。这是工程规则，不声称 16 篇论文全部采用同一个均值定义。

## 3. 多注释热图：共享索引的组合，不是反复拼截图

**实证 C04 / P09。** 作者把富集 P 值与 OR 做成两个矩阵，颜色为截断后的 −log10(P)，格内文字为 OR，边缘条形为基因数。三种编码回答不同问题。

实现流程：先得到唯一的 row_order / column_order，再同时重排主矩阵、效应矩阵、顶部和侧面注释。禁止每一层独立聚类后按位置拼接。基因模块已按生物学含义指定时，可以在模块内聚类，但必须记录最终顺序。聚类距离、链接方式、输入尺度属于分析参数。

Python：基础版以 `GridSpec` + `imshow` + `bar/barh` + 共享轴完成；模块多或注释多时可考虑 Marsilea/PyComplexHeatmap（补充推荐，不是已核实的 P09 作者工具）。

R：`ComplexHeatmap::Heatmap` + `HeatmapAnnotation`/`rowAnnotation` + `anno_barplot`。作者使用 `cell_fun`；本包原创实现使用向量化 `layer_fun`，以 `labels[cbind(i,j)]` 按真正的行列索引取值。不要把索引 j/i 颠倒。

不要把论文的 P 值悄悄改标为 FDR q 值。输入为 q 时，图例才写 −log10(q)。q=0 的处理要声明数值精度下限或已知检测边界，不能生成无穷值再任意替换。热图色标显示截断阈值；不能给同一颜色在相邻同类 panel 上安排不同含义而不说明。

实现：Python `annotated_heatmap`；R `annotated_enrichment_heatmap`。R 数字标签和绘图设备尺寸必须足够，不可为容纳过多条目无限缩小字号。

## 4. 空间多图层：坐标系统先于美术

**实证 P12 Fig.2、C06 当前教程；P01 Fig.3。** 图像、细胞 polygon、spot、分子点、ROI 可以属于同一空间对象，但可能处于不同坐标系。

```text
[x_plot, y_plot, 1]^T = A × [x_native, y_native, 1]^T
```

A 可包含尺度、平移、旋转和反射。记录 image origin、像素到微米的校准以及坐标列的 x/y 含义；row/column 不自动等于 x/y。仿射变换不能冒充非线性配准。切片上的多个“同名区域”也不是天然对齐的。

推荐图层顺序：已配准底图 → 分割面/空间表达 → 边界与 ROI → 比例尺/标注。保持 equal aspect；不要独立拉伸 x/y。反转 y 轴只能由已声明的原点约定驱动，而且必须是幂等操作，重复调用不能翻回去。

跨样本比较同一种量时，锁定数值单位、色标和展示尺度。不同基因可以采用不同范围，但必须各自标清；不能据此直接比较绝对强度。ROI 选择依据提前确定，保留全片定位图。没有可靠校准时只写 pixel，不能编造 µm 比例尺。

基础实现：`affine_coordinates` 和 `plot_spatial_values`。Python 接受已配准的 image_extent；R 基础函数仅画点，不自动完成组织图像配准。真实细胞轮廓需要 polygon/segmentation，散点尺寸只是显示尺寸，不是细胞物理大小。

高级路由：Python SpatialData/spatialdata-plot、Squidpy；R SpatialExperiment + ggplot2/sf，独立色标可考虑 ggnewscale。使用当前版本前检查官方 API。空间坐标不等于地理经纬度。

## 5. 空间饼图：局部组成与 top-k 成员集合分开

**实证 C05 / P09。** 某脚本先把 top3/top6 类别变成 0/1，再绘制。这种等权切片表示“属于排名前 k 的类型”，不表示真实细胞比例。

真实比例图需要所有非负组分之和为 1。只展示重要类型时，把其他所有组分的质量加为 Other，而不是丢弃后无说明地重归一化。零总量 spot 应标记不可估计，不应平均分给所有类型。

R `collapse_proportions` 保留质量，`plot_spatial_pies` 使用 scatterpie；半径用输入空间单位。比较不同切片时不要用不同缩放的半径产生虚假的细胞总量差别。若半径编码总量，明确面积编码还是半径编码。本包默认统一半径，不额外暗示总量。

大量 spot × 多种类型时，饼图可能既难读又文件巨大；改成预先选择的类型分面图、区域组成热图或者确定 ROI 内的饼图。这里的选择属于工程推荐，不是要求所有论文都使用饼图。

## 6. 邻域、通讯、弦图：先定义边再绘制

建立图前声明节点是什么（单细胞、spot、细胞类型、区域），边是什么（空间邻接、配体受体统计得分、OT coupling），方向和边权单位是什么。

Python `radius_graph_edges` 使用每个 section 内的 cKDTree 半径查询，预估边数后再物化边表，避免 n×n 全距离矩阵。它不会自动处理组织空洞、物理屏障或细胞边界；需要另加过滤。空间接近本身不是通讯、物理接触或因果证据。

网络图必须固定相同节点位置后比较条件；如果每张图重新 spring layout，视觉移动可能完全来自算法。阈值与 top-N 规则要事先定义，报告被删除的边/权重；没有足够证据时不要用箭头装饰成定向通讯。

R 可使用 igraph/ggraph，弦图可使用 circlize；Python 可使用 NetworkX + Matplotlib。这些是推荐实现路线，不是本轮已确认 LIANA+ 用于某个特定主图的工具。类别很多时，矩阵热图常比“毛线团”更便于比较。置换检验要保留样本、区域等设计约束。

## 7. 谱系轨迹热图：先拟合曲线，再选择行顺序

**实证 C02 / P06。** 作者以 CellRank 谱系 driver 结果选择基因，建立 GAM，使用 lineage 与 ct_pseudotime 绘制热图；正式 Fig.3 图注说明了平滑趋势与峰值排序。

对基因 k、谱系 l，拟合 `f[k,l](t)`，谱系概率可作为拟合权重。将趋势预测到共同的时间网格；选择按峰值时间、已定义模块或另一可解释标准排序，最后才渲染矩阵。颜色显示的是拟合表达或其标准化结果，不应标成未经模型处理的原始 counts。

不要把每个基因独立 min-max 后的相同颜色误解为相同绝对表达。图注需交代选择了哪些基因、在哪些细胞上拟合、权重来源、平滑参数和标准化方向。没有数据覆盖的时间段不应随意外推连线。伪时间不是自然时间，RNA velocity 不是组织中的真实运动速度。

Python 推荐使用 CellRank 已拟合模型对象；R 可选择 mgcv/tradeSeq 等合适分析工具后输出共同结果表。Python `weighted_time_bins` 只是描述性加权分箱，**不是 GAM、不是 CellRank 替代品，也不生成置信区间**。

不确定性需要与设计相符的模型或生物学重复 bootstrap；本包的权重 n_eff 只是权重诊断，不能充当 donor 数或独立样本数。

## 8. 发育与 OT 流图：先守恒，再画 Bézier 曲线

**方法背景 P13 / P16；流图代码为本包原创，未核实作者采用某个特定 Sankey 包。**

设 P 是 cell×cell coupling，A/B 是源/目标细胞到类型的指示矩阵：

```text
F = A.T @ P @ B
sum(F) = sum(P)
```

如果输入是行随机转移概率 T，而不是 joint coupling，必须先根据来源分布 μ 构造 `P = diag(μ) @ T`，或明确画的是其他非总体质量的汇总。直接对 T 求和会隐含每个来源细胞等权，不一定符合模型定义。

先在稀疏空间聚合，再将小型 group×group 矩阵变成密集矩阵。source_fraction 应在聚合后按来源归一化，零质量来源保持 NA。不平衡 OT 的总质量可能不为 1；不能偷偷校正成守恒比例。

每条 ribbon 的厚度来自同一套质量单位；计算源端/目标端累积区间，用 Bézier 路径连接。不要对两端分别归一化，也不要隐性丢掉小边。删除小边应保留 Other 或报告丢弃质量。二维弯曲连线是版式，不是空间运动路径；推断的谱系概率不是已观测的克隆追踪关系。

实现：两版 `aggregate_transport`；Python `transport_ribbons`；R `plot_transport_alluvial`。两阶段流图的排序应按预先确定的发育顺序，不为显著视觉效果调顺序。

## 9. 定量对照：生物学重复与不确定性

每个点的单位写清楚：cell、spot、section、donor 或独立培养。细胞多不等于生物学重复多。实验设计以 donor 为单位时，效应量和区间应来自相应的 donor-level/mixed model/pseudobulk 分析，不能因为单细胞散点很多就把所有细胞当独立重复。

本包不自动提供显著性星号。绘图函数接收已经校验的 estimate/lower/upper、test、n_samples、adjustment 等字段；不要在渲染时默默重新检验。展示观测离散程度的 SD 与估计不确定性的 CI 不能混标。

这是统计语义保护，不声称本次已经审计每篇论文全部统计设计。

## 10. 复合排版与矢量/栅格混合导出

最终物理尺寸先确定，随后安排 panel、字体、边距和图例；不要先画一张巨大图再整体缩小，导致所有文字不可读。89/183 mm、正文 7 pt、panel 8 pt 是本包可改的工作室默认值，不是全部 CNS 子刊统一硬性规定。Nature 风格示例可使用小写 panel label；Cell/Science 往往另有命名约定，应以目标论文/期刊为准。

Python 优先统一 Matplotlib Figure/Axes；作者 C03 的 plotnine+patchworklib 需要匹配版本。R 中 ggplot 可用 patchwork/cowplot；ComplexHeatmap 属于 grid 系统，不应直接当普通 ggplot 使用。`grid.grabExpr` 捕获时应指定目标物理尺寸，含 anno_mark 等位置敏感注释时尤其要检查最终设备；无法可靠嵌入时单独导出，再按记录的流程组合。

高密度点层栅格化，文本、坐标轴和线条保留矢量；不要把全图截图放进 PDF 就称为“矢量图”。Matplotlib 可按 artist 设置 rasterized；R 可用 ggrastr 或 Heatmap 的受控栅格选项。PDF/SVG 都要实际检查；SVG 将文字保留为 text 不代表在未安装字体的电脑上绝不会替换。

本包 Python 固定画布导出，不使用 bbox_inches='tight' 改变最终物理尺寸。它不会自动保证每个标签都在画布内；必须在最终尺寸预览中检查裁切。文字删除版只作排版资产，不能作为没有图例/单位的独立科学结果。

## 官方实现文档

- Matplotlib 分层栅格化：https://matplotlib.org/stable/gallery/misc/rasterization_demo.html
- ComplexHeatmap 注释与设备尺寸：https://jokergoo.github.io/ComplexHeatmap-reference/book/heatmap-annotations.html
- ComplexHeatmap cell_fun / layer_fun：https://jokergoo.github.io/ComplexHeatmap-reference/book/a-single-heatmap.html
- patchwork 组合：https://patchwork.data-imaginist.com/articles/guides/assembly.html
- ggnewscale：https://eliocamp.github.io/ggnewscale/index.html
- Marsilea：https://marsilea.readthedocs.io/en/stable/
- PyComplexHeatmap：https://pypi.org/project/PyComplexHeatmap/

这些是辅助实现来源；论文与精确代码出处见 `evidence_catalogue.md`。可视化建议是定性综合，不是包使用频率的系统统计。
