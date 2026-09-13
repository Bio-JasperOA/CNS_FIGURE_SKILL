---
name: singlecell-spatial-figures
description: >-
  Plan, create, refactor, and audit publication-oriented single-cell and spatial
  transcriptomics figures in Python or R. Use for UMAPs, marker dotplots,
  annotated heatmaps, spatial maps, cell-neighborhood or communication diagrams,
  lineage trends, transport/alluvial plots, model benchmarks, multi-panel figures,
  and requests for Nature/Cell/Science-style scientific visualization.
  适用于单细胞、空间转录组、胚胎发育与虚拟细胞研究的科研绘图和整图框架设计。
metadata:
  version: "2.1"
---

# 单细胞与空间转录组科研绘图 Skill

**目标：从科学问题出发，把已有分析结果组织为可解释、可追溯、可修改的单图或多 panel Figure。统一科学与视觉规则，按项目环境选择 Python 或 R。**

主流程：**科学问题 → 证据结构 → 数据核查 → 视觉编码 → 整图布局 → 语言实现 → 质检与交付。**

本 Skill 总结已有文献审计与 v2 框架。它不是 CNS 官方绘图标准，也不代替细胞注释、模型训练、统计分析或机制验证。论文披露、源码核验与本包实现必须分开归因。

## 1. 先选择执行模式

**快速模式：** 单图、字号/配色修改、已有 panel 的局部修订。只读取必要数据与所选语言说明，直接修改、导出并检查；不要建立无关工程。

**整图模式：** 多 panel Figure、跨图统一、复杂图层或整图重构。先完成 FigureSpec，再运行数据/布局预检、渲染、审阅与导出。不要从默认绘图函数反推论文结论。

优先使用项目已有语言、对象和依赖；没有偏好时，根据数据对象与图形任务选后端，不为美化强行转换整个分析流程。沟通语言跟随用户；公开图中文字默认英文，用户指定时覆盖。

## 2. 先明确输入，不默默修改分析

开始时检查项目文件与已有元数据，只询问无法从现有材料确定、且会改变结果的问题。样式缺项可以使用已声明默认值；数值语义不明则暂停受影响 panel，继续完成不受影响的部分。

| 输入 | 必须确认 |
|---|---|
| 科学任务 | 整图问题、目标比较、已有证据、目标读者 |
| 数据对象 | 文件路径、版本、唯一 cell/gene/spot ID、矩阵方向、assay/layer |
| 数值定义 | counts、归一化表达、residual、丰度、概率、效应量或预测值；单位、转换与分母 |
| 实验设计 | donor/animal/sample/section ID、配对关系、独立重复、已有检验与区间 |
| 空间与时间 | 坐标、原点、方向、pixel/µm、切片、配准、真实时间或伪时间 |
| 输出要求 | Python/R、物理尺寸、字体、文件格式、完整标注/无字素材 |

禁止默认 AnnData `.X` 是 counts；禁止把 Seurat integrated assay/scale.data 当检测计数。Python 原有汇总函数接收 cells × genes；R 接收 genes × cells。先以 ID 核对矩阵和 metadata，再提取明确层；不默默取交集丢弃细胞，不覆盖原对象。

稀疏数据只对选定基因、ROI 或已聚合的小矩阵做必要稠密化；不得为作图对全图谱直接 `.toarray()`。缺失或无法估计不等于 0。

详细输入约定：[data_contracts.md](references/data_contracts.md)。

## 3. 先设计证据结构，再选图

每个 panel 写明 **问题、数据来源、证据职责、比较对象、数值定义**。证据职责可用 overview、identity、spatial_context、quantification、mechanism_candidate、validation、benchmark、uncertainty。尚未看到结果时写研究问题，不预设阳性结论。

| 整图路线 | 可选阅读顺序 | 必须防止 |
|---|---|---|
| 细胞图谱 | 身份概览 → marker 支持 → 空间定位 → 样本级差异 | 只展示聚类，缺少身份与重复证据 |
| 空间微环境 | 全切片 → 有依据的 ROI → 局部关联/效应 → 样本级复核 | 以单个漂亮 ROI 代表整个队列 |
| 发育/状态转变 | 时间与身份 → 预测转移 → 谱系程序 → 留出时间/外部验证 | 将伪时间当真实时间，将连线当运动轨迹 |
| 模型评估 | 数据拆分 → 配对性能 → 校准/不确定性 → 失败分层 | donor/相邻切片泄漏，指标分母不一致 |

按证据决定 panel 数量、大小与顺序。复杂热图可以跨列；主空间图保持真实几何；不强制四宫格、六宫格或所有 panel 一样大。证据不足就保留缺口，不用装饰图补齐版面。

## 4. 六层职责与 FigureSpec

| 层级 | 负责 | 产物 |
|---|---|---|
| 科学证据层 | 整图问题、panel 职责、对照与验证 | Figure brief |
| 数据接口层 | 提取、按 ID 对齐、定义单位和来源 | 审阅后的长表/矩阵/边表 |
| 视觉语义层 | 类别颜色、顺序、连续尺度、字体 | 统一 scales/design |
| 整图布局层 | 分配毫米级区域与图例空间 | layout、panel content boxes |
| 语言执行层 | 按规范渲染，不修改统计含义 | Python/R 图形对象 |
| 质检交付层 | 数值、几何、导出与审阅记录 | 图、源数据、provenance、QA |

整图模式使用实际的 [FigureSpec schema](assets/figure_spec.schema.json)，不要另造一套不兼容配置。字段分为 `figure / datasets / scales / design / layout / panels`。每个 panel 绑定 `data_id`、`renderer`、`channels`、`scale_ids`、`slot` 与统计说明。

从 [atlas](assets/atlas.yaml)、[spatial_niche](assets/spatial_niche.yaml)、[development](assets/development.yaml)、[model_benchmark](assets/model_benchmark.yaml) 中选接近的模板，再删改。所有 `DRAFT:`、路径、类别与尺度均须按真实任务填写；模板不是现成生物学结果。

`slot=[row,col,row_span,col_span]` 从 0 开始；margin/padding 顺序为 `[top,right,bottom,left]`。只在 panel 自己的内容区组织子图。模板附带的 render_plan 是结构示例，真实项目必须重新预检生成。

## 5. 统一视觉规则

**身份一致。** 同一细胞类型在 UMAP、空间图、组成图和流图中使用同一命名颜色与类别顺序；缺少颜色映射时报错，不随机补色。类别过多时采用分层、分面和必要标签，不一味添加颜色。

**比较一致。** 同一量的对比共享定义、转换、单位、分母和预先审阅的范围。非负表达使用顺序尺度；带符号效应使用有明确中心的发散尺度；不同量分别设置图例。收集图例不能代替尺度核验。不同基因之间不必硬套相同范围，但同一基因跨条件比较不得逐 panel 自动拉伸后冒称共用尺度。

**几何真实。** 空间图与已有嵌入保持 x/y 等比；equal aspect 不等于外框必须 1:1。不重跑/旋转嵌入制造分离。组织变换要记录配准参数，物理比例尺必须有校准依据。

**版式先定。** 先确定最终画布 mm，再设置字号 pt、线宽、图例和 panel 标签。采用统一无衬线字体、克制的轴线与背景；显微图保留合理成像背景。需要默认值时可从单栏 89 mm/双栏 183 mm、正文 7 pt、panel 标签 8 pt 起步，但它们不是所有期刊的统一要求。优先增大 panel、缩写标签或拆分内容，不靠极小字号硬塞。

**密度受控。** 稳定绘制顺序，记录下采样与筛选；仅栅格化密集点或图像层，保留文字、坐标轴和必要轮廓。整图导出不得通过 tight 裁切偷偷改变最终物理尺寸。

进一步规则：[design_system.md](references/design_system.md)。

## 6. 复杂图形：先定义数值，再实现图层

下表是任务路由，不表示每个图形都已有一键渲染器。源码证据与推荐工具见 [packages_v1.md](references/packages_v1.md)，具体配方见 [complex_recipes_v1.md](references/complex_recipes_v1.md)。

| 图形 | 可迁移的代码思想 | 必须检查 |
|---|---|---|
| Marker dotplot | 明确层汇总 → 命名行列顺序 → 颜色编码均值、面积编码检测比例 | 检测阈值、均值是否含零、面积而非半径、两个图例 |
| 多注释热图 | 单次确定行列索引 → 主矩阵 + 顶/侧注释 + 格内效应量 → 同区组合 | 各矩阵/注释按同一 ID 排列；效应与 P/q 分开 |
| 空间多图层 | 坐标变换 → 底图 → 细胞/spot 几何 → 数值层 → ROI/比例尺 | 原点、方向、单位、切片、配准与尺度 |
| 空间组成图 | 保留真实比例 → 合并省略类为 Other → 固定几何与类别颜色 | top-k 0/1 成员不等于丰度；不丢弃后偷偷重归一化 |
| 邻域/通讯网络 | 分 section 建稀疏边 → 明确筛选 → 固定布局 → 编码方向/权重 | 邻近、相关、配体受体候选与因果机制不可混写 |
| 谱系趋势热图 | 读取已拟合趋势 → 共同时间网格 → 按峰值/模块等规则排序 | 真时间/伪时间、平滑方法、拟合值/标准化值；不伪造区间 |
| OT/发育流图 | 核验 coupling 单位 → 类型聚合 → 节点累计区间 → 连接带 | 联合质量与条件概率不同；弯曲连线仅用于排版 |
| 样本效应/模型对比 | 审阅后的样本级估计或配对结果 → 点/区间/分层 | 独立重复、配对、区间含义、数据泄漏与比较公平性 |

OT 类型聚合可写为 `F = A.T @ P @ B`：A/B 为源/目标类型指示矩阵，P 必须是含义明确的 coupling。检验聚合前后总质量；若为 unbalanced OT，报告实际输入质量，不强迫其等于 1。行归一化转移概率必须另行解释，不能直接称为细胞数。

渲染器不得执行归一化、聚类、模型拟合、差异检验或选择“最好看”的 ROI。这些步骤需要独立的上游逻辑与 provenance。

## 7. Python/R 执行分支

### Python

先读 [Python 分支](references/python.md)。核心使用 `scripts/figure_core.py`、`complex_recipes.py`、`composer.py` 与 `native_renderers.py`；按需接入领域对象，不安装无关训练依赖。

renderer 接收 `PanelContext + DataFrame`，返回 `PanelResult`；通过 `ctx.add_axes()` 或 `BoundedFigure` 在分配区域内绘图。可比较色标由 `ctx.norm(channel)` 提供；多注释热图共用索引，返回 mappables 供审核。不另开无关 Figure。

已接入整图 registry 的图型仅有 `embedding / spatial / marker_dot / annotated_heatmap`。其他路线使用已有原子函数或新增显式本地 adapter，不把模板数量当成现成渲染器数量。

### R

先读 [R 分支](references/r.md)。使用 `scripts/figure_core.R`、`complex_recipes.R` 与 `compose_plan.R`。按唯一 ID 对齐 genes × cells 与 metadata；Seurat 多 layer 显式选择或受控合并，不覆盖原对象。

renderer 为 `(ctx, table)`，返回 `figure_panel(object, system='ggplot'/'grob'/'heatmap')`。ggplot 转为 grob；ComplexHeatmap 在最终 panel 尺寸下绘制/捕获，不把 Heatmap 直接当 ggplot 相加。纯 ggplot 可选择 patchwork 作为替代全局布局，不混用两套全局排版器。

整图模式由共享 Python 规划器生成 `render_plan.json`，R 进程独立消费；R 快速单图模式不需要规划器。R 项目须注册实际使用的构造函数，不假定任意模板都能直接运行。

### 命令入口

以下路径相对于 Skill 根目录；`/path/to/project` 必须替换为实际项目路径。不要覆盖已有输出目录。

```bash
# 整图：结构、数据引用、文件与主键预检
python scripts/framework_contract.py /path/to/project/figure_spec.yaml \
  --root /path/to/project --check-files --out /path/to/project/build/preflight

# Python：仅限全部 renderer 已被默认 registry 支持的 FigureSpec
python scripts/render_project.py /path/to/project/figure_spec.yaml \
  --root /path/to/project --out /path/to/project/build/Fig1
```

新增渲染器通过可信本地 registry 显式注册，不从 YAML 执行函数体，不自动下载运行远程脚本。依赖只按需要安装；固定项目版本并记录真实运行环境，不伪造锁文件。

## 8. 证据与来源归因

引用论文风格或特殊包时，按 [literature_audit_v1.md](references/literature_audit_v1.md) 保留证据等级：作者声明公开、仓库可访问、已读作图代码、已实际重跑。包/API 与脚本用途必须有实际查阅的来源支持；代码读过不等于执行通过，一般推荐不得写成作者用过。

既有核验中，CellRank 2 的样式上下文与谱系趋势、spatialDLPFC 的多注释热图与 top-k 成员处理、LIANA+ 的绘图工具导入，各有不同核验深度；检索记录提供具体出处。不要把某个包公开写成全论文可复现，也不要猜测作者原字体或最终排版软件。

本包函数为此前交付的原创实现，不是原作者源码复制品。摘要整合不增加论文数量、不升级源码证据、不等于重新执行全部论文。

## 9. 质检闸门与完成条件

按 `draft → preflight_passed → rendered → manually_reviewed → released` 记录状态；这是审阅流程，不是自动批准。

**数据/统计检查：** 主键与顺序、层与单位、检测比例、缺失值、样本设计、效应与区间、P/q、空间切片、OT 质量、预测/观测标记。常规组间推断不能用细胞数冒充独立样本数；两个生物学重复也不自动意味着充分功效。特殊设计另立统计依据。

**版式/视觉检查：** panel 不重叠或越界；最终尺寸字号可读；相同实体颜色一致；比较尺度与分母一致；图例完整；轴向和比例尺正确；长标签、标注与图例不互相遮挡；检查灰阶/色觉可读性以及矢量/栅格和字体导出。

**自动检查边界：** 当前 Python 仅覆盖部分文字边界、最小字号及已登记连续色标等；不保证发现所有碰撞、统计错误或科学解释问题。R 尚无自动文字几何审核。未执行项目必须标记 `not_run/pending`，不能从另一语言或历史测试推定通过。

缺少数据不得用随机值代替研究结果；测试矩阵仅标为 SOFTWARE QA。无字素材必须另存，完整标注图才用于科学审阅。受限数据与患者标识不得随源数据包公开。

## 10. 交付协议

快速模式交付所改图、实际脚本、必要源数据/来源记录及检查结果。整图模式交付：

```text
Fig1/
├── Fig1.pdf / Fig1.svg / Fig1.png
├── figure_spec.json（或实际使用的 YAML）
├── render_plan.json / preflight.json
├── 源数据 CSV/TSV 与实际绘图脚本
├── provenance：输入/输出哈希、转换、种子、环境版本
└── QA：已执行、失败和待人工审阅项目
```

按用户需要选择格式；不要只换文件后缀就声称矢量可编辑。不把上述逻辑目录伪称每个后端完全相同的自动文件命名。详细交付规则见 [qa_protocol.md](references/qa_protocol.md)，本包验证范围见 [QA_REPORT.md](QA_REPORT.md)。

最终说明只需回答：**完成了什么图；数据和主要处理是什么；实际跑过哪些检查；还有哪些限制。** 交付真实存在的文件，不仅给包名或建议，不声称已安装到用户环境。
