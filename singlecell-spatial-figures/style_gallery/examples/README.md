# Minimal / Advanced · v3.2

所有数值均为合成样式测试；不是实验结果。图内无subtitle。

## 01 · 嵌入 / UMAP

| Minimal | Advanced |
|---|---|
| ![](figures/embedding_minimal.png) | ![](figures/embedding_advanced.png) |

输入的状态图 + 明确的父类分层 + 直接身份标注

**数据边界：** abstract_edges、edge_definition、parent；不从点云虚构谱系

**对照依据：** BANKSY Fig.3a–b；图型对照继承v3.1，非本轮逐图复现

## 02 · 空间表达

| Minimal | Advanced |
|---|---|
| ![](figures/spatial_minimal.png) | ![](figures/spatial_advanced.png) |

真实输入的分割多边形 + 指定ROI + 物理比例尺

**数据边界：** vertices、rois、coordinate_unit；缺少分割只能画点

**对照依据：** Squidpy Fig.3–4；本轮读图注/方法，不声称像素复现

## 03 · Marker 点阵

| Minimal | Advanced |
|---|---|
| ![](figures/dotplot_minimal.png) | ![](figures/dotplot_advanced.png) |

条件内成对行 + 基因模块括号 + 独立身份色带

**数据边界：** condition、module；大小是面积而非半径

**对照依据：** spatialDLPFC Fig.5–6；继承作者代码和图注对照

## 04 · 多注释热图

| Minimal | Advanced |
|---|---|
| ![](figures/heatmap_minimal.png) | ![](figures/heatmap_advanced.png) |

模块分块 + 样本条件轨道 + 对齐计数；可显示另一个已声明效应

**数据边界：** module、condition、n、可选effect；索引不可错位

**对照依据：** spatialDLPFC Fig.3D/6C–D；继承对照

## 05 · 分布 / 分层雨云

| Minimal | Advanced |
|---|---|
| ![](figures/distribution_minimal.png) | ![](figures/distribution_advanced.png) |

条件分层半密度 + 全部点 + median/IQR + n

**数据边界：** condition可选；KDE不是统计区间

**对照依据：** BANKSY Fig.3j；violin为图型对照，不称作者画过本雨云布局

## 06 · 细胞组成

| Minimal | Advanced |
|---|---|
| ![](figures/composition_minimal.png) | ![](figures/composition_advanced.png) |

逐样本×类型比例矩阵 + 条件块 + 实际分母

**数据边界：** fraction是上游比例；显式零与缺失不同

**对照依据：** HNOCA Fig.5g–h；组成及样本注释思路，矩阵为原创变体

## 07 · 配对比较

| Minimal | Advanced |
|---|---|
| ![](figures/paired_minimal.png) | ![](figures/paired_advanced.png) |

全部配对差值、排序、零参考和样本IQR

**数据边界：** sample对应真实配对；median/IQR是描述不是CI

**对照依据：** LIANA+ Extended Data Fig.3；统计单位对照，差值版原创

## 08 · 火山图

| Minimal | Advanced |
|---|---|
| ![](figures/volcano_minimal.png) | ![](figures/volcano_advanced.png) |

基因集圈选 + 预先声明标签 + 双向数量

**数据边界：** feature_set须输入；不以美观决定阈值

**对照依据：** HNOCA Fig.5m；继承图注对照

## 09 · 富集图

| Minimal | Advanced |
|---|---|
| ![](figures/enrichment_minimal.png) | ![](figures/enrichment_advanced.png) |

基因数面积 + 通路分组 + 区间和标签

**数据边界：** lower/upper、interval_label；不计算富集

**对照依据：** LIANA+ Fig.5d；继承图注对照

## 10 · 谱系曲线

| Minimal | Advanced |
|---|---|
| ![](figures/trajectory_minimal.png) | ![](figures/trajectory_advanced.png) |

指定阶段 + 关键峰 + 末端直标

**数据边界：** stages、lower/upper；图不拟合GAM

**对照依据：** CellRank 2 Fig.3；继承作图源码对照

## 11 · 候选通信

| Minimal | Advanced |
|---|---|
| ![](figures/network_minimal.png) | ![](figures/network_advanced.png) |

按输入权重分配弧长的弦带 + 接收端箭头 + 节点流入/流出

**数据边界：** source、target、weight、edge_unit；非因果边

**对照依据：** spatialDLPFC Fig.5B；圆形网络的设计对照，不宣称原图算法一致

## 12 · 多阶段转移

| Minimal | Advanced |
|---|---|
| ![](figures/flow_minimal.png) | ![](figures/flow_advanced.png) |

中间节点核对质量守恒、阶段名与节点总质量

**数据边界：** stage可选；中间质量不守恒直接报错

**对照依据：** moscot Fig.5f；继承图注对照

## 13 · 模型基准

| Minimal | Advanced |
|---|---|
| ![](figures/benchmark_minimal.png) | ![](figures/benchmark_advanced.png) |

基线配对差值矩阵 + 格内原始分数 + 中位差值

**数据边界：** 同一dataset集合；raw score与delta分开

**对照依据：** BANKSY Fig.5b；配对比较思路，矩阵布局原创

## 14 · 相关矩阵

| Minimal | Advanced |
|---|---|
| ![](figures/correlation_minimal.png) | ![](figures/correlation_advanced.png) |

可选一次排序 + 下三角数字 + 上三角幅度点

**数据边界：** 仅对称数据；排序属于显式显示变换

**对照依据：** spatialDLPFC Fig.3；继承对照，双编码为原创

## 15 · 效应量森林图

| Minimal | Advanced |
|---|---|
| ![](figures/forest_minimal.png) | ![](figures/forest_advanced.png) |

同行数值/区间表 + 零或比值参考 + 行定位

**数据边界：** interval_label必填；不估计置信区间

**对照依据：** 补充通用统计图形；未指定CNS对应panel

## 16 · 集合交集

| Minimal | Advanced |
|---|---|
| ![](figures/upset_minimal.png) | ![](figures/upset_advanced.png) |

与交集柱共用列索引的成员矩阵

**数据边界：** item/set；exclusive intersection，不混同inclusive

**对照依据：** UpSetPlot官方文档；补充软件依据，非CNS归因

## 17 · 山脊图

| Minimal | Advanced |
|---|---|
| ![](figures/ridge_minimal.png) | ![](figures/ridge_advanced.png) |

四分位段 + 样本支持 + 中位位置

**数据边界：** 每组至少5个非恒定值；密度高度按组归一化

**对照依据：** 补充通用分布图形；非论文数值复现

## 18 · 经验累积分布

| Minimal | Advanced |
|---|---|
| ![](figures/ecdf_minimal.png) | ![](figures/ecdf_advanced.png) |

分位位置与中位值投影

**数据边界：** 不进行假设分布拟合；分位插值方法明确

**对照依据：** 补充通用分布图形；非CNS特定版式

## 19 · 密度 / QC

| Minimal | Advanced |
|---|---|
| ![](figures/hexbin_minimal.png) | ![](figures/hexbin_advanced.png) |

六边形计数与声明阈值

**数据边界：** gridsize、log_counts；图不筛除细胞

**对照依据：** Matplotlib hexbin官方接口；补充技术依据

## 20 · ROC

| Minimal | Advanced |
|---|---|
| ![](figures/roc_minimal.png) | ![](figures/roc_advanced.png) |

预先指定的工作点与阈值

**数据边界：** 不在渲染器中重新训练或选择最优阈值

**对照依据：** scikit-learn官方ROC文档；补充技术依据

## 21 · PR曲线

| Minimal | Advanced |
|---|---|
| ![](figures/precision_recall_minimal.png) | ![](figures/precision_recall_advanced.png) |

工作点、阈值及显式阳性比例参考

**数据边界：** prevalence须输入；不把PR-AUC当AP

**对照依据：** scikit-learn官方PR文档；补充技术依据

## 22 · 校准图

| Minimal | Advanced |
|---|---|
| ![](figures/calibration_minimal.png) | ![](figures/calibration_advanced.png) |

分箱样本量面积、误差线和校准偏差段

**数据边界：** bin/n/interval；不生成未估计的误差线

**对照依据：** scikit-learn CalibrationDisplay官方文档；补充技术依据

## 23 · 混淆矩阵

| Minimal | Advanced |
|---|---|
| ![](figures/confusion_minimal.png) | ![](figures/confusion_advanced.png) |

同一原始表的行比例 + 保留原始n + 行分母

**数据边界：** 每个实际类的分母；零必须显式给出

**对照依据：** scikit-learn混淆矩阵官方文档；补充技术依据

## 24 · 富集运行曲线

| Minimal | Advanced |
|---|---|
| ![](figures/gsea_minimal.png) | ![](figures/gsea_advanced.png) |

与排名对齐的命中rug、rank-metric轨道、峰

**数据边界：** 不在作图阶段进行GSEA检验；轨道尺度单独声明

**对照依据：** GSEA开发者文档；补充方法依据，非CNSpanel归因

## 25 · 空间去卷积混合

| Minimal | Advanced |
|---|---|
| ![](figures/spatial_composition_minimal.png) | ![](figures/spatial_composition_advanced.png) |

完整比例扇区 + 固定实际空间半径

**数据边界：** 每个spot总量为1；不把top-k等权成员当比例

**对照依据：** spatialDLPFC作者scatter-pie代码为对照；完整比例实现是原创

## 26 · 时间基因程序

| Minimal | Advanced |
|---|---|
| ![](figures/trajectory_heatmap_minimal.png) | ![](figures/trajectory_heatmap_advanced.png) |

稳定峰时排序 + 峰位置 + 模块轨道

**数据边界：** value为给定趋势；不把gene z-score冒称原始表达

**对照依据：** CellRank 2 Fig.3/作者heatmap接口对照
