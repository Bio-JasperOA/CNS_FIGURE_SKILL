"""Publish standalone comparison figures without adding subtitles to any chart."""
from pathlib import Path
import json,html
from PIL import Image,ImageDraw,ImageFont

def publish(root):
    root=Path(root);catalog=json.loads(Path(__file__).with_name('catalogue_v32.json').read_text())
    (root/'catalogue.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
    md=['# Minimal / Advanced · v3.2','','所有数值均为合成样式测试；不是实验结果。图内无subtitle。','']
    page=['<!doctype html><meta charset="utf-8"><title>CNS Style Gallery v3.2</title><style>body{font:15px system-ui;max-width:1500px;margin:35px auto;padding:0 20px;color:#263641}section{border-top:1px solid #dae1e4;padding:20px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}img{width:100%}p{line-height:1.6}h2{font-size:21px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>Minimal / Advanced · v3.2</h1><p>All data are synthetic style fixtures. No chart subtitles.</p>']
    for r in catalog:
        k=r['kind'];title=f"{r['number']:02d} · {r['name']}"
        md.extend([f'## {title}','','| Minimal | Advanced |','|---|---|',f'| ![](figures/{k}_minimal.png) | ![](figures/{k}_advanced.png) |','',r['advanced'],'', '**数据边界：** '+r['input_boundary'],'','**对照依据：** '+r['evidence'],''])
        page.append(f'<section><h2>{html.escape(title)}</h2><div class="pair"><div>Minimal<img src="figures/{k}_minimal.png"></div><div>Advanced<img src="figures/{k}_advanced.png"></div></div><p>{html.escape(r["advanced"])}</p><p>{html.escape(r["input_boundary"])}</p><p>{html.escape(r["evidence"])}</p></section>')
    (root/'README.md').write_text('\n'.join(md));(root/'index.html').write_text('\n'.join(page))
    # A contact sheet is a review index, not a fused scientific plot.
    selected=['heatmap','dotplot','network','spatial','upset','flow','forest','calibration','spatial_composition']
    font=ImageFont.truetype('DejaVuSans.ttf',20)
    for filename,kinds,cols in [('selected.png',selected,3),('overview.png',[r['kind'] for r in catalog],4)]:
        w=650;h=500;canvas=Image.new('RGB',(cols*w,((len(kinds)+cols-1)//cols)*h),'white');dr=ImageDraw.Draw(canvas)
        for i,k in enumerate(kinds):
            im=Image.open(root/'figures'/f'{k}_advanced.png').convert('RGB');im.thumbnail((w,h-34));x=(i%cols)*w;y=(i//cols)*h
            canvas.paste(im,(x,y+28));dr.text((x+16,y+5),k,font=font,fill='#263641')
        canvas.save(root/filename)
    import fitz
    pdf=fitz.open()
    for r in catalog:
        a=fitz.open(root/'figures'/f'{r["kind"]}_minimal.pdf');b=fitz.open(root/'figures'/f'{r["kind"]}_advanced.pdf')
        w=a[0].rect.width;h=a[0].rect.height;gap=24;p=pdf.new_page(width=2*w+gap,height=h)
        p.show_pdf_page(fitz.Rect(0,0,w,h),a,0);p.show_pdf_page(fitz.Rect(w+gap,0,2*w+gap,h),b,0)
        a.close();b.close()
    pdf.set_toc([[1,f'{r["number"]:02d} {r["kind"]}',i+1] for i,r in enumerate(catalog)])
    pdf.save(root/'paired_gallery.pdf');pdf.close()
