# 单细胞与空间转录组论文：源代码核验目录

检索日：2026-09-13。范围：2022–2026 年正式发表研究，含 Nature、Cell、Science 及相关研究子刊。
这是面向可复用绘图 Skill 的目的性代表样本，不是所有文献的系统综述；不能由此计算整个领域的代码公开率。

## 核验等级

- **D**：读到论文/正式作者来源的代码声明，确认其披露范围。链接不代表本轮已经执行。
- **R**：本轮实际返回仓库目录、README 或文件内容。目录可访问不等于数据与全部依赖可用。
- **F**：实际阅读相关作图函数或脚本。`F-partial` 只核查 notebook 导入/环境片段，不能证明所有图形调用。
- **X**：本轮从原始输入运行并复现作者论文图。本轮没有任何论文标为 X。

`D+R+F` 也不是“所有主图都已核验”。作者代码当前快照可能含发表后修改；有确切 SHA 的检索片段已记录在后文，尚未将这些快照全面对应到发表时归档。

## 论文目录

| ID | 年份 / 期刊 | 论文 | 代码披露与核验 | 绘图学习点 |
|---|---|---|---|---|
| P01 | 2022 · Nature Methods | [Squidpy: a scalable framework for spatial omics analysis](https://doi.org/10.1038/s41592-021-01358-2) | **D** · [代码/归档](https://github.com/theislab/squidpy)。公开框架、文档与教程；本轮未逐个核验论文复现 notebook。 | 空间图、图像特征与细胞邻域；实看 Fig. 3。 |
| P02 | 2022 · Nature Biotechnology | [Cell2location maps fine-grained cell types in spatial transcriptomics](https://doi.org/10.1038/s41587-021-01139-4) | **D** · [代码/归档](https://github.com/vitkl/cell2location_paper)。算法包另在 BayraktarLab/cell2location；声明指向论文分析 notebooks、合成数据与分割代码。 | 解卷积丰度连续图；区分绝对/相对丰度与按类型单独缩放。 |
| P03 | 2022 · Cell | [Mapping transcriptomic vector fields of single cells](https://doi.org/10.1016/j.cell.2021.12.045) | **D** · [代码/归档](https://github.com/aristoteleo/dynamo-notebooks)。算法 aristoteleo/dynamo-release；声明另有 dynamo-notebooks 和 dynamo-tutorials 用于研究图的复现。 | 流线、Jacobian、动力学路径；本轮依据正文方法和图注，未执行 notebook。 |
| P04 | 2022 · Cell | [Spatiotemporal transcriptomic atlas of mouse organogenesis using DNA nanoball-patterned arrays](https://doi.org/10.1016/j.cell.2022.04.003) | **D** · [代码/归档](https://github.com/BGIResearch/SAW)。声明公开 SAW 等处理代码；不能把上游测序处理流程等同于所有主图的作图源码。 | 胚胎多时期、多分辨率空间展示；逐图脚本覆盖未确认。 |
| P05 | 2023 · Nature | [A high-resolution transcriptomic and spatial atlas of cell types in the whole mouse brain](https://doi.org/10.1038/s41586-023-06812-z) | **D** · [代码/归档](https://github.com/AllenInstitute/scrattch.bigcat)。声明指向 scrattch.bigcat 及 scrattch.mapping；abc_atlas_access 是数据访问资源，不等于逐图脚本。 | 层级分类与空间映射；固定类别层级和颜色关系。 |
| P06 | 2024 · Nature Methods | [CellRank 2: unified fate mapping in multiview single-cell data](https://doi.org/10.1038/s41592-024-02303-9) | **D+R+F** · [代码/归档](https://github.com/theislab/cellrank2_reproducibility)。软件之外有独立论文复现仓库和 Zenodo 10809425；已读实际作图脚本。 | 实看 Fig. 3；谱系加权 GAM、热图、scVelo/Matplotlib 画布。 |
| P07 | 2024 · Nature Genetics | [BANKSY unifies cell typing and tissue domain segmentation for scalable spatial omics data analysis](https://doi.org/10.1038/s41588-024-01664-3) | **D** · [代码/归档](https://github.com/jleechung/banksy-zenodo)。R 复现脚本和 Banksy_py 的 Banksy-manuscript 分支 notebooks；Zenodo 10258795。 | 细胞类型与组织区域并置；改变 lambda 是改变分析，不是换配色。 |
| P08 | 2024 · Nature Cell Biology | [LIANA+ provides an all-in-one framework for cell–cell communication inference](https://doi.org/10.1038/s41556-024-01469-w) | **D+R+F-partial** · [代码/归档](https://github.com/saezlab/lianaplus_manuscript)。算法 liana-py 与论文脚本分开；已核查绘图 notebook 的导入语句及环境文件。 | 实际出现 plotnine、patchworklib；通讯结果多种汇总视图。 |
| P09 | 2024 · Science | [A data-driven single-cell and spatial transcriptomic map of the human prefrontal cortex](https://doi.org/10.1126/science.adh1938) | **D+R+F** · [代码/归档](https://github.com/LieberInstitute/spatialDLPFC)。公开分析与作图脚本；已读富集热图函数、空间 top-k 饼图及相关检索片段。 | ComplexHeatmap 多注释；top-k 等权成员图并非实际比例。 |
| P10 | 2024 · Science Advances | [Melanoma progression and prognostic models drawn from single-cell, spatial maps of benign and malignant tumors](https://doi.org/10.1126/sciadv.adm8206) | **D** · [代码/归档](https://doi.org/10.5061/dryad.ksn02v7b1)。声明将原始空间数据、元数据及 GitHub codes 存于 Dryad；本轮未下载并执行归档。 | RNA-SMI、组织 ROI、热图和临床关联的证据链；代码不是只有 GitHub 一种发布方式。 |
| P11 | 2024 · Cell Reports Medicine | [Spatial transcriptomics analysis identifies a tumor-promoting function of the meningeal stroma in melanoma leptomeningeal disease](https://doi.org/10.1016/j.xcrm.2024.101606) | **D+R** · [代码/归档](https://github.com/oospina/spatial_transcriptomics_leptomeningeal_disease)。论文声明所有 original code 公开；仓库 README 可读，介绍 Unix/R、Seurat、STdeconvolve、spatialGE。 | STgradient/STenrich；最终发表标题不含预印本标题中的 unique。 |
| P12 | 2025 · Nature Methods | [SpatialData: an open and universal data framework for spatial omics](https://doi.org/10.1038/s41592-024-02212-x) | **D+R(tutorial)** · [代码/归档](https://github.com/scverse/spatialdata-notebooks/tree/main/notebooks/paper_reproducibility)。2024-03-20 online，2025 卷期。论文指向 paper_reproducibility；原仓库已改名 spatialdata-tutorials。 | 实看 Fig. 2；图像、polygon、点与 ROI 对齐；本轮读取的是当前教程检索片段，未确认逐图文件历史路径。 |
| P13 | 2025 · Nature | [Mapping cells through time and space with moscot](https://doi.org/10.1038/s41586-024-08453-2) | **D** · [代码/归档](https://github.com/theislab/moscot-framework_reproducibility)。公开方法与论文复现资源；本轮代码搜索未返回 sankey 命中，不能据此断言未公开或使用了某一 Sankey 包。 | 从 cell-cell coupling 聚合到类型间流量；本 Skill 的流图实现是原创推荐。 |
| P14 | 2025 · Nature Methods | [Spotiphy enables single-cell spatial whole transcriptomics across an entire section](https://doi.org/10.1038/s41592-025-02622-5) | **D** · [代码/归档](https://github.com/jyyulab/Spotiphy)。声明公开 Python 软件及教程；本轮未确认所有最终论文图均有独立脚本。 | 推断结果的空间可视化要标明预测值、分辨率和不确定性。 |
| P15 | 2025 · Nature Methods | [Nicheformer: a foundation model for single-cell and spatial omics](https://doi.org/10.1038/s41592-025-02814-z) | **D** · [代码/归档](https://github.com/theislab/nicheformer)。声明公开 Python 软件、预处理及下游使用教程；不能扩展为所有排版文件已公开。 | 模型嵌入、空间邻域与评估图；不以嵌入形状作为机制证据。 |
| P16 | 2026 · Nature Communications | [Accurate trajectory inference in time-series spatial transcriptomics with structurally-constrained optimal transport](https://doi.org/10.1038/s41467-026-74927-8) | **D** · [代码/归档](https://github.com/algo-bio-lab/SOCS)。2026-06-29 发表；声明公开开发、分析、结果与教程，归档 Zenodo 20722957。 | 结构约束的时空匹配；几何结构与推断轨迹分开表达。 |

## 实际代码证据：精确路径与本次检索快照

### C01 · CellRank 2：全局风格上下文并不取代分析绘图

仓库：`theislab/cellrank2_reproducibility`；检索返回 commit `8020e797c0afcde5ba9b8c2f0182b1c25d56f11f`。

[脚本 scripts/labeling_kernel/cr1_vs_cr2.py](https://github.com/theislab/cellrank2_reproducibility/blob/8020e797c0afcde5ba9b8c2f0182b1c25d56f11f/scripts/labeling_kernel/cr1_vs_cr2.py) 的检索片段明确导入 `matplotlib.pyplot`、`mplscience`、`seaborn`，并使用 `mplscience.style_context()`。
只据此确认该脚本使用这些工具；不能推断 Nature Methods 要求安装 mplscience，也不能断言该环境设置没有在最终排版中再被调整。

### C02 · CellRank 2：先推断/拟合，再画轨迹热图

[脚本 scripts/cytotrace_kernel/embryoid_body/cytotrace.py](https://github.com/theislab/cellrank2_reproducibility/blob/8020e797c0afcde5ba9b8c2f0182b1c25d56f11f/scripts/cytotrace_kernel/embryoid_body/cytotrace.py)，读取约 260–460 行范围。
使用谱系 driver 排序，构建 `cr.models.GAM(adata)`，向 `cr.pl.heatmap` 传入指定 lineage、top genes 和 `ct_pseudotime`；另用 `scv.pl.scatter(..., ax=ax)` 画命运概率和基因表达。
源文件 blob SHA：`37ae8033c3b6bddf791c193d59e83e0efe960581`。
论文 Fig. 3 的热图依赖平滑趋势与峰值顺序，而不只是对原始表达矩阵使用默认聚类。

### C03 · LIANA+：Python 中也存在 ggplot 风格与组合图层

仓库：`saezlab/lianaplus_manuscript`；commit `37c712d280ed4f6ef55cd17490366c2f062ee513`。

[notebooks/classification/2.PlotOutput.ipynb](https://github.com/saezlab/lianaplus_manuscript/blob/37c712d280ed4f6ef55cd17490366c2f062ee513/notebooks/classification/2.PlotOutput.ipynb) 导入 `plotnine as p9` 和 `patchworklib as pw`。
[environments/env.yml](https://github.com/saezlab/lianaplus_manuscript/blob/37c712d280ed4f6ef55cd17490366c2f062ee513/environments/env.yml) 包含 `plotnine==0.12.4`、`patchworklib==0.6.3`；另一个环境文件出现不同 plotnine 版本。
这些是作者快照中的环境，不是本 Skill 建议直接装入所有新项目的“最新版”。不要混装任意版本再声称可复现。

### C04 · spatialDLPFC：复杂热图本质上是共用索引的多个对象

仓库：`LieberInstitute/spatialDLPFC`；commit `c9dfac534ad3c6b475716718485776ec3f5c86e8`。

[code/analysis/10_clinical_gene_set_enrichment/gene_set_enrichment_plot_complex.R](https://github.com/LieberInstitute/spatialDLPFC/blob/c9dfac534ad3c6b475716718485776ec3f5c86e8/code/analysis/10_clinical_gene_set_enrichment/gene_set_enrichment_plot_complex.R)，读取约 100–295 行。
将 P 值与 OR 分别变成两个矩阵，依据同一行列名称重排；热图颜色编码截断的 `-log10(P)`，格内文字是 OR，顶部/侧边通过 `anno_barplot` 显示基因数。
使用 `columnAnnotation`、`rowAnnotation`、`Heatmap`、`cell_fun` 和 `grid.text`；这些不是同一个值换着画。
本 Skill 的 R 原创版本改用向量化 `layer_fun`，并要求调用方明确 P 还是 FDR q 值，不能悄悄替换统计量。
源文件 blob SHA：`43afa5be34a1494c02ef62be49e476911148f113`。

### C05 · spatialDLPFC：空间饼图不一定是比例图

[code/analysis/15_cell_composition/02-plot_scatter_pie_top3.R](https://github.com/LieberInstitute/spatialDLPFC/blob/c9dfac534ad3c6b475716718485776ec3f5c86e8/code/analysis/15_cell_composition/02-plot_scatter_pie_top3.R)，读取约 1–210 行。
按每个 spot 的估计值排序后，top3/top6 类型被转换成 0/1 指示值，分别检查行和为 3 或 6，再传给 `vis_scatter_pie`。因此图表示等权 top-k 成员集合，不能称为真实细胞比例。
该脚本还从对象 metadata 读取持久化颜色、显式设置 factor levels；其中出现实验室绝对数据路径，移植时必须参数化。
源文件 blob SHA：`0e2e27b2e70da35614b9fc0979aefa168e44995c`。

[code/spot_deconvo/04-spotlight/01-IF.R](https://github.com/LieberInstitute/spatialDLPFC/blob/c9dfac534ad3c6b475716718485776ec3f5c86e8/code/spot_deconvo/04-spotlight/01-IF.R) 的检索片段明确导入 `scatterpie`、`ggcorrplot`、`SPOTlight`。**这不能单凭名称证明前述 vis_scatter_pie 的内部实现完全相同。**

### C06 · SpatialData：历史论文链接与当前教程分开记录

论文给出的 `scverse/spatialdata-notebooks` 通过 GitHub API 返回重定向；仓库 ID `544047684` 当前名称为 `scverse/spatialdata-tutorials`。
检索快照 commit：`ba7c7c9c3730be3f080627a85fc6f40d1a9ab1bd`。

[notebooks/examples/technology_stereoseq.ipynb](https://github.com/scverse/spatialdata-tutorials/blob/ba7c7c9c3730be3f080627a85fc6f40d1a9ab1bd/notebooks/examples/technology_stereoseq.ipynb) 与 [technology_curio.ipynb](https://github.com/scverse/spatialdata-tutorials/blob/ba7c7c9c3730be3f080627a85fc6f40d1a9ab1bd/notebooks/examples/technology_curio.ipynb) 片段显示 `render_shapes` 的类别/连续值调用。
这是当前教程 API 证据，不是已确认的论文 Fig. 2 完整渲染脚本；历史 paper_reproducibility 目录迁移位置未在本轮全部追踪。

### C07 · Cell Reports Medicine：specialized spatial analysis 不是画图主题

[作者仓库 README](https://github.com/oospina/spatial_transcriptomics_leptomeningeal_disease) 说明使用 Seurat、STdeconvolve 和 spatialGE 的 STgradient/STenrich。
这支持作者分析工具归属；未逐条读取最终 panel 绘制语句，不能把 spatialGE 笼统称为“Cell 的图形主题包”。

## 视觉核验边界

实际打开并目视检查的正式发表图：

- [Squidpy Fig. 3](https://www.nature.com/articles/s41592-021-01358-2/figures/3)：图像/分割/特征/定量并置，局部放大框、比例尺、紧凑标题。显微图可为暗底，不能概括为全部白底。
- [CellRank 2 Fig. 3](https://www.nature.com/articles/s41592-024-02303-9/figures/3)：重复使用同一 UMAP 几何，灰色上下文突出局部终末状态，命运概率、marker 与有序时间热图形成关联。
- [SpatialData Fig. 2](https://www.nature.com/articles/s41592-024-02212-x/figures/2)：共同坐标、统一 ROI、图像/多边形/分子点多层数据、局部比较与数值核验。

其余论文主要基于正式正文、图注和声明核查；**没有宣称对这 16 篇所有主图作逐像素风格分析**。
来源选择偏向技术/方法论文，视觉观察偏向 Nature Methods；跨全部 CNS 的视觉频率比较需要扩大并均衡采样。

## 本次不作的推断

代码仓库公开 ≠ 每个最终 panel 都公开；没有搜索命中 ≠ 没有代码；当前主分支 ≠ 发表时版本；代码 imports ≠ 所有图片使用该包；图看起来像某字体 ≠ 确認原字体；最终排版软件未披露时不得猜成 Illustrator。
