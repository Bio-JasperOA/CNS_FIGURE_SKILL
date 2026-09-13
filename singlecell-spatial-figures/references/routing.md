# 图形路由与数据门槛

| 要回答的问题 | 先准备的数据 | 首选图形 | 可选复杂路线 | 阻断条件 |
|---|---|---|---|---|
| 哪些身份被识别？ | 固定 embedding + 细胞 ID + label | embedding | 分层标注 | 坐标重算后当作同一对照 |
| 身份有何表达证据？ | 明确 detection 层的表达汇总 | area-dotplot | 多注释 heatmap | residual 被当 counts；只有颜色没有面积图例 |
| 在组织哪里？ | 同一 section 坐标/单位/方向 | spatial map | 图像+轮廓+ROI | 缺失标定；多切片混在一张坐标系 |
| 各组差多少？ | donor/animal 级估计 | 点+区间/配对图 | 矩阵带效应与不确定性 | 用细胞数伪造独立重复 |
| 哪些关联候选？ | 经审阅边表/效应矩阵 | matrix/dotplot | 网络/环图 | 相关性画成已验证机制 |
| 如何随时间变化？ | 有方向依据的时间与拟合结果 | trend | 谱系趋势 heatmap | 伪时间与真实时间混写 |
| 去往哪些状态？ | coupling 单位及类型聚合矩阵 | 流量矩阵 | mass-preserving ribbons | row probability 被当联合质量 |
| 模型是否有效？ | 相同 held-out 单位的结果 | 配对指标/校准 | 分层失败图 | 跨组不同分母或 data leakage |

升级图形复杂度必须增加可解释信息。环图不是交互矩阵的默认替代，空间饼图不是空间热图的默认升级。缺少合适的输入时返回缺口，而不是用随机数据填一个示例结果。

## package 三层选择

默认核心：Python Matplotlib；R ggplot2 + grid。领域对象：Python Scanpy/SpatialData/CellRank，R Seurat/SpatialExperiment 等，按项目已有版本接入。复杂组件：Python Marsilea/PyComplexHeatmap；R ComplexHeatmap/circlize/ggnewscale/patchwork 等，按具体图形需求启用。

上表是工程路由，不等于“所有原论文使用这些包”。作者使用证据仍以 v1 文献审计与精确代码路径为准。可选包不是本版自动安装或已验证依赖。
