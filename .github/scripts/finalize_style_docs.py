"""Assemble release documents from immutable Git originals and explicit release text."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path.cwd().resolve()
SKILL = ROOT / 'singlecell-spatial-figures'
GALLERY = SKILL / 'style_gallery'
TAG = 'STYLE_GALLERY_V3_2'

SKILL_BODY = '''## 图形样式执行规则 · v3.2

**所有绘图均不显示 subtitle。** 不将副标题搬成主标题下的另一行说明，也不保留副标题空白。主标题、坐标名称、单位、图例和必要的真实/合成标识是不同概念，不得为删副标题而删掉数值语义。

先读 `style_gallery/examples/README.md` 选择 26 类之一，再读 `style_gallery/DESIGN_GUIDE.md`。同一个 `style_gallery/render.py` 的 minimal/advanced 入口已更新，不另建平行绘图路线。原 FigureSpec schema 3.0、四类 renderer、52 个色卡家族保留。

高级版必须有输入支持的结构性新增：真实条件对照、共索引注释轨道、配对差值、多阶段质量、空间轮廓、给定区间或错误结构。只增加标签/边框不算高级。缺少数据列时不要伪造，必要时退回最简版并解释缺口。图型与对应数据字段见 `style_gallery/catalogue_v32.json`；范例 CSV 只是合成测试，不得代替实验结果。

```bash
python style_gallery/render.py plot --kind heatmap --input reviewed.csv --config reviewed.json --mode advanced --out results/Fig1
python -m pytest style_gallery/tests -q
```

必须检查数值、共同分母、变换与不确定性；高级版如改画配对差值/行比例，轴与图例必须同步改名。每次导出保存输入哈希与语义图层记录。旧版最终 PDF/载体审核仍使用 `scripts/render_v3.py inspect-pdf` / `bind-report`，不把新增 Canvas 检查称为全自动科学审阅。R 仅为共享 Python 引擎的 wrapper，未声明原生 R 等价。
'''
README_BODY = '''## v3.2 · 26 类无副标题图形

[最简 / 高级实图对照](singlecell-spatial-figures/style_gallery/examples/README.md) · [设计与来源](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [验证](singlecell-spatial-figures/style_gallery/QA_REPORT.md)

原入口升级为 26 类图；高级版补充数据支持的比较、分层、空间轮廓和质量结构，不只是额外标签。所有新范例无 subtitle。附 52 张常规范例、100 类别的两版图与完整色键；附带数据全部是合成测试。保留 v3 大版本、schema 3.0 和已有 52 色卡家族。

[远端测试记录](singlecell-spatial-figures/style_gallery/CI_REPORT.txt) · [发布校验报告](singlecell-spatial-figures/style_gallery/PUBLISH_REPORT.json)。记录明确区分合成范例、实际运行的检查和未验证的原生 R/生物学项目。
'''
QA_BODY = '''# v3.2 当前样式检查

当前远端构建记录见 [style_gallery/CI_REPORT.txt](style_gallery/CI_REPORT.txt)，逐图、来源及兼容性校验见 [style_gallery/PUBLISH_REPORT.json](style_gallery/PUBLISH_REPORT.json)。范例、输入和代码的实施边界见 [style_gallery/QA_REPORT.md](style_gallery/QA_REPORT.md)。

此前 v3.1 与 v3.0 的报告为历史记录，不能重复算为本轮测试；本轮检查不代表原生 R 后端或真实生物学项目已验证。下面保留原流水线的历史说明。
'''


def strip_blocks(text):
    for tag in ('STYLE_GALLERY_V3_1', TAG):
        text = re.sub(r'<!-- ' + tag + r':START -->.*?<!-- ' + tag + r':END -->\s*', '', text, flags=re.S)
    return text


def normalize(text):
    return '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n'


def marked(body):
    return '<!-- ' + TAG + ':START -->\n' + body.strip() + '\n<!-- ' + TAG + ':END -->'


def finalize():
    paths = ['README.md', 'singlecell-spatial-figures/SKILL.md', 'singlecell-spatial-figures/QA_REPORT.md']
    originals = {p: subprocess.check_output(['git', 'show', 'HEAD:' + p]).decode('utf-8') for p in paths}
    skill_path = paths[1]
    original = originals[skill_path]
    assert len(original.encode('utf-8')) > 5000 and '## 1.' in original and '## 10.' in original, 'Incomplete immutable Skill'
    print('Original Git Skill:', len(original.encode('utf-8')), 'bytes')
    print('Working Skill before finalization:', len((ROOT / skill_path).read_bytes()), 'bytes')
    updater = GALLERY / 'repository_update.py'
    print('Metadata source:', len(updater.read_bytes()), hashlib.sha256(updater.read_bytes()).hexdigest())
    catalogue = json.loads((GALLERY / 'catalogue_v32.json').read_text())
    assert len(catalogue) == 26 and len({r['kind'] for r in catalogue}) == 26
    base = strip_blocks(original)
    header = re.match(r'\A---\n.*?\n---(?:\n|$)', base, re.S)
    assert header, 'Missing original YAML frontmatter'
    result = base[:header.end()].rstrip() + '\n\n' + marked(SKILL_BODY) + '\n\n' + base[header.end():].lstrip()
    assert ' '.join(strip_blocks(result).split()) == ' '.join(strip_blocks(original).split()), 'Original Skill body changed'
    outputs = {
        skill_path: normalize(result),
        paths[0]: normalize(strip_blocks(originals[paths[0]]).rstrip() + '\n\n' + marked(README_BODY)),
        paths[2]: normalize(marked(QA_BODY) + '\n\n' + strip_blocks(originals[paths[2]]).lstrip())
    }
    hashes = {}
    for rel, text in outputs.items():
        raw = text.encode('utf-8')
        assert all(line == line.rstrip() for line in text.splitlines())
        target = ROOT / rel
        tmp = target.with_name(target.name + '.publish-tmp')
        tmp.write_bytes(raw)
        tmp.replace(target)
        assert target.read_bytes() == raw
        subprocess.run(['git', 'add', '--', rel], check=True)
        assert subprocess.check_output(['git', 'show', ':' + rel]) == raw, 'Staged bytes differ: ' + rel
        hashes[rel] = hashlib.sha256(raw).hexdigest()
    final = (ROOT / skill_path).read_text()
    assert final.startswith('---\nname: singlecell-spatial-figures\n')
    assert final.count('<!-- ' + TAG + ':START -->') == 1
    assert '所有绘图均不显示 subtitle' in final and '## 1.' in final and '## 10.' in final
    assert len(final.encode('utf-8')) > 5000
    caps = json.loads((SKILL / 'CAPABILITIES.json').read_text())
    assert caps['version'] == '3.2.0' and len(caps['style_gallery']['kinds']) == 26
    report_path = GALLERY / 'PUBLISH_REPORT.json'
    report = json.loads(report_path.read_text())
    report['publication_documents'] = hashes
    report['original_skill_body_preserved'] = True
    report['skill_document_bytes'] = len(final.encode('utf-8'))
    report['skill_document_lines'] = len(final.splitlines())
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print('Verified final and staged Skill:', report['skill_document_bytes'], 'bytes;', report['skill_document_lines'], 'lines')


if __name__ == '__main__':
    finalize()
