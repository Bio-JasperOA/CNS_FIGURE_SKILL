<!-- STYLE_GALLERY_V3_2:START -->
# v3.2 当前样式检查

本轮实际运行范围见 [style_gallery/QA_REPORT.md](style_gallery/QA_REPORT.md)。此前 v3.1 与 v3.0 的报告为历史记录，不能算本轮 CI。下面保留原流水线的历史验证，不以本轮样式测试替代原生 R 或真实数据检验。
<!-- STYLE_GALLERY_V3_2:END -->

# v3.0 当前验证记录

日期：2026-09-14。代码基于 main 的 `bda11f2bd4da4c77166da2154011c8cf6573c9d3` 修改。本次新增的是工程/视觉决策/验收能力，不扩大旧版论文检索或逐图复现声明。

## 实际执行

在 Skill 目录运行 `python -m pytest -q`：**134 passed, 1 skipped, 12 warnings**。其中 76 项通过继承的 v1/v2 回归测试，58 项通过来自本轮测试；另 1 项 R 原生执行测试跳过。实际日志保留在 `tests/VALIDATION_v3.txt`。

11 个 warning 来自旧版测试中 Arial 不可用而明确回退到 DejaVu Sans；另 1 个来自故意插入 U+10FFFF 的缺字测试。没有隐瞒字体回退，没有分发字体。Rscript 不在当前环境，因此 R 的语法、设备及结果没有被本轮执行验证。

## 本轮自动测试覆盖

- 六种 norm、中心/阈值/非线性刻度、四种越界政策、log 非法值、缺失、最终分段端点和显式 under/over 色。
- 明度、近似 deltaE76、背景对比、三种 Machado severity-100 模拟的数值边界。不是色觉可访问性认证。
- 严格配置/未知 renderer/无效 guide 选项；完整标签换行、密集图例、非线性刻度挤压、极端长宽比、共享图例、标题及检测比例单独缺失。
- 文字包围盒碰撞、局部裁切、跨 panel 侵入、保护区、字形和数学文本检查。
- 四个连接 renderer 的实际 PDF/SVG/PNG 导出、当前软件示例、最终 PDF 尺寸与实际载体缩放/字号。
- 文件/配置/数据/代码/产物的哈希、共享图例与依赖闭包、过期审阅、warning 理由、报告绑定、连续修复升级。
- 人工基线/候选图的像素回归与尺寸改变阻断；CLI 在比较失败时返回非零。
- 能力登记中全部 17 项的代码/测试引用存在且四种 renderer 名称与执行端一致。

## 实际目视与跨 PDF 渲染器检查

执行 `examples/v3_software_qa/figure.yaml`，生成 183×95 mm 双 panel 人工软件图。使用 Poppler 144 dpi 将其最终 PDF 渲染成 PNG 并打开查看。图中显式显示 ARTIFICIAL SOFTWARE QA，没有把 12 个测试点或 2×3 矩阵当作生物学结果。核对了标题/标签、共享中心色阶、缺失 swatch、格内效果值和注释轨道；该尺寸下未见标题或边界裁切。浅色对背景对比仍由 QA 提示并保留，不将自动通过改成感知质量已获认可。

独立的人工 PDF fixture 在本环境分别用 Poppler 与 PDFium 渲染，在相同尺寸、144 dpi 下执行像素比较；以 RGB 差异阈值 32、超阈像素比例不超过 2.5% 的软件回归政策通过。这不是所有 PDF、字体、操作系统、Acrobat 或打印机的一致性证明，也不是科学图审美指标。

## 未验证和明确限制

**R native 未运行。** R bridge 使用 Python 编译后的颜色和几何，最终 PDF 检查器可共用，但不保证 R 与 Python 字形、尺寸或图形像素等价。TeX 自动翻译、复杂/负值注释轨道、完整 R 轨道刻度均不由本 bridge 保证。

**没有使用真实生物学项目或原论文数据执行本轮 v3。** 软件测试补足了复杂失败场景，不替代真实标签规模、切片配准、真实统计设计、科研叙事和复现检查。

**人工检查仍必需。** 完整 glyph-level 碰撞、所有数据/箭头遮挡、光学字距、机制解释以及最终感知均不由程序证实。包围盒相交可能误报，warning 必须逐项看真实输出。

**最终载体支持有限。** 实际 PDF 锚点检查针对未旋转、保留文字的插入；纯栅格、描边文字、锚点不足、复杂变形或 DOCX/PPTX 原生排版未获自动验证。必须导出目标软件真正交付的 PDF；不能靠填写意图尺寸就算通过。

**不是自动发布系统。** `review` 验收的是绑定到具体文件的人工记录完整性；不能判定 reviewer 的科学判断是否正确，不自动授权发表。`repair_decision` 给出明确重构升级建议，但不会自动重写整张布局。`impact` 在运行时比较快照，没有后台监听或增量渲染缓存。

## 环境

Python 3.13.5。以下是本次实际导入的版本，不是全平台兼容声明：

```json
{
  "numpy": "2.3.5",
  "pandas": "2.2.3",
  "scipy": "1.17.0",
  "matplotlib": "3.10.8",
  "pytest": "9.0.2",
  "PyMuPDF": "1.26.7",
  "Pillow": "12.3.0",
  "PyYAML": "6.0.3",
  "jsonschema": "4.26.0",
  "pypdfium2": "5.8.0"
}
```

当前能力范围的唯一登记是 `CAPABILITIES.json`。`references/QA_REPORT_v2.md` 与旧日志属于历史记录，不与本报告合并计数。未运行官方 Agent Skills 认证器；本项目的测试不是第三方认证。

## v3.0.1 palette preset extension — 2026-09-15

This is an additive patch within v3. `spec_version` remains `3.0`; original tests and original manual palettes are retained.

Current local run: **213 passed, 1 skipped, 12 warnings**. Includes **79 new preset tests**, covering all 55 callable entries / 52 families, capacity, repeated/unknown category handling, stable saved mappings, six scalar normalization mechanisms, cyclic-role handling, table SHA256 mismatch rejection, endpoint HEX, preset resolution/replay, and end-to-end v3 render/provenance/snapshot/failure behavior. Existing tests account for 134 passes and one native-R skip. Warnings are the previous explicit Arial fallbacks and the deliberate missing-glyph fixture.

No native R execution is claimed (Rscript absent). R helper performs structural input validation; SHA256 verification and dependency binding are done by Python. No new original-paper or real-biological-data reproduction is claimed. Continuous presets intentionally freeze the review HEX values as RGB8, not the source float64 LUT bytes. The saved original review-catalogue hashes provide provenance for the full floating-point tables.

Palette figures remain drafts requiring human review. High capacity is a count of unique RGB entries, not evidence that all category pairs are perceptually separable. The existing 3.0.0 validation above is historical and is not overwritten by this extension.
