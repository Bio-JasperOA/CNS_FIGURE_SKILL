# Python Figure Backend

## 总体执行规则

单图微调：最小数据校验 + 一个 renderer + 最终尺寸检查。整图任务：科学问题 → FigureSpec → reviewed tables → backend → QA。不要从默认绘图函数反推研究结论。

先读 [routing](routing.md)，只在实际需要时再读 [architecture](architecture.md)、[data contracts](data_contracts.md)、[design system](design_system.md) 和 [QA protocol](qa_protocol.md)。

FigureSpec 的 scales 是唯一颜色与尺度来源；所有比较量锁定定义、单位和范围。layout 是毫米级分区，不是图像缩放指令。不得在 renderer 中标准化、聚类、拟合、检验或挑选 ROI。上游结果必须可追溯。

证据来源保持分级：作者声明公开 / 可访问仓库 / 实际读过作图代码 / 实际重跑。没有新增核验时不升级证据等级。作者代码思想见 [recipes](complex_recipes_v1.md)，包的作者证据见 [packages](packages_v1.md)。

## Python 具体路径

1. 上游从 AnnData 明确提取 assay/layer、ID、坐标和元数据。`.X` 不默认等于 counts；只有必要的小矩阵可稠密化。exchange 输入采用显式 keys 的 CSV/TSV 或已核对 DataFrame。
2. `scripts/framework_contract.py` 先验证 [schema](../assets/figure_spec.schema.json)，并输出 preflight 和 render_plan。不要把未填完的 [starter](../assets/atlas.yaml) 当最终可运行项目。
3. 使用 `composer.load_tables()` 或传入已核对的 tables；`composer.compose(spec,tables,registry)` 根据毫米位置创建 panel。renderer 接收 `PanelContext, DataFrame`，返回 `PanelResult`，只能在 `ctx.add_axes()` 或 `BoundedFigure` 分配的区域绘图。
4. `scripts/native_renderers.py` 已登记 embedding、spatial、marker_dot、annotated_heatmap。其他路线仍需要项目 adapter：不得把 blueprint 名称误称为现成函数。
5. 多注释 heatmap 通过 BoundedFigure 将已有 GridSpec 配方绑定到本 panel；共享 row/col order。复杂子图应返回 mappables，以便审核连续色标。
6. `composer.write_bundle()` 输出固定画布和 source/provenance；其状态始终是 draft/review pending。检查完整导出，不用 tight 裁切改变画布尺寸。

## 最小项目入口

```python
from framework_contract import read_spec
from composer import load_tables, compose, write_bundle
from native_renderers import REGISTRY
spec = read_spec('figure_spec.yaml')
tables = load_tables(spec, root='.')
registry = dict(REGISTRY)
# Register explicit local functions for any additional renderer names.
figure = compose(spec, tables, registry)
write_bundle(figure, 'build/Fig1')
```

在运行入口配置本包根目录下的 scripts 到 Python 导入路径，或使用项目自己的 package 化方式；不要猜測 agent 的安装路径。上述入口只有在数据真实存在、spec 已填写、全部 renderer 已注册后才可执行。

## 整图命令入口

当 spec 只使用四个已注册 renderer 时，执行：

```bash
python scripts/render_project.py figure_spec.yaml --root . --out build/Fig1
```

该入口保存实际输入文件的 SHA256、preflight 与 render_plan，再输出图和 QA。需要其他图型时使用 `render_project(..., registry=your_registry)` 传入可信的本地函数，不从 YAML 执行代码。

## 测试和边界

`python -m pytest tests -q`。新层测试与继承 v1 核心一起运行。`requirements-planner.txt` 是规划器依赖，既有 `requirements-tested.txt` 记录 v1 核心环境，不声称覆盖全部可选包。实际本轮结果见 [QA report](QA_REPORT_v2.md)。

自动检查不包括完整文字碰撞、色觉模拟、统计模型正确性和生物学结论。不得自动批准 publication。字体缺失报告真实 fallback，不分发字体文件。


## 合并包中的执行位置

本文中的 `scripts/`、`assets/`、`tests/` 均相对于整个 Skill 根目录，不是本 references 目录。先读取根目录 `SKILL.md`。本次整理没有修改 v2 Python 函数实现；最新的本地回归检查见根目录 `QA_REPORT.md`。
