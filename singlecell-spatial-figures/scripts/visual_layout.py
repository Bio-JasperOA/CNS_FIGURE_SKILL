"""Measured panel/guide composition. Bounded fitting, not a universal layout solver."""
from __future__ import annotations
from copy import deepcopy
from itertools import product
import math
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib.text import Text
from matplotlib import colors as mc
from visual_contract import VisualScale,VISUAL_DEFAULTS


class LayoutFailure(ValueError):
    pass


class Measure:
    def __init__(self,fig,font,size,spacing=1.15):
        self.fig,self.font,self.size,self.spacing=fig,font,size,spacing
        fig.canvas.draw();self.renderer=fig.canvas.get_renderer();self.cache={}
    def __call__(self,text,size=None):
        size=size or self.size;k=(str(text),size)
        if k not in self.cache:
            t=Text(0,0,str(text),fontfamily=self.font,fontsize=size,linespacing=self.spacing)
            t.set_figure(self.fig);bb=t.get_window_extent(self.renderer)
            self.cache[k]=(bb.width/self.fig.dpi*25.4,bb.height/self.fig.dpi*25.4)
        return self.cache[k]
    def wrap(self,text,width,size=None):
        import re
        lines=[]
        for paragraph in str(text).split('\n'):
            if '$' in paragraph:
                if self(paragraph,size)[0]>width:raise LayoutFailure('Math label needs a wider region; do not split its expression.')
                lines.append(paragraph);continue
            current=''
            for word in re.findall(r'\S+|\s+',paragraph):
                trial=current+word
                if current and self(trial.rstrip(),size)[0]>width:
                    lines.append(current.rstrip());current=''
                if not current and word.isspace():continue
                for char in word:
                    if current and self(current+char,size)[0]>width:lines.append(current);current=''
                    current+=char
            lines.append(current.rstrip())
        return '\n'.join(lines)


def all_guides(spec):
    guides=deepcopy(spec.get('guides',{}));used={(pid,g['channel']) for g in guides.values() for pid in g['panels']}
    for p in spec['panels']:
        for ch in ['category','color','size']:
            if ch not in p['channels'] or (p['id'],ch) in used:continue
            if ch=='size' and p['renderer']!='marker_dot':continue
            g=dict(owner=p['id'],panels=[p['id']],channel=ch,position='auto',orientation='auto')
            if ch!='size':g['scale_id']=p['scale_ids'][ch]
            guides[f"{p['id']}_{ch}"]=g
    return guides


def guide_details(g,spec,tables,measure,available_w):
    g=deepcopy(g);size=g.get('font_pt',measure.size);ch=g['channel'];missing=False
    if ch=='category':
        s=spec['scales'][g['scale_id']];labels=s['order'];g['colors']=[s['colors'][x] for x in labels];title=g.get('title',s['label'])
    elif ch=='size':
        vals=g.get('ticks',[.25,.5,1.]);labels=g.get('labels',[f'{v:.0%}' for v in vals]);g['ticks']=vals
        title=g.get('title','Detected cells');g['max_area_pt2']=g.get('max_area_pt2',45.)
    else:
        s=spec['scales'][g['scale_id']];vs=VisualScale(s);vals,labels=vs.ticks(g);g['ticks']=vals.tolist();title=g.get('title',s['label'])
        for p in spec['panels']:
            if p['id'] in g['panels']:
                a,counts=vs.prepare(pd.to_numeric(tables[p['data_id']][p['channels'][ch]],errors='raise').to_numpy(float))
                missing|=bool(np.ma.getmaskarray(a).any())
                if p['renderer']=='marker_dot':missing|=bool(pd.to_numeric(tables[p['data_id']][p['channels']['size']],errors='raise').isna().any())
                if p['renderer'] in {'annotated_heatmap','marker_dot'}:
                    tab=tables[p['data_id']];cx,cy=p['channels']['x'],p['channels']['y']
                    missing|=len(tab)<tab[cx].nunique()*tab[cy].nunique()
        g['missing']=missing
    wrap=min(spec.get('visual',{}).get('wrap_mm',24.),available_w)
    g['labels']=[measure.wrap(x,wrap,size) for x in labels]
    g['title']=measure.wrap(title,wrap,size);g['font_pt']=size
    if ch=='color':
        orientation=g.get('orientation','auto')
        if orientation=='auto':orientation='vertical' if g['position']=='right' else 'horizontal'
        g['orientation']=orientation;vs=VisualScale(spec['scales'][g['scale_id']])
        g['positions']=(np.linspace(0,1,len(g['ticks'])) if isinstance(vs.norm,mc.BoundaryNorm) else np.asarray(vs.norm(g['ticks']))).tolist()
    return g


def guide_size(g,m,available_w):
    size=g['font_pt'];gap=2.;titlew,titleh=m(g['title'],size)
    lw=max([m(t,size)[0] for t in g['labels']]+[0]);lh=max([m(t,size)[1] for t in g['labels']]+[0])
    g['_title_h']=titleh+gap;g['_line_h']=max(lh,size*25.4/72)+gap
    if g['channel']=='color':
        thick=g.get('thickness_mm',3.);extra=(m('Missing / masked',size)[1]+gap) if g.get('missing') else 0
        positions=np.asarray(g['positions']);diff=np.diff(positions)
        if np.any(diff<=0):raise LayoutFailure('Guide tick positions coincide. Use a truthful, less crowded tick set.')
        spans=[m(x,size)[1 if g['orientation']=='vertical' else 0] for x in g['labels']]
        required=max([(spans[i]+spans[i+1])/2/diff[i]+gap/diff[i] for i in range(len(diff))]+[18.])
        length=g.get('length_mm',required)
        if length<required:raise LayoutFailure('Explicit colorbar length cannot accommodate its tick labels.')
        g['_length']=length;g['_thickness']=thick
        if g['orientation']=='vertical':w=max(thick+lw+3,titlew,m('Missing / masked',size)[0]+3 if g.get('missing') else 0);h=length+g['_title_h']+extra+lh
        else:w=max(length+lw,titlew,m('Missing / masked',size)[0]+3 if g.get('missing') else 0);h=thick+lh+g['_title_h']+extra+3
    else:
        symbol=max(2.,np.sqrt(g.get('max_area_pt2',12.))*25.4/72)
        g['_symbol_mm']=float(symbol);g['_line_h']=max(g['_line_h'],symbol+gap)
        cell=lw+symbol+5
        ncol=g.get('ncol',1 if g['position']=='right' else max(1,int(available_w/cell)));ncol=min(ncol,len(g['labels']))
        g['_ncol']=ncol;g['_cell_w']=cell
        w=max(titlew,ncol*cell);h=g['_title_h']+math.ceil(len(g['labels'])/ncol)*g['_line_h']+2
    return w,h


def fit_panel(fig,spec,p,box,tables,guides,font):
    """Measure labels/guides, compare right/bottom arrangements, preserve geometry.

    Only placement choices are automatic. No font shrinking, hidden categories,
    automatic clipping, data rescaling or row/column reassignment is permitted.
    """
    policy=dict(VISUAL_DEFAULTS,**spec.get('visual',{}));gap=policy['gap_mm'];d=spec['design']
    m=Measure(fig,font,d['font_pt'],policy['line_spacing']);tab=tables[p['data_id']];ch=p['channels']
    xlabels=ylabels=[];aspect=None
    if p['renderer'] in {'marker_dot','annotated_heatmap'}:
        xlabels=[str(x) for x in pd.unique(tab[ch['x']])];ylabels=[str(x) for x in pd.unique(tab[ch['y']])]
    if p['renderer'] in {'spatial','embedding'}:
        xy=tab[[ch['x'],ch['y']]].to_numpy(float)
        if not np.isfinite(xy).all():raise ValueError('Non-finite spatial/embedding coordinates.')
        span=np.ptp(xy,axis=0);aspect=float(span[0]/span[1]) if min(span)>0 else 1.
    xlabels=[m.wrap(t,policy['wrap_mm']) for t in xlabels];ylabels=[m.wrap(t,policy['wrap_mm']) for t in ylabels]
    xl=max([m(t)[1] for t in xlabels]+[0])+gap if xlabels else 0
    yl=max([m(t)[0] for t in ylabels]+[0])+gap if ylabels else 0
    own=[dict(g,id=gid) for gid,g in guides.items() if g['owner']==p['id']]
    choices=[['right','bottom'] if g.get('position','auto')=='auto' else [g['position']] for g in own]
    x,y,W,H=box['content_mm'];candidates=[];failures=[]
    title=m.wrap(p.get('title',''),W)
    title_mm=[x,y,W,m(title)[1] if title else 0]
    if title:y+=title_mm[3]+gap;H-=title_mm[3]+gap
    if H<=0:raise LayoutFailure('Panel title exhausts its content area.')
    for positions in product(*choices):
        try:
            prepared=[]
            for g,pos in zip(own,positions):
                a=guide_details(dict(g,position=pos),spec,tables,m,W-yl);a['_size']=guide_size(a,m,W-yl);prepared.append(a)
            right=[g for g in prepared if g['position']=='right'];bottom=[g for g in prepared if g['position']=='bottom']
            rw=max([g['_size'][0] for g in right]+[0]);bh=sum(g['_size'][1] for g in bottom)+gap*max(len(bottom)-1,0)
            pw=W-yl-(rw+gap if right else 0);ph=H-xl-(bh+gap if bottom else 0)
            if sum(g['_size'][1] for g in right)+gap*max(len(right)-1,0)>ph:raise LayoutFailure('Right guides exceed available height.')
            if any(g['_size'][0]>W-yl for g in bottom):raise LayoutFailure('Bottom guide exceeds available width.')
            if aspect:
                if pw/ph>aspect:pw=ph*aspect
                else:ph=pw/aspect
            if pw<policy['min_plot_mm'][0] or ph<policy['min_plot_mm'][1]:raise LayoutFailure('Data region falls below project minimum.')
            if xlabels and max(m(t)[0] for t in xlabels)+gap>pw/len(xlabels):raise LayoutFailure('Column labels need a wider panel or fewer displayed columns; identifiers were not hidden.')
            if ylabels and max(m(t)[1] for t in ylabels)+gap>ph/len(ylabels):raise LayoutFailure('Row labels need a taller panel or a split matrix.')
            cursor_r=y;cursor_b=y+ph+xl+gap
            for g in prepared:
                gw,gh=g['_size']
                if g['position']=='right':g['box_mm']=[x+W-rw,cursor_r,gw,gh];cursor_r+=gh+gap
                else:g['box_mm']=[x+yl,cursor_b,gw,gh];cursor_b+=gh+gap
            candidates.append(dict(outer_mm=box['outer_mm'],content_mm=box['content_mm'],plot_mm=[x+yl,y,pw,ph],guides=prepared,
                xlabels=xlabels,ylabels=ylabels,title=title,title_mm=title_mm,score=pw*ph,plot_area_fraction=pw*ph/(W*H)))
        except (LayoutFailure,ZeroDivisionError) as e:failures.append(str(e))
    if not candidates:raise LayoutFailure(f"{p['id']}: RESTRUCTURE_REQUIRED; "+'; '.join(sorted(set(failures))))
    return max(candidates,key=lambda c:c['score'])


def add_axis(fig,box,owner):
    x,y,w,h=box;fw,fh=fig.get_size_inches()*25.4
    ax=fig.add_axes([x/fw,1-(y+h)/fh,w/fw,h/fh]);ax._v3_owner=owner;return ax


def figure_text(fig,x,y,text,size,owner,**kwargs):
    fw,fh=fig.get_size_inches()*25.4
    artist=fig.text(x/fw,1-y/fh,text,fontsize=size,va='top',**kwargs);artist._v3_owner=owner;return artist


def draw_guide(fig,g,spec):
    x,y,w,h=g['box_mm'];size=g['font_pt'];owner=g['owner'];axes=[]
    figure_text(fig,x,y,g['title'],size,owner)
    if g['channel']=='color':
        vs=VisualScale(spec['scales'][g['scale_id']]);y+=g['_title_h'];th=g['_thickness'];length=g['_length']
        if g['orientation']=='vertical':b=[x,y+size*25.4/144,th,length]
        else:b=[x+max(len(t) for t in g['labels'])*size*.08,y,length,th]
        ax=add_axis(fig,b,owner);axes.append(ax)
        cb=fig.colorbar(mpl.cm.ScalarMappable(norm=vs.norm,cmap=vs.cmap),cax=ax,
            orientation=g['orientation'],ticks=g['ticks'],extend='both' if vs.spec.get('out_of_range','extend')=='extend' else 'neither',
            spacing='uniform' if isinstance(vs.norm,mc.BoundaryNorm) else 'proportional')
        cb.set_ticklabels(g['labels']);ax.tick_params(labelsize=size)
        if g.get('missing'):
            xx,yy=g['box_mm'][0],g['box_mm'][1]+h-size*25.4/72-1
            sw=add_axis(fig,[xx,yy,2,2],owner);sw.set_facecolor(vs.cmap.get_bad());sw.set_xticks([]);sw.set_yticks([])
            axes.append(sw);figure_text(fig,xx+3,yy,'Missing / masked',size,owner)
    else:
        ax=add_axis(fig,[x,y+g['_title_h'],w,h-g['_title_h']],owner);ax.set_axis_off();axes.append(ax)
        for i,label in enumerate(g['labels']):
            row,col=divmod(i,g['_ncol']);xx=col*g['_cell_w'];yy=row*g['_line_h']+g['_line_h']/2
            u,v=(xx+1+g['_symbol_mm']/2)/w,1-yy/(h-g['_title_h'])
            c=g['colors'][i] if g['channel']=='category' else 'none'
            area=12. if g['channel']=='category' else g['max_area_pt2']*g['ticks'][i]
            ax.scatter([u],[v],s=area,facecolors=c,edgecolors=c if g['channel']=='category' else 'black',linewidths=.5,transform=ax.transAxes)
            ax.text((xx+g['_symbol_mm']+3)/w,v,label,fontsize=size,va='center',transform=ax.transAxes)
    return axes


def draw_panel(fig,spec,p,layout,tables,guides):
    """Four implemented renderers; missing/overflow statistics accompany artists."""
    tab=tables[p['data_id']].copy();ch=p['channels'];kind=p['renderer'];pid=p['id'];box=list(layout['plot_mm']);axes=[];counts={}
    if layout.get('title'):
        figure_text(fig,*layout['title_mm'][:2],layout['title'],spec['design']['font_pt'],pid)
    for channel in ['color','size','row_metric','col_metric']:
        if channel in ch:tab[ch[channel]]=pd.to_numeric(tab[ch[channel]],errors='raise')
    if kind not in {'embedding','spatial','marker_dot','annotated_heatmap'}:raise ValueError(f'{kind}: register a reviewed project renderer; not implemented in v3.')
    if kind=='annotated_heatmap':
        if tab.duplicated([ch['x'],ch['y']]).any():raise ValueError('Duplicate heatmap cells.')
        rows=list(pd.unique(tab[ch['y']]));cols=list(pd.unique(tab[ch['x']]));x,y,w,h=box
        # Measured tick-label clearance plus a physical annotation track, not % of a panel.
        m=Measure(fig,spec['design']['font_family'],spec['design']['font_pt'])
        rw=8+max(m(f'{v:.2g}')[0] for v in tab[ch['row_metric']])+2;th=10.
        box=[x,y+th+2,w-rw-2,h-th-2]
        if min(box[2:])<min(spec.get('visual',{}).get('min_plot_mm',[18,18])):raise LayoutFailure(f'{pid}: annotation tracks require a larger panel.')
        top=add_axis(fig,[box[0],y,box[2],th],pid);side=add_axis(fig,[box[0]+box[2]+2,box[1],rw,box[3]],pid)
        for axis_key,metric in [('y','row_metric'),('x','col_metric')]:
            if (tab.groupby(ch[axis_key])[ch[metric]].nunique(dropna=False)>1).any():raise ValueError('Heatmap annotations disagree for the same ID.')
        cm=tab.drop_duplicates(ch['x']).set_index(ch['x'])[ch['col_metric']].reindex(cols)
        rm=tab.drop_duplicates(ch['y']).set_index(ch['y'])[ch['row_metric']].reindex(rows)
        top.bar(np.arange(len(cols)),cm);top.set_xlim(-.5,len(cols)-.5);top.set_xticks([])
        side.barh(np.arange(len(rows)),rm);side.set_ylim(len(rows)-.5,-.5);side.set_yticks([]);side.xaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
        axes.extend([top,side])
    ax=add_axis(fig,box,pid);axes.insert(0,ax);mappables={}
    if kind=='embedding':
        scale=spec['scales'][p['scale_ids']['category']];values=tab[ch['category']].astype(str)
        if set(values)-set(scale['colors']):raise ValueError('Unmapped categorical values.')
        order=np.random.default_rng(0).permutation(len(tab));xy=tab[[ch['x'],ch['y']]].to_numpy(float)
        ax.scatter(xy[order,0],xy[order,1],c=[scale['colors'][v] for v in values.iloc[order]],s=p.get('marks',{}).get('area_pt2',3.),linewidths=0,rasterized=True)
        ax.set_aspect('equal');ax.set_axis_off()
    else:
        vs=VisualScale(spec['scales'][p['scale_ids']['color']])
        if kind=='spatial':
            geo=p['spatial']
            if tab[geo['section_column']].isna().any() or tab[geo['section_column']].nunique()!=1:raise ValueError('Spatial panel requires exactly one nonmissing section.')
            vals,counts=vs.prepare(pd.to_numeric(tab[ch['color']],errors='raise'))
            artist=ax.scatter(tab[ch['x']],tab[ch['y']],c=vals,norm=vs.norm,cmap=vs.cmap,s=p.get('marks',{}).get('area_pt2',4.),linewidths=0,rasterized=True,plotnonfinite=True)
            ax.set_aspect('equal');ax.set_axis_off()
            if geo['y_axis_down']:ax.invert_yaxis()
        else:
            if tab.duplicated([ch['x'],ch['y']]).any():raise ValueError('Duplicate matrix/dotplot cells.')
            rows=list(pd.unique(tab[ch['y']]));cols=list(pd.unique(tab[ch['x']]))
            mat=tab.pivot(index=ch['y'],columns=ch['x'],values=ch['color']).reindex(index=rows,columns=cols)
            vals,counts=vs.prepare(mat.to_numpy(float))
            if kind=='annotated_heatmap':
                artist=ax.imshow(vals,norm=vs.norm,cmap=vs.cmap,aspect='auto',interpolation='nearest')
                if 'effect' in ch:
                    effects=tab.pivot(index=ch['y'],columns=ch['x'],values=ch['effect']).reindex(index=rows,columns=cols)
                    for i in range(len(rows)):
                        for j in range(len(cols)):
                            if pd.notna(effects.iloc[i,j]) and str(effects.iloc[i,j]).strip():
                                rgb=vs.cmap(vs.norm(vals[i,j]))[:3];ink='black' if np.dot(rgb,[.2126,.7152,.0722])>.55 else 'white'
                                ax.text(j,i,str(effects.iloc[i,j]),ha='center',va='center',color=ink)
            else:
                frac=tab.pivot(index=ch['y'],columns=ch['x'],values=ch['size']).reindex(index=rows,columns=cols).to_numpy(float)
                if np.any(np.isfinite(frac)&((frac<0)|(frac>1))):raise ValueError('Detected-cell fractions must lie in [0,1].')
                sizeguide=next(g for g in guides.values() if pid in g['panels'] and g['channel']=='size')
                yy,xx=np.indices(vals.shape);missing=np.ma.getmaskarray(vals)|~np.isfinite(frac)
                counts['missing_size']=int((~np.isfinite(frac)).sum())
                vals=np.ma.array(vals,mask=missing)
                area=np.where(missing,sizeguide.get('max_area_pt2',45.)*.25,frac*sizeguide.get('max_area_pt2',45.))
                artist=ax.scatter(xx.ravel(),yy.ravel(),s=area.ravel(),c=vals.ravel(),norm=vs.norm,cmap=vs.cmap,linewidths=0,plotnonfinite=True)
                ax.scatter(xx[missing],yy[missing],marker='x',s=12,c='black',linewidths=.5)
                ax.set_xlim(-.5,len(cols)-.5);ax.set_ylim(len(rows)-.5,-.5)
            ax.set_xticks(np.arange(len(cols)),layout['xlabels']);ax.set_yticks(np.arange(len(rows)),layout['ylabels'])
        mappables['color']=artist
    protected=[]
    for region in p.get('protected_regions',[]):
        x,y,w,h=region['bounds_data'];xy=ax.transData.transform([[x,y],[x+w,y+h]])
        protected.append(dict(id=region['id'],panel=pid,pixels=[float(xy[:,0].min()),float(xy[:,1].min()),float(np.ptp(xy[:,0])),float(np.ptp(xy[:,1]))]))
    for g in layout['guides']:axes.extend(draw_guide(fig,g,spec))
    return dict(axes=axes,mappables=mappables,disclosure=counts,protected=protected)


def design_audit(spec,layouts,tables):
    """Operational design signals. They request review, not automatic aesthetics."""
    from visual_audit import issue
    out=[];order=spec.get('visual',{}).get('reading_order')
    physical=sorted(layouts,key=lambda k:(layouts[k]['outer_mm'][1],layouts[k]['outer_mm'][0]))
    if order and order!=physical:out.append(issue('READING_ORDER_REVIEW','Declared reading order differs from top-to-bottom/left-to-right geometry.',severity='warning',declared=order,geometric=physical))
    lead=spec.get('visual',{}).get('lead_panel')
    areas={k:v['plot_mm'][2]*v['plot_mm'][3] for k,v in layouts.items()}
    if lead and areas[lead]<max(areas.values())*.75:out.append(issue('VISUAL_HIERARCHY_REVIEW','The declared lead has less than 75% of the largest data area; document a deliberate alternative emphasis.',severity='warning',panel=lead))
    for p in spec['panels']:
        l=layouts[p['id']];t=tables[p['data_id']];ch=p['channels']
        if p['renderer'] in ['marker_dot','annotated_heatmap']:
            cells=[l['plot_mm'][2]/t[ch['x']].nunique(),l['plot_mm'][3]/t[ch['y']].nunique()]
            if max(cells)>spec.get('visual',{}).get('max_cell_mm',12.):out.append(issue('INFORMATION_DENSITY_REVIEW','Large matrix cells relative to information count; consider a smaller panel or a different encoding.',severity='warning',panel=p['id'],cell_mm=cells))
    return out
