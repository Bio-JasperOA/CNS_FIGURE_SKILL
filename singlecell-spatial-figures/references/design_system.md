# Semantic design 与视觉系统

这是一套可修改的项目默认值，不是所有 CNS 子刊的官方格式。默认 Arial 优先、明确 fallback；白底用于多数定量图，显微图按实际成像背景；最终画布用 mm、字体用 pt。对 R ggplot2 的线宽需做单位转换，不能直接复制 Matplotlib 的 pt 数值。

相同实体：颜色与标签一致。相同量的比较：范围、转换、分母一致。不同量：分开 scale ID 和图例。类别身份、连续表达、带符号效应、概率和不确定性不得共享一个含糊的“score”图例。

优先让主证据占据较大区域；一个区域内的热图、条形注释、效应量文本复用同一索引。先调整 panel 大小、标签缩写与内容分组，再考虑缩小字号。默认不得低于 min_font_pt；必须缩小的例外要在审阅中记录。

保留 equal aspect 的空间/嵌入图；equal aspect 指 x/y 单位等比，不是强迫每幅图的外框是正方形。整页不使用 bbox_inches='tight' 擅自改变物理画布。面向后续排版的无字素材必须与完整科学图分别命名，不可单独作为最终结果。

复杂图层模板：
- 多注释 heatmap：主量→color；效应→text/marker；规模→边缘条形；共同 row/col IDs。
- Spatial：registered image→geometry→numeric layer→ROI outline→legend/scale bar；只在可校准时给物理比例尺。
- Lineage：已拟合趋势→共同时间网格→预先确定 gene order→矩阵；不在绘图内部伪造平滑或区间。
- Transport：类型聚合 mass→节点上下界→流带厚度→路径；路径弯曲只是排版，不是细胞实际运动。
- Network：固定节点布局→审阅的边筛选→方向/权重说明；不能自动把共表达变成有向信号机制。
