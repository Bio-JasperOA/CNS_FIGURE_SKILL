"""Shared rendering contracts for v3.2.0. No model fitting, no subtitle renderer."""
from __future__ import annotations
import copy, hashlib, json, math, textwrap, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors as mc
from matplotlib.lines import Line2D
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.ticker import MaxNLocator

VERSION='3.2.0'
ROOT=Path(__file__).resolve().parent
PAL=json.loads((ROOT/'palette_snapshots_v32.json').read_text(encoding='utf-8'))
INK='#263641'; MUTED='#65757F'; GRID='#E6EBEE'; NA='#D4DADF'
REQUIRED={
 'embedding':['id','x','y','group'], 'spatial':['id','x','y','value','section'],
 'dotplot':['group','feature','mean','fraction'], 'heatmap':['group','feature','value'],
 'distribution':['id','group','value'], 'composition':['sample','group','fraction'],
 'paired':['sample','condition','value'], 'volcano':['feature','effect','q'],
 'enrichment':['term','effect','q','count'], 'trajectory':['lineage','time','mean','lower','upper'],
 'network':['source','target','weight'], 'flow':['source','target','mass'],
 'benchmark':['dataset','method','score'], 'correlation':['row','column','value'],
 'forest':['term','estimate','lower','upper'], 'upset':['item','set'],
 'ridge':['id','group','value'], 'ecdf':['id','group','value'],
 'hexbin':['id','x','y'], 'roc':['model','fpr','tpr'],
 'precision_recall':['model','recall','precision'],
 'calibration':['model','bin','predicted','observed','n'],
 'confusion':['actual','predicted','count'], 'gsea':['rank','running_score','hit','rank_metric'],
 'spatial_composition':['id','x','y','section','group','fraction'],
 'trajectory_heatmap':['gene','time','value']}
KEYS={
 'embedding':['id'], 'spatial':['id'], 'dotplot':['group','feature'], 'heatmap':['group','feature'],
 'distribution':['id'],'composition':['sample','group'],'paired':['sample','condition'],
 'volcano':['feature'],'enrichment':['term'],'trajectory':['lineage','time'],
 'network':['source','target'],'flow':['source','target'],'benchmark':['dataset','method'],
 'correlation':['row','column'],'forest':['term'],'upset':['item','set'],
 'ridge':['id'],'ecdf':['id'],'hexbin':['id'],'roc':None,'precision_recall':None,
 'calibration':['model','bin'],'confusion':['actual','predicted'],'gsea':['rank'],
 'spatial_composition':['id','group'],'trajectory_heatmap':['gene','time']}
TITLES={
 'embedding':'Cell identity and lineage hierarchy', 'spatial':'Spatial expression and tissue compartments',
 'dotplot':'Marker programmes across cell states', 'heatmap':'Expression modules and sample context',
 'distribution':'Distribution across biological samples', 'composition':'Cell composition across samples',
 'paired':'Matched sample responses','volcano':'Differential expression and annotated gene sets',
 'enrichment':'Pathway effects and supporting evidence','trajectory':'Lineage programmes over time',
 'network':'Candidate sender–receiver communication','flow':'State transitions and conserved mass',
 'benchmark':'Matched-dataset method performance','correlation':'Correlation structure',
 'forest':'Effect sizes and uncertainty','upset':'Exact intersections between gene sets',
 'ridge':'Expression distributions across ordered states','ecdf':'Cumulative sample distributions',
 'hexbin':'Density and quality-control thresholds','roc':'Discrimination across models',
 'precision_recall':'Precision–recall trade-offs','calibration':'Probability calibration',
 'confusion':'Classification errors by cell type','gsea':'Ranked enrichment profile',
 'spatial_composition':'Spatial mixtures of cell identities','trajectory_heatmap':'Temporal gene programmes'}


def order(d,key,cfg):
    levels=list(cfg.get(key+'_order',pd.unique(d[key])))
    if len(levels)!=len(set(levels)) or set(levels)!=set(d[key]):
        raise ValueError(f'{key}_order must contain each observed level exactly once')
    return levels


def palette(levels,cfg):
    """A persistent named map can contain unobserved levels; it is never regenerated."""
    pid=cfg.get('categorical_preset','C03'); explicit=cfg.get('colors')
    if explicit is not None:
        if 'categorical_preset' in cfg: raise ValueError('Use preset or explicit colors, not both')
        if not isinstance(explicit,dict) or set(levels)-set(explicit): raise ValueError('Missing named colors')
        result={x:mc.to_hex(explicit[x]) for x in levels}
    else:
        reference=cfg.get('palette_order',levels)
        if len(reference)!=len(set(reference)) or set(levels)-set(reference): raise ValueError('Invalid palette_order')
        if pid not in PAL:
            import sys
            folder=ROOT.parent/'scripts'
            if str(folder) not in sys.path: sys.path.insert(0,str(folder))
            try:
                from palette_presets import categorical_map
                all_colors=categorical_map(pid,reference)
                result={x:all_colors[x] for x in levels}
            except ImportError as exc: raise ValueError('Preset requires complete Skill repository') from exc
        else:
            values=PAL[pid]['colors']
            if not pid.startswith('C') or len(reference)>len(values): raise ValueError('Categorical palette capacity exceeded')
            complete=dict(zip(reference,values)); result={x:complete[x] for x in levels}
    if len(set(mc.to_hex(x) for x in result.values()))!=len(result): raise ValueError('Duplicate category colors')
    return result


def cmap(cfg,signed=False):
    pid=cfg.get('continuous_preset','D03' if signed else 'M02')
    if 'continuous_colors' in cfg:
        if 'continuous_preset' in cfg: raise ValueError('Use preset or explicit continuous colors')
        cm=mc.LinearSegmentedColormap.from_list('explicit',cfg['continuous_colors'])
    elif pid in PAL:
        if pid.startswith('C'): raise ValueError('Categorical preset used for scalar values')
        cm=mc.ListedColormap(PAL[pid]['colors'],name=pid)
    else:
        import sys
        if str(ROOT.parent/'scripts') not in sys.path: sys.path.insert(0,str(ROOT.parent/'scripts'))
        try:
            from palette_presets import palette_colormap
            cm=palette_colormap(pid)
        except ImportError as exc: raise ValueError('Preset requires complete Skill repository') from exc
    if cfg.get('reverse',not signed and pid=='M02' and 'continuous_preset' not in cfg): cm=cm.reversed()
    cm=cm.copy(); cm.set_bad(cfg.get('missing_color',NA))
    cm.set_under(cfg.get('under_color',cm(0.0))); cm.set_over(cfg.get('over_color',cm(1.0)))
    return cm


def normalization(cfg,values,signed=False,default=None):
    v=np.asarray(values,float); finite=v[np.isfinite(v)]
    limits=cfg.get('limits',default)
    if limits is None:
        if not len(finite): raise ValueError('All missing: supply explicit limits')
        limits=[float(finite.min()),float(finite.max())]
        if limits[0]==limits[1]: limits=[limits[0]-.5,limits[1]+.5]
    lo,hi=map(float,limits)
    if not np.isfinite([lo,hi]).all() or not lo<hi: raise ValueError('Invalid limits')
    typ=cfg.get('norm','two_slope' if signed and lo<0<hi else 'linear')
    opts=typ if isinstance(typ,dict) else {'type':typ}; typ=opts.get('type','linear')
    center=opts.get('center',cfg.get('center',0))
    if typ=='linear': norm=mc.Normalize(lo,hi)
    elif typ=='two_slope': norm=mc.TwoSlopeNorm(center,lo,hi)
    elif typ=='log':
        if lo<=0 or (finite<=0).any(): raise ValueError('Log normalization needs positive values')
        norm=mc.LogNorm(lo,hi)
    elif typ=='symlog': norm=mc.SymLogNorm(opts.get('linthresh',1),vmin=lo,vmax=hi)
    elif typ=='power': norm=mc.PowerNorm(opts.get('gamma',.5),lo,hi)
    elif typ=='boundary':
        edges=np.asarray(opts.get('boundaries',cfg.get('boundaries',[])),float)
        if len(edges)<3 or not np.isfinite(edges).all() or not np.all(np.diff(edges)>0): raise ValueError('Invalid boundaries')
        norm=mc.BoundaryNorm(edges,256)
    else: raise ValueError('Unknown normalization')
    return norm


def numeric(d,keys,allow_na=()):
    for k in keys:
        d[k]=pd.to_numeric(d[k],errors='raise')
        a=d[k].to_numpy(float)
        if np.isinf(a).any() or (k not in allow_na and np.isnan(a).any()): raise ValueError('Nonfinite '+k)


def validate(kind,d,c):
    if kind not in REQUIRED or len(d)==0: raise ValueError('Unknown kind or empty table')
    missing=set(REQUIRED[kind])-set(d)
    if missing: raise ValueError('Missing fields: '+str(missing))
    keys=KEYS[kind]
    if kind=='dotplot' and 'condition' in d: keys=keys+['condition']
    if kind=='flow' and 'stage' in d: keys=['stage']+keys
    if keys and (d[keys].isna().any().any() or d.duplicated(keys).any()): raise ValueError('Null or duplicated identity keys')
    if kind in ['roc','precision_recall'] and d.duplicated().any():raise ValueError('Duplicated curve identity row')
    nums=set(REQUIRED[kind])&set(['x','y','value','mean','fraction','effect','q','count','time','lower','upper','weight','mass','score','estimate','rank','running_score','hit','rank_metric','fpr','tpr','recall','precision','observed','n'])
    if kind=='calibration':nums.add('predicted')
    if kind in ['enrichment','roc','precision_recall','calibration']:
        if ('lower' in d)!=('upper' in d):raise ValueError('Supply both interval bounds')
        if 'lower' in d:nums.update(['lower','upper'])
    numeric(d,nums,allow_na=['value'] if kind in ['spatial','heatmap','correlation','trajectory_heatmap'] else [])
    for k in nums&{'fraction','q','fpr','tpr','recall','precision','observed'}:
        if ((d[k]<0)|(d[k]>1)).any(): raise ValueError(k+' outside [0,1]')
    if 'q' in nums and (d.q<=0).any(): raise ValueError('Provide positive q, with any plotting floor declared upstream')
    for k in nums&{'count','weight','mass','n'}:
        if (d[k]<0).any(): raise ValueError('Negative '+k)
    for k in nums&{'count','n'}:
        if not np.allclose(d[k],np.round(d[k])):raise ValueError('Non-integer count: '+k)
    if kind in ['spatial','spatial_composition']:
        if d.section.nunique()!=1 or not c.get('coordinate_unit'): raise ValueError('One section and coordinate_unit required')
    if kind=='spatial_composition':
        if not np.allclose(d.groupby('id').fraction.sum(),1,atol=1e-6): raise ValueError('Mixtures must sum to one')
        if any(d.groupby('id')[k].nunique().gt(1).any() for k in ['x','y','section']): raise ValueError('Inconsistent spot geometry')
    if kind=='composition':
        if not np.allclose(d.groupby('sample').fraction.sum(),1,atol=1e-6): raise ValueError('Fractions must sum to one within sample')
        if 'condition' in d and d.groupby('sample').condition.nunique().gt(1).any(): raise ValueError('Inconsistent sample conditions')
    if kind=='paired' and (d.condition.nunique()!=2 or not d.groupby('sample').size().eq(2).all()): raise ValueError('Incomplete pairs')
    if kind in ['trajectory','forest']:
        k='mean' if kind=='trajectory' else 'estimate'
        if ((d.lower>d[k])|(d.upper<d[k])).any(): raise ValueError('Invalid supplied interval')
        if not c.get('interval_label'): raise ValueError('Declare interval_label')
    if kind=='flow' and (d.mass.sum()<=0 or not c.get('mass_unit')): raise ValueError('Positive mass and mass_unit required')
    if kind=='network' and (d.weight.sum()<=0 or not c.get('edge_unit')): raise ValueError('Declare positive edge_unit')
    if kind=='calibration':
        if ((d.predicted<0)|(d.predicted>1)|(d.n<=0)).any(): raise ValueError('Invalid calibration bin')
        if {'lower','upper'}<=set(d):
            numeric(d,['lower','upper'])
            if ((d.lower>d.observed)|(d.upper<d.observed)|(d.lower<0)|(d.upper>1)).any(): raise ValueError('Invalid bin interval')
            if not c.get('interval_label'): raise ValueError('Declare calibration interval_label')
    if kind=='correlation':
        if (d.value.abs()>1).any():raise ValueError('Invalid r')
        mat=d.pivot(index='row',columns='column',values='value')
        if set(mat.index)!=set(mat.columns):raise ValueError('Correlation axes differ')
        mat=mat.loc[mat.columns,mat.columns]
        if not np.allclose(mat,mat.T,equal_nan=True):raise ValueError('Correlation is not symmetric')
    if kind=='gsea' and not set(d.hit)<=set([0,1]):raise ValueError('hit must be binary')
    if kind in ['roc','precision_recall']:
        if 'lower' in d and ((d.lower<0)|(d.upper>1)).any():raise ValueError('Probability interval outside [0,1]')
        if d.model.isna().any():raise ValueError('Null model identity')
        x='fpr' if kind=='roc' else 'recall'
        for _,g in d.groupby('model',sort=False):
            if len(g)<2 or (np.diff(g[x])<0).any(): raise ValueError('Curves must be provided in increasing x order')
            if kind=='roc' and (np.diff(g.tpr)<0).any():raise ValueError('ROC tpr must be nondecreasing')
    if kind in ['heatmap','composition'] and 'n' in d:
        numeric(d,['n'])
        if (d.n<0).any() or not np.allclose(d.n,np.round(d.n)):raise ValueError('Invalid count annotation')
        key='group' if kind=='heatmap' else 'sample'
        if d.groupby(key).n.nunique(dropna=False).gt(1).any():raise ValueError('Inconsistent n annotation')
    if not c.get('demo',False) and not c.get('provenance'):raise ValueError('Real data requires provenance')
    if c.get('demo') not in [True,False,None]:raise ValueError('demo must be a Boolean')


def frame(kind,c):
    width=float(c.get('width_mm',190)); height=float(c.get('height_mm',135))
    if width<80 or height<65:raise ValueError('Canvas too small for this gallery route')
    font=c.get('font_family','DejaVu Sans')
    resolved=FontProperties(fname=findfont(FontProperties(family=font))).get_name()
    if resolved!=font:warnings.warn(f'{font} unavailable; using {resolved}')
    fig=plt.figure(figsize=(width/25.4,height/25.4),facecolor='white')
    # Main title only. Old subtitle keys are ignored, never rendered.
    if c.get('title',TITLES[kind]):
        t=fig.text(.075,.94,c.get('title',TITLES[kind]),size=c.get('title_pt',11.5),weight='bold',color=INK,va='top')
        t.set_gid('main_title')
    if c.get('demo'):
        t=fig.text(.075,.025,'SYNTHETIC EXAMPLE',size=6,color=MUTED);t.set_gid('synthetic_disclosure')
    fig._actual_font=resolved;fig._config=copy.deepcopy(c);fig._kind=kind;fig._semantic_layers=[]
    box=c.get('axes_box',[.15,.17,.68,.65])
    if len(box)!=4 or min(box)<0 or box[0]+box[2]>1 or box[1]+box[3]>1 or min(box[2:])<=0:raise ValueError('Invalid axes_box')
    ax=fig.add_axes(box)
    ax.spines[['top','right']].set_visible(False)
    for s in ['left','bottom']:ax.spines[s].set_color('#AAB6BE');ax.spines[s].set_linewidth(.6)
    ax.tick_params(length=3,width=.5,labelcolor=INK,color=MUTED)
    ax.xaxis.set_major_locator(MaxNLocator(5));ax.yaxis.set_major_locator(MaxNLocator(5))
    return fig,ax


def layer(ax,name,fields):
    ax.figure._semantic_layers.append({'name':name,'fields':list(fields)})


def ticks(ax,labels,axis='x',rotation=0,width=20):
    labs=['\n'.join(textwrap.wrap(str(v),width,break_long_words=False)) for v in labels]
    if axis=='x':ax.set_xticks(np.arange(len(labs)),labs,rotation=rotation,ha='right' if rotation else 'center')
    else:ax.set_yticks(np.arange(len(labs)),labs)


def colorbar(ax,mappable,label):
    bar=ax.figure.colorbar(mappable,ax=ax,pad=.035,fraction=.045,shrink=.85)
    bar.outline.set_visible(False);bar.ax.tick_params(length=2,labelsize=7)
    bar.set_label(label,size=8)
    return bar


def key(ax,pal,title=None):
    handles=[Line2D([],[],marker='o',ls='',color=v,ms=4.2,label='\n'.join(textwrap.wrap(str(k),18,break_long_words=False))) for k,v in pal.items()]
    if len(pal)>14 or ax.figure._config.get('legend_mode')=='external':
        ax.figure._external_color_key=dict(pal)
        return None
    return ax.legend(handles=handles,title=title,frameon=False,loc='upper left',bbox_to_anchor=(1.02,1),borderaxespad=0,fontsize=7,title_fontsize=7.5)


def matrix(ax,values,xlabels,ylabels,c,*,signed=False,label='Value',default=None):
    cm=cmap(c,signed);norm=normalization(c,values,signed,default)
    im=ax.imshow(np.ma.masked_invalid(np.asarray(values,float)),interpolation='nearest',aspect='auto',cmap=cm,norm=norm)
    ticks(ax,xlabels,rotation=40);ticks(ax,ylabels,'y');ax.tick_params(length=0)
    ax.spines[['left','bottom']].set_visible(False);colorbar(ax,im,label)
    return im


def text_color(rgba):
    rgb=np.asarray(rgba[:3]);linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
    return INK if linear@np.array([.2126,.7152,.0722])>.34 else 'white'


def audit(fig):
    fig.canvas.draw();r=fig.canvas.get_renderer();outside=[];inactive=set()
    for ax in fig.axes:
        for axis in [ax.xaxis,ax.yaxis]:
            lo,hi=sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if tick.get_loc()<lo-1e-10 or tick.get_loc()>hi+1e-10:inactive|={id(tick.label1),id(tick.label2)}
    rendered=[]
    for t in fig.findobj(Text):
        if id(t) in inactive or not t.get_visible() or not t.get_text():continue
        b=t.get_window_extent(r)
        if b.width==0 or b.height==0:continue
        rendered.append({'text':t.get_text(),'size_pt':t.get_fontsize(),'gid':t.get_gid()})
        if not np.isfinite(b.extents).all() or b.x0<-.5 or b.y0<-.5 or b.x1>fig.bbox.x1+.5 or b.y1>fig.bbox.y1+.5:outside.append(t.get_text())
    return {'outside_canvas':outside,'subtitle_count':sum(t.get('gid')=='subtitle' for t in rendered),
     'rendered_text':rendered,'semantic_layers':fig._semantic_layers,'font':fig._actual_font,
     'width_mm':fig.get_figwidth()*25.4,'height_mm':fig.get_figheight()*25.4,
     'input_csv_sha256':getattr(fig,'_input_sha256',None),
     'derived_order':getattr(fig,'_derived_order',None),
     'omitted_intersections':getattr(fig,'_omitted_intersections',None),
     'axes_count':len(fig.axes),'scope':'canvas bounds and subtitle policy; not a scientific or universal collision certificate'}


def export(fig,out):
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    report=audit(fig)
    if report['outside_canvas']:raise ValueError('Outside canvas: '+repr(report['outside_canvas']))
    if report['subtitle_count']:raise ValueError('Subtitle policy violation')
    with plt.rc_context({'pdf.fonttype':42,'svg.fonttype':'none'}):
        for ext in ['png','pdf','svg']:fig.savefig(out.with_suffix('.'+ext),dpi=180,facecolor='white')
    if getattr(fig,'_external_color_key',None):
        pal=fig._external_color_key
        pd.DataFrame({'category':list(pal),'color':list(pal.values())}).to_csv(out.with_suffix('.colors.csv'),index=False)
        rows=25;cols=math.ceil(len(pal)/rows);keyfig=plt.figure(figsize=(max(7.5,cols*2.3),9.5),facecolor='white');keyax=keyfig.add_axes([0,0,1,1]);keyax.axis('off')
        keyfig.text(.04,.96,'Complete identity key',size=12,weight='bold')
        for i,(name,color) in enumerate(pal.items()):
            col=i//rows;row=i%rows;x=.04+col*.92/cols;y=.90-row*.034
            keyax.add_patch(Rectangle((x,y),.018,.017,fc=color,ec='none'))
            keyax.text(x+.025,y+.0085,str(name),size=7,va='center')
        with plt.rc_context({'pdf.fonttype':42,'svg.fonttype':'none'}):
            keyfig.savefig(out.with_suffix('.key.pdf'));keyfig.savefig(out.with_suffix('.key.png'),dpi=160)
        plt.close(keyfig)
    report['outputs']={ext:hashlib.sha256(out.with_suffix('.'+ext).read_bytes()).hexdigest() for ext in ['png','pdf','svg']}
    out.with_suffix('.qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    plt.close(fig);return report
