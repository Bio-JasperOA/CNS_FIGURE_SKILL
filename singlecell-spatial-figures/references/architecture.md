# 单细胞与空间组学 Figure Framework · v2.0

## 设计目标

把“参考论文 → 一串包名 → 手工拼图”改为“科学问题 → FigureSpec → 可核查的数据 → 可替换渲染器 → 整图排版 → 审阅与导出”。这里的框架同时指科学证据结构、软件结构和 Figure 版面结构，不是一个新的配色主题。

本版是基于既有文献审计的原创工程重构，不新增论文样本，也不把之前仅检查部分代码的工作升级宣称为全文逐图复现。

## 一、六层架构：每层只有一个主要职责

| 层 | 负责什么 | 明确不负责什么 | 核心产物 |
|---|---|---|---|
| 1. Evidence planning | 定义整图问题、主信息、对照和每个 panel 的证据职责 | 没看结果先编写阳性结论 | Figure brief、panel question、evidence level |
| 2. Data contracts | 将已有分析对象转换为带 ID、单位和来源的图形输入 | 默认 `.X` 是 counts，或绘图时重新训练模型 | 经过审阅的长表/矩阵/边表及 manifest |
| 3. Semantic design | 注册类别颜色、顺序、连续量范围、字体与单位 | 每张图重新取色、重新标准化而不说明 | 同一份 FigureSpec 中的 scales/design |
| 4. Figure composition | 分配物理画布、主次 panel、图例与边缘注释空间 | 自动把全部 panel 塞成等大小九宫格 | 毫米级 outer/content boxes |
| 5. Language backends | Python Axes/GridSpec 或 R ggplot/grid/Heatmap 渲染 | 决定生物学结论或修改分析值 | 具名渲染器与 panel 对象 |
| 6. QA and delivery | 记录结构错误、检查渲染、审阅科学语义并导出 | 把测试通过冒称论文图已获科学验证 | preflight、source data、provenance、QA |

依赖方向是从上到下。换 Matplotlib、Marsilea 或 ComplexHeatmap 不应该改变统计量；换一个调色板不应该重新进行细胞注释。

## 二、三个 Skill，但只维护一套契约

`sc-figure-director` 是薄入口，负责问题分解、选择图形路线、生成并校验 FigureSpec。`sc-figure-python` 和 `sc-figure-r` 是执行端，读取同样的数据定义、尺度和物理布局。

三个目录都可以独立携带规则和模板；其中共享 schema 与校验器按内容校验一致，避免 Python/R 自行发展出冲突的颜色或坐标含义。主 SKILL.md 只保留触发规则、选择逻辑和执行顺序；方法细节、文献和代码按需读取。这是渐进加载，而不是要求 agent 每次先读所有论文和所有函数。[S1]

### 使用路径

**快速模式**：单张已定义的图，或仅修改字号、配色、坐标范围。直接使用语言 Skill 和已有渲染函数，记录源数据与最小 provenance，不强迫建立完整工程。

**论文模式**：整张多 panel Figure、跨图一致性或复合图。先填写 FigureSpec；执行 `preflight → render → review → export`。只在存在实际缺口时增加 adapter 或 renderer，不为一个 dotplot 安装整个深度学习生态。

## 三、整张 Figure 的框架先于绘图函数

先写出一句整图问题，再选择证据角色：overview、identity、spatial_context、quantification、mechanism_candidate、validation、benchmark、uncertainty。角色不是固定图型。例如 validation 可以是样本级点图，也可以是独立实验，而不必又画一个 UMAP。

主图只分配必要的证据空间。为让复杂热图的行名可读，允许它占用两列；空间 overview 保留真实长宽比；局部细节与定量 panel 可以更小。留白应服务于分组和图例，不能用于制造重要性。1:1 可以是单个嵌入 panel 的偏好，不应强迫整张组织切片或复合 Figure 都变成正方形。

四种 starter blueprint：

| Blueprint | 阅读逻辑 | 易错点 |
|---|---|---|
| Atlas | 身份定位 → marker 证据 → 空间定位 → 样本间差异 | 只列细胞数，不报告生物学样本 |
| Spatial niche | 全切片 → 预定义 ROI → 局部关联/效应矩阵 → 样本级复核 | 从一个漂亮 ROI 推广到整个队列 |
| Development | 时间与身份 → 预测转移 → 谱系程序 → 留出时间验证 | 将 OT/velocity 曲线解释为真实运动路径 |
| Model benchmark | 数据拆分 → 配对比较 → 校准/不确定性 → 失败分层 | 相邻切片或同 donor 泄漏到训练和测试两侧 |

这些 YAML 只含布局和字段示范，没有生物学数值；`DRAFT:`、文件路径、类别和色标范围必须替换。四 panel 不是硬性要求。

## 四、FigureSpec 是实际执行输入，不只是 Markdown 清单

核心字段包括 figure、datasets、scales、design、layout 和 panels。每个 panel 绑定一个 data_id，声明 channels、scale_ids、slot、统计设计和依赖关系。所有颜色/色标集中定义，panel 只引用其 ID。

`slot: [row, col, row_span, col_span]` 从 0 开始。`margin_mm` 和 `padding_mm` 顺序是 `[top, right, bottom, left]`。`outer_mm` 是 panel 的完整地盘，`content_mm` 是扣除标题、坐标与图例预留后的内容区。任何复杂子图只能在自己的区域里组合。

同一比较组必须引用相同尺度定义。单纯收集合并图例不能证明使用了相同数值范围；patchwork 的图例收集按图形表现去重，本框架先核验语义再排版。[S3]

## 五、复杂图形使用“可组合模块”，不使用截图拼接

### Python

普通 renderer 接收 `PanelContext + DataFrame`，返回 `PanelResult`；通过 `ctx.add_axes()` 在该 panel 内建立一个或多个轴。每个 renderer 不得另开无关 Figure，也不能在里面做差异分析。可比较的连续色标从 `ctx.norm(channel)` 获取。

已有的 `annotated_heatmap` 通过 `BoundedFigure` 接入整图：它原本的 GridSpec 只作用于自己的毫米级 content box。这样主热图、顶部/侧面条形、格内效应量与 colorbar 仍然有共享索引，不需要输出 PNG 再缩放回来。Matplotlib 也提供 constrained layout、嵌套网格等路线；本版为跨语言可核对尺寸，采用显式物理分区，而不混用多套自动排版引擎。[S2]

### R

同样的 render_plan.json 定义物理区域；renderer 返回 `figure_panel(object, system)`。ggplot 走 ggplotGrob/grid；ComplexHeatmap 走匹配目标内容区尺寸的 grid 捕获；不能把 Heatmap 当普通 ggplot 相加。

尤其是 `anno_mark`、`anno_link` 等依赖设备尺寸的注释，不能在默认 7×7 英寸设备上捕获，然后随意缩小到小 panel。捕获时必须使用最终 panel 的 width/height。[S4]

纯 ggplot 项目也可使用 patchwork 的 design/area 做替代组合；它是可选路线，不是与 grid 再叠加的第二套全局布局。[S3]

## 六、数据交换与语言边界

AnnData/Seurat/SpatialExperiment 的 assay/layer、稀疏矩阵和原始坐标由上游 adapter 明确提取。当前 FigureSpec 文件校验器支持 CSV/TSV exchange tables，不会直接读取或全量稠密化 h5ad/rds。

R/Python 的数值汇总函数保留 v1，不宣称两种矩阵方向相同：Python 为 cells×genes；R 为 genes×cells。交换到 FigureSpec 时使用带唯一键的长表；未观测不能自动变成 0。

通用结构校验器用 Python 实现，可为任一后端生成 render_plan.json；R 绘图进程不调用 Python，只消费规划产物。R 单图快速模式不需要该规划器。当前没有把 JSON Schema 校验器重新实现成一套未验证的 R 代码。

## 七、状态与质量闸门

`draft → preflight_passed → rendered → manually_reviewed → released` 是工作流约定，不是自动批准状态机。本版实现 preflight 和渲染；不会自动将产物标记为 released。

**硬错误**：未知数据或尺度引用、重叠/越界 panel、依赖循环、错误颜色映射、缺失/重复主键、非法色标、未声明空间单位、以细胞/spot 替代独立样本进行常规组间推断。

**自动渲染检查**：Python 检查画布外文字、低于配置字号阈值的文字、已登记 mappable 的色标范围；不宣称检出所有标签互相遮挡。R 自动几何审核尚未实现。

**必须人工审阅**：图是否回答问题、比较是否公平、数值和图例是否一致、样本单位、ROI 选择、坐标校准、色觉可读性、最终尺寸的文字碰撞、统计方法和机制表述。

没有 n≥2 的一般统计保证：校验器只把少于两个生物学重复视为常规重复组比较的阻断条件，不把 n=2 当作充分功效。特殊单细胞实验或单病例设计须另立统计契约。

## 八、可扩展，但不虚报实现状态

新增一个图形只需编写 renderer 并放入显式 registry，再写最小输入测试、尺寸测试及源数据检查。YAML 不接受待 eval 的函数体，也不动态下载运行远程代码。

本版 Python 已接线：embedding、spatial、marker_dot、annotated_heatmap。其余 starter 中的 transport、ROI、sample_effect、lineage_trend、benchmark 等是计划路由，需要调用 v1 已有函数或补充项目 adapter。不能把 blueprint 数量当成已实现 renderer 数量。

R 提供通用 composer 和既有原子函数；项目需注册自己的 ggplot/grob/Heatmap 构造函数。本次运行边界见 QA_REPORT.md，不用 Python 的测试结果替代 R 验证。

## 官方技术来源

[S1] Agent Skills specification: https://agentskills.io/specification
[S2] Matplotlib constrained layout guide: https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html
[S3] patchwork controlling layouts: https://patchwork.data-imaginist.com/articles/guides/layout.html
[S4] ComplexHeatmap integration / device-size-dependent capture: https://jokergoo.github.io/ComplexHeatmap-reference/book/integrate-with-other-packages.html

检索日期：2026-09-13。以上支持格式/API与排版能力；六层结构、具体契约和本版代码是本次原创设计，并非上述软件官方要求。
