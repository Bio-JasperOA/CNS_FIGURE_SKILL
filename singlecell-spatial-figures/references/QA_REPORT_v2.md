# v2.0 实际检验记录

日期：2026-09-13。本报告仅记录这次重构的实际运行情况，不扩大上一版文献核验范围。

## Python

命令：`python -m pytest tests -q`，在 sc-figure-python 目录执行。

结果：**76 passed, 11 warnings, 0 failed**。其中 38 项是继承的 v1 核心回归测试，38 项是本轮新增的框架测试。11 个 warning 均为同一已知环境情况：Arial 未安装，使用 DejaVu Sans。没有把缺失字体静默忽略，也没有分发字体文件。

新增测试覆盖：四份模板；schema 错误；非法数值；颜色/尺度/数据引用；panel 重叠、越界、尺寸、padding；依赖排序与循环；常规组间推断的独立样本单位；输入文件存在、主键及 SHA256；直接传入表格的空主键；项目 root 约束；renderer 显式注册；跨 Figure 的错误创建；副本保护；最终物理画布；画布外文字及字号；未实际绘制的边界外 tick 避免误报；复杂热图与另一个 panel 同页组合；单 section 空间图；embedding/marker dot；完整文件读取—渲染—导出流程。

测试数据均为显式人工 SOFTWARE QA 数据，不是单细胞/空间组学实验结果，没有作为生物学图随包分发。

## PDF / 目视核查

实际生成一张双 panel 软件测试图：左侧是共享索引的 heatmap + 顶部/侧面条形 + 格内数值 + colorbar，右侧是简单测试折线。整张图明确标注 SOFTWARE QA ONLY / NO BIOLOGICAL RESULT。

使用 pdftoppm 将 PDF 渲染成 PNG，实际打开检查；该测试尺寸下未见图层错位、文字裁切或 panel 覆盖。注意这不是任意真实数据标签长度或所有 blueprint 的视觉验证。

pdfinfo：画布约 518.740 × 311.811 pt，对应 183 × 110 mm。pdffonts：DejaVu Sans 与 DejaVu Sans Bold 为嵌入/子集化 CID TrueType；未验证用户机器上的 Arial。Python 自动渲染检查在修正边界外未绘制 tick 的误报后通过。

仍需对真实图执行：科学解释审阅、统计设计与数值核对、全部标签间碰撞、灰阶/色觉可读性、空间配准与物理比例尺、所有可选绘图包和操作系统。

## R

当前环境没有 Rscript。新增 compose_plan.R、数值测试和 test_composer_smoke.R 已交付，但没有运行 R 解析器、ggplot/grid/ComplexHeatmap 或 PDF/SVG/PNG 设备。

R 的架构接口与运行边界已写明：共用 Python 规划器的 render_plan.json；R 后端自行渲染，不在 R 中嵌套 Python。R 没有自动文字几何审核。不得把 76 项 Python 测试写成 R 测试通过。

## 模板与打包

四种 FigureSpec 均通过结构/语义/布局预检；三份 Skill 中的 schema 和规划器按 SHA256 校验一致。每份模板都保留 DRAFT 标志，真实文件未提供，未执行 --check-files 后的真实数据审核。

检查主 SKILL.md 的 YAML frontmatter、目录名一致性和相对链接；压缩包排除 Python 缓存、测试临时图、字体与用户实验数据。没有运行官方 skills-ref 验证器，不把自有检查标为官方认证。

## 本轮 Python 环境

Python 3.13.5。

```json
{
  "numpy": "2.3.5",
  "pandas": "2.2.3",
  "scipy": "1.17.0",
  "matplotlib": "3.10.8",
  "pytest": "9.0.2",
  "PyYAML": "6.0.3",
  "jsonschema": "4.26.0"
}
```

v1 原有论文资料位于 evidence_v1/；本次没有新增论文检索、逐图复现或作者源码重跑。
