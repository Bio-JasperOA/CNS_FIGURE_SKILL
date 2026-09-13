# R Figure Backend

## 总体执行规则

单图微调：最小数据校验 + 一个 renderer + 最终尺寸检查。整图任务：科学问题 → FigureSpec → reviewed tables → backend → QA。不要从默认绘图函数反推研究结论。

先读 [routing](routing.md)，只在实际需要时再读 [architecture](architecture.md)、[data contracts](data_contracts.md)、[design system](design_system.md) 和 [QA protocol](qa_protocol.md)。

FigureSpec 的 scales 是唯一颜色与尺度来源；所有比较量锁定定义、单位和范围。layout 是毫米级分区，不是图像缩放指令。不得在 renderer 中标准化、聚类、拟合、检验或挑选 ROI。上游结果必须可追溯。

证据来源保持分级：作者声明公开 / 可访问仓库 / 实际读过作图代码 / 实际重跑。没有新增核验时不升级证据等级。作者代码思想见 [recipes](complex_recipes_v1.md)，包的作者证据见 [packages](packages_v1.md)。

## R 具体路径

1. 快速模式直接使用 `scripts/figure_core.R` 与 `scripts/complex_recipes.R`。genes×cells 矩阵和 metadata 必须按唯一 ID 完全一致，Seurat 多 layer 明确选择或受控合并，不默默覆盖原对象。
2. 论文模式读取规划阶段产生的 render_plan.json。通用 schema/文件预检用随附 Python CLI 执行一次；R 渲染进程本身不启动 Python。不能把这个架构写成“两套完全独立的 schema 校验器”。
3. source `scripts/compose_plan.R`；为每个 renderer 注册显式 R 函数 `(ctx, table)`，返回 `figure_panel(object, system='ggplot'/'grob'/'heatmap')`。YAML 不携带待执行代码。
4. 从 `ctx$spec$scales` 读取 palette/limits；从 `ctx$width_mm/height_mm` 获取目标大小。ggplot 走 grid grob，ComplexHeatmap 在该目标尺寸捕获后绘制，避免默认设备大小导致注释偏移。
5. `export_plan()` 在实际尺寸设备上重新绘图，输出 PDF/SVG/PNG、source CSV、provenance、sessionInfo。R 后端尚无自动文字几何审核，必须目视检查。

## 接线示例

```r
source('PATH_TO_SINGLECELL_SPATIAL_FIGURES/scripts/figure_core.R')
source('PATH_TO_SINGLECELL_SPATIAL_FIGURES/scripts/complex_recipes.R')
source('PATH_TO_SINGLECELL_SPATIAL_FIGURES/scripts/compose_plan.R')
plan <- read_render_plan('build/render_plan.json')
# 'tables' is a named list of reviewed data frames keyed by data_id.
# Each function reads declared scales from ctx; no statistics are fitted here.
registry <- list(
  sample_effect = function(ctx, table) {
    p <- make_project_effect_plot(table, ctx$spec$scales)
    figure_panel(p, system='ggplot')
  }
)
export_plan(plan, tables, registry, 'build/Fig1')
```

`make_project_effect_plot` 是明确需要用户项目实现的构造函数，不是本包已有函数。每个 plan 中的 renderer 都必须注册；不声称运行任意 starter 就会自动画出完整论文图。

## 执行边界

原 v2 构建环境无 Rscript，R composer 与原子函数未做 R 运行/设备验证；见 [QA report](QA_REPORT_v2.md)。提供数值测试和新 composer smoke test，进入项目环境后先运行。Python 测试通过不能作为 R 通过依据。

纯 ggplot 也可以使用 patchwork design/area 代替通用 grid composer；两个路线只选一个做全局布局。共享 guides 之前确认 scale 的定义与 limits 相同。ComplexHeatmap 不直接与 patchwork `+` 混用。


## 合并包中的执行位置

本文中的 `scripts/`、`assets/`、`tests/` 均相对于整个 Skill 根目录。先读取根目录 `SKILL.md`；R 所需包见 `dependencies.R`。从根目录运行 `Rscript tests/test_core.R` 与 `Rscript tests/test_composer_smoke.R`；测试通过后仍须检查实际图形。最新执行边界见根目录 `QA_REPORT.md`。
