# Single-cell / Spatial Figures · 3.0

入口为 [SKILL.md](SKILL.md)。当前能力仅见 [CAPABILITIES.json](CAPABILITIES.json)，执行记录仅见 [QA_REPORT.md](QA_REPORT.md)。详细设计与验收见 [v3 playbook](references/v3_playbook.md)。

v3 聚焦“已审核数据 → 可控视觉映射 → 内容测量 → 导出/载体检查 → 人工签署”，不承诺自动科学推断或任意图形的全自动排版。Python 四种连接 renderer；R bridge 未运行验证。旧版函数保留供有明确需求的项目调用。

```bash
python -m pip install -r requirements-v3.txt
python scripts/render_v3.py render examples/v3_software_qa/figure.yaml --root examples/v3_software_qa --out build/software_qa
python scripts/render_v3.py --help
python -m pytest -q
```

安装命令应在隔离环境中执行，不覆盖既有分析环境。`requirements-v3.txt` 固定本次已验证环境中的核心包，不是所有历史论文或所有操作系统的锁文件。原生 R 使用已安装的 jsonlite 与 cairo/grid，运行前由使用者验证。

`build/` 不应混入真实研究源数据或未经审阅的发表结果。示例是人工软件数据、不是生物学证据。使用真实数据后填写文件来源和版本，重新运行检查。

目录：`scripts/` 为执行逻辑；`tests/` 为回归与失败场景；`examples/` 为可跑的软件测试项目；`assets/` 为保留的 v2 schema/templates；`references/` 为按需资料。v3 schema 由 `visual_contract.schema_v3()` 扩展原闭合 schema，未知配置字段仍会报错；不要把旧 `assets/*.render_plan.json` 当作新数据的结果。
