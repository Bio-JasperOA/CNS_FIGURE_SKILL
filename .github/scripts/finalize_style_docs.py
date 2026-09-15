"""Finalize entry documents from immutable Git blobs, not mutable test worktrees."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess

ROOT = Path.cwd().resolve()
SKILL = ROOT / 'singlecell-spatial-figures'
GALLERY = SKILL / 'style_gallery'
TAG = 'STYLE_GALLERY_V3_2'


def git_bytes(path):
    return subprocess.check_output(['git', 'show', 'HEAD:' + path])


def strip_blocks(text):
    for tag in ('STYLE_GALLERY_V3_1', TAG):
        text = re.sub(r'<!-- ' + tag + r':START -->.*?<!-- ' + tag + r':END -->\s*', '', text, flags=re.S)
    return text


def normalize(text):
    return '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n'


def finalize():
    updater = GALLERY / 'repository_update.py'
    tree = ast.parse(updater.read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'update')
    skill_blocks = [n.value.value for n in ast.walk(function)
                    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'body' for t in n.targets)
                    and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)]
    other_blocks = [n.args[1].value for n in ast.walk(function)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'block'
                    and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str)]
    assert len(skill_blocks) == 1 and len(other_blocks) == 2, 'Unexpected metadata source structure'
    originals = {p: git_bytes(p).decode('utf-8') for p in
                 ['README.md', 'singlecell-spatial-figures/SKILL.md', 'singlecell-spatial-figures/QA_REPORT.md']}
    skill_path = 'singlecell-spatial-figures/SKILL.md'
    original = originals[skill_path]
    assert len(original.encode('utf-8')) > 5000 and '## 1.' in original and '## 10.' in original
    print('Immutable Skill bytes:', len(original.encode('utf-8')))
    print('Pre-finalization working Skill:', repr((ROOT / skill_path).read_text()[:180]))

    def marked(body):
        return '<!-- ' + TAG + ':START -->\n' + body.strip() + '\n<!-- ' + TAG + ':END -->'

    base = strip_blocks(original)
    match = re.match(r'\A---\n.*?\n---(?:\n|$)', base, re.S)
    assert match, 'Missing original YAML frontmatter'
    result = base[:match.end()].rstrip() + '\n\n' + marked(skill_blocks[0]) + '\n\n' + base[match.end():].lstrip()
    assert ' '.join(strip_blocks(result).split()) == ' '.join(strip_blocks(original).split())
    readme_body = next(b for b in other_blocks if '26 类无副标题图形' in b)
    qa_body = next(b for b in other_blocks if '当前样式检查' in b)
    outputs = {
        skill_path: normalize(result),
        'README.md': normalize(strip_blocks(originals['README.md']).rstrip() + '\n\n' + marked(readme_body)),
        'singlecell-spatial-figures/QA_REPORT.md': normalize(marked(qa_body) + '\n\n' + strip_blocks(originals['singlecell-spatial-figures/QA_REPORT.md']).lstrip())
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
        staged = subprocess.check_output(['git', 'show', ':' + rel])
        assert staged == raw, 'Staged publication document differs: ' + rel
        hashes[rel] = hashlib.sha256(raw).hexdigest()
    final = (ROOT / skill_path).read_text()
    assert final.startswith('---\nname: singlecell-spatial-figures\n')
    assert final.count('<!-- ' + TAG + ':START -->') == 1
    assert '所有绘图均不显示 subtitle' in final
    assert '## 1.' in final and '## 10.' in final
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
