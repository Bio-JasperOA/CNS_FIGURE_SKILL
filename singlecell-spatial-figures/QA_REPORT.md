# 统一入口 Skill：本次整理与验证

依据：本对话已有 v1 文献审计与 v2 Figure Framework；本轮没有新增论文检索或重跑原作者分析。

## 本次改动

合并 Director/Python/R 为一个 `SKILL.md`，两种语言说明改为按需读取的 reference。共用同一个 scripts、assets、tests 目录，保留此前实现与数据规范，不复制三套契约。

主文件包含快速/整图模式、输入约定、四类证据结构、六层架构、统一视觉规则、复杂图形路由、Python/R 执行分支、证据归因、质量闸门和交付要求。

## 实际运行

从合并包根目录运行：

```bash
python -m pytest tests -q --disable-warnings --junitxml=/mnt/data/_skill_consolidation_tests.xml
```

结果：**76 passed，11 warnings，0 failed，4.97 秒。** 使用人工软件测试输入，不代表真实生物学数据或原论文复现。测试日志另存 `references/consolidation_pytest.log`；警告未被计作失败，也未声称本次没有警告。

本轮运行环境：

```json
{
  "Python": "3.13.5",
  "numpy": "2.3.5",
  "pandas": "2.2.3",
  "scipy": "1.17.0",
  "matplotlib": "3.10.8",
  "pytest": "9.0.2",
  "PyYAML": "6.0.3",
  "jsonschema": "4.26.0"
}
```

**Rscript 当前不可用；本轮未运行 R 解析器、数值测试、composer 或 R 图形设备。** 不将 Python 测试结果视为 R 验证。

本轮不重新主张进行了人工看图、色觉模拟、真实空间配准检查或真实项目统计审阅；这些依然需要项目级检查。旧版目视检查仅见 `references/QA_REPORT_v2.md` 的历史记录。

## 包结构

检查项包括唯一 SKILL 入口、YAML frontmatter、Markdown 本地引用、YAML/JSON 解析、继承脚本与源包字节一致，以及压缩包完整性。实际结果另见 `references/package_validation.json`。它们是本地检查，不是任何平台的官方认证。

所有代码、配置均为既有 v2 版本；本次新写主入口、README、语言导航与整理报告。保留旧文件中的版本/历史执行说明，不据此提升本次验证范围。无用户生物学数据、字体或原论文全文随包分发。
