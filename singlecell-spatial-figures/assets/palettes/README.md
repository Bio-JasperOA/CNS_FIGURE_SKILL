# Palette presets · v3.0.1

本次为 v3 的向后兼容预设扩充；`spec_version: '3.0'` 和原有六种归一化机制不变。原有 cmap 和显式颜色字典照常使用，不自动替换项目配色。

## 范围与来源

共 **52 个色卡家族**：21 个类别家族、6 个单色系顺序、12 个多色系顺序、8 个发散、5 个循环。C06 包含四个独立的三色变体，因此共 55 个可调用 ID，但不重复计为 55 个家族。

证据等级保持原审计：R 研究/复现代码 12 项，P 作者实现 28 项，E 示例 2 项，S 补充参考 9 项，D 衍生试选 1 项。C21 不是顶刊作者原色。所有候选均作为可选预设发布，不表示已经通过每个真实数据场景的视觉审阅。

[色卡预览](preview.svg) · [完整数据与来源索引](index.json)。预览选取 12 个示例（不是重新指定默认配色）：高容量类别卡只展示前 20 色；渐变条展示 9 个锚点，实际使用完整 LUT。完整 52 家族色卡可用 `python scripts/preview_palettes.py build/all_palettes.svg --all` 生成；先创建 build 目录。

## 数据表示与复现

颜色按 ID 保存为 RGB8 表。类别表为可直接阅读的六位十六进制字符串，连续表使用文末定义的无损压缩。Python/R 接口解码为同一套 `#RRGGBB`。类别颜色和顺序与两次审核包完全一致；连续色阶由审核包的原始 RGBA LUT 用 `matplotlib.colors.to_hex` 转为 8-bit sRGB，保存完整采样表及白色前缀。这里保证审核图 HEX 一致，不冒称原始 float64 LUT 逐字节不变。原审核目录文件的 SHA256 保留在索引中，可追溯完整浮点表与详细提取记录。端点使用浮点归一化坐标读取，不使用容易混淆的整数 `cmap(1)`。

运行时不联网，不依赖 Seaborn/Plotly/Colorcet 的安装版本。R helper 需要 jsonlite；其原生设备和数值执行未在当前环境验证。Python 对每份 RGB8 表检查 SHA256；R helper 做结构/唯一性检查，不独立计算 SHA256。

## Python / v3 YAML 调用

```yaml
spec_version: '3.0'
# 其余 figure、datasets、panels 等沿用现有 v3 定义。
scales:
  cell_type:
    kind: categorical
    preset: C19
    order: [T_cell, B_cell, Myeloid]
    label: Cell type
  expression:
    kind: continuous
    preset: M02
    limits: [0, 5]
    label: Reviewed expression
    norm: {type: linear}
  effect:
    kind: continuous
    preset: D03
    limits: [-2, 5]
    label: Reviewed effect
    norm: {type: two_slope, center: 0}
```

`preset + order` 与显式 `colors` 二选一；连续量 `preset` 与 `cmap` 二选一。`render_v3.py` 在现有校验前解析，输出仍为普通 v3 配置。直接调用 `validate_visual_spec` 时先调用 `resolve_presets`。

```bash
# 从 Skill 目录执行；该示例只含人工软件测试数据。
python scripts/render_v3.py render examples/palette_presets.yaml --root examples --out build/presets
python scripts/palette_presets.py C19 --n 50
python scripts/palette_presets.py C01 --levels T_cell B_cell Myeloid Stromal
```

```python
from palette_presets import categorical_map, palette_colormap
colors = categorical_map("C19", ["T_cell", "B_cell", "Myeloid"])
colors = categorical_map("C19", ["B_cell", "Fibroblast"], existing=colors)
cmap = palette_colormap("M02")
```

类别使用完整参考顺序，筛选子集时保留原映射；不要根据本次观察到的类别重新建立颜色字典。辅助函数允许保存旧映射并追加新类别，不重新着色旧类别，也不因为某类别暂未出现而回收颜色。容量不足报错，不循环、不插值。C19/C20/C21 为 100 色，C18 为 102 色；数量只说明唯一 RGB 数，不保证 100 类都能靠颜色识别。

## R 调用

```r
source("scripts/palette_presets.R")
cols <- cns_color_map("C19", c("T_cell", "B_cell", "Myeloid"))
cols <- cns_color_map("C19", c("B_cell", "Fibroblast"), existing = cols)
# 示例：Seurat::DimPlot(object, cols = cols)
continuous_lut <- cns_palette("M02")
```

R bridge 仍使用 Python render_plan 中已经映射的 RGB8 颜色。原生 R helper 是按名称读取同一数据表的便利接口，不是新的独立布局或质量审核引擎。

## 归一化、循环与特殊家族

六种机制 `linear / two_slope / log / symlog / power / boundary` 与色卡分开选择。类别只做身份映射。循环 Y01–Y05 使用完整周期的显式 limits；不自动对相位取模、不新增第七种归一化，也不把周期值当线性距离。循环卡跳过顺序型单调明度假设，但仍需人工检查接缝、CVD 和实际含义。

C06 必须写 `C06.green`、`C06.orange`、`C06.purple` 或 `C06.blue`，不能默认把四组拼成 12 类身份卡。C02 保留原 11 个条目；与其原细胞标签的对应可见索引，移用到新项目时由自己的固定参考顺序明确重映射。

## 追踪、验收与兼容

输出增加 `palette_bindings.json`（ID、来源、证据、容量、校验值）和 `figure_spec.input.json`（原始配置）。原始输入、解析后的配置和所用色卡文件加入 snapshot；改变色卡数据会使旧审阅过期。不得仅因预设来自某论文就自动通过可辨认性审核。

## 全部预设

| ID | 名称 | 家族 | 容量/采样数 | 证据 |
|---|---|---|---:|---|
| C01 | Coral / cyan / jade / navy | categorical | 4 | R |
| C02 | Organoid identities / all 11 entries | categorical | 11 | R |
| C03 | Tableau medium / 10 colors | categorical | 10 | E |
| C04 | Set2 / soft categorical | categorical | 8 | P |
| C05 | Warm gold / mint | categorical | 2 | R |
| C06 | Neutral + comparison family | categorical | 4 × 3 | R |
| C07 | Pharyngeal identity set | categorical | 5 | R |
| C08 | Colorblind / full library base | categorical | 10 | R |
| C09 | Zebrafish / 12 anchors | categorical | 12 | P |
| C10 | Paired / exact five-color subset | categorical | 5 | R |
| S01 | Blues | sequential_single | 256 | P |
| S02 | Greens | sequential_single | 256 | P |
| S03 | Purples | sequential_single | 256 | P |
| S04 | Oranges | sequential_single | 256 | P |
| S05 | Reds | sequential_single | 256 | P |
| S06 | Greys | sequential_single | 256 | P |
| M01 | Viridis | sequential_multi | 256 | R |
| M02 | Mako | sequential_multi | 256 | P |
| M03 | Magma reversed | sequential_multi | 256 | P |
| M04 | Plasma | sequential_multi | 256 | R |
| M05 | Cividis | sequential_multi | 256 | R |
| M06 | Inferno | sequential_multi | 256 | P |
| M07 | White + YlOrRd (50) | sequential_multi | 51 | P |
| M08 | White + BuGn (50) | sequential_multi | 51 | E |
| M09 | Indigo / plum / amber | sequential_multi | 256 | P |
| M10 | BuPu | sequential_multi | 256 | P |
| M11 | PuBuGn | sequential_multi | 256 | P |
| M12 | RdPu | sequential_multi | 256 | P |
| D01 | PRGn / 7-anchor recipe | diverging | 201 | R |
| D02 | RdBu reversed | diverging | 256 | P |
| D03 | Vlag / muted blue / rose | diverging | 256 | P |
| D04 | Coolwarm | diverging | 256 | R |
| D05 | Tealrose | diverging | 256 | S |
| D06 | Tropic | diverging | 256 | S |
| D07 | Armyrose | diverging | 256 | S |
| D08 | Icefire / dark midpoint | diverging | 256 | S |
| Y01 | Twilight | cyclic | 510 | S |
| Y02 | Phase | cyclic | 256 | S |
| Y03 | mrybm | cyclic | 256 | S |
| Y04 | mygbm | cyclic | 256 | S |
| Y05 | Edge | cyclic | 256 | S |
| C11 | Scanpy / Vega 20 | categorical | 20 | P |
| C12 | Zeileis 28 | categorical | 28 | P |
| C13 | Stereo 30 | categorical | 30 | P |
| C14 | Alphabet 26 | categorical | 26 | P |
| C15 | Glasbey 32 (Seurat) | categorical | 32 | P |
| C16 | Polychrome 36 | categorical | 36 | P |
| C17 | Parade 78 | categorical | 78 | P |
| C18 | Godsnot 102 | categorical | 102 | P |
| C19 | Glasbey dark / first 100 | categorical | 100 | P |
| C20 | Glasbey no-gray / first 100 | categorical | 100 | P |
| C21 | Restrained 100 / derived trial | categorical | 100 | D |

## 来源归属

上游来源、commit、路径、表达式与证据限制保存在 sources.json 中；不将当前包默认值或示例误称为最终论文用色。原作者源代码、字体、模型或真实生物学数据均未随本次预设扩充引入。第三方颜色定义保留上游归属，见 [THIRD_PARTY.md](THIRD_PARTY.md)。

### Lossless scalar storage

Scalar tables use `gz-delta8:` followed by Base64-encoded GZIP bytes. The first RGB triple is literal; later triples store per-channel differences modulo 256. Decode cumulatively by channel, modulo 256. This is lossless byte compression, not color interpolation or quantization. All table checksums bind the decoded uppercase RGB8 HEX string, without `#` or separators. Python uses the standard library; R uses `jsonlite::base64_dec` and base `memDecompress`. Category tables remain directly readable HEX.
