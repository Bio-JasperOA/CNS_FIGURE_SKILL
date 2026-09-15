"""Data-bearing variants: primitives, aligned annotations, and explicit comparisons."""
from __future__ import annotations
import json, math
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform
from matplotlib import colors as mc
from matplotlib.patches import Rectangle, Polygon, Wedge, PathPatch, FancyArrowPatch
from matplotlib.path import Path as MP
from matplotlib.collections import PolyCollection
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
from chart_core import *


def embedding(ax,d,a,c):
    lev=order(d,'group',c);pal=palette(lev,c);s=d.sample(frac=1,random_state=0)
    ax.scatter(s.x,s.y,c=[pal[v] for v in s.group],s=c.get('point_area',4),alpha=.85,lw=0,rasterized=True)
    ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([]);ax.set_xlabel(c.get('x_label','Embedding 1'));ax.set_ylabel(c.get('y_label','Embedding 2'))
    key(ax,pal)
    layer(ax,'identity',['x','y','group'])
    if a:
        label_groups=c.get('label_groups',lev if len(lev)<=14 else [])
        if len(label_groups)>18:raise ValueError('Use selected label_groups or separate subtype figures')
        for i,g in enumerate(lev):
            if g not in label_groups:continue
            part=d[d.group==g];x,y=part[['x','y']].median()
            ax.text(x,y,str(g),ha='center',va='center',size=7.3,color=INK,bbox={'facecolor':'white','edgecolor':'none','alpha':.8,'pad':1})
        if c.get('abstract_edges'):
            if not c.get('edge_definition'):raise ValueError('Declare abstract graph edge_definition')
            centers=d.groupby('group')[['x','y']].median()
            for edge in c['abstract_edges']:
                if edge['source'] not in centers.index or edge['target'] not in centers.index:raise ValueError('Unknown abstract edge endpoint')
                if not np.isfinite(edge['weight']) or edge['weight']<0:raise ValueError('Invalid abstract edge weight')
                p=centers.loc[edge['source']].to_numpy();q=centers.loc[edge['target']].to_numpy()
                ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-' if not edge.get('directed',False) else '-|>',lw=.5+2*edge['weight'],color=MUTED,alpha=.5,zorder=1,connectionstyle='arc3,rad=.12'))
            layer(ax,'supplied abstract state graph',['config.abstract_edges'])
        # Biological hierarchy is provided, not inferred from the 2-D geometry.
        if 'parent' in d:
            if d.groupby('group').parent.nunique().gt(1).any():raise ValueError('Each group must have one parent')
            parents=list(pd.unique(d.parent));lim=ax.get_ylim();span=lim[1]-lim[0]
            for p,g in d.groupby('parent',sort=False):
                ax.text(g.x.median(),g.y.max()+.08*span,str(p),ha='center',size=8.5,weight='bold',color=INK)
            ax.set_ylim(lim[0],lim[1]+.20*span);layer(ax,'declared hierarchy',['parent'])
        layer(ax,'direct identity lookup',['group'])


def spatial(ax,d,a,c):
    cm=cmap(c);norm=normalization(c,d.value)
    im=ax.scatter(d.x,d.y,c=np.ma.masked_invalid(d.value.to_numpy()),cmap=cm,norm=norm,s=c.get('point_area',12),lw=0,plotnonfinite=True,rasterized=True)
    layer(ax,'spatial expression',['x','y','value'])
    if a and 'vertices' in d:
        polys=[]
        for row in d.itertuples():
            p=np.asarray(json.loads(row.vertices) if isinstance(row.vertices,str) else row.vertices,float)
            if p.ndim!=2 or p.shape[1]!=2 or len(p)<3 or not np.isfinite(p).all():raise ValueError('Invalid supplied segmentation polygon')
            polys.append(p)
        im.remove();im=PolyCollection(polys,array=np.ma.masked_invalid(d.value.to_numpy()),cmap=cm,norm=norm,edgecolor='white',linewidth=.12)
        ax.add_collection(im);ax.autoscale_view();layer(ax,'supplied segmentation',['vertices'])
    if a:
        for roi in c.get('rois',[]):
            points=np.asarray(roi['vertices'],float)
            ax.add_patch(Polygon(points,fill=False,ec=INK,lw=1.1,ls='--'))
            ax.text(points[:,0].min(),points[:,1].max(),roi['label'],va='bottom',size=8,color=INK)
        if c.get('rois'):layer(ax,'declared ROI',['config.rois'])
        if c.get('scale_bar'):
            length=float(c['scale_bar']);xr=d.x.max()-d.x.min();yr=d.y.max()-d.y.min();x=d.x.min()+.04*xr;y=d.y.min()-.10*yr
            if length<=0 or length>xr*.8:raise ValueError('Invalid scale bar length')
            ax.plot([x,x+length],[y,y],lw=2,color=INK);ax.text(x+length/2,y-.035*yr,f'{length:g} {c["coordinate_unit"]}',ha='center',va='top',size=7)
            ax.set_ylim(y-.13*yr,d.y.max()+.08*yr)
    ax.set_aspect('equal');ax.set_xlabel('x ('+c['coordinate_unit']+')');ax.set_ylabel('y ('+c['coordinate_unit']+')')
    if c.get('invert_y'):ax.invert_yaxis()
    colorbar(ax,im,c.get('value_label','Expression'))


def _module_runs(items,lookup):
    start=0;last=None
    for i,x in enumerate(items):
        cur=lookup[x]
        if i and cur!=last:yield start,i,last;start=i
        last=cur
    yield start,len(items),last


def dotplot(ax,d,a,c):
    groups=order(d,'group',c);features=order(d,'feature',c);conditions=order(d,'condition',c) if 'condition' in d else ['all']
    ng=len(conditions);cm=cmap(c);norm=normalization(c,d['mean']);pal=palette(groups,c)
    ax.set_position(c.get('axes_box',[.17,.24,.63,.54] if ng>1 else [.17,.22,.63,.57]))
    for gi,g in enumerate(groups):
        if a and gi%2==0:ax.axhspan(gi-.48,gi+.48,fc='#F2F5F6',ec='none',zorder=0)
        for ci,cond in enumerate(conditions):
            p=d[d.group==g];p=p[p.condition==cond] if 'condition' in p else p
            yy=gi+(ci-(ng-1)/2)*(.64/ng)
            area=p.fraction.to_numpy()*c.get('max_area',150)/(ng**.5)
            im=ax.scatter([features.index(x) for x in p.feature],np.repeat(yy,len(p)),s=area,c=p['mean'],cmap=cm,norm=norm,lw=.4 if ng>1 else 0,edgecolors=INK if ci==1 else 'none',zorder=3)
        if a:
            ax.add_patch(Rectangle((-.029,gi-.43),.014,.86,transform=ax.get_yaxis_transform(),clip_on=False,fc=pal[g],ec='none'))
    ticks(ax,features,rotation=45);ticks(ax,groups,'y');ax.set_ylim(len(groups)-.5,-.5);ax.set_xlim(-.5,len(features)-.5)
    ax.spines[['left','bottom']].set_visible(False);ax.tick_params(length=0);ax.tick_params(axis='y',pad=11)
    colorbar(ax,im,c.get('value_label','Mean expression'))
    sizes=[.25,.5,1];handles=[Line2D([],[],ls='',marker='o',ms=np.sqrt(x*c.get('max_area',150)/(ng**.5)),mec=MUTED,mfc='none',label=f'{x:.0%}') for x in sizes]
    ax.legend(handles=handles,title='Detected',frameon=False,bbox_to_anchor=(1.20,.25),loc='upper left',fontsize=7,title_fontsize=7)
    if ng>1:ax.text(0,-.34,'Row order: '+' / '.join(map(str,conditions)),transform=ax.transAxes,size=7,va='top',color=MUTED)
    layer(ax,'expression and detection',['mean','fraction'])
    if a and 'module' in d:
        lookup=d.drop_duplicates('feature').set_index('feature').module.to_dict()
        for start,end,module in _module_runs(features,lookup):
            ax.plot([start-.36,end-.64],[-.72,-.72],lw=2,color=INK,clip_on=False)
            ax.text((start+end-1)/2,-.89,module,ha='center',va='bottom',size=7.5,clip_on=False)
            if start:ax.axvline(start-.5,lw=.7,c='white')
        layer(ax,'gene modules',['module'])


def heatmap(ax,d,a,c):
    groups=order(d,'group',c);features=order(d,'feature',c)
    m=d.pivot(index='feature',columns='group',values='value').reindex(index=features,columns=groups)
    ax.set_position(c.get('axes_box',[.27,.22,.53,.50] if a else [.22,.19,.61,.63]))
    im=matrix(ax,m,groups,features,c,signed=True,label=c.get('value_label','Supplied z-score'))
    layer(ax,'expression matrix',['value'])
    if a:
        if 'module' in d:
            if d.groupby('feature').module.nunique().gt(1).any():raise ValueError('Ambiguous module annotation')
            lookup=d.drop_duplicates('feature').set_index('feature').module.to_dict();mods=list(dict.fromkeys(lookup[x] for x in features));colors=palette(mods,{'categorical_preset':'C03'})
            for start,end,mod in _module_runs(features,lookup):
                ax.add_patch(Rectangle((-.17,start-.5),.020,end-start,transform=ax.get_yaxis_transform(),clip_on=False,fc=colors[mod],ec='none'))
                ax.text(-.205,(start+end-1)/2,mod,transform=ax.get_yaxis_transform(),ha='right',va='center',size=7.5,color=colors[mod],weight='bold')
                if start:ax.axhline(start-.5,color='white',lw=2)
            layer(ax,'row modules',['module'])
        if 'n' in d:
            if d.groupby('group').n.nunique().gt(1).any():raise ValueError('Inconsistent group n')
            ns=d.groupby('group').n.first().reindex(groups).astype(float);scale=max(ns.max(),1)
            for i,n in enumerate(ns):
                ax.add_patch(Rectangle((i-.37,1.08),.74,.18*n/scale,transform=ax.get_xaxis_transform(),clip_on=False,fc='#698D99',ec='none'))
                ax.text(i,1.09+.18*n/scale,str(int(n)),transform=ax.get_xaxis_transform(),ha='center',va='bottom',size=6.7)
            ax.text(-.035,1.15,'n',transform=ax.transAxes,ha='right',size=7)
            layer(ax,'aligned cell counts',['n'])
        if 'condition' in d:
            if d.groupby('group').condition.nunique().gt(1).any():raise ValueError('Inconsistent column condition')
            conds=d.groupby('group').condition.first().reindex(groups);p=palette(list(pd.unique(conds)),{'categorical_preset':'C01'})
            for i,x in enumerate(conds):ax.add_patch(Rectangle((i-.5,1.025),1,.032,transform=ax.get_xaxis_transform(),clip_on=False,fc=p[x],ec='white',lw=.3))
            ax.legend(handles=[Line2D([],[],ls='',marker='s',color=v,label=k,ms=5) for k,v in p.items()],title='Condition',frameon=False,loc='upper center',bbox_to_anchor=(.5,-.28),ncol=len(p),fontsize=7,title_fontsize=7);layer(ax,'column condition',['condition'])
        if 'effect' in d:
            if not c.get('effect_label'):raise ValueError('Declare effect_label for cell text')
            ax.text(1.05,-.35,'Cell text: '+c['effect_label'],transform=ax.transAxes,ha='right',va='top',size=6.5,color=MUTED)
            eff=d.pivot(index='feature',columns='group',values='effect').reindex(index=features,columns=groups)
            for i in range(len(features)):
                for j in range(len(groups)):
                    if np.isfinite(eff.iloc[i,j]):ax.text(j,i,f'{eff.iloc[i,j]:.1f}',ha='center',va='center',size=6.2,color=text_color(im.cmap(im.norm(m.iloc[i,j]))))
            layer(ax,'cell-wise supplied effect',['effect'])


def distribution(ax,d,a,c):
    groups=order(d,'group',c);pal=palette(groups,c);rng=np.random.default_rng(52)
    conditions=order(d,'condition',c) if 'condition' in d else ['all'];width=.65/len(conditions)
    for i,g in enumerate(groups):
        for j,cond in enumerate(conditions):
            v=d[d.group==g];v=v[v.condition==cond] if 'condition' in v else v;vals=v.value.to_numpy();center=i+(j-(len(conditions)-1)/2)*width
            if not len(vals):raise ValueError('Empty group / condition combination')
            if a and len(vals)>4 and np.std(vals)>0:
                grid=np.linspace(vals.min()-.2*np.std(vals),vals.max()+.2*np.std(vals),180)
                dens=gaussian_kde(vals)(grid);dens=dens/dens.max()*width*.83
                ax.fill_betweenx(grid,center-dens,center,color=pal[g],alpha=.35 if j==0 else .65,lw=.5,edgecolor=pal[g])
            jitter=rng.uniform(.04,.18,len(vals)) if a else rng.uniform(-.13,.13,len(vals))
            ax.scatter(center+jitter,vals,s=12,c=pal[g],ec='white',lw=.4,alpha=.8,zorder=3)
            if a:
                q=np.quantile(vals,[.25,.5,.75]);ax.plot([center,center],q[[0,2]],c=INK,lw=2.4);ax.scatter(center,q[1],c='white',ec=INK,s=16,zorder=5)
                ax.text(center,1.015,f'n={len(vals)}',transform=ax.get_xaxis_transform(),ha='center',size=6.5)
    ticks(ax,groups);ax.set_ylabel(c.get('value_label','Sample-level value'));ax.set_xlim(-.6,len(groups)-.4)
    if len(conditions)>1:ax.set_xlabel('Within group: '+' / '.join(conditions))
    layer(ax,'observations',['value','id'])
    if a:layer(ax,'density, median and IQR',['value']);layer(ax,'stratified distributions',['condition'] if 'condition' in d else ['group'])


def composition(ax,d,a,c):
    samples=order(d,'sample',c);groups=order(d,'group',c);pal=palette(groups,c)
    m=d.pivot(index='group',columns='sample',values='fraction').reindex(index=groups,columns=samples)
    if m.isna().any().any():raise ValueError('Provide explicit zero fractions for absent cell types')
    if not a:
        bottom=np.zeros(len(samples))
        for g in groups:ax.bar(np.arange(len(samples)),m.loc[g],bottom=bottom,color=pal[g],width=.8,edgecolor='white',lw=.4);bottom+=m.loc[g]
        ticks(ax,samples,rotation=45);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylabel('Within-sample fraction');key(ax,pal)
    else:
        ax.set_position(c.get('axes_box',[.20,.24,.62,.53]));im=matrix(ax,m,samples,groups,dict(c,limits=[0,1],norm='linear'),label='Within-sample fraction')
        ax.tick_params(axis='y',pad=11)
        for i,g in enumerate(groups):ax.add_patch(Rectangle((-.030,i-.45),.014,.90,transform=ax.get_yaxis_transform(),fc=pal[g],ec='none',clip_on=False))
        if 'condition' in d:
            cond=d.groupby('sample').condition.first().reindex(samples);cp=palette(list(pd.unique(cond)),{'categorical_preset':'C01'})
            for start,end,state in _module_runs(samples,cond.to_dict()):
                ax.plot([start-.4,end-.6],[-.7,-.7],color=cp[state],lw=3,clip_on=False);ax.text((start+end-1)/2,-.9,state,ha='center',va='bottom',color=cp[state],size=8)
                if start:ax.axvline(start-.5,color='white',lw=2)
            layer(ax,'sample condition blocks',['condition'])
        if 'n' in d:
            nn=d.groupby('sample').n.first().reindex(samples)
            for i,n in enumerate(nn):ax.text(i,1.16,f'{int(n):,}',transform=ax.get_xaxis_transform(),ha='center',size=6.2,rotation=45)
            layer(ax,'sample denominators',['n'])
    layer(ax,'same sample-by-cell-type proportions',['fraction'])


def paired(ax,d,a,c):
    conditions=order(d,'condition',c);p=d.pivot(index='sample',columns='condition',values='value').reindex(columns=conditions);pal=palette(conditions,c)
    if not a:
        for _,r in p.iterrows():ax.plot([0,1],r,c='#B7C3C9',lw=.55,zorder=1)
        for i,g in enumerate(conditions):ax.scatter(np.repeat(i,len(p)),p[g],s=20,c=pal[g],ec='white',lw=.4,zorder=3)
        ticks(ax,conditions);ax.set_xlim(-.35,1.35);ax.set_ylabel(c.get('value_label','Value'))
    else:
        diff=(p.iloc[:,1]-p.iloc[:,0]).sort_values();ix=np.arange(len(diff));med=float(diff.median());q1,q3=np.quantile(diff,[.25,.75])
        ax.axvspan(q1,q3,color='#E8EEF0',zorder=0);ax.axvline(0,color=MUTED,lw=.7);ax.axvline(med,color=INK,lw=1,ls='--')
        ax.hlines(ix,0,diff,color=[pal[conditions[1]] if v>=0 else pal[conditions[0]] for v in diff],lw=1)
        ax.scatter(diff,ix,c=[pal[conditions[1]] if v>=0 else pal[conditions[0]] for v in diff],s=28,zorder=3)
        ticks(ax,list(diff.index),'y');ax.invert_yaxis();ax.set_xlabel(f'{conditions[1]} − {conditions[0]}');ax.set_ylabel('Matched sample')
        ax.text(.98,.98,f'Median Δ = {med:.2f}\nIQR = {q1:.2f} to {q3:.2f}',transform=ax.transAxes,ha='right',va='top',size=7.5,bbox={'fc':'white','ec':'none','alpha':.9})
        layer(ax,'within-sample difference',['sample','condition','value'])
    layer(ax,'matched observations',['sample','condition','value'])


def volcano(ax,d,a,c):
    qcut=float(c.get('q_threshold',.05));ecut=float(c.get('effect_threshold',1));y=-np.log10(d.q)
    sig=(d.q<qcut)&(d.effect.abs()>=ecut);down=sig&(d.effect<0);up=sig&(d.effect>0)
    col=np.where(up,'#C26463',np.where(down,'#3D8597','#CCD4D9'))
    ax.scatter(d.effect,y,c=col,s=10,alpha=.8,lw=0,rasterized=True)
    ax.axhline(-np.log10(qcut),c=MUTED,lw=.7,ls='--')
    for x in [-ecut,ecut]:ax.axvline(x,c=MUTED,lw=.7,ls='--')
    ax.set_xlabel(c.get('effect_label','log₂ fold change'));ax.set_ylabel('−log₁₀(q)');layer(ax,'effect and adjusted evidence',['effect','q'])
    if a:
        if 'feature_set' in d:
            for k,grp in d[d.feature_set.ne('none')].groupby('feature_set'):
                ax.scatter(grp.effect,-np.log10(grp.q),s=40,facecolors='none',edgecolors=INK,lw=.7,label=str(k))
            ax.legend(frameon=False,loc='upper left',fontsize=7);layer(ax,'supplied gene-set membership',['feature_set'])
        names=c.get('label_features',[])
        if not names:names=d.loc[sig].sort_values('q').head(c.get('n_labels',6)).feature.tolist()
        ymax=max(float(y.max()),1);xmin,xmax=float(d.effect.min()),float(d.effect.max());pad=(xmax-xmin)*.14
        for side,sel in [(-1,d[d.feature.isin(names)&(d.effect<0)]),(1,d[d.feature.isin(names)&(d.effect>=0)])]:
            sel=sel.sort_values('q');heights=np.linspace(ymax*.95,ymax*.58,len(sel))
            for (_,r),yy in zip(sel.iterrows(),heights):
                tx=xmin-pad*.6 if side==-1 else xmax+pad*.6
                ax.annotate(r.feature,(r.effect,-np.log10(r.q)),xytext=(tx,yy),ha='right' if side==-1 else 'left',va='center',fontsize=7,arrowprops={'arrowstyle':'-','lw':.5,'color':MUTED})
        ax.set_xlim(xmin-2.5*pad,xmax+2.5*pad)
        ax.text(.01,1.015,f'Down: {int(down.sum())}',transform=ax.transAxes,size=8,color='#3D8597')
        ax.text(.99,1.015,f'Up: {int(up.sum())}',transform=ax.transAxes,ha='right',size=8,color='#C26463')
        layer(ax,'fixed rule labels and direction counts',['feature','effect','q'])


def enrichment(ax,d,a,c):
    terms=order(d,'term',c);v=d.set_index('term').loc[terms];y=np.arange(len(v));cm=cmap(c);n=normalization(c,-np.log10(v.q))
    if a and v['count'].max()<=0:raise ValueError('Advanced enrichment requires positive gene counts')
    ax.set_position(c.get('axes_box',[.35,.18,.46,.64]));ax.axvline(0,c=MUTED,lw=.7)
    if a:ax.hlines(y,0,v.effect,color='#C2CCD2',lw=1.2)
    if {'lower','upper'}<=set(v):
        if not c.get('interval_label'):raise ValueError('Declare enrichment interval_label')
        if ((v.lower>v.effect)|(v.upper<v.effect)).any():raise ValueError('Invalid enrichment intervals')
        ax.errorbar(v.effect,y,xerr=[v.effect-v.lower,v.upper-v.effect],fmt='none',ecolor=MUTED,lw=.9,capsize=2)
        ax.text(0,-.21,c['interval_label'],transform=ax.transAxes,ha='left',size=6.5,color=MUTED)
        layer(ax,'supplied effect intervals',['lower','upper'])
    areas=(v['count']/max(v['count'].max(),1)*150).to_numpy() if a else 35
    im=ax.scatter(v.effect,y,c=-np.log10(v.q),cmap=cm,norm=n,s=areas,lw=.4,edgecolors='white',zorder=3)
    ticks(ax,terms,'y');ax.invert_yaxis();ax.set_xlabel(c.get('effect_label','Enrichment effect'));colorbar(ax,im,'−log₁₀(q)')
    if a:
        vals=np.unique(np.quantile(v['count'],[.25,.5,1]).astype(int));handles=[Line2D([],[],marker='o',ls='',mfc='none',mec=MUTED,ms=np.sqrt(x/v['count'].max()*150),label=str(x)) for x in vals]
        ax.legend(handles=handles,title='Genes',loc='upper left',bbox_to_anchor=(1.25,.35),frameon=False,fontsize=7,title_fontsize=7)
        if 'module' in v:
            for start,end,mod in _module_runs(terms,v.module.to_dict()):
                ax.axhspan(start-.5,end-.5,fc='#F1F4F5' if start%2==0 else 'white',zorder=0)
                if start:ax.axhline(start-.5,lw=1,c='white')
            layer(ax,'pathway groupings',['module'])
        layer(ax,'evidence and gene count',['q','count'])
    layer(ax,'signed effects',['effect'])


def trajectory(ax,d,a,c):
    lev=order(d,'lineage',c);pal=palette(lev,c);xmax=d.time.max();xmin=d.time.min();span=xmax-xmin
    endpoint_labels=[]
    for g,p in d.groupby('lineage',sort=False):
        p=p.sort_values('time');ax.plot(p.time,p['mean'],color=pal[g],lw=1.8,label=g);ax.fill_between(p.time,p.lower,p.upper,color=pal[g],alpha=.16,lw=0)
        if a:
            idx=p['mean'].idxmax();peak=p.loc[idx];ax.scatter(peak.time,peak['mean'],s=24,c=pal[g],edgecolor='white',lw=.6,zorder=5)
            endpoint_labels.append((float(p['mean'].iloc[-1]),g))
    if not a:
        existing=key(ax,pal)
        if existing is not None:ax.add_artist(existing)
    else:
        gap=max(float(d.upper.max()-d.lower.min())*.065,1e-6);previous=-float('inf')
        for actual,g in sorted(endpoint_labels):
            display=max(actual,previous+gap);previous=display
            ax.annotate(g,xy=(xmax,actual),xytext=(xmax+.035*span,display),ha='left',va='center',size=8,color=pal[g],arrowprops={'arrowstyle':'-','lw':.7,'color':pal[g]})
        ax.figure._endpoint_labels=[g for _,g in endpoint_labels]
        for i,stage in enumerate(c.get('stages',[])):
            ax.axvspan(stage['start'],stage['end'],fc='#EFF3F5',alpha=.6 if i%2==0 else 0,zorder=-1)
            ax.text((stage['start']+stage['end'])/2,1.015,stage['label'],ha='center',transform=ax.get_xaxis_transform(),size=7,color=MUTED)
        ax.set_xlim(xmin,xmax+.24*span);layer(ax,'declared stages and trend peaks',['config.stages','mean','time'])
    ax.set_xlabel(c.get('time_label','Pseudotime'));ax.set_ylabel(c.get('value_label','Supplied fitted expression'))
    ax.legend(handles=[Line2D([],[],lw=5,color='#C9D4DA',label=c['interval_label'])],frameon=False,loc='lower left',fontsize=6.7)
    layer(ax,'supplied trends and uncertainty',['mean','lower','upper'])


def network(ax,d,a,c):
    src=order(d,'source',c);dst=order(d,'target',c);nodes=list(dict.fromkeys(src+dst));pal=palette(nodes,c)
    if not a:
        pos={('s',x):(0,i) for i,x in enumerate(src)}|{('t',x):(1,i*(len(src)-1)/max(len(dst)-1,1)) for i,x in enumerate(dst)}
        mx=d.weight.max()
        for r in d.itertuples():
            if r.weight<=0:continue
            ax.add_patch(FancyArrowPatch(pos[('s',r.source)],pos[('t',r.target)],arrowstyle='->' if c.get('directed',True) else '-',mutation_scale=9,lw=3*r.weight/mx,color=pal[r.source],alpha=.4))
        for (side,name),(x,y) in pos.items():ax.scatter(x,y,s=70,c=pal[name],ec='white',zorder=4);ax.text(x+(-.07 if side=='s' else .07),y,name,ha='right' if side=='s' else 'left',va='center',size=8)
        ax.set_xlim(-.35,1.35);ax.set_ylim(-.6,max(len(src),len(dst))-.4);ax.axis('off')
    else:
        # One chord per supplied edge. Arc allocations use incoming + outgoing mass;
        # the ribbon area is geometric, while endpoint arc length encodes weight.
        ax.set_position(c.get('axes_box',[.12,.11,.76,.75]))
        outgoing=d.groupby('source').weight.sum();incoming=d.groupby('target').weight.sum()
        mass={g:float(outgoing.get(g,0)+incoming.get(g,0)) for g in nodes}
        total=sum(mass.values());gap=.075;unit=(2*np.pi-len(nodes)*gap)/total
        start_angle={};cursor=np.pi/2
        for g in nodes:start_angle[g]=cursor;cursor+=mass[g]*unit+gap
        sc={g:start_angle[g] for g in nodes};tc={g:start_angle[g]+outgoing.get(g,0)*unit for g in nodes}
        def polar(t,r=.94):return np.array([r*np.cos(t),r*np.sin(t)])
        for row in d.sort_values('weight',ascending=False).itertuples():
            if row.weight<=0:continue
            s0=sc[row.source];s1=s0+row.weight*unit;t0=tc[row.target];t1=t0+row.weight*unit
            source_arc=[polar(t) for t in np.linspace(s0,s1,12)]
            target_arc=[polar(t) for t in np.linspace(t0,t1,12)]
            verts=source_arc+[source_arc[-1]*.18,target_arc[0]*.18,target_arc[0]]+target_arc[1:]+[target_arc[-1]*.18,source_arc[0]*.18,source_arc[0],source_arc[0]]
            codes=[1]+[2]*11+[4]*3+[2]*11+[4]*3+[79]
            ax.add_patch(PathPatch(MP(verts,codes),fc=pal[row.source],ec='white',lw=.3,alpha=.60))
            if c.get('directed',True):
                middle=(t0+t1)/2
                ax.add_patch(FancyArrowPatch(polar(middle,.76),polar(middle,.94),arrowstyle='-|>',mutation_scale=8,color=pal[row.source],lw=.5))
            sc[row.source]=s1;tc[row.target]=t1
        for g in nodes:
            t0=start_angle[g];t1=t0+mass[g]*unit;middle=(t0+t1)/2;p=polar(middle,1.21)
            ax.add_patch(Wedge((0,0),1.04,np.degrees(t0),np.degrees(t1),width=.075,fc=pal[g],ec='white',lw=.5))
            ax.text(*p,g,ha='left' if p[0]>.1 else 'right' if p[0]<-.1 else 'center',va='center',size=8,color=pal[g],weight='bold')
            ax.text(*polar(middle,1.10),f'{outgoing.get(g,0):g}/{incoming.get(g,0):g}',ha='center',va='center',size=6,color=INK)
        ax.text(0,-1.47,'Node values: out / in ('+c['edge_unit']+')'+('; arrows mark receivers' if c.get('directed',True) else ''),ha='center',size=6.8,color=MUTED)
        ax.set_xlim(-1.66,1.66);ax.set_ylim(-1.57,1.49);ax.set_aspect('equal');ax.axis('off')
        layer(ax,'mass-allocated chord endpoints and node totals',['weight','source','target'])
    layer(ax,'weighted candidate edges',['weight','source','target'])


def flow(ax,d,a,c):
    stages=order(d,'stage',c) if 'stage' in d else [0];edges={st:d[d.stage==st] if 'stage' in d else d for st in stages}
    levels=[list(pd.unique(edges[stages[0]].source))]+[list(pd.unique(edges[st].target)) for st in stages]
    nodes=list(dict.fromkeys(sum(levels,[])));pal=palette(nodes,c)
    totals=[edges[stages[0]].groupby('source').mass.sum()]+[edges[st].groupby('target').mass.sum() for st in stages]
    for i in range(1,len(stages)):
        outgoing=edges[stages[i]].groupby('source').mass.sum();incoming=totals[i]
        if set(incoming.index)!=set(outgoing.index) or not np.allclose(incoming.sort_index(),outgoing.sort_index()):raise ValueError('Intermediate mass is not conserved; declare and model sources/sinks upstream')
    total=totals[0].sum();gap=total*.035;offsets=[]
    for lev,tot in zip(levels,totals):
        off={};b=0
        for x in lev:off[x]=b;b+=tot[x]+gap
        offsets.append(off)
    for i,st in enumerate(stages):
        sb=offsets[i].copy();tb=offsets[i+1].copy()
        for r in edges[st].itertuples():
            v=r.mass
            if not v:continue
            x=i;y=i+1;p=sb[r.source];q=tb[r.target]
            verts=[(x,p),(x+.42,p),(y-.42,q),(y,q),(y,q+v),(y-.42,q+v),(x+.42,p+v),(x,p+v),(x,p)]
            ax.add_patch(PathPatch(MP(verts,[1,4,4,4,2,4,4,4,79]),fc=pal[r.source],ec='white',lw=.3,alpha=.58))
            sb[r.source]+=v;tb[r.target]+=v
    for i,(lev,tot,off) in enumerate(zip(levels,totals,offsets)):
        for x in lev:
            ax.add_patch(Rectangle((i-.015,off[x]),.03,tot[x],fc=pal[x],ec='white',lw=.4))
            if i in [0,len(levels)-1]:
                ax.text(i+(-.04 if i==0 else .04),off[x]+tot[x]/2,x+(f'\n{tot[x]:g}' if a else ''),ha='right' if i==0 else 'left',va='center',size=7.5)
            elif a:ax.text(i,off[x]+tot[x]/2,f'{x}\n{tot[x]:g}',ha='center',va='center',size=6.5,bbox={'fc':'white','ec':'none','alpha':.9,'pad':1})
        name=c.get('stage_labels',[f'Stage {j+1}' for j in range(len(levels))])[i];ax.text(i,-gap*1.3,name,ha='center',size=8,weight='bold')
    ax.set_xlim(-.35,len(stages)+.35);ax.set_ylim(total+gap*max(map(len,levels)), -gap*3);ax.axis('off')
    ax.text(.5,-.06,f'Total {total:g} {c["mass_unit"]}',transform=ax.transAxes,ha='center',size=7,color=MUTED)
    layer(ax,'conserved multistage edge mass',['source','target','mass']+(['stage'] if 'stage' in d else []))
    if a:layer(ax,'per-stage node totals',['mass'])


def benchmark(ax,d,a,c):
    methods=order(d,'method',c);datasets=order(d,'dataset',c);wide=d.pivot(index='dataset',columns='method',values='score').reindex(index=datasets,columns=methods)
    if wide.isna().any().any():raise ValueError('Matched benchmark needs every dataset for each method')
    pal=palette(methods,c)
    if not a:
        for i,m in enumerate(methods):ax.scatter(np.repeat(i,len(wide)),wide[m],s=20,c=pal[m],ec='white',lw=.5)
        ticks(ax,methods);ax.set_ylabel(c.get('value_label','Score'))
    else:
        baseline=c.get('baseline_method',methods[0]);delta=wide.subtract(wide[baseline],axis=0);maxv=max(abs(delta.to_numpy()).max(),.01)
        ax.set_position(c.get('axes_box',[.23,.23,.59,.57]))
        im=matrix(ax,delta,methods,datasets,dict(c,limits=[-maxv,maxv],norm='two_slope'),signed=True,label='Score difference vs '+baseline)
        for i in range(len(datasets)):
            for j in range(len(methods)):ax.text(j,i,f'{wide.iloc[i,j]:.2f}',ha='center',va='center',size=7,color=text_color(im.cmap(im.norm(delta.iloc[i,j]))))
        for i,m in enumerate(methods):ax.text(i,-.9,f'Δ {delta[m].median():+.2f}',ha='center',va='bottom',size=7,clip_on=False)
        ax.text(.5,-.27,'Cell text = raw score; top = median paired difference',transform=ax.transAxes,ha='center',size=7,color=MUTED)
        layer(ax,'matched reference differences and raw scores',['dataset','method','score'])
    layer(ax,'dataset-level performance',['dataset','method','score'])


def correlation(ax,d,a,c):
    rows=order(d,'row',c);cols=order(d,'column',c)
    if rows!=cols:raise ValueError('Correlation row/column order must match')
    m=d.pivot(index='row',columns='column',values='value').reindex(index=rows,columns=cols)
    if a and c.get('cluster',False):
        if m.isna().any().any():raise ValueError('Cannot cluster incomplete correlation matrix')
        dist=np.sqrt(np.clip(2*(1-m.to_numpy()),0,None));np.fill_diagonal(dist,0)
        ix=leaves_list(linkage(squareform(dist,checks=False),method='average'));rows=[rows[i] for i in ix];cols=rows;m=m.iloc[ix,ix]
        ax.figure._derived_order=rows;layer(ax,'explicit display clustering',['value'])
    im=matrix(ax,m,cols,rows,dict(c,limits=[-1,1],norm='two_slope'),signed=True,label=c.get('value_label','Pearson r'))
    if a:
        for i in range(len(rows)):
            for j in range(len(cols)):
                v=m.iloc[i,j]
                if np.isfinite(v):
                    if j<=i:ax.text(j,i,f'{v:.2f}',ha='center',va='center',size=6.5,color=text_color(im.cmap(im.norm(v))))
                    else:ax.add_patch(Rectangle((j-.5,i-.5),1,1,fc='white',ec='none'));ax.scatter(j,i,s=abs(v)*100,color=im.cmap(im.norm(v)),edgecolor='none')
        layer(ax,'upper-triangle magnitude and lower-triangle numeric r',['value'])
    ax.set_aspect('equal');layer(ax,'fixed-scale correlation',['value'])


def forest(ax,d,a,c):
    terms=order(d,'term',c);p=d.set_index('term').loc[terms];yy=np.arange(len(terms));reference=c.get('reference',0)
    ax.set_position(c.get('axes_box',[.31,.18,.47,.63]));ax.axvline(reference,c=MUTED,lw=.8,ls='--')
    if a:
        for i in range(len(p)):
            if i%2==0:ax.axhspan(i-.5,i+.5,fc='#F1F4F5',zorder=0)
    ax.errorbar(p.estimate,yy,xerr=[p.estimate-p.lower,p.upper-p.estimate],fmt='o',c='#3F7F91',ecolor='#5E7987',lw=1.2,capsize=3,ms=4.8)
    ticks(ax,terms,'y');ax.invert_yaxis();ax.set_xlabel(c.get('effect_label','Effect estimate'))
    if c.get('xscale')=='log':
        if (p.lower<=0).any():raise ValueError('Log ratio intervals must be positive')
        ax.set_xscale('log')
    if a:
        for i,(_,r) in enumerate(p.iterrows()):ax.text(1.03,i,f'{r.estimate:.2f} [{r.lower:.2f}, {r.upper:.2f}]',transform=ax.get_yaxis_transform(),va='center',size=6.8)
        ax.text(1.03,1.035,c['interval_label'],transform=ax.transAxes,size=7,ha='left');layer(ax,'exact effect/interval table',['estimate','lower','upper'])
    layer(ax,'supplied effect intervals',['estimate','lower','upper'])


def upset(ax,d,a,c):
    sets=order(d,'set',c);members=d.groupby('item')['set'].agg(set)
    patterns={}
    for ss in members:pat=tuple(x in ss for x in sets);patterns[pat]=patterns.get(pat,0)+1
    patterns=sorted(patterns.items(),key=lambda z:(-z[1],-sum(z[0]),z[0]));limit=int(c.get('max_intersections',16));shown=patterns[:limit]
    if len(patterns)>limit and not c.get('allow_top_k',False):raise ValueError('Too many intersections; explicitly set allow_top_k and retain source table')
    x=np.arange(len(shown));counts=[v for _,v in shown];pal=palette(sets,c)
    if not a:
        ax.bar(x,counts,color='#628A98',width=.72);ticks(ax,[' & '.join(s for s,on in zip(sets,pat) if on) for pat,_ in shown],rotation=50,width=16);ax.set_ylabel('Exact intersection size')
    else:
        ax.set_position(c.get('axes_box',[.25,.29,.66,.52]));mx=max(counts);offset=mx*.12
        ax.bar(x,counts,color='#628A98',width=.7)
        for i,v in enumerate(counts):ax.text(i,v+mx*.025,str(v),ha='center',size=7)
        for j,s in enumerate(sets):
            yy=-(j+1)*offset
            ax.scatter(x,np.repeat(yy,len(x)),s=22,c='#D9E1E5',edgecolor='none')
            ax.text(-.8,yy,s,ha='right',va='center',size=7.5)
        for i,(pat,count) in enumerate(shown):
            ids=np.where(pat)[0];ys=-(ids+1)*offset
            if len(ids)>1:ax.plot([i,i],[ys.min(),ys.max()],c=INK,lw=1)
            ax.scatter(np.repeat(i,len(ids)),ys,s=25,c=[pal[sets[j]] for j in ids],zorder=4,edgecolor='none')
        ax.set_ylim(-(len(sets)+1)*offset,mx*1.15);ax.set_xticks([]);ax.set_yticks(np.linspace(0,mx,4,dtype=int));ax.set_ylabel('Exact intersection size')
        ax.spines['bottom'].set_visible(False);ax.axhline(0,c=MUTED,lw=.5)
        layer(ax,'aligned membership matrix',['set','item'])
    if len(patterns)>limit:
        omitted=sum(n for _,n in patterns[limit:])
        ax.text(1.0,-.17,f'{len(patterns)-limit} intersections / {omitted} items not displayed',transform=ax.transAxes,ha='right',size=7,color=MUTED)
        ax.figure._omitted_intersections={'patterns':len(patterns)-limit,'items':omitted}
    ax.figure._intersections=[{'membership':list(p),'n':n} for p,n in patterns];layer(ax,'exclusive set intersections',['item','set'])


def ridge(ax,d,a,c):
    lev=order(d,'group',c);pal=palette(lev,c);lo=d.value.min();hi=d.value.max();span=max(hi-lo,1e-6);grid=np.linspace(lo-.1*span,hi+.1*span,240)
    for i,g in enumerate(lev):
        v=d[d.group==g].value.to_numpy()
        if len(v)<5 or np.std(v)==0:raise ValueError('Ridgeline requires at least five nonconstant observations per group')
        den=gaussian_kde(v)(grid);den=den/den.max()*.8
        ax.fill_between(grid,i,i+den,color=pal[g],alpha=.6 if a else .28,lw=.6,edgecolor=pal[g])
        if a:
            q=np.quantile(v,[.25,.5,.75]);mask=(grid>=q[0])&(grid<=q[2]);ax.fill_between(grid[mask],i,i+den[mask],color=pal[g],alpha=.75)
            for p in q:ax.plot([p,p],[i,i+np.interp(p,grid,den)],c='white' if p==q[1] else pal[g],lw=1.1 if p==q[1] else .6)
            ax.text(hi+.12*span,i+.2,f'n={len(v)}',size=7,color=MUTED)
    ticks(ax,lev,'y');ax.set_ylim(-.2,len(lev));ax.set_xlabel(c.get('value_label','Expression'));ax.set_xlim(grid.min(),hi+.32*span);ax.spines[['left','top','right']].set_visible(False)
    layer(ax,'per-group KDE',['value','group'])
    if a:layer(ax,'quartiles and sample support',['value','id'])


def ecdf(ax,d,a,c):
    lev=order(d,'group',c);pal=palette(lev,c)
    for g in lev:
        v=np.sort(d[d.group==g].value.to_numpy());yy=np.arange(1,len(v)+1)/len(v)
        ax.step(np.r_[v[0],v],np.r_[0,yy],where='post',c=pal[g],lw=1.6,label=g)
        if a:
            q=np.quantile(v,[.25,.5,.75]);ax.scatter(q,[.25,.5,.75],c=pal[g],s=25,edgecolor='white',lw=.5,zorder=3)
            ax.vlines(q[1],0,.5,colors=pal[g],linestyles=':',lw=.8)
    if a:
        for q in [.25,.5,.75]:ax.axhline(q,c=GRID,lw=.6,zorder=0)
        layer(ax,'quantile locations',['value'])
    key(ax,pal);ax.set_ylim(0,1.02);ax.set_xlabel(c.get('value_label','Value'));ax.set_ylabel('Cumulative fraction');layer(ax,'empirical cumulative probabilities',['value','group'])


def hexbin(ax,d,a,c):
    if not a:ax.scatter(d.x,d.y,s=4,c='#5E8C9C',alpha=.3,lw=0,rasterized=True)
    else:
        hb=ax.hexbin(d.x,d.y,gridsize=c.get('gridsize',35),mincnt=1,cmap=cmap(c),linewidths=0,bins='log' if c.get('log_counts',True) else None)
        colorbar(ax,hb,'Observations per hexagon')
        for k,axis in [('x_thresholds','x'),('y_thresholds','y')]:
            for value in c.get(k,[]):
                (ax.axvline if axis=='x' else ax.axhline)(value,c='#B46164',lw=1,ls='--')
        layer(ax,'binned density and declared QC cutoffs',['x','y','config.thresholds'])
    ax.set_xlabel(c.get('x_label','Observed counts'));ax.set_ylabel(c.get('y_label','Detected genes'));layer(ax,'paired observations',['x','y'])


def roc(ax,d,a,c):
    _performance_curve(ax,d,a,c,'fpr','tpr','False positive rate','True positive rate')
    ax.plot([0,1],[0,1],c=MUTED,lw=.75,ls='--')


def precision_recall(ax,d,a,c):
    _performance_curve(ax,d,a,c,'recall','precision','Recall','Precision')
    if c.get('prevalence') is not None:
        if not 0<=c['prevalence']<=1:raise ValueError('Invalid prevalence')
        ax.axhline(c['prevalence'],c=MUTED,ls='--',lw=.8);ax.text(.98,c['prevalence']+.025,'Prevalence',ha='right',size=7,color=MUTED)


def _performance_curve(ax,d,a,c,x,y,xlab,ylab):
    lev=order(d,'model',c);pal=palette(lev,c)
    for g,p in d.groupby('model',sort=False):
        ax.plot(p[x],p[y],c=pal[g],lw=1.8,label=g)
        if {'lower','upper'}<=set(p):
            if not c.get('interval_label'):raise ValueError('Declare curve interval_label')
            if ((p.lower>p[y])|(p.upper<p[y])).any():raise ValueError('Invalid curve interval')
            ax.fill_between(p[x],p.lower,p.upper,color=pal[g],alpha=.12,lw=0)
        if a and 'operating_point' in p:
            z=p[p.operating_point.astype(bool)];ax.scatter(z[x],z[y],s=35,c=pal[g],ec='white',lw=.6,zorder=4)
            if 'threshold' in z:
                for r in z.to_dict('records'):ax.annotate(f'{r["threshold"]:.2f}',(r[x],r[y]),xytext=(5,-12),textcoords='offset points',size=6.5,color=pal[g])
    ax.set_xlim(0,1);ax.set_ylim(0,1.02);ax.set_aspect('equal');ax.set_xlabel(xlab);ax.set_ylabel(ylab);key(ax,pal,c.get('interval_label') if 'lower' in d else None)
    layer(ax,'supplied evaluation curves',['model',x,y])
    if a:layer(ax,'supplied interval and operating thresholds',[k for k in ['lower','upper','threshold','operating_point'] if k in d])


def calibration(ax,d,a,c):
    lev=order(d,'model',c);pal=palette(lev,c);ax.plot([0,1],[0,1],ls='--',c=MUTED,lw=.9)
    for g,p in d.groupby('model',sort=False):
        p=p.sort_values('predicted');ax.plot(p.predicted,p.observed,c=pal[g],lw=1.4)
        ax.scatter(p.predicted,p.observed,s=(p.n/d.n.max()*100) if a else 25,c=pal[g],ec='white',lw=.5,zorder=3)
        if {'lower','upper'}<=set(p):ax.errorbar(p.predicted,p.observed,yerr=[p.observed-p.lower,p.upper-p.observed],fmt='none',ecolor=pal[g],lw=.8,capsize=2,alpha=.7)
        if a:ax.vlines(p.predicted,p.predicted,p.observed,color=pal[g],lw=.7,alpha=.45)
    models=key(ax,pal,c.get('interval_label') if 'lower' in d else None)
    if a:
        if models is not None:ax.add_artist(models)
        levels=np.unique(np.maximum(1,np.round(np.array([.25,.5,1.])*d.n.max()).astype(int)))
        handles=[Line2D([],[],marker='o',ls='',mfc='none',mec=MUTED,ms=np.sqrt(n/d.n.max()*100),label=str(n)) for n in levels]
        ax.legend(handles=handles,title='Bin n',loc='upper left',bbox_to_anchor=(1.02,.42),frameon=False,fontsize=7,title_fontsize=7)
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.set_aspect('equal');ax.set_xlabel('Mean predicted probability');ax.set_ylabel('Observed fraction positive')
    layer(ax,'bin calibration',['predicted','observed'])
    if a:
        ax.text(.02,.98,'Area ∝ bin n\nSegments = calibration gap',transform=ax.transAxes,ha='left',va='top',size=7,color=MUTED)
        layer(ax,'bin support and calibration error',['n','predicted','observed'])
        if 'lower' in d:layer(ax,'supplied bin intervals',['lower','upper'])


def confusion(ax,d,a,c):
    ax.set_position(c.get('axes_box',[.22,.23,.58,.60]))
    actual=order(d,'actual',c);pred=order(d,'predicted',c);raw=d.pivot(index='actual',columns='predicted',values='count').reindex(index=actual,columns=pred)
    if raw.isna().any().any():raise ValueError('Provide explicit zero cells for unobserved confusion combinations')
    if (raw.sum(axis=1)<=0).any():raise ValueError('No observations in an actual class')
    val=raw.div(raw.sum(axis=1),axis=0) if a else raw
    im=matrix(ax,val,pred,actual,dict(c,limits=[0,1] if a else [0,max(raw.max().max(),1)],norm='linear'),label='Row fraction' if a else 'Observation count')
    for i in range(len(actual)):
        for j in range(len(pred)):
            label=f'{int(raw.iloc[i,j])}\n{val.iloc[i,j]:.0%}' if a else str(int(raw.iloc[i,j]))
            ax.text(j,i,label,ha='center',va='center',size=7,color=text_color(im.cmap(im.norm(val.iloc[i,j]))))
    ax.set_xlabel('Predicted identity');ax.set_ylabel('Observed identity')
    if a:
        ticks(ax,[f'{name}\n(n={int(n)})' for name,n in zip(actual,raw.sum(axis=1))],'y')
        layer(ax,'row denominators with retained raw counts',['count','actual'])
    layer(ax,'classification counts',['count','actual','predicted'])


def gsea(ax,d,a,c):
    p=d.sort_values('rank');ax.plot(p['rank'],p.running_score,c='#3C8390',lw=1.7);ax.axhline(0,c=MUTED,lw=.6)
    ax.set_xlabel('Position in ranked list');ax.set_ylabel('Supplied running enrichment score')
    if a:
        peak=int(p.running_score.abs().argmax());xp=p['rank'].iloc[peak];yp=p.running_score.iloc[peak]
        ax.scatter(xp,yp,c='#B36668',s=30,zorder=4);ax.plot([xp,xp],[0,yp],ls='--',c='#B36668',lw=.9)
        hits=p[p.hit.eq(1)]['rank'];span=max(p.running_score.max()-p.running_score.min(),.1);base=p.running_score.min()-.18*span
        ax.vlines(hits,base-.06*span,base+.04*span,color='#465E69',lw=.65)
        rm=p.rank_metric.to_numpy();scaled=rm/max(abs(rm).max(),1)*.17*span;offset=base-.30*span
        ax.fill_between(p['rank'],offset,offset+scaled,where=rm>=0,color='#B77373',lw=0,alpha=.75)
        ax.fill_between(p['rank'],offset,offset+scaled,where=rm<0,color='#5594A3',lw=0,alpha=.75)
        ax.set_ylim(offset-.20*span,p.running_score.max()+.10*span)
        ax.text(1.02,base,'Set hits',transform=ax.get_yaxis_transform(),va='center',size=7);ax.text(1.02,offset,'Rank metric\n(scaled track)',transform=ax.get_yaxis_transform(),va='center',size=7)
        ax.set_yticks(np.linspace(max(0,p.running_score.min()),p.running_score.max(),4))
        layer(ax,'aligned hit and ranking tracks',['hit','rank_metric','rank'])
    layer(ax,'upstream enrichment profile',['running_score','rank'])


def spatial_composition(ax,d,a,c):
    groups=order(d,'group',c);pal=palette(groups,c);m=d.pivot(index='id',columns='group',values='fraction').reindex(columns=groups)
    if m.isna().any().any():raise ValueError('Every spot needs explicit zero entries for absent components')
    coords=d.drop_duplicates('id').set_index('id').loc[m.index];r=float(c.get('spot_radius',5))
    if r<=0:raise ValueError('Positive spot_radius required in coordinate units')
    for name,row in m.iterrows():
        x,y=coords.loc[name,['x','y']];angle=0
        if not a:
            group=row.idxmax();ax.scatter(x,y,c=pal[group],s=35,lw=0)
        else:
            for g in groups:
                size=360*row[g]
                if size>0:ax.add_patch(Wedge((x,y),r,angle,angle+size,fc=pal[g],ec='white',lw=.2))
                angle+=size
    ax.set_xlim(coords.x.min()-r*2,coords.x.max()+r*2);ax.set_ylim(coords.y.min()-r*2,coords.y.max()+r*2);ax.set_aspect('equal');key(ax,pal,'Fraction by type' if a else 'Dominant type')
    ax.set_xlabel('x ('+c['coordinate_unit']+')');ax.set_ylabel('y ('+c['coordinate_unit']+')')
    layer(ax,'full mixtures' if a else 'dominant component',['fraction','group'])
    if a:layer(ax,'mass-preserving spot sectors',['fraction'])


def trajectory_heatmap(ax,d,a,c):
    times=sorted(d.time.unique());genes=order(d,'gene',c);m=d.pivot(index='gene',columns='time',values='value').reindex(index=genes,columns=times)
    if a and c.get('order_by_peak',True):
        if m.isna().all(axis=1).any():raise ValueError('Cannot peak-order an all-missing gene')
        indices=np.argsort(m.idxmax(axis=1).to_numpy(),kind='stable');m=m.iloc[indices];genes=list(m.index);ax.figure._derived_order=genes
    ax.set_position(c.get('axes_box',[.23,.19,.61,.64]));im=ax.imshow(np.ma.masked_invalid(m.to_numpy()),aspect='auto',interpolation='nearest',cmap=cmap(c),norm=normalization(c,m))
    ticks(ax,genes,'y');inds=np.linspace(0,len(times)-1,5).round().astype(int);ax.set_xticks(inds,[f'{times[i]:.2f}' for i in inds]);ax.set_xlabel(c.get('time_label','Pseudotime'));colorbar(ax,im,c.get('value_label','Supplied fitted expression'))
    if a:
        peaks=np.nanargmax(m.to_numpy(),axis=1);ax.scatter(peaks,np.arange(len(genes)),s=7,fc='none',ec=INK,lw=.6)
        if 'module' in d:
            lookup=d.drop_duplicates('gene').set_index('gene').module.to_dict();mods=list(dict.fromkeys(lookup[x] for x in genes));pal=palette(mods,c)
            for i,g in enumerate(genes):ax.add_patch(Rectangle((-.048,i-.5),.018,1,transform=ax.get_yaxis_transform(),clip_on=False,fc=pal[lookup[g]],ec='none'))
            key(ax,pal,'Module')
        layer(ax,'stable peak-time ordering and modules',['time','value']+(['module'] if 'module' in d else []))
    layer(ax,'same supplied temporal matrix',['time','value','gene'])

PLOTTERS={k:globals()[k] for k in REQUIRED}
