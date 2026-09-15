# Scientific Chart Style Gallery · v3.2.0

**[26 类最简 / 高级范例](examples/README.md)** · [离线浏览](examples/index.html) · [设计与来源](DESIGN_GUIDE.md) · [验证范围](QA_REPORT.md)

本版在原来的 `style_gallery/render.py` 入口内更新，不需要再选择一条 v3.2 绘图路径。保留 v3 大版本、原 FigureSpec schema 3.0、原来的四个 FigureSpec renderer 与 52 个可选色卡家族。

## 三项改变

所有图取消 subtitle；旧配置中的 `subtitle` 字段会被忽略，不产生文字或保留空带。主标题可用 `title: ""` 关闭。单位、图例、不确定性定义和合成数据标识仍保留。

原有 14 类图不是仅加标签：空间图读取输入分割轮廓；条件 marker 对照、热图模块/条件/计数共索引；雨云按条件分层；组成图高级版改为逐样本比例矩阵；配对图展示全部差值；网络使用与权重一致的 chord 端点；流图支持多阶段质量守恒；基准图展示相对基线的逐数据集差值。

新增 12 类：forest、upset、ridge、ecdf、hexbin、roc、precision_recall、calibration、confusion、gsea、spatial_composition、trajectory_heatmap。每类都有两版和同一份源表。模式之间允许有已声明的统计显示变换，例如配对差值或混淆矩阵行比例；不改变原始数据，也不重新估计模型。

## 运行

```bash
cd singlecell-spatial-figures/style_gallery
python -m pip install -r requirements-tested.txt
python -m pytest tests -q
python render.py demo --out examples
```

独立真实数据任务：

```bash
python render.py plot --kind heatmap --input reviewed.csv \
  --config reviewed.json --mode advanced --out results/Fig1
```

参照 `examples/source_data/<kind>.json` 与 CSV。真实任务设 `demo: false` 并填写 `provenance`、数值含义、分类顺序和共同尺度。`advanced` 只能使用数据中真实存在的信息；它不代表自动获批或自动优于最简版。

`categorical_preset` / `continuous_preset` 沿用主 Skill 的 preset ID。独立包包含 C01、C03、C19、M02、D03 的 RGB8 快照；其他 ID 读取完整仓库 `scripts/palette_presets.py`。不得把 C19 的 100 色保证为人眼可辨 100 类；示例保留完整外部色键。

接口仍为：

```python
from render import render, export
fig = render('dotplot', reviewed_table, reviewed_config, mode='advanced')
export(fig, 'results/Fig1')
```

## 能力边界

这些是 26 类独立 Figure 的实际实现，并非 26 个已接入旧版多 panel FigureSpec 的 renderer。高级模块共用数据索引，图像/轮廓/区间必须由上游提供。原论文对照与新图型的软件参考分开记录，不宣称所有例子都是 CNS 原图复刻。

所有附带数值和图均为明确标注的合成测试范例。PDF/SVG保留文字，PNG用于预览。R入口只调用同一 Python 后端，本环境未运行R；未新增原生R的26类实现。
