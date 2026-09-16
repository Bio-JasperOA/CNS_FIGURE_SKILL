<!-- REMOTE_PUBLICATION:START -->
# GitHub publication verification

420 passed, 2 skipped, 12 warnings in 31.28s

26 families; 54 no-subtitle figures; 26-page paired PDF; existing palette, schema and legacy script hashes unchanged.

[Build run](https://github.com/Bio-JasperOA/CNS_FIGURE_SKILL/actions/runs/35073957293) | [Machine-readable report](PUBLISH_REPORT.json). The authoring report below is historical; its earlier not-uploaded status does not describe this publication.
<!-- REMOTE_PUBLICATION:END -->

# v3.2.0 实际检查记录

日期：2026-09-15。**本轮是本地完成的代码与范例；未推送 GitHub，也未运行远端 CI。** 最后核对的远端 main 为 ff12b7806d522aebf5985c6bcad00961efa03aa3。历史 v3.1 的 299 项 CI 不能算作这次的结果。

## 实际测试

命令：`python -m pytest tests -q`。最终结果 **192 passed，0 failed，0 skipped，无 warnings**。其中 187 项涉及绘图、数值语义与导出，5 项涉及能力登记、v3 大版本和元数据更新的幂等性。原有主流水线全套测试未在此局部更新环境重跑。

包括 26 类 × minimal/advanced 渲染、26 类 PDF/PNG/SVG 真导出、空/重复键拒绝、真实任务来源要求、输入和配置不可变、类别容量/颜色固定、六种归一化、点面积、曲线/效果区间两版均保留、阶段质量守恒、精确集合交集、校准点面积跨模型共同尺度、混淆矩阵分母、缺失值、外部 100 类完整色键、字幕哨兵不显示、越界文字导出阻断。包内提供实际测试代码，不借用旧测试计数。

## 实际输出

26 类的 52 张常规图 + 100 类别的两张压力图，共 **54 张独立图**。每张导出 PNG/PDF/SVG 和 QA JSON；两版共享源 CSV 与配置，manifest 记录 SHA256。100 类别另有完整颜色 CSV 和 key PDF/PNG。

程序逐一检查 54 个 PDF：页面物理尺寸与配置一致、合成数据标识为可检索文字、无字幕测试哨兵。54 份 QA 记录无 subtitle、无已检测的画布外文字。`EXPORT_AUDIT.json` 记录逐图结果。

`paired_gallery.pdf` 有 **26 页**，同页左右为最简/高级，保持各自原始物理尺寸。实际打开六张接触表检查全部图的整体布局，另打开热图、弦带通信、校准、趋势等关键图的全尺寸或 PDF 预览。修复了热图模块/标签位置、图例与色标挤压、趋势末端两条标签重叠，以及校准面积偏移导致比例不准确的问题。

`pdffonts` 核查热图 PDF：DejaVu Sans / Bold 为嵌入、子集化 CID TrueType 字体。没有检测本机 Arial，也没有分发字体。图内的主标题和科学图例不是 subtitle；只有演示图保留小型 SYNTHETIC EXAMPLE 标识。

## 边界

这是合成范例和实现验证，不是原论文数值复现或真实项目的科学验证。部分复杂结构只有提供明确字段才渲染，例如分割 vertices、module、n、condition、抽象状态边、上下界及分阶段 mass。循环选色、伪造区间或由 UMAP 猜测状态边不属于功能。

高级图的复杂程度与数据有关，不承诺每类都应无限复杂；简单的 ROC/PR 在区间与操作点之外不应堆放无关图层。色觉缺陷、全部局部文字碰撞、任意长标签/全部设备组合、图像配准、科学叙事仍需项目级人工审阅。Canvas 边界检查不等于全自动感知验收。

Rscript 不可用。R 文件是调用同一 Python 入口的 wrapper，未运行；没有新增并验证 26 类原生 R 后端。旧 FigureSpec 四类 renderer/schema 3.0 不被此代码替换。整个旧图形入口未被误报为 26 个 FigureSpec 注册。

## 安装与发布

`APPLY_UPDATE.py` 是带 dry-run、源文件校验、目标修改保护与回滚备份的本地合入工具，不会安装依赖、提交或推送。元数据更新保留 palette 和旧 renderer 字段；旧的 v3.1 交付解包被从 CI 中移除，避免覆盖新版代码。更新工作流使用仓库原有的固定 action refs；其远端运行尚未验证。

安装工具的单独冒烟检查结果见更新包根目录 `INSTALLER_CHECK.json`，不混入上面的 192 项绘图/元数据测试。

## 实际环境

Python 3.13.5；NumPy 2.3.5；pandas 2.2.3；SciPy 1.17.0；Matplotlib 3.10.8；Pillow 12.3.0；PyMuPDF 1.26.7；pytest 9.0.2。
