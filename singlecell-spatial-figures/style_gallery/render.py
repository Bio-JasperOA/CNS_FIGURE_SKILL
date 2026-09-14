"""Fourteen table-driven, paired scientific chart recipes. All bundled data are synthetic.
Run: python render.py demo --out build
     python render.py plot --kind dotplot --input reviewed.csv --config config.json --out Fig1
No model fitting or significance testing occurs in the renderer.
"""
from __future__ import annotations
import argparse, hashlib, json, math, textwrap, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors as mc
from matplotlib.patches import Rectangle, PathPatch, FancyArrowPatch
from matplotlib.path import Path as MPath
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, PercentFormatter
from matplotlib.font_manager import FontProperties, findfont
from scipy.stats import gaussian_kde

VERSION = '3.1.0'
# C03 / BANKSY vignette: Tableau medium, unchanged RGB8 order. Supplementary neutral is not data.
COLORS = ['#729ECE','#FF9E4A','#67BF5C','#ED665D','#AD8BC9','#A8786E',
          '#ED97CA','#A2A2A2','#CDCC5D','#6DCCDA']
INK, MUTED, GRID = '#24313B', '#69747D', '#E5E9EC'
# Exact RGB8 snapshots of existing C03 / M02 / D03 presets, with source provenance.
PALETTE_SNAPSHOT = json.loads((Path(__file__).with_name('palettes.json')).read_text())
COLORS = PALETTE_SNAPSHOT['C03']['colors']
SEQ = mc.ListedColormap(PALETTE_SNAPSHOT['M02']['colors'], name='M02_mako_rgb8')
DIV = mc.ListedColormap(PALETTE_SNAPSHOT['D03']['colors'], name='D03_vlag_rgb8')
KINDS = ['embedding','spatial','dotplot','heatmap','distribution','composition','paired',
         'volcano','enrichment','trajectory','network','flow','benchmark','correlation']
REQUIRED = {
 'embedding':['id','x','y','group'], 'spatial':['id','x','y','value','section'],
 'dotplot':['group','feature','mean','fraction'], 'heatmap':['group','feature','value'],
 'distribution':['id','group','value'], 'composition':['sample','group','fraction'],
 'paired':['sample','condition','value'], 'volcano':['feature','effect','q'],
 'enrichment':['term','effect','q','count'], 'trajectory':['lineage','time','mean','lower','upper'],
 'network':['source','target','weight'], 'flow':['source','target','mass'],
 'benchmark':['dataset','method','score'], 'correlation':['row','column','value']}
TITLES = dict(zip(KINDS, ['Cell identity in an embedding','Spatial expression pattern',
 'Marker expression and detection','Coordinated expression modules','Distribution across groups',
 'Cell composition across samples','Paired sample response','Differential expression summary',
 'Pathway enrichment profile','Lineage-specific temporal trends','Candidate cell communication',
 'Mass-preserving state transitions','Performance across matched datasets','Correlation structure']))


def _hash(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _write(path, obj): Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')
def _order(d, key, cfg):
    levels = cfg.get(key+'_order', list(pd.unique(d[key])))
    if len(levels) != len(set(levels)) or set(levels) != set(d[key].unique()):
        raise ValueError(f'{key}_order must contain each observed level exactly once')
    return levels

def _palette(levels, cfg):
    pal = cfg.get('colors')
    pid = cfg.get('categorical_preset')
    if pid is not None:
        if pal is not None: raise ValueError('Choose categorical_preset or explicit colors, not both')
        if pid in PALETTE_SNAPSHOT and pid.startswith('C'):
            values=PALETTE_SNAPSHOT[pid]['colors']
            if len(levels)>len(values): raise ValueError('Palette capacity exceeded')
            return dict(zip(levels,values))
        import sys
        api=Path(__file__).resolve().parent.parent/'scripts'
        if not (api/'palette_presets.py').is_file():
            raise ValueError('This preset requires the full Skill repository; standalone snapshots: C03, M02, D03')
        if str(api) not in sys.path: sys.path.insert(0,str(api))
        from palette_presets import categorical_map
        return categorical_map(pid,levels)
    if pal is None:
        if len(levels)>len(COLORS): raise ValueError('Supply a named high-capacity palette; colors never recycle')
        return dict(zip(levels,COLORS))
    if not isinstance(pal,dict) or set(levels)-set(pal): raise ValueError('Missing named category colors')
    for c in pal.values(): mc.to_rgba(c)
    if len({mc.to_hex(pal[g]) for g in levels}) != len(levels): raise ValueError('Repeated category colors')
    return pal

def validate(kind, d, cfg):
    if kind not in REQUIRED: raise ValueError('Unknown chart kind')
    if not len(d): raise ValueError('Empty input table')
    if set(REQUIRED[kind])-set(d.columns): raise ValueError('Missing required fields: '+str(REQUIRED[kind]))
    keys = {'embedding':['id'],'spatial':['id'],'dotplot':['group','feature'],
      'heatmap':['group','feature'],'distribution':['id'],'composition':['sample','group'],
      'paired':['sample','condition'],'volcano':['feature'],'enrichment':['term'],
      'trajectory':['lineage','time'],'network':['source','target'],'flow':['source','target'],
      'benchmark':['dataset','method'],'correlation':['row','column']}[kind]
    if d[keys].isna().any().any() or d.duplicated(keys).any(): raise ValueError('Null or duplicated identity keys')
    numeric=[c for c in ['x','y','value','mean','fraction','effect','q','count','time','lower','upper','weight','mass','score'] if c in REQUIRED[kind]]
    for c in numeric:
        values=pd.to_numeric(d[c],errors='raise').to_numpy(float)
        # Explicit missing matrix/spatial values are shown; numeric identities/geometry cannot be missing.
        allow = (kind in ['heatmap','correlation','spatial'] and c=='value')
        if np.isinf(values).any() or (not allow and np.isnan(values).any()): raise ValueError('Nonfinite '+c)
    for c in ['fraction','q']:
        if c in numeric and ((d[c]<0)|(d[c]>1)).any(): raise ValueError(c+' outside [0,1]')
    if 'q' in numeric and (d.q<=0).any(): raise ValueError('Supply positive q or an explicitly censored plotting floor upstream')
    for c in ['count','weight','mass']:
        if c in numeric and (d[c]<0).any(): raise ValueError('Negative '+c)
    if kind=='spatial' and (d.section.nunique()!=1 or cfg.get('coordinate_unit') is None):
        raise ValueError('One section and explicit coordinate_unit required')
    if kind=='composition' and not np.allclose(d.groupby('sample').fraction.sum(),1,atol=1e-6):
        raise ValueError('Fractions must already sum to 1 within each sample')
    if kind=='paired' and not (d.condition.nunique()==2 and (d.groupby('sample').size()==2).all()):
        raise ValueError('Each sample must have exactly two declared conditions')
    if kind=='trajectory' and ((d.lower>d['mean'])|(d.upper<d['mean'])).any(): raise ValueError('Invalid interval bounds')
    if kind=='trajectory' and not cfg.get('interval_label'): raise ValueError('Declare what the supplied interval means')
    if kind=='network' and d.weight.sum()<=0: raise ValueError('Network needs positive total score')
    if kind=='flow' and d.mass.sum()<=0: raise ValueError('Zero total mass')
    if kind=='flow' and not cfg.get('mass_unit'): raise ValueError('Declare mass_unit; probability is not a cell count')
    if kind=='correlation' and (d.value.abs()>1).any(): raise ValueError('Correlation outside [-1,1]')
    for ccol in ['n']:
        if ccol in d and (pd.to_numeric(d[ccol],errors='raise')<0).any(): raise ValueError('Negative count annotation')
    for key,meta in [('feature','module'),('group','n')] if kind=='heatmap' else ([('sample','n'),('sample','condition')] if kind=='composition' else []):
        if meta in d and d.groupby(key)[meta].nunique(dropna=False).gt(1).any():
            raise ValueError(f'Inconsistent {meta} annotation for {key}')
    if not cfg.get('demo',False) and not cfg.get('provenance'): raise ValueError('Real-data rendering requires provenance')


def _base(kind, advanced, cfg):
    width=cfg.get('width_mm',183)/25.4; height=cfg.get('height_mm',118)/25.4
    font=cfg.get('font_family','DejaVu Sans')
    resolved=FontProperties(fname=findfont(FontProperties(family=font))).get_name()
    if resolved != font: warnings.warn(f'Font {font} unavailable; using {resolved}')
    fig=plt.figure(figsize=(width,height),facecolor='white')
    ax=fig.add_axes([.16,.21,.66,.57])
    for s in ['top','right']: ax.spines[s].set_visible(False)
    for s in ['left','bottom']: ax.spines[s].set_color('#94A0A8'); ax.spines[s].set_linewidth(.55)
    ax.tick_params(width=.5,length=2.8,color='#94A0A8',labelcolor=INK,pad=3)
    fig.text(.055,.935,cfg.get('title',TITLES[kind]),size=12,weight='bold',color=INK)
    fig.text(.055,.883,cfg.get('subtitle','Same source table; advanced changes encoding, not the analysis.'),size=7.8,color=MUTED)
    footer='ILLUSTRATIVE DATA / NOT A BIOLOGICAL RESULT' if cfg.get('demo') else str(cfg['provenance'])
    fig.text(.055,.044,textwrap.shorten(footer,width=114,placeholder='...'),size=6.8,color=MUTED)
    fig.text(.945,.044,'ADVANCED' if advanced else 'MINIMAL',size=6.8,color=MUTED,ha='right')
    fig._actual_font=resolved
    fig._legend_mode=cfg.get('legend_mode','inline')
    return fig,ax

def _ticks(ax,labels,axis='x',rotation=0):
    labs=['\n'.join(textwrap.wrap(str(x),18,break_long_words=False)) for x in labels]
    if axis=='x': ax.set_xticks(range(len(labs)),labs,rotation=rotation,ha='right' if rotation else 'center')
    else: ax.set_yticks(range(len(labs)),labs)

def _legend(ax, pal, counts=None, title='Group'):
    if getattr(ax.figure,'_legend_mode','inline')=='external':
        ax.figure._external_color_key=dict(pal)
        ax.text(0,-.22,'Complete identity key: accompanying colors.csv / key.pdf',transform=ax.transAxes,size=7,color=MUTED)
        return None
    handles=[Line2D([],[],marker='o',ls='',ms=4.4,color=c,label=str(g)+(f'  (n={counts[g]})' if counts is not None else '')) for g,c in pal.items()]
    return ax.legend(handles=handles,frameon=False,loc='center left',bbox_to_anchor=(1.03,.5),borderaxespad=0,title=title,handletextpad=.5,labelspacing=.65)

def _cmap(cfg, signed=False):
    pid=cfg.get('continuous_preset')
    if pid is not None:
        if cfg.get('continuous_colors'): raise ValueError('Choose continuous_preset or explicit colors')
        if pid in PALETTE_SNAPSHOT and not pid.startswith('C'):
            return mc.ListedColormap(PALETTE_SNAPSHOT[pid]['colors'],name=pid+'_rgb8')
        import sys
        api=Path(__file__).resolve().parent.parent/'scripts'
        if not (api/'palette_presets.py').is_file(): raise ValueError('Preset requires full Skill repository')
        if str(api) not in sys.path: sys.path.insert(0,str(api))
        from palette_presets import palette_colormap
        return palette_colormap(pid)
    if cfg.get('continuous_colors'):
        return mc.LinearSegmentedColormap.from_list('configured',cfg['continuous_colors'])
    return DIV if signed else SEQ.reversed()

def _bar(fig, ax, im, label):
    cb=fig.colorbar(im,ax=ax,fraction=.045,pad=.035,shrink=.8)
    cb.outline.set_visible(False); cb.ax.tick_params(length=2,width=.5)
    cb.set_label(label,size=7.5)
    return cb

def embedding(ax,d,a,c):
    levels=_order(d,'group',c); pal=_palette(levels,c)
    ordered=d.sample(frac=1,random_state=0)
    ax.scatter(ordered.x,ordered.y,c=[pal[x] for x in ordered.group],s=c.get('point_area',4),lw=0,alpha=.9,rasterized=True)
    ax.set_aspect('equal'); ax.set_xlabel('Embedding 1'); ax.set_ylabel('Embedding 2'); ax.set_xticks([]); ax.set_yticks([])
    if a:
        focus=c.get('label_groups',levels)
        if len(focus)>18: raise ValueError('For >18 clusters specify label_groups and retain complete color key')
        for i,g in enumerate(levels):
            if g in focus:
                p=d[d.group==g][['x','y']].median()
                ax.text(*p,str(i+1),ha='center',va='center',size=7,weight='bold',bbox=dict(boxstyle='circle,pad=.22',fc='white',ec=pal[g],lw=.7),zorder=4)
        _legend(ax,{f'{i+1}. {g}':pal[g] for i,g in enumerate(levels)},title='Identity / cluster ID')
        ax.text(0,-.12,f'{len(d):,} cells; supplied coordinates retained',transform=ax.transAxes,size=7,color=MUTED)
    else: _legend(ax,pal)


def spatial(ax,d,a,c):
    limits=c.get('limits',[0,float(d.value.max())]); norm=mc.Normalize(*limits)
    cmap=_cmap(c).copy(); cmap.set_bad('#B8BEC4')
    p=ax.scatter(d.x,d.y,c=np.ma.masked_invalid(d.value.to_numpy()),cmap=cmap,norm=norm,s=c.get('point_area',10),lw=0,rasterized=True)
    ax.set_aspect('equal'); ax.set_xlabel('x ('+c['coordinate_unit']+')'); ax.set_ylabel('y ('+c['coordinate_unit']+')')
    if c.get('origin','lower')=='upper': ax.invert_yaxis()
    _bar(ax.figure,ax,p,c.get('value_label','Expression score'))
    if a:
        if 'region' in d:
            for region,g in d.groupby('region',sort=False):
                center=g[['x','y']].median()
                ax.annotate(str(region),center,xytext=(0,12),textcoords='offset points',ha='center',size=7.2,bbox=dict(fc='white',ec='none',alpha=.92,pad=2))
        if c.get('scale_bar'):
            length=float(c['scale_bar']); xmin,xmax=ax.get_xlim(); ymin,ymax=sorted(ax.get_ylim())
            if length<=0 or length>(xmax-xmin)*.4: raise ValueError('Scale bar must be positive and fit')
            x=xmin+.06*(xmax-xmin); y=ymin+.07*(ymax-ymin)
            ax.plot([x,x+length],[y,y],c=INK,lw=2)
            ax.text(x+length/2,y+.025*(ymax-ymin),f'{length:g} {c["coordinate_unit"]}',ha='center',size=7)
        ax.text(0,-.25,'One section; supplied region assignments',transform=ax.transAxes,size=7,color=MUTED)


def dotplot(ax,d,a,c):
    groups=_order(d,'group',c); features=_order(d,'feature',c)
    norm=mc.Normalize(*c.get('limits',[0,max(d['mean'])])); cmap=_cmap(c)
    x=d.feature.map({x:i for i,x in enumerate(features)}); y=d.group.map({x:i for i,x in enumerate(groups)})
    if a:
        for i in range(len(groups)):
            if i%2==0: ax.axhspan(i-.5,i+.5,color='#F4F6F7',zorder=0)
    p=ax.scatter(x,y,s=90*d.fraction,c=d['mean'],norm=norm,cmap=cmap,lw=.35,edgecolors='white')
    _ticks(ax,features,rotation=45); _ticks(ax,groups,'y'); ax.set_xlim(-.6,len(features)-.4); ax.set_ylim(len(groups)-.4,-.7)
    ax.set_xlabel('Marker gene'); ax.set_ylabel('Cell group'); _bar(ax.figure,ax,p,c.get('value_label','Mean supplied expression'))
    h=[ax.scatter([],[],s=90*f,c=INK,lw=0,label=f'{f:.0%}') for f in [.25,.5,1]]
    ax.legend(handles=h,title='Detected fraction',frameon=False,loc='lower center',bbox_to_anchor=(.5,1.04),ncol=3,fontsize=7,title_fontsize=7)
    if a and 'module' in d:
        mods=d.drop_duplicates('feature').set_index('feature').loc[features,'module']
        for i in range(1,len(features)):
            if mods.iloc[i]!=mods.iloc[i-1]: ax.axvline(i-.5,color='#ABB5BB',lw=.65)


def heatmap(ax,d,a,c):
    rows=_order(d,'feature',c); cols=_order(d,'group',c)
    m=d.pivot(index='feature',columns='group',values='value').reindex(index=rows,columns=cols)
    cmap=_cmap(c,True).copy(); cmap.set_bad('#B9C1C7')
    lim=c.get('limits',[-2.5,2.5]); p=ax.imshow(np.ma.masked_invalid(m),cmap=cmap,norm=mc.TwoSlopeNorm(0,*lim),aspect='auto',interpolation='nearest')
    _ticks(ax,cols,rotation=45); _ticks(ax,rows,'y'); _bar(ax.figure,ax,p,c.get('value_label','Supplied gene z-score'))
    ax.set_xlabel('Sample / group'); ax.set_ylabel('Gene'); ax.spines[['left','bottom']].set_visible(False)
    if a:
        if 'module' in d:
            mods=d.drop_duplicates('feature').set_index('feature').loc[rows,'module']; pal=_palette(list(pd.unique(mods)),c.get('module_style',{}))
            for i,v in enumerate(mods): ax.add_patch(Rectangle((-.16, i-.5),.025,1,transform=ax.get_yaxis_transform(),color=pal[v],clip_on=False,lw=0))
            for module in pd.unique(mods):
                inds=np.flatnonzero(mods.to_numpy()==module)
                ax.text(-.21,inds.mean(),str(module),transform=ax.get_yaxis_transform(),rotation=90,ha='center',va='center',fontsize=7,color=pal[module])
            ax.set_ylabel('')
            for i in range(1,len(rows)):
                if mods.iloc[i]!=mods.iloc[i-1]: ax.axhline(i-.5,c='white',lw=2)
        if 'n' in d:
            n=d.drop_duplicates('group').set_index('group').loc[cols,'n']; maximum=max(n)
            for j,v in enumerate(n):
                ax.add_patch(Rectangle((j-.36,1.035),.72,.12*v/maximum,transform=ax.get_xaxis_transform(),fc='#849BA8',clip_on=False,lw=0))
            ax.text(0,1.175,'n cells (max = '+str(maximum)+')',transform=ax.transAxes,size=7,color=MUTED)


def distribution(ax,d,a,c):
    groups=_order(d,'group',c); pal=_palette(groups,c)
    for i,g in enumerate(groups):
        v=d.loc[d.group==g,'value'].to_numpy(); q=np.quantile(v,[.25,.5,.75])
        if a and len(np.unique(v))>2:
            xx=np.linspace(v.min(),v.max(),80); density=gaussian_kde(v)(xx); density=.33*density/density.max()
            ax.fill_betweenx(xx,i,i+density,fc=pal[g],alpha=.3,lw=.7,ec=pal[g])
        jitter=np.random.default_rng(11+i).uniform(-.22,-.045,len(v)) if a else np.zeros(len(v))
        ax.scatter(i+jitter,v,s=12,c=pal[g],lw=.35,edgecolors='white',zorder=3)
        if a:
            ax.plot([i,i],[q[0],q[2]],c=INK,lw=2); ax.scatter(i,q[1],s=22,fc='white',ec=INK,lw=.7,zorder=4)
    _ticks(ax,groups); ax.set_xlim(-.65,len(groups)-.35); ax.set_ylabel(c.get('value_label','Sample-level module score'))
    ax.set_xlabel('Biological group'); ax.yaxis.set_major_locator(MaxNLocator(5)); ax.grid(axis='y',color=GRID,lw=.5,zorder=0)
    ax.text(0,-.19,'Each point = one sample; '+('density + median / IQR' if a else 'all observations shown'),transform=ax.transAxes,size=7,color=MUTED)


def composition(ax,d,a,c):
    groups=_order(d,'group',c); samples=_order(d,'sample',c); pal=_palette(groups,c)
    m=d.pivot(index='sample',columns='group',values='fraction').reindex(index=samples,columns=groups)
    if m.isna().any().any(): raise ValueError('Supply explicit zero fractions for absent groups, not missing cells')
    bottom=np.zeros(len(samples))
    for g in groups:
        ax.bar(np.arange(len(samples)),m[g],bottom=bottom,color=pal[g],width=.76,edgecolor='white',lw=.4,label=g); bottom+=m[g]
    _ticks(ax,samples,rotation=45); ax.set_ylim(0,1); ax.yaxis.set_major_formatter(PercentFormatter(1)); ax.set_ylabel('Within-sample fraction'); ax.set_xlabel('Biological sample')
    ax.legend(frameon=False,loc='center left',bbox_to_anchor=(1.03,.5),title='Cell type')
    if a:
        if 'condition' in d:
            cond=d.drop_duplicates('sample').set_index('sample').loc[samples,'condition']
            for i in range(1,len(samples)):
                if cond.iloc[i]!=cond.iloc[i-1]: ax.axvline(i-.5,color=INK,lw=.8,ls='--')
            for g in pd.unique(cond):
                pos=np.flatnonzero(cond.to_numpy()==g); ax.text(pos.mean(),1.07,str(g),ha='center',size=8)
        if 'n' in d:
            n=d.drop_duplicates('sample').set_index('sample').loc[samples,'n']
            for i,v in enumerate(n): ax.text(i,1.012,str(v),ha='center',size=6,color=MUTED)
        ax.text(0,-.21,'Denominator: all classified cells within each sample',transform=ax.transAxes,size=7,color=MUTED)


def paired(ax,d,a,c):
    cond=_order(d,'condition',c); pal=_palette(cond,c); m=d.pivot(index='sample',columns='condition',values='value').reindex(columns=cond)
    for i,(_,row) in enumerate(m.iterrows()):
        if a: ax.plot([0,1],row,c='#AEB8BE',lw=.8,zorder=1)
        ax.scatter([0,1],row,s=24,c=[pal[g] for g in cond],lw=.4,edgecolors='white',zorder=3)
    _ticks(ax,cond); ax.set_xlim(-.4,1.65 if a else 1.4); ax.set_ylabel(c.get('value_label','Sample-level abundance (%)'))
    if a:
        delta=m.iloc[:,1]-m.iloc[:,0]
        ax.text(.83,.9,f'{len(m)} matched samples\nMedian change\n{np.median(delta):+.2f}',transform=ax.transAxes,ha='left',va='top',size=8,color=INK)
    ax.grid(axis='y',color=GRID,lw=.5); ax.text(0,-.18,'Connected observations belong to the same sample' if a else 'Same paired table; pairing not drawn',transform=ax.transAxes,size=7,color=MUTED)


def volcano(ax,d,a,c):
    q=float(c.get('q_threshold',.05)); e=float(c.get('effect_threshold',1)); x=d.effect; y=-np.log10(d.q)
    pos=(d.q<q)&(x>e); neg=(d.q<q)&(x<-e)
    cols=np.where(pos,'#AB626B',np.where(neg,'#527F9C','#C7CDD1'))
    ax.scatter(x,y,s=11,c=cols,lw=0,rasterized=True)
    ax.set_xlabel(c.get('effect_label','log2 fold change')); ax.set_ylabel('-log10(adjusted P)')
    # Explicitly retain significance boundaries in BOTH modes.
    ax.axhline(-np.log10(q),c=MUTED,ls='--',lw=.6)
    for t in [-e,e]: ax.axvline(t,c=MUTED,ls='--',lw=.6)
    if a:
        selected=d.loc[pos|neg].sort_values('q').head(int(c.get('label_n',6)))
        for side in [-1,1]:
            s=selected[selected.effect*side>0].sort_values('q'); ymax=max(y)
            for j,(_,r) in enumerate(s.iterrows()):
                ax.annotate(r.feature,(r.effect,-np.log10(r.q)),xytext=(side*max(abs(x))*.98,ymax*(.94-j*.12)),ha='right' if side>0 else 'left',size=7.4,arrowprops=dict(arrowstyle='-',color=MUTED,lw=.55),annotation_clip=False)
        ax.text(.02,.98,f'Lower: {neg.sum()}     Higher: {pos.sum()}',transform=ax.transAxes,ha='left',va='top',size=7.5)
    ax.margins(x=.19,y=.12)


def enrichment(ax,d,a,c):
    d=d.sort_values('effect',ascending=True,kind='stable'); y=np.arange(len(d)); norm=mc.Normalize(*c.get('q_color_limits',[0,max(-np.log10(d.q))])); cmap=_cmap(c)
    if a: ax.hlines(y,0,d.effect,lw=1,color='#C5D0D4',zorder=0)
    p=ax.scatter(d.effect,y,s=(4*d['count']) if a else 28,c=-np.log10(d.q),cmap=cmap,norm=norm,edgecolors='white',lw=.5,zorder=2)
    _ticks(ax,d.term,'y'); ax.set_xlabel(c.get('effect_label','Enrichment effect (supplied score)')); ax.axvline(0,c=GRID,lw=.8); _bar(ax.figure,ax,p,'-log10(adjusted P)')
    if a:
        handles=[ax.scatter([],[],s=4*n,c=MUTED,label=str(n)) for n in [5,15,30]]
        ax.legend(handles=handles,title='Genes',frameon=False,loc='lower center',bbox_to_anchor=(.5,1.04),ncol=3)
    ax.margins(y=.07)


def trajectory(ax,d,a,c):
    groups=_order(d,'lineage',c); pal=_palette(groups,c)
    for g in groups:
        t=d[d.lineage==g].sort_values('time'); ax.plot(t.time,t['mean'],c=pal[g],lw=1.8,label=g)
        # Statistical content is not deleted to make a minimal plot: both modes retain intervals.
        ax.fill_between(t.time,t.lower,t.upper,fc=pal[g],alpha=.16,lw=0)
        if a:
            ax.text(t.time.iloc[-1]+.02*(d.time.max()-d.time.min()),t['mean'].iloc[-1],str(g),color=pal[g],size=8,va='center')
            peak=t.loc[t['mean'].idxmax()]; ax.scatter(peak.time,peak['mean'],s=25,fc='white',ec=pal[g],lw=1,zorder=3)
    ax.set_xlabel(c.get('time_label','Pseudotime (supplied ordering)')); ax.set_ylabel(c.get('value_label','Smoothed expression'))
    if not a: ax.legend(frameon=False)
    ax.text(0,-.2,c['interval_label'],transform=ax.transAxes,size=7,color=MUTED); ax.margins(x=.16 if a else .04)
    ax.grid(axis='y',color=GRID,lw=.5)


def network(ax,d,a,c):
    sources=list(pd.unique(d.source)); targets=list(pd.unique(d.target)); levels=list(dict.fromkeys(sources+targets)); pal=_palette(levels,c)
    left={g:(0,i/max(1,len(sources)-1)) for i,g in enumerate(sources)}; right={g:(1,i/max(1,len(targets)-1)) for i,g in enumerate(targets)}
    for _,r in d.sort_values('weight').iterrows():
        if r.weight==0: continue
        w=3*r.weight/max(d.weight)
        patch=FancyArrowPatch(left[r.source],right[r.target],arrowstyle='-|>' if a else '-',connectionstyle='arc3,rad=0',mutation_scale=6,shrinkA=7,shrinkB=7,lw=w,color=pal[r.source],alpha=.5)
        ax.add_patch(patch)
    for lookup,ha,dx in [(left,'right',-.06),(right,'left',.06)]:
        for g,(x,y) in lookup.items():
            ax.scatter(x,y,s=105,fc=pal[g],ec='white',lw=.8,zorder=3); ax.text(x+dx,y,g,ha=ha,va='center',size=8)
    ax.set_xlim(-.42,1.42); ax.set_ylim(-.12,1.14); ax.axis('off')
    ax.text(0,1.12,'Sender',ha='center',size=8,weight='bold'); ax.text(1,1.12,'Receiver',ha='center',size=8,weight='bold')
    ax.text(.5,-.12,'Width = supplied interaction score; direction = hypothesis, not causal proof',ha='center',size=7,color=MUTED)
    if a:
        handles=[Line2D([],[],c=MUTED,lw=3*f,label=f'{f*max(d.weight):.2f}') for f in [.2,.6,1]]
        ax.legend(handles=handles,frameon=False,title='Score',loc='lower center',bbox_to_anchor=(.5,-.23),ncol=3)


def flow(ax,d,a,c):
    src=_order(d,'source',c); dst=_order(d,'target',c); pal=_palette(list(dict.fromkeys(src+dst)),c)
    m=d.pivot(index='source',columns='target',values='mass').reindex(index=src,columns=dst).fillna(0)
    # The sparse edge-table convention makes absent edges zero; listed missing masses are rejected.
    total=m.to_numpy().sum(); gap=.045*total; source_tot=m.sum(axis=1); target_tot=m.sum(axis=0)
    so=np.r_[0,np.cumsum(source_tot.to_numpy()+gap)[:-1]]; to=np.r_[0,np.cumsum(target_tot.to_numpy()+gap)[:-1]]
    sb=so.copy(); tb=to.copy()
    for i,s in enumerate(src):
        for j,t in enumerate(dst):
            v=m.loc[s,t]
            if v==0: continue
            pts=[(0,sb[i]),(.42,sb[i]),(.58,tb[j]),(1,tb[j]),(1,tb[j]+v),(.58,tb[j]+v),(.42,sb[i]+v),(0,sb[i]+v),(0,sb[i])]
            path=MPath(pts,[1,4,4,4,2,4,4,4,79]); ax.add_patch(PathPatch(path,fc=pal[s],ec='white',lw=.25,alpha=.5 if a else .75))
            sb[i]+=v; tb[j]+=v
    for xs,labels,offsets,totals in [(0,src,so,source_tot),(1,dst,to,target_tot)]:
        for i,g in enumerate(labels):
            ax.add_patch(Rectangle((xs-.012,offsets[i]),.024,totals[g],fc=pal[g],ec='white',lw=.4))
            label=g+(f'  {totals[g]:g}' if a else '')
            ax.text(xs+(-.03 if xs==0 else .03),offsets[i]+totals[g]/2,label,ha='right' if xs==0 else 'left',va='center',size=7.5)
    ax.set_xlim(-.28,1.28); ax.set_ylim(-.04*total,max(sb.max(),tb.max())+.04*total); ax.invert_yaxis(); ax.axis('off')
    ax.text(.5,-.1,f'Total = {total:g} {c["mass_unit"]}; one mass scale at both endpoints',ha='center',transform=ax.transAxes,size=7,color=MUTED)


def benchmark(ax,d,a,c):
    methods=_order(d,'method',c); pal=_palette(methods,c)
    wide=d.pivot(index='dataset',columns='method',values='score').reindex(columns=methods)
    if wide.isna().any().any(): raise ValueError('Use the same dataset set for paired benchmarking')
    for _,row in wide.iterrows():
        if a: ax.plot(range(len(methods)),row,c='#C6CDD2',lw=.7,zorder=1)
    for i,g in enumerate(methods):
        v=wide[g]; ax.scatter(np.repeat(i,len(v)),v,s=19,fc=pal[g],ec='white',lw=.5,zorder=2)
        if a:
            median=np.median(v); ax.plot([i-.14,i+.14],[median,median],color=INK,lw=2,zorder=4)
    _ticks(ax,methods,rotation=0); ax.set_ylabel(c.get('value_label','Evaluation score')); ax.grid(axis='y',color=GRID,lw=.5); ax.set_xlim(-.45,len(methods)-.55)
    if c.get('reference') is not None: ax.axhline(c['reference'],c=MUTED,ls='--',lw=.7,label='Reference')
    ax.text(0,-.18,f'{len(wide)} matched datasets; '+('horizontal bar = median' if a else 'each dot = one dataset'),transform=ax.transAxes,size=7,color=MUTED)


def correlation(ax,d,a,c):
    rows=_order(d,'row',c); cols=_order(d,'column',c)
    if rows!=cols: raise ValueError('Correlation matrix requires matching row / column order')
    m=d.pivot(index='row',columns='column',values='value').reindex(index=rows,columns=cols)
    if not np.allclose(m,m.T,equal_nan=True): raise ValueError('Correlation matrix not symmetric')
    mask=np.triu(np.ones(m.shape,dtype=bool),1) if a else np.zeros(m.shape,dtype=bool)
    arr=np.ma.masked_where(mask|m.isna(),m.to_numpy()); cmap=_cmap(c,True).copy(); cmap.set_bad('white')
    p=ax.imshow(arr,cmap=cmap,norm=mc.Normalize(-1,1),interpolation='nearest',aspect='equal')
    _ticks(ax,cols,rotation=45); _ticks(ax,rows,'y'); _bar(ax.figure,ax,p,c.get('value_label','Pearson r'))
    if a:
        for i in range(len(rows)):
            for j in range(i+1):
                v=m.iloc[i,j]
                if np.isfinite(v): ax.text(j,i,f'{v:.2f}',ha='center',va='center',size=6.7,color='white' if abs(v)>.68 else INK)
    ax.spines[['left','bottom']].set_visible(False)


PLOTTERS={k:globals()[k] for k in KINDS}

def render(kind, table, config=None, mode='advanced'):
    cfg=dict(config or {}); d=table.copy(deep=True); validate(kind,d,cfg)
    if mode not in ['minimal','advanced']: raise ValueError('Mode must be minimal or advanced')
    with plt.rc_context({'font.family':cfg.get('font_family','DejaVu Sans'),'font.size':8,
         'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,
         'legend.title_fontsize':7.5,'pdf.fonttype':42,'svg.fonttype':'none'}):
        fig,ax=_base(kind,mode=='advanced',cfg)
        if kind in ['heatmap','dotplot']: ax.set_position([.19,.25,.61,.48])
        if kind=='enrichment': ax.set_position([.35,.21,.48,.55])
        if kind in ['paired','embedding']: ax.set_position([.12,.22,.56,.55])
        if cfg.get('axes_box') is not None:
            box=cfg['axes_box']
            if len(box)!=4 or min(box)<0 or box[0]+box[2]>1 or box[1]+box[3]>1 or min(box[2:])<=0:
                raise ValueError('axes_box must be a positive in-canvas fraction rectangle')
            ax.set_position(box)
        PLOTTERS[kind](ax,d,mode=='advanced',cfg)
        for t in fig.findobj(matplotlib.text.Text): t.set_fontfamily(fig._actual_font)
        fig.canvas.draw()
        return fig


def audit(fig):
    """Bounded export check. Does NOT certify all inter-label or data-mark collisions."""
    r=fig.canvas.get_renderer(); bounds=fig.bbox; outside=[]
    inactive=set()
    for ax in fig.axes:
        for axis in [ax.xaxis,ax.yaxis]:
            lo,hi=sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if tick.get_loc()<lo-1e-10 or tick.get_loc()>hi+1e-10:
                    inactive.update([id(tick.label1),id(tick.label2)])
    for t in fig.findobj(matplotlib.text.Text):
        if id(t) in inactive or not t.get_visible() or not t.get_text(): continue
        b=t.get_window_extent(r)
        if not np.isfinite(b.extents).all():
            outside.append('nonfinite: '+t.get_text()); continue
        if b.width==0 or b.height==0: continue
        if b.x0 < bounds.x0-1 or b.y0<bounds.y0-1 or b.x1>bounds.x1+1 or b.y1>bounds.y1+1:
            outside.append(t.get_text())
    return {'outside_canvas':outside,'axes_count':len(fig.axes),'font':fig._actual_font,
            'width_mm':fig.get_figwidth()*25.4,'height_mm':fig.get_figheight()*25.4,
            'scope':'canvas text bounds only; visual and scientific review remain required'}


def export(fig,out):
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
    report=audit(fig)
    if report['outside_canvas']: raise ValueError('Layout outside canvas: '+str(report['outside_canvas']))
    with plt.rc_context({'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'}):
        for ext in ['png','pdf','svg']: fig.savefig(out.with_suffix('.'+ext),dpi=180,facecolor='white',metadata={'Creator':'CNS Figure Skill style gallery'} if ext=='pdf' else None)
    if getattr(fig,'_external_color_key',None):
        key=fig._external_color_key
        pd.DataFrame({'category':list(key),'color':list(key.values())}).to_csv(out.with_suffix('.colors.csv'),index=False)
        keyfig=plt.figure(figsize=(183/25.4,210/25.4)); keyax=keyfig.add_axes([0,0,1,1]);keyax.axis('off')
        keyfig.text(.06,.955,'Complete categorical identity key',size=12,weight='bold')
        for i,(name,color) in enumerate(key.items()):
            col=i//25; row=i%25; x=.06+col*.23; y=.89-row*.031
            keyax.add_patch(Rectangle((x,y),.025,.016,fc=color,transform=keyax.transAxes))
            keyax.text(x+.034,y+.008,str(name),va='center',size=7)
        keyfig.text(.06,.04,'Key for '+out.name+'; colors are never recycled.',size=7)
        with plt.rc_context({'pdf.fonttype':42,'svg.fonttype':'none'}):
            keyfig.savefig(out.with_suffix('.key.pdf'));keyfig.savefig(out.with_suffix('.key.png'),dpi=160)
        plt.close(keyfig)
    _write(out.with_suffix('.qa.json'),report); plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='command',required=True)
    d=sub.add_parser('demo'); d.add_argument('--out',default='build')
    p=sub.add_parser('plot'); p.add_argument('--kind',choices=KINDS,required=True); p.add_argument('--input',required=True); p.add_argument('--config',required=True); p.add_argument('--out',required=True); p.add_argument('--mode',choices=['minimal','advanced'],default='advanced')
    args=parser.parse_args()
    if args.command=='demo':
        from fixtures import generate
        root=Path(args.out); root.mkdir(parents=True,exist_ok=True); manifest=[]
        for kind,(data,cfg) in generate().items():
            csv=root/'source_data'/f'{kind}.csv'; csv.parent.mkdir(exist_ok=True); data.to_csv(csv,index=False)
            _write(csv.with_suffix('.json'),cfg)
            for mode in ['minimal','advanced']: export(render(kind,data,cfg,mode),root/'figures'/f'{kind}_{mode}')
            manifest.append({'kind':kind,'data_sha256':_hash(csv),'config_sha256':_hash(csv.with_suffix('.json')),'demo':True})
        from fixtures import high_capacity
        data,cfg=high_capacity()
        csv=root/'source_data'/'embedding_100.csv';data.to_csv(csv,index=False);_write(csv.with_suffix('.json'),cfg)
        for mode in ['minimal','advanced']:
            export(render('embedding',data,cfg,mode),root/'figures'/f'embedding_100_{mode}')
        _write(root/'manifest.json',{'version':VERSION,'data_kind':'synthetic_style_fixture','pairs':manifest})
        from publish import publish
        publish(root)
    else:
        cfg=json.loads(Path(args.config).read_text()); data=pd.read_csv(args.input)
        fig=render(args.kind,data,cfg,args.mode); export(fig,args.out)
        _write(Path(args.out).with_suffix('.provenance.json'),{'input_sha256':_hash(args.input),'config_sha256':_hash(args.config),'version':VERSION,'demo':cfg.get('demo',False)})
if __name__=='__main__': main()
