"""Deterministic synthetic data for display tests only; never used by real-data plotting."""
import json
import numpy as np
import pandas as pd

def generate():
    rng=np.random.default_rng(20260915);out={}
    celltypes=['T cells','B cells','Myeloid','Stromal','Endothelial','Epithelial']
    cellcolors=dict(zip(celltypes,['#729ECE','#FF9E4A','#67BF5C','#AD8BC9','#6DCCDA','#ED665D']))
    common={'demo':True,'width_mm':190,'height_mm':135,'subtitle':'THIS MUST NEVER BE RENDERED'}
    def add(k,rows,**c):out[k]=(pd.DataFrame(rows),dict(common,**c))
    centers=[(-4,2),(-2,4),(0,1),(3,4),(5,1),(2,-2)]
    rows=[]
    for i,(g,(x,y)) in enumerate(zip(celltypes,centers)):
        points=rng.normal(size=(260,2))@np.array([[.65,.25],[0,.43]])+[x,y]
        rows.extend({'id':f'cell{i}_{j}','x':p[0],'y':p[1],'group':g,'parent':['Immune','Immune','Immune','Tissue','Vascular','Tissue'][i]} for j,p in enumerate(points))
    add('embedding',rows,colors=cellcolors,group_order=celltypes,label_groups=celltypes,point_area=4,edge_definition='Supplied illustrative state connectivity, not inferred migration',abstract_edges=[{'source':'T cells','target':'B cells','weight':.75},{'source':'T cells','target':'Myeloid','weight':.45},{'source':'Stromal','target':'Endothelial','weight':.70},{'source':'Stromal','target':'Epithelial','weight':.30}])
    rows=[]
    for iy,y in enumerate(np.arange(0,260,12)):
        for ix,x in enumerate(np.arange(0,430,12)):
            if ((x-215)/205)**2+((y-125)/118)**2>1:continue
            val=2+2.2*np.sin(x/100)+1.2*np.cos(y/45);pts=[[float(x+5.5*np.cos(t)),float(y+5.5*np.sin(t))] for t in np.linspace(0,2*np.pi,7)[:-1]]
            rows.append({'id':f's{iy}_{ix}','x':x,'y':y,'value':val,'section':'section1','vertices':json.dumps(pts)})
    add('spatial',rows,coordinate_unit='µm',limits=[-1.5,5.5],scale_bar=80,rois=[{'label':'Region A','vertices':[[75,55],[175,55],[175,150],[75,150]]}],point_area=10)
    features=['CD3D','IL7R','MS4A1','CD79A','LYZ','LST1','COL1A1','DCN','PECAM1','VWF','EPCAM','KRT8']
    rows=[]
    for i,g in enumerate(celltypes):
        for j,f in enumerate(features):
            for cond in ['Baseline','Stimulated']:
                mean=.2+4*np.exp(-((j//2-i)/.8)**2)+(0.6 if cond=='Stimulated' and i in [0,2] else 0)+rng.uniform(0,.25)
                rows.append({'group':g,'feature':f,'condition':cond,'mean':mean,'fraction':min(.96,.04+mean/5),'module':['Lymphoid','Lymphoid','Myeloid','Matrix','Vascular','Epithelial'][j//2]})
    add('dotplot',rows,colors=cellcolors,group_order=celltypes,feature_order=features,condition_order=['Baseline','Stimulated'],limits=[0,5],height_mm=145)
    groups=[f'{s}{j}' for s in ['Early','Mid','Late'] for j in [1,2,3]];genes=[f'{m}-{i}' for m in ['TF','Cycle','Matrix'] for i in range(1,6)];rows=[]
    ns=rng.integers(350,1600,len(groups))
    for i,gene in enumerate(genes):
        for j,grp in enumerate(groups):
            v=1.9*np.cos((i//5-j//3)*2.1)+rng.normal(0,.28)
            rows.append({'feature':gene,'group':grp,'value':v,'module':['TF','Cycle','Matrix'][i//5],'n':int(ns[j]),'condition':['Early','Mid','Late'][j//3]})
    add('heatmap',rows,group_order=groups,feature_order=genes,limits=[-2.5,2.5],value_label='Supplied expression z-score')
    rows=[]
    for i,g in enumerate(['State A','State B','State C','State D']):
        for condition in ['Control','Perturbed']:
            for j,v in enumerate(rng.normal(1.5+i*.4+(.55 if condition=='Perturbed' else 0),.30+i*.06,36)):
                rows.append({'id':f'{g}-{condition}-{j}','group':g,'condition':condition,'value':float(v)})
    add('distribution',rows,condition_order=['Control','Perturbed'],value_label='Sample-level module score')
    rows=[]
    for i in range(12):
        p=rng.dirichlet(np.array([5,3,2,2,1,1]) if i<6 else np.array([2,1,5,3,2,1]));n=int(rng.integers(800,3000))
        for g,frac in zip(celltypes,p):rows.append({'sample':f'D{i+1:02d}','group':g,'fraction':float(frac),'condition':'Reference' if i<6 else 'Disease','n':n})
    add('composition',rows,colors=cellcolors,group_order=celltypes,height_mm=145)
    rows=[]
    for i in range(16):
        before=float(rng.normal(2,.45));after=before+float(rng.normal(.65,.5))
        rows.extend([{'sample':f'Donor {i+1:02d}','condition':'Before','value':before},{'sample':f'Donor {i+1:02d}','condition':'After','value':after}])
    add('paired',rows,condition_order=['Before','After'],categorical_preset='C01',height_mm=145)
    effects=rng.normal(0,1,500);q=np.maximum(10**(-np.abs(effects)*1.7-rng.uniform(0,1,500)),1e-9)
    rows=[{'feature':f'Gene{i:03d}','effect':float(e),'q':float(qq),'feature_set':'Regulators' if i%35==0 else 'none'} for i,(e,qq) in enumerate(zip(effects,q))]
    add('volcano',rows,q_threshold=.05,effect_threshold=1,n_labels=6)
    rows=[]
    terms=['Cytokine signalling','Antigen presentation','Interferon response','T cell activation','Matrix organisation','Collagen assembly','Cell adhesion','Vascular development','Oxidative metabolism','Fatty acid transport']
    for i,term in enumerate(terms):
        effect=float(np.linspace(2.3,-1.8,10)[i]);rows.append({'term':term,'effect':effect,'q':float(10**(-rng.uniform(1.5,6))),'count':int(rng.integers(12,70)),'module':['Immune','Immune','Immune','Immune','Tissue','Tissue','Tissue','Tissue','Metabolic','Metabolic'][i],'lower':effect-.25,'upper':effect+.32})
    add('enrichment',rows,term_order=terms,interval_label='Supplied illustrative interval',effect_label='Supplied enrichment effect',limits=[1,6],height_mm=145)
    rows=[]
    for i,g in enumerate(['Early programme','Transient programme','Late programme']):
        for t in np.linspace(0,1,60):
            mean=[2.7*np.exp(-4*t),2.2*np.exp(-((t-.5)/.19)**2),2.8/(1+np.exp(-10*(t-.65)))][i]
            rows.append({'lineage':g,'time':float(t),'mean':float(mean),'lower':float(mean-.16),'upper':float(mean+.16)})
    add('trajectory',rows,interval_label='Supplied illustrative interval',stages=[{'start':0,'end':.3,'label':'Early'},{'start':.3,'end':.65,'label':'Transition'},{'start':.65,'end':1,'label':'Late'}])
    rows=[{'source':s,'target':t,'weight':float(rng.integers(1,10))} for i,s in enumerate(celltypes) for j,t in enumerate(celltypes) if i!=j and (i+j)%3!=0]
    add('network',rows,colors=cellcolors,edge_unit='score',directed=True)
    rows=[]
    m=np.array([[70,20,10],[15,65,20],[5,20,75]],float)
    for stage in [0,1]:
        names=['Progenitor','Intermediate','Committed'] if stage==0 else ['Branch A','Branch B','Branch C'];targets=['Branch A','Branch B','Branch C'] if stage==0 else ['Fate A','Fate B','Fate C']
        mm=m if stage==0 else np.diag(m.sum(axis=0))@np.array([[.8,.15,.05],[.1,.8,.1],[.05,.15,.8]])
        rows += [{'stage':stage,'source':names[i],'target':targets[j],'mass':float(mm[i,j])} for i in range(3) for j in range(3)]
    add('flow',rows,mass_unit='coupling units',stage_order=[0,1],stage_labels=['Input state','Lineage branch','Outcome'],width_mm=210)
    methods=['Baseline','Model B','Model C','Model D'];rows=[]
    for i in range(10):
        baseline=float(rng.uniform(.55,.82))
        for j,meth in enumerate(methods):rows.append({'dataset':f'Dataset {i+1:02d}','method':meth,'score':float(np.clip(baseline+[0,.03,.065,.09][j]+rng.normal(0,.025),0,1))})
    add('benchmark',rows,method_order=methods,baseline_method='Baseline',continuous_preset='D03')
    x=rng.normal(size=(90,8));x[:,1]=x[:,0]*.8+rng.normal(0,.4,90);x[:,5]=-x[:,4]*.7+rng.normal(0,.5,90);corr=np.corrcoef(x.T);labels=[f'Module {i+1}' for i in range(8)]
    add('correlation',[{'row':r,'column':s,'value':float(corr[i,j])} for i,r in enumerate(labels) for j,s in enumerate(labels)],row_order=labels,column_order=labels,cluster=True)
    terms=['T-cell abundance','B-cell abundance','Myeloid state','Matrix programme','Vascular score','Inflammation','Differentiation','Stress response'];rows=[]
    for i,term in enumerate(terms):
        e=float(np.linspace(1.4,-.9,8)[i]);rows.append({'term':term,'estimate':e,'lower':e-.28-.04*(i%3),'upper':e+.25+.05*(i%2)})
    add('forest',rows,term_order=terms,interval_label='Illustrative interval',effect_label='Supplied effect estimate',width_mm=210)
    rows=[];sets=['RNA','ATAC','Protein','Spatial']
    patterns=[(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),(1,1,0,0),(1,0,1,0),(1,0,0,1),(1,1,1,0),(1,1,1,1)]
    for i,pattern in enumerate(patterns):
        for item in range(int(42-3*i)):
            for name,on in zip(sets,pattern):
                if on:rows.append({'item':f'feature_{i}_{item}','set':name})
    add('upset',rows,set_order=sets,height_mm=150,width_mm=205)
    rows=[]
    for i in range(7):
        rows.extend({'id':f'r{i}_{j}','group':f'Day {i+1}','value':float(v)} for j,v in enumerate(rng.normal(1+i*.5,.4+.05*i,70)))
    add('ridge',rows,value_label='Supplied expression value')
    rows=[]
    for i,g in enumerate(['Control','Low dose','High dose']):rows.extend({'id':f'e{i}_{j}','group':g,'value':float(v)} for j,v in enumerate(rng.lognormal(.1+i*.4,.5,150)))
    add('ecdf',rows,value_label='Sample response')
    x=rng.gamma(3,1100,5500);y=np.sqrt(x)*45+rng.normal(0,130,len(x))
    add('hexbin',[{'id':i,'x':float(xx),'y':float(yy)} for i,(xx,yy) in enumerate(zip(x,y))],x_label='Library size (counts)',y_label='Detected genes',x_thresholds=[1200,8500],y_thresholds=[1000],gridsize=40)
    for kind in ['roc','precision_recall']:
        rows=[]
        for i,meth in enumerate(['Baseline','Multimodal','Fine-tuned']):
            for j,t in enumerate(np.linspace(0,1,45)):
                val=1-(1-t)**(2.5+1.3*i) if kind=='roc' else 1-.75*t**(2+i*.5)
                row={'model':meth,('fpr' if kind=='roc' else 'recall'):float(t),('tpr' if kind=='roc' else 'precision'):float(val),'lower':max(0,float(val-.045)),'upper':min(1,float(val+.045)),'threshold':float(1-t),'operating_point':j==12+5*i}
                rows.append(row)
        add(kind,rows,interval_label='Supplied illustrative band',prevalence=.25)
    rows=[]
    for i,meth in enumerate(['Uncalibrated','Calibrated']):
        for j,x in enumerate(np.linspace(.07,.93,8)):
            obs=float(np.clip(x**(.62 if i==0 else 1.03),0,1));rows.append({'model':meth,'bin':j,'predicted':float(x),'observed':obs,'n':int(90+180*np.sin(x*np.pi)),'lower':max(0,obs-.06),'upper':min(1,obs+.06)})
    add('calibration',rows,interval_label='Supplied illustrative bin interval')
    labels=celltypes[:5];m=rng.integers(0,12,(5,5))+np.eye(5,dtype=int)*rng.integers(60,150,(5,))
    add('confusion',[{'actual':r,'predicted':s,'count':int(m[i,j])} for i,r in enumerate(labels) for j,s in enumerate(labels)],actual_order=labels,predicted_order=labels)
    ranks=np.arange(1,201);hit=np.zeros(200,int);hit[np.r_[rng.choice(np.arange(0,70),23,False),rng.choice(np.arange(70,200),12,False)]]=1
    metric=np.linspace(2.5,-2,200);weights=abs(metric)*hit;running=np.cumsum(weights/weights.sum()-(1-hit)/(1-hit).sum())
    add('gsea',[{'rank':int(i),'running_score':float(e),'hit':int(h),'rank_metric':float(m)} for i,e,h,m in zip(ranks,running,hit,metric)])
    rows=[]
    for iy,y in enumerate(np.arange(0,150,16)):
        for ix,x in enumerate(np.arange(0,240,16)):
            if ((x-115)/118)**2+((y-65)/65)**2>1:continue
            vec=rng.dirichlet([1.2+(x<100)*4,1.2+(y>60)*4,2+(x>120)*4]);
            rows.extend({'id':f'p{ix}_{iy}','x':x,'y':y,'section':'section1','group':g,'fraction':float(v)} for g,v in zip(celltypes[:3],vec))
    add('spatial_composition',rows,colors={g:cellcolors[g] for g in celltypes[:3]},coordinate_unit='µm',spot_radius=6.6)
    rows=[];geneorder=[]
    for i in rng.permutation(24):
        g=f'Gene {i+1:02d}';geneorder.append(g)
        for t in np.linspace(0,1,60):rows.append({'gene':g,'time':float(t),'value':float(.1+3*np.exp(-((t-(i/26+.03))/.14)**2)),'module':['Early','Middle','Late'][min(i//8,2)]})
    add('trajectory_heatmap',rows,gene_order=geneorder,limits=[0,3.2],height_mm=155,value_label='Supplied fitted expression',order_by_peak=True)
    return out


def high_capacity():
    rng=np.random.default_rng(35);rows=[]
    for i in range(100):
        center=np.array([i%10,i//10])*2;points=center+rng.normal(0,.2,(45,2))
        rows.extend({'id':f'c{i}_{j}','group':f'Type {i+1:03d}','x':float(x),'y':float(y)} for j,(x,y) in enumerate(points))
    return pd.DataFrame(rows),{'demo':True,'categorical_preset':'C19','label_groups':[f'Type {i+1:03d}' for i in range(0,100,10)],'legend_mode':'external','width_mm':190,'height_mm':160}
