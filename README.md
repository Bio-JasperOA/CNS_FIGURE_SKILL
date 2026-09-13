# CNS Figure Skill

用于单细胞与空间转录组科研绘图的统一 Skill，包含 Python / R 实现、整图框架、模板、文献与源码审计，以及测试脚本。

## 使用入口

**从 [`singlecell-spatial-figures/SKILL.md`](singlecell-spatial-figures/SKILL.md) 开始。**

保留整个 `singlecell-spatial-figures/` 文件夹。主文件可单独作为执行规则；运行代码、使用模板或读取证据资料时，需要完整目录。

```text
singlecell-spatial-figures/
├── SKILL.md
├── README.md
├── QA_REPORT.md
├── MANIFEST.sha256
├── assets/       # FigureSpec、布局模板与示例规划
├── references/   # 文献、源码、数据契约、设计与质检规范
├── scripts/      # Python / R 绘图、组合与预检
└── tests/        # 测试脚本
```

给开发助手的任务示例：

> 读取 `singlecell-spatial-figures/SKILL.md`，按照其中的流程完成当前绘图任务。优先沿用项目已有数据与 Python/R 环境；单图使用快速模式，多 panel Figure 先规划证据结构与 FigureSpec。交付图、实际脚本、源数据与质检记录，不为作图修改分析结论。

## 资料与验证

- [完整使用说明](singlecell-spatial-figures/README.md)
- [文献与源代码审计](singlecell-spatial-figures/references/literature_audit_v1.md)
- [框架说明](singlecell-spatial-figures/references/architecture.md)
- [验证记录与限制](singlecell-spatial-figures/QA_REPORT.md)

包内记录的 Python 回归测试结果为 **76 passed**；R 版本尚未在记录所用环境中运行验证。历史测试结果不等于当前机器、全部可选依赖或真实生物学项目已经验证。

本仓库保留交付包的 44 个原始文件及其相对路径。它不是 Nature、Cell、Science 的官方标准，不分发字体、原论文全文、原作者模型权重或用户实验数据。公开可见不代表已授予特定开源许可证；仓库未另行指定许可证。
