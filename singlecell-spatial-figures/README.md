# 单细胞与空间转录组绘图 Skill · 统一入口

`SKILL.md` 是本包唯一入口，已合并前面的 Figure Director、Python、R 三套规则。主文件包含选图、证据组织、数据/尺度/布局、复杂图路由与交付要求；语言接口、源码证据和实现细节按需读取。

## 文件组成

```text
singlecell-spatial-figures/
├── SKILL.md                 # 唯一入口：共同流程 + Python/R 分支
├── references/              # 语言接口、文献、复杂图形、数据/设计/QA
├── scripts/                 # 继承 v2 的 Python 与 R 实现
├── assets/                  # 共用 schema、四类布局模板与示例规划
├── tests/                   # Python 回归测试与 R 测试脚本
├── QA_REPORT.md             # 本次整合的验证记录
└── MANIFEST.sha256          # 文件校验清单
```

## 使用

保留整个文件夹，让开发助手先读取 `SKILL.md`。只需要指令规范时，可单独使用主文件；运行配套脚本或读取引用资料时必须保留完整包。具体 agent 的安装位置按其当前环境确定；本次没有写入任何用户工具的安装目录。

示例任务提示：

> 请读取 singlecell-spatial-figures/SKILL.md，并按照此 Skill 处理我的单细胞/空间转录组绘图任务。先检查当前项目已有数据与分析结果；单图采用快速模式，多 panel 使用 FigureSpec。沿用项目的 Python/R 环境，统一身份颜色、连续尺度和物理尺寸。交付图、实际脚本、源数据与 QA，不为绘图重跑模型或补造统计结果。

复杂整图先编辑 `assets` 中最接近的模板，另存到实际项目；结构预检不等于真实数据审核，示例 render_plan 必须重新生成。Python 默认整图渲染器只有四类，其余要补本地 adapter；R 需要项目注册对应 renderer。

## 验证

从本包根目录执行：

```bash
python -m pytest tests -q
Rscript tests/test_core.R
Rscript tests/test_composer_smoke.R
```

这些命令是测试入口，不是全部已经运行的承诺；实际结果见 `QA_REPORT.md`。不要把历史测试环境当作所有可选依赖的统一锁文件。

## 来源和版本

本包依据本对话中已有的 v1 文献审计与 v2 Figure Framework 整理为一个入口，不新增外部检索。Python/R 实现、schema 与模板按原字节保留；文档入口重新归并。`references/QA_REPORT_v2.md` 是旧版记录，根目录 `QA_REPORT.md` 才是本次整合记录。

没有分发字体、原论文全文、原作者模型、用户实验数据或受限源数据。配套软件测试数据不作为生物学结果。
