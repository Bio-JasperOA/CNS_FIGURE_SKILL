# Pipeline-aware Figure Rendering

**Analysis-module to figure-set mapping for reproducible scientific visualization.**  
**面向可复现科研可视化的“分析模块—配套图组”映射系统。**

This layer consumes reviewed upstream result tables and renders the figures associated with a registered analysis module. It does not rerun biological or statistical models.

本层读取已审核的上游结果表，并为注册分析模块生成对应图组；不会重新运行生物学或统计模型。

## Governing rule · 核心规则

Every registered analysis process must map to at least one scientifically necessary figure. Advanced analyses must map to at least one figure that exposes the additional scientific dimension.

每个注册分析过程都必须对应至少一张科学上必要的图；高级分析必须对应至少一张能够体现其新增科学维度的图。

## What this layer does not do · 本层不会执行的内容

The renderer does not rerun Seurat, Scanpy, CellRank, scVelo, CellChat, LIANA, Milo, scCODA, Squidpy, cell2location, Tangram, scVI, segmentation, enrichment statistics or model fitting.

Renderer 不重新执行 Seurat、Scanpy、CellRank、scVelo、CellChat、LIANA、Milo、scCODA、Squidpy、cell2location、Tangram、scVI、分割、富集统计或模型拟合。

Missing uncertainty, lineage, boundaries, transitions, neighborhoods, morphology or model-error information is recorded as unavailable or skipped rather than fabricated.

缺失的不确定性、谱系、边界、转变、邻域、形态或模型误差信息会被记录为 unavailable/skipped，而不是被伪造。

## Main files · 主要文件

- `PIPELINE_TREE.md` — human-readable analysis → figure tree / 人类可读的分析→图形树
- `MODULE_REGISTRY.json` — registered analysis modules / 注册分析模块
- `RESULT_CONTRACTS.json` — reusable result-table contracts / 可复用结果表字段约定
- `IMPLEMENTED_MODULES.json` — executable module boundary / 可执行模块边界
- `run_pipeline.py` — canonical module router / 统一模块路由入口
- `runtime*.py` — rendering adapters / 绘图适配器
- `build_gallery.py` — synthetic demonstration gallery / 合成示例图库生成器
- `validate_registry.py` — registry and mapping validation / 注册表与映射校验
- `tests/` — routing, rendering and output regression tests / 路由、绘图与输出回归测试

## Rendering levels · 绘图层级

1. `minimal` — smallest scientifically complete view / 最小科学完整视图。
2. `advanced` — adds a real dimension such as comparison, uncertainty, hierarchy, paired structure, spatial context, transition structure or prediction error / 增加比较、不确定性、层级、配对结构、空间背景、转变结构或预测误差等真实维度。
3. `panel` — publication-oriented composition of validated views without changing numerical meaning / 将已验证视图组合为发表级 panel，不改变数值含义。

## Global rules · 全局规则

- No subtitle renderer. / 不使用 subtitle renderer。
- Cell identities should keep stable named colors across related views. / 相同细胞身份在相关视图中尽量保持固定命名颜色。
- Palette choice and numeric normalization are separate. / 色板与数值归一化独立处理。
- Multi-section scalar maps use a common scientifically appropriate scale before composition. / 多切片标量图在组图前使用科学上合适的共同尺度。
- Standalone PDF/SVG files are publication candidates; raster contact sheets are review/navigation artifacts. / 独立 PDF/SVG 可作为发表候选；栅格 contact sheet 仅用于审核与导航。
- Synthetic fixtures are software tests, never biological evidence. / 合成 fixture 仅用于软件测试，不是生物学证据。

## Validate · 校验

```bash
python pipeline_tree/validate_registry.py validate
python -m pytest pipeline_tree/tests -q
```

## Render one module · 绘制一个分析模块

```bash
python pipeline_tree/run_pipeline.py \
  --module spatial.communication \
  --input spatial=results/spatial.csv \
  --input interaction=results/interaction.csv \
  --config project/spatial_communication.json \
  --out build/spatial_communication
```

Before connecting real project outputs, check `IMPLEMENTED_MODULES.json` for named inputs and `RESULT_CONTRACTS.json` for required fields.

接入真实项目结果前，请先在 `IMPLEMENTED_MODULES.json` 中确认输入名称，并在 `RESULT_CONTRACTS.json` 中确认字段约定。

The generated manifest is the authoritative record of rendered and skipped targets for that run.

每次运行生成的 manifest 是该次实际生成与跳过目标的权威记录。
