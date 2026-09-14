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

## Palette presets · v3.0.1（兼容扩充）

保留 `spec_version: '3.0'`。本次增加 52 个可选色卡家族，原有默认色和六种 norm 不变。使用前读 [色卡索引与调用规则](assets/palettes/README.md)。类别尺度可写 `preset: C19` 加固定 `order`；连续尺度可写 `preset: M02`，中心发散可用 `preset: D03` 加 `norm: {type: two_slope, center: 0}`。`preset` 不可与显式 colors/cmap 混用。C06 必须选具体变体；C21 是衍生试选，不标为论文原色。

`render_v3.py` 自动编译预设并保留 `palette_bindings.json`、原始配置及色卡依赖哈希。类别颜色不足时停止，不循环或插值；只筛选群组时重用已保存的命名颜色字典。R 的 `scripts/palette_presets.R` 读取同一 RGB8 表，但当前未运行原生 R 测试，不能扩张为跨后端等价验证。
