"""Idempotent metadata updates for the additive v3.1 gallery; preserves legacy fields."""
from pathlib import Path
import argparse, hashlib, json, sys
HERE=Path(__file__).resolve().parent
SKILL=HERE.parent
REPO=SKILL.parent
TAG='STYLE_GALLERY_V3_1'

def block(text,body,at_top=False):
    start=f'<!-- {TAG}:START -->';end=f'<!-- {TAG}:END -->'
    if start in text:
        a=text.index(start);b=text.index(end,a)+len(end)
        text=text[:a]+text[b:]
    new=f'{start}\n{body.strip()}\n{end}\n'
    return new+'\n'+text.lstrip() if at_top else text.rstrip()+'\n\n'+new

def update():
    from catalogue import CATALOG
    p=SKILL/'CAPABILITIES.json';c=json.loads(p.read_text())
    if c['version'].split('.')[0]!='3':raise ValueError('This updater never changes a major version')
    if tuple(map(int,c['version'].split('.'))) < (3,1,0):c['version']='3.1.0'
    c['style_gallery']={'version':'3.1.0','path':'style_gallery/README.md','kinds':[x['kind'] for x in CATALOG],
      'implementation':'style_gallery/render.py','test':'style_gallery/tests/test_gallery.py',
      'catalogue':'style_gallery/catalogue.py','gallery':'style_gallery/examples/README.md',
      'status':'standalone_table_driven_python_renderers','examples':'14 minimal/advanced pairs + 100-category stress pair; all synthetic',
      'R':'shared Python entry point only; native R not tested',
      'limits':['Not additional FigureSpec registrations; existing four remain unchanged',
                'Not original-paper numerical reproduction','Canvas text bounds are not a full perception or collision audit']}
    p.write_text(json.dumps(c,indent=2,ensure_ascii=False)+'\n')
    p=SKILL/'SKILL.md';p.write_text(block(p.read_text(),'''## 图形样式库 · v3.1（不更改大版本 / schema）

先按图型阅读 [最简版与高级版实例](style_gallery/examples/README.md) 和 [设计操作手册](style_gallery/DESIGN_GUIDE.md)，再编写项目图。不要先执行默认绘图函数、最后仅修改字体。此路线新增14类表格驱动的独立Figure；原有FigureSpec四类与schema 3.0保持不变。

从 `style_gallery/catalogue.py` 选择对应问题、最低必要编码、高级信息层和失败条件。优先复用现有命名色卡；类别颜色在嵌入、组成、通信图中必须一致。高级版增加真实输入支持的模块/计数、分布、配对、方向或不确定性，不增加装饰性复杂度。内置CSV和图全部是合成样式fixture，不是研究结果，不能用于填补缺少的实验数据。

```bash
python style_gallery/render.py plot --kind dotplot --input reviewed.csv --config reviewed.json --mode advanced --out results/Fig1
python -m pytest style_gallery/tests -q
```

配置结构参照对应 `style_gallery/examples/source_data/*.json`；真实任务设置 `demo: false`并给出`provenance`、值的定义与固定尺度。先保留最简必要编码，再使用高级层次；与论文对照时区分实际看图、读图注和读源码，禁止称为逐图复现。100类别嵌入示例使用C19、重点编号及独立完整色键，不保证100色可由人眼完全区分。

`style_gallery/render_from_R.R`调用同一Python渲染器，不是14套原生R后端。需要旧版最终PDF与载体审核时继续用 `scripts/render_v3.py inspect-pdf` / `bind-report`；新的Canvas边界检查不替代正式人工审核。'''))
    p=REPO/'README.md';p.write_text(block(p.read_text(),'''## v3.1 · 图形样式与实例

**[浏览14类最简版 / 高级版](singlecell-spatial-figures/style_gallery/examples/README.md)** · [设计手册](singlecell-spatial-figures/style_gallery/DESIGN_GUIDE.md) · [运行代码](singlecell-spatial-figures/style_gallery/README.md) · [新增测试记录](singlecell-spatial-figures/style_gallery/QA_REPORT.md)

每类含同一输入的两版图、PNG/PDF/SVG、源表和配置，以及CNS及子刊论文具体panel的设计对照。另有100类别嵌入图与完整色键。所有实例均为合成样式测试，不是生物学结果或论文数值复现。保留v3大版本、schema 3.0及52个色卡家族；不覆盖现有分析流程。'''))
    p=SKILL/'QA_REPORT.md';p.write_text(block(p.read_text(),'''# v3.1 样式模块增量验证

最新样式模块的实际记录见 [style_gallery/QA_REPORT.md](style_gallery/QA_REPORT.md)，服务器构建结果见 [style_gallery/CI_REPORT.txt](style_gallery/CI_REPORT.txt)。本地新增样式测试87项通过；不要把历史213项重复计为本轮运行结果。下文保留既有v3/v3.0.1审核记录。R入口不声称原生后端已验证。''',at_top=True))

def presets():
    sys.path.insert(0,str(SKILL/'scripts'))
    from palette_presets import palette_colors
    d=json.loads((HERE/'palettes.json').read_text())
    for pid,p in d.items():
        assert [x.upper() for x in palette_colors(pid)]==p['colors'],pid
    print('Verified 4 exact RGB8 snapshots against v3.0.1 published presets')

def manifest():
    excluded={'__pycache__','.pytest_cache','.git','.venv'}
    rows=[]
    for p in sorted(SKILL.rglob('*')):
        if p.is_file() and p.name!='MANIFEST.sha256' and not (excluded&set(p.relative_to(SKILL).parts)):
            rows.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(SKILL).as_posix())
    (SKILL/'MANIFEST.sha256').write_text('\n'.join(rows)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['metadata','presets','manifest']);a=p.parse_args()
    {'metadata':update,'presets':presets,'manifest':manifest}[a.command]()
