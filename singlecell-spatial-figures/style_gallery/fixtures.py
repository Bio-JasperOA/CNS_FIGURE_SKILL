"""Deterministic artificial tables for visual regression, never biological evidence."""
from __future__ import annotations
import numpy as np
import pandas as pd


def generate(seed: int = 81):
    rng=np.random.default_rng(seed)
    base={'demo':True,'font_family':'DejaVu Sans','width_mm':183,'height_mm':118,
          'subtitle':'Synthetic style fixture | identical data in both versions'}
    result={}
    def put(kind,rows,extra=None):
        result[kind]=(pd.DataFrame(rows),dict(base,**(extra or {})))
    groups=['T cells','B cells','Myeloid','Stromal','Endothelial','Epithelial']
    angles=np.array([-.6,.15,1.12,2.25,3.05,4.1])
    centers=np.c_[np.cos(angles)*4,np.sin(angles)*3]
    rows=[]
    for j,(g,center) in enumerate(zip(groups,centers)):
        xy=rng.normal(size=(300,2))@np.array([[.5,.15],[0,.35]])+center
        for i,(x,y) in enumerate(xy): rows.append(dict(id=f'g{j}_{i}',x=x,y=y,group=g))
    put('embedding',rows,{'title':'Cell identities on shared coordinates',
        'subtitle':'Synthetic embedding coordinates | not a computed UMAP','group_order':groups})
    xy=np.array([(x,y) for y in np.arange(0,801,25) for x in np.arange(0,1101,25)])
    keep=((xy[:,0]-550)/510)**2+((xy[:,1]-400)/345)**2<1
    xy=xy[keep]; values=3*np.exp(-((xy[:,0]-670)**2+(xy[:,1]-470)**2)/(2*185**2))+.12*rng.uniform(size=len(xy))
    regions=np.where(xy[:,0]<480,'Region A','Region B')
    put('spatial',dict(id=[f'p{i}' for i in range(len(xy))],x=xy[:,0],y=xy[:,1],value=values,
         section='section-01',region=regions),{'limits':[0,3.2],'coordinate_unit':'um','scale_bar':200,
         'point_area':12,'value_label':'Supplied expression score'})
    genes=['CD3D','IL7R','MS4A1','CD79A','LYZ','LST1','COL1A1','DCN','PECAM1','VWF','EPCAM','KRT8']
    rows=[]
    for i,g in enumerate(groups):
        for j,f in enumerate(genes):
            enriched=(j//2==i)
            rows.append(dict(group=g,feature=f,mean=float(rng.uniform(1.5,3) if enriched else rng.uniform(.0,.6)),
                fraction=float(rng.uniform(.65,.98) if enriched else rng.uniform(.03,.35)),module=groups[j//2]))
    put('dotplot',rows,{'group_order':groups,'feature_order':genes,'limits':[0,3]})
    rows=[]; heatgenes=['G01','G02','G03','G04','G05','G06','G07','G08','G09','G10','G11','G12']
    for i,f in enumerate(heatgenes):
        for j,g in enumerate(groups):
            v=float(1.8*np.cos((j-i//4*2)*np.pi/3)+rng.normal(0,.18))
            rows.append(dict(group=g,feature=f,value=v,module=f'Module {i//4+1}',n=300+20*j))
    put('heatmap',rows,{'group_order':groups,'feature_order':heatgenes,'limits':[-2.5,2.5],
        'title':'Expression modules with aligned annotations'})
    rows=[]
    for i,g in enumerate(['Reference','Early','Late']):
        for j,v in enumerate(rng.normal([1.1,1.6,2.2][i],.35,16)):
            rows.append(dict(id=f'{i}_{j}',group=g,value=float(v)))
    put('distribution',rows,{'group_order':['Reference','Early','Late'],
        'subtitle':'48 synthetic independent samples | 16 per group'})
    rows=[]
    for i in range(12):
        alpha=np.array([5,3,3,2,2,2]) if i<6 else np.array([3,2,6,4,2,2])
        fractions=rng.dirichlet(alpha*2)
        for g,f in zip(groups,fractions): rows.append(dict(sample=f'S{i+1:02d}',group=g,fraction=f,
            condition='Reference' if i<6 else 'Comparison',n=1200+31*i))
    put('composition',rows,{'group_order':groups,'sample_order':[f'S{i+1:02d}' for i in range(12)]})
    rows=[]
    for i in range(10):
        before=float(rng.normal(4,1)); after=before+float(rng.normal(1.3,1.1))
        for g,v in [('Before',before),('After',after)]: rows.append(dict(sample=f'S{i+1:02d}',condition=g,value=v))
    put('paired',rows,{'condition_order':['Before','After'],'subtitle':'10 synthetic paired biological samples | no P value invented'})
    n=320; effect=rng.normal(0,1.15,n); q=10**(-np.maximum(.02,np.abs(effect)*1.5+rng.normal(0,.6,n)))
    put('volcano',dict(feature=[f'Gene{i+1:03d}' for i in range(n)],effect=effect,q=q),
        {'effect_threshold':1,'q_threshold':.05,'label_n':6,
         'subtitle':'320 synthetic effect estimates and adjusted P values | thresholds fixed'})
    terms=['Cytokine signaling','Antigen presentation','Cell adhesion','Matrix organization','Interferon response',
           'Lipid metabolism','Cell-cycle program','Oxidative metabolism']
    put('enrichment',dict(term=terms,effect=np.array([2.4,1.8,1.35,1.1,.7,-.8,-1.1,-1.9]),
         q=10.**(-np.array([5,4.2,3.4,3.2,2.6,2.8,4.1,3.7])),count=[28,22,19,16,12,15,23,26]),
         {'effect_label':'Supplied normalized enrichment score','q_color_limits':[0,5]})
    rows=[]
    for i,g in enumerate(['Lineage A','Lineage B','Lineage C']):
        for t in np.linspace(0,1,35):
            mean=[1.5*np.exp(-((t-.25)/.22)**2)+.4,2*t+.2,1.3*np.exp(-((t-.72)/.3)**2)+.4][i]
            half=.12+.06*np.sin(t*np.pi)**2
            rows.append(dict(lineage=g,time=t,mean=mean,lower=mean-half,upper=mean+half))
    put('trajectory',rows,{'interval_label':'Band = supplied illustrative interval; not estimated confidence',
        'time_label':'Supplied developmental ordering (0-1)'})
    rows=[]
    src=['Myeloid','Stromal','T cells']; dst=['Epithelial','Endothelial','B cells']
    for i,s in enumerate(src):
        for j,t in enumerate(dst): rows.append(dict(source=s,target=t,weight=float([.9,.2,.45,.3,.85,.25,.2,.4,.72][i*3+j])))
    put('network',rows,{'title':'Candidate ligand-receptor communication','subtitle':'Synthetic aggregate interaction scores | not a causal network'})
    rows=[]
    matrix=np.array([[90,40,5],[20,70,35],[5,20,115]])
    for i,s in enumerate(['Progenitor A','Progenitor B','Progenitor C']):
        for j,t in enumerate(['State X','State Y','State Z']): rows.append(dict(source=s,target=t,mass=int(matrix[i,j])))
    put('flow',rows,{'mass_unit':'arbitrary mass units','subtitle':'Synthetic coupling table | widths retain the original aggregate mass'})
    rows=[]
    for i in range(8):
        baseline=rng.uniform(.63,.8)
        for j,g in enumerate(['Baseline','Method A','Method B','Proposed']):
            rows.append(dict(dataset=f'D{i+1:02d}',method=g,score=float(baseline+[0,.04,.07,.12][j]+rng.normal(0,.035))))
    put('benchmark',rows,{'method_order':['Baseline','Method A','Method B','Proposed'],'value_label':'Supplied held-out score',
        'subtitle':'8 synthetic matched datasets | each method uses the same evaluation set'})
    latent=rng.normal(size=(100,3)); loads=np.array([[1,0,0],[.8,.1,0],[.7,0,.3],[0,1,0],[0,.8,.2],[0,.6,-.4],[0,0,1],[0,.2,.8]])
    cov=np.corrcoef((latent@loads.T+rng.normal(0,.45,(100,8))).T); labs=[f'Program {i+1}' for i in range(8)]
    put('correlation',[dict(row=r,column=co,value=float(cov[i,j])) for i,r in enumerate(labs) for j,co in enumerate(labs)],
        {'row_order':labs,'column_order':labs,'subtitle':'Synthetic symmetric matrix | fixed range -1 to 1'})
    color_map=dict(zip(groups,['#729ECE','#FF9E4A','#67BF5C','#ED665D','#AD8BC9','#A8786E']))
    for k in ['embedding','composition','network']: result[k][1]['colors']=color_map
    return result


def high_capacity(seed=101):
    rng=np.random.default_rng(seed);rows=[];levels=[f'C{i+1:03d}' for i in range(100)]
    for i,g in enumerate(levels):
        a=2*np.pi*(i//10)/10; b=2*np.pi*(i%10)/10
        center=np.array([np.cos(a),np.sin(a)])*7+np.array([np.cos(b),np.sin(b)])*1.35
        xy=rng.normal(0,.16,(80,2))+center
        for j,(x,y) in enumerate(xy): rows.append(dict(id=f'{g}_{j}',group=g,x=x,y=y))
    return pd.DataFrame(rows),dict(demo=True,categorical_preset='C19',legend_mode='external',
      title='High-capacity categorical embedding',subtitle='100 synthetic categories / 8,000 points | not a computed UMAP',
      group_order=levels,label_groups=levels[::10],point_area=3)
