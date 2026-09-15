# v3.2 图型和验收清单

所有图片禁止 subtitle。主标题、坐标、图例、样本量和必要的编码说明仍可保留。图片不承载论文背景段落。

原v3.1的14类已重做；新增12类。变体不是为了堆砌装饰，同一数据对比保留原表及变换记录。新增图形的CNS归因不得超过下表的证据等级。

| 图型 | 最简 | 高级增加的有效信息 | 数据边界 / 文献对照 |
|---|---|---|---|
| 01 嵌入 / UMAP | 固定坐标、固定具名色键 | 输入的状态图 + 明确的父类分层 + 直接身份标注 | abstract_edges、edge_definition、parent；不从点云虚构谱系；BANKSY Fig.3a–b；图型对照继承v3.1，非本轮逐图复现 |
| 02 空间表达 | 位置与共同色标 | 真实输入的分割多边形 + 指定ROI + 物理比例尺 | vertices、rois、coordinate_unit；缺少分割只能画点；Squidpy Fig.3–4；本轮读图注/方法，不声称像素复现 |
| 03 Marker 点阵 | 均值颜色与检测面积，保留双图例 | 条件内成对行 + 基因模块括号 + 独立身份色带 | condition、module；大小是面积而非半径；spatialDLPFC Fig.5–6；继承作者代码和图注对照 |
| 04 多注释热图 | 固定矩阵、范围、缺失值 | 模块分块 + 样本条件轨道 + 对齐计数；可显示另一个已声明效应 | module、condition、n、可选effect；索引不可错位；spatialDLPFC Fig.3D/6C–D；继承对照 |
| 05 分布 / 分层雨云 | 所有样本观测 | 条件分层半密度 + 全部点 + median/IQR + n | condition可选；KDE不是统计区间；BANKSY Fig.3j；violin为图型对照，不称作者画过本雨云布局 |
| 06 细胞组成 | 逐样本堆叠比例 | 逐样本×类型比例矩阵 + 条件块 + 实际分母 | fraction是上游比例；显式零与缺失不同；HNOCA Fig.5g–h；组成及样本注释思路，矩阵为原创变体 |
| 07 配对比较 | 配对观测与连接 | 全部配对差值、排序、零参考和样本IQR | sample对应真实配对；median/IQR是描述不是CI；LIANA+ Extended Data Fig.3；统计单位对照，差值版原创 |
| 08 火山图 | 双阈值效应—q分布 | 基因集圈选 + 预先声明标签 + 双向数量 | feature_set须输入；不以美观决定阈值；HNOCA Fig.5m；继承图注对照 |
| 09 富集图 | 效应、q、已有区间 | 基因数面积 + 通路分组 + 区间和标签 | lower/upper、interval_label；不计算富集；LIANA+ Fig.5d；继承图注对照 |
| 10 谱系曲线 | 输入趋势与全部区间 | 指定阶段 + 关键峰 + 末端直标 | stages、lower/upper；图不拟合GAM；CellRank 2 Fig.3；继承作图源码对照 |
| 11 候选通信 | 双列加权边 | 按输入权重分配弧长的弦带 + 接收端箭头 + 节点流入/流出 | source、target、weight、edge_unit；非因果边；spatialDLPFC Fig.5B；圆形网络的设计对照，不宣称原图算法一致 |
| 12 多阶段转移 | 保留所有阶段的流带 | 中间节点核对质量守恒、阶段名与节点总质量 | stage可选；中间质量不守恒直接报错；moscot Fig.5f；继承图注对照 |
| 13 模型基准 | 全部测试集的分数 | 基线配对差值矩阵 + 格内原始分数 + 中位差值 | 同一dataset集合；raw score与delta分开；BANKSY Fig.5b；配对比较思路，矩阵布局原创 |
| 14 相关矩阵 | 完整对称矩阵 | 可选一次排序 + 下三角数字 + 上三角幅度点 | 仅对称数据；排序属于显式显示变换；spatialDLPFC Fig.3；继承对照，双编码为原创 |
| 15 效应量森林图 | 输入效应与区间 | 同行数值/区间表 + 零或比值参考 + 行定位 | interval_label必填；不估计置信区间；补充通用统计图形；未指定CNS对应panel |
| 16 集合交集 | 精确交集大小 | 与交集柱共用列索引的成员矩阵 | item/set；exclusive intersection，不混同inclusive；UpSetPlot官方文档；补充软件依据，非CNS归因 |
| 17 山脊图 | 有序分布轮廓 | 四分位段 + 样本支持 + 中位位置 | 每组至少5个非恒定值；密度高度按组归一化；补充通用分布图形；非论文数值复现 |
| 18 经验累积分布 | 全部经验阶梯曲线 | 分位位置与中位值投影 | 不进行假设分布拟合；分位插值方法明确；补充通用分布图形；非CNS特定版式 |
| 19 密度 / QC | 全部观测散点 | 六边形计数与声明阈值 | gridsize、log_counts；图不筛除细胞；Matplotlib hexbin官方接口；补充技术依据 |
| 20 ROC | 输入ROC及已有区间 | 预先指定的工作点与阈值 | 不在渲染器中重新训练或选择最优阈值；scikit-learn官方ROC文档；补充技术依据 |
| 21 PR曲线 | 输入PR及已有区间 | 工作点、阈值及显式阳性比例参考 | prevalence须输入；不把PR-AUC当AP；scikit-learn官方PR文档；补充技术依据 |
| 22 校准图 | 实际分箱预测/观测与区间 | 分箱样本量面积、误差线和校准偏差段 | bin/n/interval；不生成未估计的误差线；scikit-learn CalibrationDisplay官方文档；补充技术依据 |
| 23 混淆矩阵 | 原始计数 | 同一原始表的行比例 + 保留原始n + 行分母 | 每个实际类的分母；零必须显式给出；scikit-learn混淆矩阵官方文档；补充技术依据 |
| 24 富集运行曲线 | 上游运行得分 | 与排名对齐的命中rug、rank-metric轨道、峰 | 不在作图阶段进行GSEA检验；轨道尺度单独声明；GSEA开发者文档；补充方法依据，非CNSpanel归因 |
| 25 空间去卷积混合 | dominant type分类位置 | 完整比例扇区 + 固定实际空间半径 | 每个spot总量为1；不把top-k等权成员当比例；spatialDLPFC作者scatter-pie代码为对照；完整比例实现是原创 |
| 26 时间基因程序 | 输入gene×time矩阵 | 稳定峰时排序 + 峰位置 + 模块轨道 | value为给定趋势；不把gene z-score冒称原始表达；CellRank 2 Fig.3/作者heatmap接口对照 |

## 默认、失败条件与验收

字号与画布是可改项目默认，不是期刊规范。新默认190×135 mm；高密度图允许更高画布。不能强制把所有图压成方形。高级版若没有额外输入，应选择最简或报告缺少的数据，不能补造分割、基因集、区间或状态连接。

检验包括：图和表一致；所有区间保留；面积/比例分母明确；主键唯一；比例与中间流量守恒；旧subtitle键不显示；最终PNG/PDF/SVG无画布外文字；色键按名称稳定；真实数据必须有provenance。自动层登记不证明美观或科学解释正确。

在真实项目中还必须人工检查邻近标签碰撞、小点可辨认性、颜色对比、主问题是否清楚和额外层是否有用。未进行完整色觉缺陷模拟或任意数据规模测试。

## 执行边界

仍然属于v3；spec_version 3.0不变。新增与升级图型通过同一个style_gallery/render.py入口调用。旧FigureSpec仅支持其已登记的四种渲染器；未把26类全部接入FigureSpec。R入口调用同一Python渲染器，本环境无Rscript，未运行原生R验证。

## 公开技术来源

- Squidpy (Nature Methods 2022): https://doi.org/10.1038/s41592-021-01358-2 — 本轮读图注与方法，支持图像/空间/邻域上下文设计，不声称新增数据复现。
- CellRank 2: https://www.nature.com/articles/s41592-024-02303-9 — 继承仓库v3.1审计，当前图为原创合成范例。
- UpSetPlot: https://upsetplot.readthedocs.io/en/stable/
- CalibrationDisplay: https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibrationDisplay.html
- Matplotlib hexbin: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.hexbin.html
- GSEA: https://www.gsea-msigdb.org/gsea/doc/GSEAUserGuideFrame.html
