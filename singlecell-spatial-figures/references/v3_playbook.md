# v3 操作手册：设计决策、修订与验收

版本 3.0；当前能力以 `../CAPABILITIES.json` 为唯一登记，实际运行以 `../QA_REPORT.md` 为准。本文的阈值不是期刊官方标准。原论文来源仍在 `literature_audit_v1.md`，本轮没有新增逐图复现。

## A. 先明确图应该让读者完成什么任务

把问题拆成“比较对象 + 要识别的差异/结构 + 支持该判断的量”。例如“某状态是否在处理后的样本中增加”需要样本级分母与组间比较；给 UMAP 染色只能定位，不能独自回答丰度变化。

设计草案记录：主问题；主 panel；读者先看哪里、接着比较什么、最后检查什么；可直接读出的结果；不能得出的结论。审阅时要求指出图上具体位置/图例/数值，不接受把问题复述一遍当作验收证据。

| 判断任务 | 首选视觉编码 | 不足时如何升级 |
|---|---|---|
| 比较效应、变化和不确定性 | 同尺度位置/区间；使用独立样本点 | 空间/嵌入图只作背景，增加真正的样本级定量 |
| 找到细胞身份与空间位置 | 同一身份颜色、已有嵌入/共同坐标 | 分面或局部放大，保留 overview 和 ROI 来源 |
| 筛选多基因、多状态模式 | 共享行列索引的矩阵或 dotplot | 行列过密则拆模块；不靠缩字解决 |
| 比较概率或时间趋势 | 共同时间坐标和明确概率定义 | 区分预测/观察，加入留出验证或误差说明 |

后两类中只有 marker/heatmap 等已连接渲染器可直接运行；样本效应、轨迹和模型评估需项目渲染器，不因推荐图型而宣称已实现。

## B. 视觉层级、信息密度、阅读顺序

**层级判断**：在最终尺寸上，不听作者讲解，能否找到主比较及其刻度/对照？若只能看到面积最大的 UMAP，却无法找到真正支持论点的定量图，应调整主次。记录 `lead_panel`，不要把面积大小当成唯一正确的强调方法。

**密度判断**：检查“每个矩阵单元分配多少 mm”“每个类别有多少标签宽度”“图例占去了多少空间”，再看这些面积是否服务于实际比较。代码报告 `plot_area_fraction`、矩阵单元 mm、主 panel 面积和阅读顺序冲突。这些是诊断量，不能用一个总分替代设计判断。

**重排顺序**：先收集合适的共享图例；再调整行/列权重和 panel 跨格；再改变整图高度/宽度；必要时将过大的矩阵拆成有科学依据的模块或改变图型。空间 overview 保留长宽比；不在不说明的情况下删去罕见类型、gene 或 ROI。

**阅读顺序**：默认从上到下、从左到右，跨行/跨列必须有明确标签或分组。`reading_order` 和实际几何顺序不同会提示人工审阅，但合理的替代路径可以记录理由。

## C. 配置与代码的一一对应

`visual_contract.schema_v3()` 在旧版严格 schema 上添加字段；`legacy_view()` 仅用于复用旧版数据/索引/布局预检，不把 v3 配置交给旧 renderer 绘制。

| 配置 | 实现与作用 |
|---|---|
| `scales.*.norm` | `VisualScale`，实际用于 artist 和独立 colorbar |
| `bad/under/over`, `out_of_range`, `invalid` | `prepare()` 处理绘图副本并报告数量；源表不变 |
| `guides` | `all_guides/guide_details/guide_size/draw_guide`，实际测量和绘制 |
| `visual.wrap_mm/line_spacing/min_plot_mm` | `Measure/fit_panel`，在目标字体下测量，放不下就失败 |
| `panels[].title/marks.area_pt2` | 实际绘制标题或非数值编码散点大小；不是生物学物理尺度 |
| `protected_regions` | 将数据坐标矩形投射到导出几何，提示文字侵入 |
| `visual.reading_order/lead_panel/max_cell_mm` | `design_audit` 的可记录审阅提示 |
| `visual.max_repair_cycles` | 渲染记录和 `escalation()`，提示由局部修改升级为重构 |
| `snapshot.json` / `review.json` | 文件哈希、依赖变化、人工签署及过期阻断 |

### 色阶语义

`two_slope` 的 `center` 必须位于范围内部。`log` 不会给零自动添加伪计数；无效值要么报错，要么明确 `invalid: mask`。`symlog` 的 `linthresh` 定义零附近线性区域。`power` 的 `gamma` 不改变源数据。`boundary` 使用 `[a,b)` 分段，最后一段包含最终上端点。

越界 `extend` 用 under/over 及延伸提示；`clip` 用端点饱和但保留越界计数；`mask` 用缺失色且报告被屏蔽数；`error` 阻断渲染。不能将截断后颜色的均匀性解释为生物学均匀。自动 ticks 来自归一化的逆映射；手工 ticks 仍按原始单位。

缺失表达与缺失检测比例都不能变成 0。marker 的缺失用缺失色并叠加叉号，比例为 0 是真正的零面积；两者分开。

### 图例设计

连续值用 colorbar、类别用身份表、点面积用检测比例。根级 guide 将它们与 panel 内容分离，明确 owner 与使用者。方向、右/底位置、列数、长度/厚度和字号都是配置。`position:auto` 只搜索受限的右/底组合，不是页面上任意位置的智能避让。

非线性尺度需按映射后的刻度间距测量，不以刻度数少就假定不拥挤。手工指定的长度不足时失败，不能无声改变指定长度或删除刻度。共享 guide 要同一 scale ID，不能因图例外观相似就合并。

## D. 感知颜色与字体检查的边界

颜色筛查计算 D65 CIELAB 明度/近似 deltaE76、对背景的亮度对比，以及 Machado severity=100 的三种 CVD 变换。结果包括模拟 RGB、近似色差对和被裁回显示色域的比例。它不是 deltaE2000、临床视觉模拟或可访问性认证。低对比的浅色点可能需要轮廓、非颜色编码、直接标签或不同图型。

程序检查 Matplotlib 中实际字形覆盖、数学解析字体和文本边界；最终 PDF 再检查文字 spans、最终字号、嵌入字体和替换字符。数学上下标的包围盒可能产生保守误报，须看实际输出。中文缺字、光学字距、字偶间距、字形回退细节与所有平台一致性不能由一个字体文件名保证。

最终成品不能依赖软件测试 fixture 的成功：换成长基因名、几十类细胞、复杂数学式或不同字体，都要重做检查。

## E. 自动 QA、人工 QA 与可接受失败

| 等级 | 例子 | 处理 |
|---|---|---|
| 硬错误 | 非法数据/尺度、未知 renderer、文字越界、字号低于最低值、跨 panel 侵入、实际载体缩放不符 | 修复并重跑，不允许通过签署豁免 |
| 审阅警告 | 文本包围盒疑似碰撞、浅色对比弱、相邻颜色近似、主次/顺序异常 | 对照最终输出，记录 warning ID、位置和具体处理或保留理由 |
| 未验证 | R native、未注册的数据遮挡、描边/栅格化载体、光学字距、真实科学结论 | 不写自动通过；补实际实验/环境/人工证据或限定交付范围 |

`review.json` 的 12 项验收分别要求指出问题回答位置、结论强度、独立单位、尺度/缺失、阅读顺序、信息密度、图例、感知颜色、字体、遮挡、最终载体和来源。每项有 failure_condition。未填写、过期、缺少 reviewer/含时区时间、未处理 warning 或硬错误，均不能通过审阅门禁。

**人工记录示例（只说明写法，不可预填为真实证据）**：

“density_layout：在 183×95 mm 的实际 PDF 中逐行核对 b 的 12 个基因标签；无裁切。warning xxx 源于两个数学 span 的包围盒，放大及原尺寸均确认字形没有覆盖数据。”

科学项必须包含“图中什么比较支持什么结论”及“一个替代解释”。不能只写“清晰、正确、符合 Nature”。程序只能验收记录完整性，不能替代科学审稿；禁止让 agent 自动把 pending 全改为 pass。

## F. 修订升级与影响追踪

检查 `repair_history.json` 和 `repair_decision.json`。默认连续两次同类未解决问题、跨 panel 修改或破坏最小字号/内容边界，转入整体重构。记录新的布局假设，例如“将三列改为两列，热图跨列，共享图例移到底部”，重新渲染全部受影响 panel 和组图。不要不断挪动单个 label 掩盖结构问题。

输入→panel→依赖 panel→共享图例使用者→整图的影响由 `impact()` 求闭包。全局样式或任何当前脚本改动保守地影响全图。删除 panel 也会令已组装输出失效；人工文件修改通过哈希识别。当前执行器重新渲染整图，**没有实现增量缓存或后台文件监听**。这是一种完整重跑时的影响/审阅失效机制，不冒称实时监控。

## G. 最终载体与 R 工作流

在报告/幻灯片的真正交付软件中导出最终 PDF，然后用 `carrier` 校验声明的区域。源图与目标区域至少要有三个唯一文字锚点、并覆盖两个方向；同时核对文字是否丢失、是否非等比缩放和实际字号。没有锚点不假装成功。当前不支持自动验证旋转、复杂变形、纯图片/描边文字或直接解析 DOCX/PPTX 的最终布局。

`bind-report` 会**重新运行**对应的 PDF 检查，把报告和实际产物的哈希加入 snapshot，并生成 `review_pending.json`；不会相信手工改成 true 的报告字段。R 导出先用 `inspect-pdf` 和 `bind-report --kind export`，再作为 source 进行 carrier 检查。不要只审 Python PDF 却交付未经审阅的 R PDF。

绑定后保留旧 review 以便审计；重新检查后用 pending 模板形成新的 review，声明 `carrier_mode: placed` 及 `carrier_reports` 的实际绝对路径。仅更新 review 哈希而不复核不构成审阅。

R bridge 共用已编译的颜色、ticks、行列顺序和几何，但本机没有 Rscript。数学标签明确拒绝，不猜测 TeX→plotmath；复杂/负注释轨道须用原生 R adapter，当前简单非负轨道没有完整坐标轴刻度，不能用于要求独立精确定量的轨道。通用 PDF 审计能检查输出，不等于 native R 的数值/图形测试通过。

## H. 测试与基线管理

运行 `python -m pytest -q`。确定性测试数据均为软件 fixture，不作生物学结论。包括色阶边界与缺失、长标签、拥挤图例、极端长宽比、共享 guide、字形/数学式、遮挡/跨 panel/裁切、实际 PDF 与缩小后的载体、配置/代码/数据/产物改变后的失效。

`compare` 对同尺寸 RGB 图逐像素比较，尺寸改变直接失败；不可先缩放图片消除回归。基线必须先经人工批准，不能自动把失败的候选图设为新基线。Poppler/PDFium 的比较只是当前环境两个渲染器的测试，不涵盖 Acrobat、所有 OS、浏览器或打印机。

原生 R 测试在 Rscript/jsonlite 可用时才运行，否则明确 skip。本轮没有导入真实病例或原论文数据。后续新增真实数据测试须记录授权来源、版本、数据子集和预期比较，不得声称本轮已覆盖。

## I. 17 项问题的整改索引

1 定位收敛；2 具体视觉决策与诊断；3 能力登记/strict renderer preflight；4 六种 norm/四种越界政策；5 CIELAB/对比/CVD 筛查；6 字体测量与有界布局；7 guide 独立对象；8 artist+math+PDF 字体检查；9 bbox/保护区/导出几何与明确 R 限制；10 实际载体锚点与字号；11 repair escalation；12 依赖闭包与哈希失效；13 问题回答/替代解释的人工验收；14 复杂软件场景与双 PDF renderer；15 逐项 failure_condition/审阅记录；16 hard invariant 与可改默认值分离；17 当前能力与验证单入口，历史参考降级为按需读取。

这些整改不意味着 17 类问题都已被自动化解决。详细实现/测试/人工边界见能力登记。

## 技术出处（检索于 2026-09-14）

- Matplotlib colormap normalization: https://matplotlib.org/stable/users/explain/colors/colormapnorms.html
- Matplotlib fonts/math: https://matplotlib.org/stable/users/explain/text/fonts.html
- PyMuPDF text spans/fonts: https://pymupdf.readthedocs.io/en/latest/textpage.html
- W3C CSS Color 4 color conversion context: https://www.w3.org/TR/css-color-4/
- Colorspacious CVD model documentation: https://colorspacious.readthedocs.io/en/latest/tutorial.html
- Severity-100 numerical matrices read from the authors' library transcription: https://raw.githubusercontent.com/njsmith/colorspacious/master/colorspacious/cvd.py ; model DOI 10.1109/TVCG.2009.113. The original supplemental web page was not fetched successfully in this run.
- ComplexHeatmap device-size-dependent integration: https://jokergoo.github.io/ComplexHeatmap-reference/book/integrate-with-other-packages.html

本项目未复制论文全文、字体或第三方绘图库；以上是方法/API依据，具体工作流和验收逻辑是本仓库的工程实现，不是上述项目或期刊认可的标准。
