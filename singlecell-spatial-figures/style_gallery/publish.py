"""Build the offline HTML comparison gallery and contact sheets from actual renders."""
from __future__ import annotations
import html, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from catalogue import CATALOG,SOURCES

def publish(root):
    root=Path(root); parts=[]
    for c in CATALOG:
        s=SOURCES[c['source_id']];k=c['kind'];e=html.escape
        panels=''.join(f'<figure><figcaption>{mode.upper()}</figcaption><a href="figures/{k}_{mode}.svg"><img src="figures/{k}_{mode}.png" alt="{e(c[mode])}"></a><p>{e(c[mode])}</p></figure>' for mode in ['minimal','advanced'])
        parts.append(f'''<section id="{k}"><h2>{c['id']} · {e(c['name'])}</h2><p class="question">{e(c['question'])}</p><div class="pair">{panels}</div><div class="compare"><b>论文对照：</b><a href="{s['url']}">{s['journal']} {s['year']} · {e(c['paper_figure'])}</a><p>{e(c['source_observation'])}</p><p><b>迁移边界：</b>{e(c['difference'])}</p><p><b>失败条件：</b>{e(c['fail_rule'])}</p><small>{e(s['evidence'])}</small></div><p><a href="source_data/{k}.csv">同一源数据 CSV</a> · <a href="source_data/{k}.json">配置</a> · <a href="figures/{k}_advanced.pdf">高级版 PDF</a></p></section>''')
    nav=' · '.join(f'<a href="#{c["kind"]}">{c["id"]} {html.escape(c["name"])}</a>' for c in CATALOG)
    document='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CNS Style Gallery · v3.1</title><style>body{max-width:1240px;margin:0 auto;padding:38px 28px;font-family:Arial,"Noto Sans CJK SC",sans-serif;color:#24313b;background:#fff;line-height:1.6}h1{font-size:30px;line-height:1.2}h2{font-size:22px}a{color:#315d79}.notice{padding:16px 22px;background:#f2f5f6;border-left:4px solid #7e9aaa}nav{font-size:13px;margin:24px 0}section{padding:26px 0;border-top:1px solid #dce3e7}.pair{display:grid;grid-template-columns:1fr 1fr;gap:22px}figure{margin:0}figcaption{font-size:12px;letter-spacing:1.5px;font-weight:bold;color:#657783}img{width:100%;height:auto}figure p{font-size:14px}.compare{background:#f6f8f8;padding:14px 20px;font-size:14px}.compare p{margin:6px 0}small{color:#69747d}.question{font-weight:bold} @media(max-width:780px){.pair{grid-template-columns:1fr}body{padding:22px 14px}}</style>'''+f'<h1>Minimal → Advanced<br>单细胞与空间组学图形样式库</h1><p>v3.1 · 14 chart families · 28 paired examples</p><div class="notice"><b>所有示例均为合成样式测试数据，不是生物学结果，也不是论文数值复现。</b><br>每对图使用相同源数据。最简版保留必要编码；高级版增加可解释信息层。论文原图只提供链接，不重新分发。</div><nav>{nav}</nav>'+''.join(parts)+'</html>'
    document=document.replace('</html>','<section><h2>Supplement · 100 categories</h2><p>Synthetic embedding fixture, not a computed UMAP. The complete key is separate.</p><img src="figures/embedding_100_advanced.png"><p><a href="figures/embedding_100_advanced.key.pdf">Complete key PDF</a> · <a href="figures/embedding_100_advanced.colors.csv">Named colors CSV</a></p></section></html>')
    (root/'index.html').write_text(document,encoding='utf-8')
    # GitHub-native Markdown gallery; all links resolve relative to the generated folder.
    md=['# Minimal → Advanced · v3.1','All values are **synthetic style fixtures**, not biological results.','']
    for c in CATALOG:
        s=SOURCES[c['source_id']];k=c['kind']
        md += [f'## {c["id"]} · {c["name"]}',c['question'],'',
          '| Minimal | Advanced |','|---|---|',f'| ![](figures/{k}_minimal.png) | ![](figures/{k}_advanced.png) |','',
          '**最简版：** '+c['minimal'],'','**高级版：** '+c['advanced'],'',
          f'**论文对照：** [{s["journal"]} {s["year"]}, {c["paper_figure"]}]({s["url"]}) — '+c['source_observation'],'',
          '**区别与边界：** '+c['difference'],'','**失败条件：** '+c['fail_rule'],'']
    md += ['## Supplement: 100 synthetic categories','![](figures/embedding_100_advanced.png)','[Complete identity key](figures/embedding_100_advanced.key.pdf) · [Colors CSV](figures/embedding_100_advanced.colors.csv)']
    (root/'README.md').write_text('\n'.join(md),encoding='utf-8')
    (root/'catalogue.json').write_text(json.dumps({'version':'3.1.0','examples':'synthetic','sources':SOURCES,'charts':CATALOG},ensure_ascii=False,indent=2),encoding='utf-8')
    # Contact sheet previews are indexes, not final-size review substitutes.
    for which,kinds in [('overview',CATALOG),('selected',[c for c in CATALOG if c['kind'] in ['embedding','heatmap','distribution','enrichment','flow','network']])]:
        w=1320;cellw=660;cellh=444;rows=(len(kinds)+1)//2
        im=Image.new('RGB',(w,rows*cellh+88),'white');draw=ImageDraw.Draw(im)
        try:font=ImageFont.truetype('DejaVuSans.ttf',22)
        except OSError:font=ImageFont.load_default()
        draw.text((28,20),'ADVANCED EXAMPLES / SYNTHETIC STYLE FIXTURES',fill='#24313B',font=font)
        for i,c in enumerate(kinds):
            p=Image.open(root/'figures'/f'{c["kind"]}_advanced.png').convert('RGB');p.thumbnail((cellw,cellh));im.paste(p,((i%2)*cellw,80+(i//2)*cellh))
        im.save(root/f'{which}.png',optimize=True)
    # Paired PDF at exact 1:1 chart size; own charts only, no journal artwork.
    try:
        import fitz
        result=fitz.open();mm=72/25.4
        for c in CATALOG:
            page=result.new_page(width=390*mm,height=270*mm)
            page.insert_text((14*mm,15*mm),f'{c["id"]} / {c["kind"]} - SAME SYNTHETIC INPUT, TWO ENCODINGS',fontsize=11)
            for j,mode in enumerate(['minimal','advanced']):
                doc=fitz.open(root/'figures'/f'{c["kind"]}_{mode}.pdf')
                rect=fitz.Rect((10+j*190)*mm,30*mm,(193+j*190)*mm,148*mm)
                page.show_pdf_page(rect,doc,0);doc.close()
            src=SOURCES[c['source_id']]
            text=f'Reference: {src["journal"]} {src["year"]}, {c["paper_figure"]}\nDOI: {src["doi"]}\nComparison scope: {src["evidence"]}\nThese tables and graphs are illustrative software fixtures. Not a reproduction of the source data.\nSource CSV, config, SVG and full design commentary accompany the HTML gallery.'
            page.insert_textbox(fitz.Rect(14*mm,167*mm,376*mm,245*mm),text,fontsize=10)
        result.save(root/'paired_gallery.pdf',garbage=4,deflate=True); result.close()
    except ImportError:
        pass # PyMuPDF is optional; PNG/PDF/SVG individual charts still exist.
if __name__=='__main__':
    import sys
    publish(sys.argv[1] if len(sys.argv)>1 else 'examples')
