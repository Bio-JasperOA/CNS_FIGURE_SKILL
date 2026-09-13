# DataBundle / 表格契约

每个 exchange 表必须有显式 keys，不依赖 CSV 隐式行名。path 相对于项目 root；不得指向 root 外部。CSV/TSV 文件审核检查文件存在、标题唯一、required columns、非空/唯一主键和输入 SHA256；不自动证明值的生物学含义正确。

| 输入族 | 建议唯一键 | 必须说明 |
|---|---|---|
| embedding | cell_id | embedding 来源、是否同一个坐标对象、原始标签 |
| spot/cell spatial | section_id + spot_id/cell_id | unit、y orientation、变换、ROI；donor 与 section 分开 |
| marker summary | group + gene | expression layer、detection layer、包含零的均值、n_cells/n_samples |
| heatmap long | row_id + column_id | value 单位、效应量、P/q 的区分、row/column order |
| donor summary | donor + condition + feature | 真实独立单位、配对关系、统计模型、区间含义 |
| transport edges | source_type + target_type | joint mass 或 source fraction，完整零与缺失的区别 |
| trends | lineage + gene + time | 时间含义、平滑方法、权重、模型区间/非区间 |
| benchmark | split + biological_unit + model + metric | 同一 holdout、指标方向、训练数据禁入规则 |

渲染时只能做几何定位、绘制顺序和明确图层组合。归一化、聚类、模型拟合、统计检验、ROI 筛选及阈值选择在 upstream 完成并记录。支持用户指定的图形转换，但必须保留未转换 source data。

Python compose 对传入 DataFrame 校验 required columns/keys 并给 renderer 一个副本；CSV/TSV 文件审核需另外使用 --check-files。即使 compose 成功，也不代表 native h5ad/rds 或原始实验数据经过验证。
