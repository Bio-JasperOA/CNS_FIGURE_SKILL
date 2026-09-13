# 包与职责：作者证据和新增推荐必须分开

更新时间 2026-09-13。下面“已确认”只指对应证据范围，不代表整个期刊的惯例。

## A. 作者实际代码/来源可确认

| 工具 | 本轮作者来源 | 真正解决的问题 | 不应如何解释 |
|---|---|---|---|
| Matplotlib + scVelo + CellRank plotting | C01–C02 / P06 | 底层 Axes、表达散点、命运概率、模型趋势热图 | CellRank/GAM 不是调色板；输出是模型推断 |
| mplscience | C01 / P06 | 用 context 管理科研图默认样式 | 不是 Nature 官方认证主题，也不证明所有最终图均保留默认样式 |
| seaborn | C01 / P06 | 作者脚本中的统计绘图/风格辅助 | 本 Skill 的 Python 核心不依赖它；不把其存在等同所有统计正确 |
| plotnine + patchworklib | C03 / P08 | Python 的图形语法和布局组合 | 要锁定相容版本；Python patchworklib 不是 R patchwork |
| ComplexHeatmap | C04 / P09 | 主矩阵、注释、分组、旁侧统计与自定义单元格 | 热图列/行顺序必须共享；不能独立排序后硬拼 |
| scatterpie | C05 / P09 的 SPOTlight 脚本 | 空间位置上的局部组成或成员集合 | equal-weight top-k pies ≠ abundance fractions |
| ggpubr、tidyverse、SpatialExperiment、SingleCellExperiment | C05 / P09 | 统计图辅助、数据整理与数据对象 | 后两者首先是容器，不是期刊绘图主题 |
| Squidpy + scikit-image + napari + Dask | P01 正文 | 空间邻域、图像特征、交互检查和大数据处理 | napari 交互截图不应替代全部定量源数据 |
| spatialGE 的 STgradient/STenrich | C07 / P11 | 空间表达梯度和富集分析 | 属于分析方法，绘图前要先核查结果定义 |

## B. 工程推荐，不伪装成上述论文均使用过

| 需求 | Python | R | 代码思想 |
|---|---|---|---|
| 复杂注释热图 | Matplotlib GridSpec；可选 Marsilea / PyComplexHeatmap | ComplexHeatmap + circlize + grid | 矩阵、侧注释、树状图共用一次计算的排列 |
| 大规模点云 | rasterized artist；可选 Datashader | ggrastr / scattermore | 只栅格化高密度点或热图主体，文字和矢量边界保留 |
| 多层空间表达 | spatialdata-plot、Shapely/GeoPandas | sf + ggplot2 + ggnewscale | 先统一坐标；不同量纲使用不同图例 |
| 标签避让 | adjustText | ggrepel | 先按规则选少量标签，再避让；不要全部 marker 自动铺满 |
| 网络/通讯 | NetworkX + Matplotlib | tidygraph + ggraph | 稀疏边表、固定布局、跨条件相同归一化 |
| Chord/Circos | pyCirclize（可选）或自定义 Path | circlize | 弧长与带宽对应一个明确定义的质量/权重；减少边 |
| Alluvial | 本包 transport_ribbons 或经版本核查的工具 | ggalluvial | 从 coupling 聚合，不按嵌入几何“画出命运” |
| 组合出版 panel | Matplotlib GridSpec/SubFigure | patchwork；ComplexHeatmap 通过 grid 桥接 | 数值图、示意图、组织图分层；最后统一尺寸 |

选择包的顺序：先明确输入/输出与数值定义，再选能够返回 Axes、ggplot 或 grob 的最小依赖工具。不要为了“看起来高级”安装全部可选包。

## 官方/作者文档入口

- [Matplotlib rasterization](https://matplotlib.org/stable/gallery/misc/rasterization_demo.html)：artist 级混合矢量/栅格。
- [Matplotlib GridSpec](https://matplotlib.org/stable/api/_as_gen/matplotlib.gridspec.GridSpec.html)：声明式布局。
- [ComplexHeatmap annotations](https://jokergoo.github.io/ComplexHeatmap-reference/book/heatmap-annotations.html)：annotation 索引、anno_barplot、anno_mark 与尺寸相关布局。
- [ComplexHeatmap custom heatmap body](https://jokergoo.github.io/ComplexHeatmap-reference/book/a-single-heatmap.html)：cell_fun 与向量化 layer_fun。
- [patchwork assembly](https://patchwork.data-imaginist.com/articles/guides/assembly.html)：wrap_elements 及非 ggplot 对象。
- [ggnewscale](https://eliocamp.github.io/ggnewscale/index.html)：多套填色/颜色尺度的作用域。
- [Marsilea](https://marsilea.readthedocs.io/en/stable/)：可组合注释热图/单细胞 panel，底层基于 Matplotlib。
- [PyComplexHeatmap](https://pypi.org/project/PyComplexHeatmap/)：复杂热图及注释；是 Python 包，不是 R ComplexHeatmap 的自动等价接口。

除 A 表明确来源外，推荐工具仅是方法可迁移的实现选择，不计入作者使用频次。安装时重新核查 API/依赖兼容性；本包只有 Python 核心经过所列环境的实际测试。
