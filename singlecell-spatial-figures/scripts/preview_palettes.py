"""Create a small SVG catalogue directly from the bundled palette tables."""
from html import escape
from pathlib import Path
import argparse
from palette_presets import inventory,palette_colors


def preview(path, all_presets=False):
    groups=[('categorical','Categorical / identity'),('sequential_single','Single-hue sequential'),
            ('sequential_multi','Multi-hue sequential'),('diverging','Diverging / centered'),('cyclic','Cyclic / phase')]
    rows=[];defs=[];y=120
    def text(x,y,t,size=13,weight='normal'):
        rows.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}">{escape(t)}</text>')
    text(28,34,'CNS PALETTE PRESETS | v3.0.1',22,'bold')
    text(28,60,'52 families available. These examples are illustrative, not new defaults.')
    text(28,83,'R research code | P implementation | E example | S supplement | D derived; not verified paper panels.',11)
    for family,title in groups:
        text(28,y,title,18,'bold');y+=25
        for p in inventory()['presets']:
            if p['family']!=family:continue
            if not all_presets and p['id'] not in {'C01','C03','C12','C19','C21','S01','M01','M02','M03','D01','D03','Y01'}:continue
            text(28,y+16,p['id']+'  '+p['name'],13,'bold')
            if 'variants' in p:
                cols=[c for v in p['variants'] for c in palette_colors(v['id'])]
                desc='4 separate 3-color variants (not one 12-class palette)'
            else:
                allcols=palette_colors(p['id']);cols=allcols[:20]
                desc=f"{p['n_colors']} colors" if family=='categorical' else f"{p['n_colors']} RGB8 lookup entries"
                if family=='categorical' and len(allcols)>20:desc+='; first 20 shown'
            text(28,y+34,p['grade']+' | '+desc,10)
            if family=='categorical':
                for i,c in enumerate(cols):
                    x=465+i*490/len(cols)
                    rows.append(f'<rect x="{x:.2f}" y="{y}" width="{490/len(cols)-1:.2f}" height="28" fill="{c}"/>')
            else:
                stops=palette_colors(p['id'],9)
                defs.append(f'<linearGradient id="{p["id"]}">'+''.join(f'<stop offset="{i/8:.3f}" stop-color="{c}"/>' for i,c in enumerate(stops))+'</linearGradient>')
                rows.append(f'<rect x="465" y="{y}" width="490" height="28" fill="url(#{p["id"]})"/>')
                text(465,y+42,allcols[0],10);text(904,y+42,allcols[-1],10)
            y+=65
        y+=20
    text(28,y,'Continuous bars show 9 sampled anchors; runtime uses the complete lookup table.',11)
    text(28,y+20,'Unique RGB entries do not guarantee perceptual separability. No fonts or biological data are included.',11)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="990" height="{y+45}" viewBox="0 0 990 {y+45}"><defs>'+''.join(defs)+'</defs><rect width="100%" height="100%" fill="white"/><g font-family="Arial,DejaVu Sans,sans-serif" fill="#222222">'+''.join(rows)+'</g></svg>\n'
    Path(path).write_text(svg,encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output');p.add_argument('--all',action='store_true');a=p.parse_args();preview(a.output,a.all)
