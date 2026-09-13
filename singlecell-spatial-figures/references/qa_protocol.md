# QA 与交付协议

## 需要明确记录的状态

1. schema/semantic preflight：通过/失败，是否检查了实际文件。
2. numerical test：实际运行哪个函数、哪个固定输入、断言什么。
3. render check：哪个引擎、画布尺寸、字号、图例、裁切、轴向。
4. scientific review：哪个数据量、哪种独立重复、何种统计设计；是否支持图注结论。
5. release：仅当项目人工审阅完成后另行记录；程序不得把 pending 自动改成 passed。

Python 本版自动检测的范围仅是画布外文字、低于阈值字号和已登记连续 mappable 尺度；同 panel 内的标签彼此碰撞、灰阶/色觉模拟、空间标定和统计真实性仍需要专门审阅。R 没有自动文字几何审核。

## 论文模式的最终目录

FigureID.pdf / .svg / .png；FigureID_data*.csv；figure_spec.json；preflight.json；render_plan.json；qa.json 或 R provenance_and_qa.json；环境信息及输入/输出哈希。只分发与该 Figure 有关的数据，先排除病人标识和受限数据。

## 真实图的视觉验收顺序

在最终尺寸看问题和主次是否清楚 → 检查同一实体的颜色/顺序 → 同一量的尺度/分母 → 图例完整 → 空间轴向/比例尺 → 标签/子图/图例的碰撞 → 灰阶或色觉检查 → 导出字体与栅格/矢量层 → source data 逐项核对。

自动检查无报错不是最终通过。测试用人工矩阵只能注明 SOFTWARE QA，不可列入生物学结果。绘图软件/API/包版本的测试边界和原论文分析复现的边界必须分别报告。
