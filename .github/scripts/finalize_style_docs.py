"""Preserve full release documents from checksum-verified immutable repository files."""
from pathlib import Path
import base64
import hashlib
import json
import os
import re
import subprocess
from urllib.request import Request, urlopen
from urllib.parse import quote

ROOT = Path.cwd().resolve()
SKILL = ROOT / 'singlecell-spatial-figures'
GALLERY = SKILL / 'style_gallery'
TAG = 'STYLE_GALLERY_V3_2'
SKILL_BODY = '''## 图形样式执行规则 · v3.2

**所有绘图均不显示 subtitle。** 不将副标题搬成主标题下的另一行说明，也不保留副标题空白。主标题、坐标名称、单位、图例和必要的真实/合成标识必须保留。

先读 `style_gallery/examples/README.md` 选择 26 类之一，再读 `style_gallery/DESIGN_GUIDE.md`。同一个 `style_gallery/render.py` 的 minimal/advanced 入口已更新。原 FigureSpec schema 3.0、四类 renderer、52 个色卡家族保留。

高级版必须有输入支持的结构性新增：条件对照、共索引注释轨道、配对差值、多阶段质量、空间轮廓、给定区间或错误结构。只增加标签或边框不算高级。缺少数据列时不要伪造。图型和字段见 `style_gallery/catalogue_v32.json`；范例 CSV 只是合成测试，不得代替实验结果。

```bash
python style_gallery/render.py plot --kind heatmap --input reviewed.csv --config reviewed.json --mode advanced --out results/Fig1
python -m pytest style_gallery/tests -q
```

必须检查数值、共同分母、变换与不确定性；改画配对差值或行比例时同步改名。导出保存输入哈希与语义图层记录。最终 PDF/载体审核仍使用 `scripts/render_v3.py inspect-pdf` / `bind-report`。R 仅为共享 Python 引擎的 wrapper，未声明原生 R 等价。
'''
README_BODY = '''## v3.2 · 26 类无副标题图形

[最简 / 高级实图对照](singlecell-spatial-figures/style_gallery/examples/README.md) · [设计与来源](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [验证](singlecell-spatial-figures/style_gallery/QA_REPORT.md)

原入口升级为 26 类图；高级版补充数据支持的比较、分层、空间轮廓和质量结构。所有新范例无 subtitle。附 52 张常规范例、100 类别的两版图与完整色键；附带数据全部是合成测试。保留 v3 大版本、schema 3.0 和已有 52 色卡家族。

[远端测试记录](singlecell-spatial-figures/style_gallery/CI_REPORT.txt) · [发布校验报告](singlecell-spatial-figures/style_gallery/PUBLISH_REPORT.json)。原生 R 和真实生物学项目未在本轮验证。
'''
QA_BODY = '''# v3.2 当前样式检查

远端构建见 [style_gallery/CI_REPORT.txt](style_gallery/CI_REPORT.txt)，逐图和兼容性校验见 [style_gallery/PUBLISH_REPORT.json](style_gallery/PUBLISH_REPORT.json)。实施边界见 [style_gallery/QA_REPORT.md](style_gallery/QA_REPORT.md)。

下文的 v3.1 与 v3.0 报告为历史记录，不重复算作本轮测试；本轮不代表原生 R 或真实生物学项目已验证。
'''


def original_file(path):
    ref = os.environ['GITHUB_SHA']
    repo = os.environ['GITHUB_REPOSITORY']
    assert repo == 'Bio-JasperOA/CNS_FIGURE_SKILL' and re.fullmatch('[0-9a-f]{40}', ref)
    url = 'https://api.github.com/repos/' + repo + '/contents/' + quote(path, safe='/') + '?ref=' + ref
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'CNS-Figure-Skill-publication'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    with urlopen(Request(url, headers=headers), timeout=60) as response:
        obj = json.load(response)
    assert obj['type'] == 'file' and obj['encoding'] == 'base64'
    raw = base64.b64decode(obj['content'])
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert blob == obj['sha'] and len(raw) == obj['size'], 'Original byte mismatch: ' + path
    print('Verified API original:', path, 'bytes=', len(raw), 'blob=', blob, flush=True)
    return raw.decode('utf-8'), blob


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
    fetched = {p: original_file(p) for p in paths}
    originals = {p: pair[0] for p, pair in fetched.items()}
    original = originals[paths[1]]
    print('Original Skill headings:', re.findall(r'^## .*$', original, re.M), flush=True)
    assert len(original.encode('utf-8')) > 5000 and '## 1.' in original and '## 10.' in original
    catalogue = json.loads((GALLERY / 'catalogue_v32.json').read_text())
    assert len(catalogue) == 26 and len({r['kind'] for r in catalogue}) == 26
    base = strip_blocks(original)
    header = re.match(r'\A---\n.*?\n---(?:\n|$)', base, re.S)
    assert header
    result = base[:header.end()].rstrip() + '\n\n' + marked(SKILL_BODY) + '\n\n' + base[header.end():].lstrip()
    assert ' '.join(strip_blocks(result).split()) == ' '.join(strip_blocks(original).split())
    outputs = {
        paths[1]: normalize(result),
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
        subprocess.run(['/usr/bin/git', 'add', '--', rel], check=True)
        expected = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        staged = subprocess.check_output(['/usr/bin/git', 'ls-files', '-s', '--', rel], text=True).split()[1]
        assert staged == expected, 'Staged document mismatch: ' + rel
        hashes[rel] = hashlib.sha256(raw).hexdigest()
    final = (ROOT / paths[1]).read_text()
    assert final.startswith('---\nname: singlecell-spatial-figures\n')
    assert final.count('<!-- ' + TAG + ':START -->') == 1
    assert '所有绘图均不显示 subtitle' in final and '## 1.' in final and '## 10.' in final
    caps = json.loads((SKILL / 'CAPABILITIES.json').read_text())
    assert caps['version'] == '3.2.0' and len(caps['style_gallery']['kinds']) == 26
    report_path = GALLERY / 'PUBLISH_REPORT.json'
    report = json.loads(report_path.read_text())
    report['publication_documents'] = hashes
    report['original_document_git_blobs'] = {p: pair[1] for p, pair in fetched.items()}
    report['original_skill_body_preserved'] = True
    report['skill_document_bytes'] = len(final.encode('utf-8'))
    report['skill_document_lines'] = len(final.splitlines())
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print('Verified complete final Skill:', report['skill_document_bytes'], 'bytes;', report['skill_document_lines'], 'lines')


if __name__ == '__main__':
    finalize()
