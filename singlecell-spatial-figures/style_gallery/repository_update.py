"""Idempotent v3.2 additive metadata. Keeps parent palettes and FigureSpec intact."""
from pathlib import Path
import argparse, hashlib, json, re, sys
HERE=Path(__file__).resolve().parent; SKILL=HERE.parent; REPO=SKILL.parent
TAG='STYLE_GALLERY_V3_2'

def block(text,body,at_top=False):
    for old in ['STYLE_GALLERY_V3_1',TAG]:
        text=re.sub(r'<!-- '+old+r':START -->.*?<!-- '+old+r':END -->\s*','',text,flags=re.S)
    b='<!-- '+TAG+':START -->\n'+body.strip()+'\n<!-- '+TAG+':END -->\n'
    return b+'\n'+text.lstrip() if at_top else text.rstrip()+'\n\n'+b

def update():
    rows=json.loads((HERE/'catalogue_v32.json').read_text(encoding='utf-8'))
    p=SKILL/'CAPABILITIES.json';c=json.loads(p.read_text(encoding='utf-8'))
    if str(c['version']).split('.')[0]!='3':raise ValueError('Major version must remain 3')
    if tuple(int(v) for v in c['version'].split('.'))<(3,2,0):c['version']='3.2.0'
    c['style_gallery']={'version':'3.2.0','path':'style_gallery/README.md','kinds':[r['kind'] for r in rows],
      'implementation':'style_gallery/render.py','modules':['style_gallery/chart_core.py','style_gallery/chart_types.py'],
      'test':'style_gallery/tests/test_gallery.py','catalogue':'style_gallery/catalogue_v32.json',
      'gallery':'style_gallery/examples/README.md','examples':'26 paired families + two 100-category stress figures; synthetic only',
      'subtitle_policy':'Never rendered, including legacy subtitle keys',
      'status':'implemented and locally tested; remote CI not claimed by this metadata',
      'R':'Python wrapper only; not executed in authoring environment',
      'limits':['The original four FigureSpec renderers and schema 3.0 remain unchanged',
                'Not original-paper numerical reproduction','No universal label/perception/scientific audit']}
    p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    p=SKILL/'SKILL.md';text=p.read_text(encoding='utf-8')
    body="""## 图形样式执行规则 · v3.2

**所有绘图均不显示 subtitle。** 不将副标题搬成主标题下的另一行说明，也不保留副标题空白。主标题、坐标名称、单位、图例和必要的真实/合成标识是不同概念，不得为删副标题而删掉数值语义。

先读 `style_gallery/examples/README.md` 选择 26 类之一，再读 `style_gallery/DESIGN_GUIDE.md`。同一个 `style_gallery/render.py` 的 minimal/advanced 入口已更新，不另建平行绘图路线。原 FigureSpec schema 3.0、四类 renderer、52 个色卡家族保留。

高级版必须有输入支持的结构性新增：真实条件对照、共索引注释轨道、配对差值、多阶段质量、空间轮廓、给定区间或错误结构。只增加标签/边框不算高级。缺少数据列时不要伪造，必要时退回最简版并解释缺口。图型与对应数据字段见 `style_gallery/catalogue_v32.json`；范例 CSV 只是合成测试，不得代替实验结果。

```bash
python style_gallery/render.py plot --kind heatmap --input reviewed.csv --config reviewed.json --mode advanced --out results/Fig1
python -m pytest style_gallery/tests -q
```

必须检查数值、共同分母、变换与不确定性；高级版如改画配对差值/行比例，轴与图例必须同步改名。每次导出保存输入哈希与语义图层记录。旧版最终 PDF/载体审核仍使用 `scripts/render_v3.py inspect-pdf` / `bind-report`，不把新增 Canvas 检查称为全自动科学审阅。R 仅为共享 Python 引擎的 wrapper，未声明原生 R 等价。
"""
    text=block(text,body)
    # Move the current rules just after the YAML header, ahead of historical instructions.
    m=re.search(r'<!-- '+TAG+r':START -->.*?<!-- '+TAG+r':END -->',text,re.S)
    current=m.group(0);text=text[:m.start()]+text[m.end():]
    if text.startswith('---\n'):
        end=text.find('\n---',4)+4;text=text[:end]+'\n\n'+current+'\n\n'+text[end:].lstrip('\n')
    else:text=current+'\n\n'+text
    p.write_text(text.rstrip()+'\n',encoding='utf-8')
    p=REPO/'README.md';p.write_text(block(p.read_text(encoding='utf-8'),"""## v3.2 · 26 类无副标题图形

[最简 / 高级实图对照](singlecell-spatial-figures/style_gallery/examples/README.md) · [设计与来源](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [验证](singlecell-spatial-figures/style_gallery/QA_REPORT.md)

原入口升级为 26 类图；高级版补充数据支持的比较、分层、空间轮廓和质量结构，不只是额外标签。所有图无 subtitle。附 52 张常规范例、100 类别的两版图与完整色键；附带数据全部是合成测试。保留 v3 大版本、schema 3.0 和已有 52 色卡家族。本地更新不等于 GitHub 已推送；远端状态另查提交。
"""),encoding='utf-8')
    p=SKILL/'QA_REPORT.md';p.write_text(block(p.read_text(encoding='utf-8'),"""# v3.2 当前样式检查

本轮实际运行范围见 [style_gallery/QA_REPORT.md](style_gallery/QA_REPORT.md)。此前 v3.1 与 v3.0 的报告为历史记录，不能算本轮 CI。下面保留原流水线的历史验证，不以本轮样式测试替代原生 R 或真实数据检验。
""",True),encoding='utf-8')

def presets():
    sys.path.insert(0,str(SKILL/'scripts'))
    from palette_presets import palette_colors
    for pid,item in json.loads((HERE/'palette_snapshots_v32.json').read_text()).items():
        expected=[x.upper() for x in palette_colors(pid)]
        if expected!=item['colors']:raise ValueError('Preset snapshot mismatch: '+pid)
    print('Five RGB8 snapshots match the installed palette library; library not modified')

def manifest():
    rows=[];skip={'__pycache__','.pytest_cache','.git','.venv'}
    for p in sorted(SKILL.rglob('*')):
        if p.is_file() and p.name!='MANIFEST.sha256' and not(skip&set(p.relative_to(SKILL).parts)):
            rows.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(SKILL).as_posix())
    (SKILL/'MANIFEST.sha256').write_text('\n'.join(rows)+'\n',encoding='utf-8')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('command',choices=['metadata','presets','manifest']);x=a.parse_args()
    {'metadata':update,'presets':presets,'manifest':manifest}[x.command]()
