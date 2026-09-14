# Scientific Chart Style Gallery · v3.1.0

**[浏览最简版 / 高级版图例](examples/README.md)** · [操作手册](DESIGN_GUIDE.md) · [检验记录](QA_REPORT.md)

14类常用单细胞/空间图形，每类使用相同的源表生成最简版和高级版；另有100类别嵌入图压力示例。所有内置数值均为明确标注的合成样式测试数据，不是生物学结果或论文数值复现。原论文图只链接，不重新分发。

```bash
cd singlecell-spatial-figures/style_gallery
python -m pip install -r requirements.txt
python -m pytest tests -q
python render.py demo --out examples
```

打开 `examples/index.html` 可离线并排比较；GitHub上直接打开 `examples/README.md`。每图有PNG、PDF、SVG、源CSV和JSON配置。`examples/paired_gallery.pdf` 把每对图以原始物理尺寸放入一页，便于检查实际字号。

真实数据调用：

```bash
python render.py plot --kind dotplot --input reviewed_marker.csv \
  --config marker_config.json --mode advanced --out results/Fig1_markers
```

配置参考 `examples/source_data/dotplot.json`，把 `demo` 改为 `false`，明确填写 `provenance`、真实字段/顺序、共同范围和数值定义。默认路径不会合成数据，也不会执行模型训练、差异分析或检验。不要将示例CSV当实验数据。

最小编程接口：

```python
from render import render, export
fig = render('dotplot', reviewed_dataframe, reviewed_config, mode='advanced')
export(fig, 'results/Fig1_markers')
```

`categorical_preset: C19`和`continuous_preset: D03`可调用主仓库已有色卡API。独立下载包随附 C03/C19/M02/D03 的RGB8快照；其他ID需要完整Skill仓库。预设和显式 `colors` / `continuous_colors` 不可同时使用。类别映射必须按名称冻结，跨图共享。支持通过 `axes_box`（0–1画布比例）和 `width_mm` / `height_mm`调整图型空间；这不是原FigureSpec的全局自适应布局器。

R入口是共享Python后端：

```bash
Rscript render_from_R.R paired reviewed.csv config.json results/Fig2 advanced
```

本次没有运行Rscript，不宣称原生R绘图等价。现有 `scripts/render_v3.py`、四个FigureSpec渲染器、52个色卡家族和schema 3.0不受替换。本轮是v3范围内的增量功能，而不是v4。

## 论文对照与证据

`catalogue.py`逐图给出研究问题、最低必要编码、高级层次、论文DOI与具体panel、实际查看深度以及迁移边界。参考包括 BANKSY（Nature Genetics）、CellRank 2（Nature Methods）、spatialDLPFC（Science）、LIANA+（Nature Cell Biology）、moscot（Nature）、dynamo（Cell）和HNOCA（Nature）。部分对照来自实际图像，部分来自原论文图注及作者代码；没有把所有来源都称为逐图视觉复现。

高级版的增加信息不应改变科学含义：例如不把细胞当生物学重复，不把OT带称为运动路径，不把推断通信称为因果边，不把KDE密度当置信区间。
