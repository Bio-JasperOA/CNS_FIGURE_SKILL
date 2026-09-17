"""CNS Figure Skill v3.2.0: 26 no-subtitle minimal/advanced recipes.
This is a plotting layer. All model estimates and statistical intervals come from input.
"""
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as mc
from matplotlib.text import Text
import chart_core as _chart_core
from chart_core import VERSION,REQUIRED,validate,frame,audit,export,palette,cmap,PAL,INK,MUTED
import chart_types as _chart_types
from chart_types import PLOTTERS
from modern_palettes import palette as editorial_palette, cmap as editorial_cmap, snapshots as editorial_snapshots

# Modern low-saturation editorial routing is the default rendering policy. Patch both
# chart_types and chart_core because helpers such as matrix() resolve palette/cmap from
# chart_core's module globals at runtime.
_chart_types.palette = editorial_palette
_chart_types.cmap = editorial_cmap
_chart_core.palette = editorial_palette
_chart_core.cmap = editorial_cmap
KINDS=list(REQUIRED)
PALETTE_SNAPSHOT={**PAL,**editorial_snapshots()}
_palette=editorial_palette
_cmap=editorial_cmap

# Explanatory microcopy is intentionally suppressed from the plotting canvas. Scientific
# meaning should live in axis labels, legends, direct data labels, captions and provenance.
_EXPLAINER_PREFIXES=(
    'Row order:',
    'Cell text:',
    'Cell text =',
    'Node values:',
    'Total ',
    'Area ∝',
    'Point area ∝',
    'Fixed point area',
)


def _prepare_demo_config(config):
    """Remove legacy palette hints so generated gallery configs match the active router."""
    c=copy.deepcopy(config)
    c.pop('subtitle',None)
    c.setdefault('palette_policy','modern_editorial')
    if c.get('palette_policy')=='modern_editorial':
        c.pop('colors',None)
        pid=str(c.get('categorical_preset',''))
        if pid.startswith('C'):c.pop('categorical_preset',None)
        pid=str(c.get('continuous_preset',''))
        if pid.startswith(('M','D','S')):c.pop('continuous_preset',None)
    return c


def _align_legend(legend):
    if legend is None:return
    try:legend.set_alignment('left')
    except Exception:
        if hasattr(legend,'_legend_box'):legend._legend_box.align='left'
    if hasattr(legend,'_legend_box'):legend._legend_box.align='left'
    title=legend.get_title()
    if title is not None:title.set_ha('left')
    for txt in legend.get_texts():txt.set_ha('left')


def finalize_figure(fig):
    """Apply publication-level legend/text cleanup to gallery and pipeline figures.

    - legend titles and entries are left aligned consistently;
    - gray explanatory microcopy is removed when it is only a plotting note;
    - remaining small muted labels are promoted to the main ink color;
    - the synthetic fixture disclosure remains explicit, but is not gray microcopy.
    """
    for ax in fig.axes:_align_legend(ax.get_legend())
    for legend in getattr(fig,'legends',[]):_align_legend(legend)

    muted=mc.to_hex(MUTED).upper();removed=[]
    for txt in fig.findobj(Text):
        text=(txt.get_text() or '').strip()
        if not text:continue
        if txt.get_gid()=='synthetic_disclosure':
            txt.set_color(INK);txt.set_fontsize(max(7,txt.get_fontsize()))
            continue
        if any(text.startswith(prefix) for prefix in _EXPLAINER_PREFIXES) or ' not displayed' in text:
            txt.set_visible(False);removed.append(text);continue
        try:color=mc.to_hex(txt.get_color()).upper()
        except Exception:color=''
        if color==muted and txt.get_fontsize()<=7.5:
            txt.set_color(INK)
    fig._legend_alignment='left'
    fig._removed_explanatory_text=removed
    return fig


def render(kind,table,config=None,mode='advanced'):
    cfg=copy.deepcopy(config or {});d=table.copy(deep=True)
    cfg.setdefault('palette_policy','modern_editorial')
    if mode not in ['minimal','advanced']:raise ValueError('Mode must be minimal or advanced')
    validate(kind,d,cfg)
    with plt.rc_context({'font.family':cfg.get('font_family','DejaVu Sans'),'font.size':8,
      'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,
      'legend.title_fontsize':7.5,'pdf.fonttype':42,'svg.fonttype':'none'}):
        fig,ax=frame(kind,cfg)
        try:
            PLOTTERS[kind](ax,d,mode=='advanced',cfg)
            finalize_figure(fig)
            for t in fig.findobj(Text):t.set_fontfamily(fig._actual_font)
            fig._mode=mode;fig._input_sha256=hashlib.sha256(table.to_csv(index=False).encode()).hexdigest()
            fig._palette_policy=cfg.get('palette_policy','modern_editorial')
            fig._palette_router='modern_palettes' if fig._palette_policy!='legacy' else 'chart_core'
            fig.canvas.draw();return fig
        except Exception:
            plt.close(fig);raise

def _hash(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _write(p,obj):Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')

def demo(out):
    from fixtures import generate,high_capacity
    root=Path(out);(root/'source_data').mkdir(parents=True,exist_ok=True);manifest=[]
    for kind,(d,c) in generate().items():
        c=_prepare_demo_config(c)
        csv=root/'source_data'/f'{kind}.csv';d.to_csv(csv,index=False);_write(csv.with_suffix('.json'),c)
        reports={}
        for mode in ['minimal','advanced']:
            reports[mode]=export(render(kind,d,c,mode),root/'figures'/f'{kind}_{mode}')
        manifest.append({'kind':kind,'data_sha256':_hash(csv),'config_sha256':_hash(csv.with_suffix('.json')),'palette_policy':c['palette_policy'],'modes':{m:{'layers':r['semantic_layers'],'outputs':r['outputs']} for m,r in reports.items()}})
        print(kind,flush=True)
    d,c=high_capacity();c=_prepare_demo_config(c);d.to_csv(root/'source_data'/'embedding_100.csv',index=False);_write(root/'source_data'/'embedding_100.json',c)
    for mode in ['minimal','advanced']:
        export(render('embedding',d,c,mode),root/'figures'/f'embedding_100_{mode}')
    _write(root/'manifest.json',{'version':VERSION,'data_kind':'synthetic_style_fixture','subtitle_policy':'forbidden','palette_policy':'modern_editorial','pairs':manifest})
    from publish_v32 import publish
    publish(root)

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    g=sub.add_parser('demo');g.add_argument('--out',default='examples')
    r=sub.add_parser('plot');r.add_argument('--kind',choices=KINDS,required=True);r.add_argument('--input',required=True);r.add_argument('--config',required=True);r.add_argument('--out',required=True);r.add_argument('--mode',choices=['minimal','advanced'],default='advanced')
    args=p.parse_args()
    if args.cmd=='demo':demo(args.out)
    else:
        c=json.loads(Path(args.config).read_text());d=pd.read_csv(args.input);fig=render(args.kind,d,c,args.mode);export(fig,args.out)
        _write(Path(args.out).with_suffix('.provenance.json'),{'input_sha256':_hash(args.input),'config_sha256':_hash(args.config),'version':VERSION,'demo':bool(c.get('demo',False)),'palette_policy':c.get('palette_policy','modern_editorial')})
if __name__=='__main__':main()
