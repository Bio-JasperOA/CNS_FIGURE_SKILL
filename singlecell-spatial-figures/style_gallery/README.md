# Scientific Chart Style Gallery

**Reusable publication-oriented chart families for reviewed biological results.**  
**面向已审核生物学结果的可复用发表级图形库。**

Browse the examples in [`examples/README.md`](examples/README.md) or the offline gallery in [`examples/index.html`](examples/index.html). Design rules are documented in [`DESIGN_GUIDE.md`](DESIGN_GUIDE.md).

示例见 [`examples/README.md`](examples/README.md) 与离线图库 [`examples/index.html`](examples/index.html)，设计规范见 [`DESIGN_GUIDE.md`](DESIGN_GUIDE.md)。

## Rendering modes · 绘图模式

The gallery provides two user-facing modes:

图库提供两种公开绘图模式：

- `minimal` — the smallest scientifically complete view. / 最小但科学信息完整的视图。
- `advanced` — adds a real scientific dimension already present in the input, such as uncertainty, hierarchy, pairing, spatial context or model comparison. / 增加输入中真实存在的不确定性、层级、配对结构、空间背景或模型比较等科学维度。

`advanced` does not mean adding more decoration, borders or colors.

`advanced` 不等于增加装饰、边框或更多颜色。

## Visual policy · 视觉规范

The default rendering policy uses low-saturation editorial palettes on light backgrounds to reduce the visual appearance of software-default plots.

默认使用低饱和 editorial 色板和浅色背景，减少默认软件截图感。

Key rules / 核心规则：

- No subtitles. / 不使用 subtitle。
- Explanatory microcopy is kept off the plotting canvas. / 不在图形画布上堆叠说明性小字。
- Stable biological categories should reuse stable named colors. / 稳定生物学类别尽量复用固定命名颜色。
- Palette choice and normalization remain independent. / 色板选择与归一化保持独立。
- High-cardinality categories use restrained high-capacity palettes instead of cycling small palettes. / 高类别数场景使用高容量克制色板，不循环小色板。
- User-provided named colors are respected unless explicitly overridden. / 用户显式提供的命名颜色默认保留。

## Plot families · 图形类型

The gallery includes common single-cell, spatial and model-evaluation primitives such as embeddings, dot plots, heatmaps, composition plots, volcano plots, forest plots, spatial maps, networks, trajectories, enrichment plots, calibration plots and trajectory heatmaps.

图库覆盖 embedding、dotplot、heatmap、composition、volcano、forest、spatial、network、trajectory、enrichment、calibration、trajectory heatmap 等常用单细胞、空间与模型评估图形。

The authoritative list of supported kinds is stored in the machine-readable catalogue used by the renderer.

支持的图形类型以 renderer 使用的机器可读 catalogue 为准。

## Run · 运行

```bash
cd singlecell-spatial-figures/style_gallery
python -m pip install -r requirements-tested.txt
python -m pytest tests -q
```

Render one reviewed result / 绘制一个已审核结果：

```bash
python render.py plot \
  --kind heatmap \
  --input reviewed.csv \
  --config reviewed.json \
  --mode advanced \
  --out results/Fig1
```

Python interface / Python 接口：

```python
from render import render, export

fig = render("dotplot", reviewed_table, reviewed_config, mode="advanced")
export(fig, "results/Fig1")
```

## Input and provenance · 输入与来源记录

Real-data tasks should set `demo: false` and provide provenance, numerical meaning, category order and any shared scale that is scientifically required.

真实数据任务应设置 `demo: false`，并提供 provenance、数值含义、类别顺序以及科学上需要共享的尺度。

The renderer never creates missing statistical intervals, significance, segmentation boundaries, trajectories or model probabilities. Any derived display transformation must remain traceable to the supplied data.

Renderer 不会生成输入中不存在的统计区间、显著性、分割边界、轨迹或模型概率。任何显示层变换都必须能够追溯到已提供数据。

## Synthetic examples · 合成示例

Bundled example values and figures are synthetic software fixtures. They demonstrate interfaces and visual behavior only and must never be interpreted as biological findings.

随附示例数值和图形均为合成软件测试数据，只用于展示接口与视觉行为，不能解释为生物学发现。
