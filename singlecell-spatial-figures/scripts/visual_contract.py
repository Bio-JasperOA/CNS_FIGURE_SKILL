"""FigureSpec 3: strict visual configuration and explicit scalar semantics.

Legacy v2 analysis helpers remain separate. No model fitting or automatic data
normalization occurs here. Numeric thresholds are project policy, not journal rules.
"""
from __future__ import annotations
from copy import deepcopy
import json
import numpy as np
import matplotlib as mpl
from matplotlib import colors as mc
from jsonschema import Draft7Validator
from framework_contract import SCHEMA_PATH, validate_spec, _has_nonfinite

SUPPORTED_RENDERERS = {'embedding','spatial','marker_dot','annotated_heatmap'}

VISUAL_DEFAULTS = dict(background='#ffffff', math_fontset='dejavusans', line_spacing=1.15,
    gap_mm=2., wrap_mm=24., min_plot_mm=[18.,18.], min_delta_e=10.,
    lightness_tolerance=0.8, mark_contrast=1.5, max_repair_cycles=2)


def schema_v3():
    """Extend, rather than silently relax, the existing closed v2 schema."""
    s=json.loads(SCHEMA_PATH.read_text()); p=s['properties']; p['spec_version']={'const':'3.0'}
    num=lambda low=0: {'type':'number','exclusiveMinimum':low}
    arr={'type':'array','items':{'type':'number'},'minItems':2}
    cont=p['scales']['additionalProperties']['oneOf'][0]['properties']
    cont.update(norm={'type':'object','additionalProperties':False,'properties':{
        'type':{'enum':['linear','two_slope','log','symlog','power','boundary']},
        'center':{'type':'number'},'linthresh':num(),'linscale':num(),'base':num(1),
        'gamma':num(),'boundaries':arr},'required':['type']},
        out_of_range={'enum':['extend','clip','mask','error']},
        invalid={'enum':['mask','error']}, bad={'type':'string'},
        under={'type':'string'},over={'type':'string'},
        palette_role={'enum':['sequential','diverging','qualitative']})
    visual={
        'background':{'type':'string'},'math_fontset':{'enum':['dejavusans','dejavuserif','cm','stix','stixsans']},
        'line_spacing':num(), 'gap_mm':num(), 'wrap_mm':num(), 'max_cell_mm':num(),
        'min_plot_mm':dict(arr,maxItems=2,items=num()), 'min_delta_e':num(),
        'lightness_tolerance':num(), 'mark_contrast':num(),
        'max_repair_cycles':{'type':'integer','minimum':1},
        'reading_order':{'type':'array','items':{'type':'string'},'uniqueItems':True},
        'lead_panel':{'type':'string'}}
    p['visual']={'type':'object','properties':visual,'additionalProperties':False}
    p['guides']={'type':'object','additionalProperties':{'type':'object','additionalProperties':False,
        'properties':{'owner':{'type':'string'},'panels':{'type':'array','items':{'type':'string'},'uniqueItems':True,'minItems':1},
        'channel':{'enum':['color','category','size']},'scale_id':{'type':'string'},
        'position':{'enum':['auto','right','bottom']},'orientation':{'enum':['auto','horizontal','vertical']},
        'ticks':arr,'labels':{'type':'array','items':{'type':'string'}},
        'ncol':{'type':'integer','minimum':1},'max_ticks':{'type':'integer','minimum':2},
        'title':{'type':'string'},'font_pt':num(),'max_area_pt2':num(),'length_mm':num(),'thickness_mm':num()},
        'required':['owner','panels','channel']}}
    pp=p['panels']['items']['properties']
    pp['title']={'type':'string'}
    pp['marks']={'type':'object','additionalProperties':False,'properties':{'area_pt2':num()}}
    pp['protected_regions']={'type':'array','items':{'type':'object','additionalProperties':False,
        'properties':{'id':{'type':'string'},'bounds_data':dict(arr,minItems=4,maxItems=4)},
        'required':['id','bounds_data']}}
    return s


def legacy_view(spec):
    s=deepcopy(spec); s['spec_version']='2.0';s.pop('visual',None);s.pop('guides',None)
    for scale in s['scales'].values():
        if scale['kind']=='continuous':
            for k in list(scale):
                if k not in {'kind','limits','label','cmap'}:scale.pop(k)
    for p in s['panels']:
        for key in ['protected_regions','title','marks']:p.pop(key,None)
    return s


class ClosedBoundaryNorm(mc.BoundaryNorm):
    """Intervals [a,b), with the final endpoint included in the last bin."""
    def __call__(self,value,clip=None):
        a=np.ma.asarray(value,dtype=float)
        a=np.ma.where(a==self.vmax,np.nextafter(self.vmax,-np.inf),a)
        return super().__call__(a,clip)


class ExplicitPowerNorm(mc.PowerNorm):
    def __call__(self,value,clip=None):
        out=super().__call__(value,clip)
        if not (self.clip if clip is None else clip):out=np.ma.where(np.ma.asarray(value)<self.vmin,-1.,out)
        return out


class VisualScale:
    def __init__(self, spec):
        self.spec=deepcopy(spec);s=self.spec;lo,hi=map(float,s['limits'])
        if not np.isfinite([lo,hi]).all() or lo>=hi:raise ValueError('Scale limits must be finite and increasing.')
        self.cmap=mpl.colormaps[s['cmap']].copy();n=s.get('norm',{'type':'linear'});t=n['type']
        allowed={'linear':set(),'two_slope':{'center'},'log':set(),
            'symlog':{'linthresh','linscale','base'},'power':{'gamma'},'boundary':{'boundaries'}}
        if t not in allowed or set(n)-{'type'}-allowed[t]:raise ValueError('Unsupported or irrelevant norm parameters.')
        if t=='linear':self.norm=mc.Normalize(lo,hi)
        elif t=='two_slope':self.norm=mc.TwoSlopeNorm(vcenter=n['center'],vmin=lo,vmax=hi)
        elif t=='log':
            if lo<=0:raise ValueError('Log scale requires positive limits; zero is not a pseudocount.')
            self.norm=mc.LogNorm(lo,hi)
        elif t=='symlog':self.norm=mc.SymLogNorm(n['linthresh'],linscale=n.get('linscale',1),base=n.get('base',10),vmin=lo,vmax=hi)
        elif t=='power':
            if n['gamma']<=0:raise ValueError('gamma must be positive.')
            self.norm=ExplicitPowerNorm(n['gamma'],vmin=lo,vmax=hi)
        else:
            b=np.asarray(n['boundaries'],float)
            if not np.isfinite(b).all() or np.any(np.diff(b)<=0) or b[0]!=lo or b[-1]!=hi:
                raise ValueError('Boundary bins must increase and span the declared limits.')
            self.cmap=self.cmap.resampled(len(b)-1);self.norm=ClosedBoundaryNorm(b,self.cmap.N)
        for name in ['bad','under','over']:
            value=s.get(name,{'bad':'#bdbdbd','under':mc.to_hex(self.cmap(0.)), 'over':mc.to_hex(self.cmap(1.))}[name])
            getattr(self.cmap,'set_'+name)(value)
        if s.get('out_of_range','extend') not in {'extend','clip','mask','error'}:raise ValueError('Unknown out_of_range policy.')
        if s.get('invalid','error') not in {'mask','error'}:raise ValueError('Unknown invalid-data policy.')

    def prepare(self, values):
        """A plotting copy plus disclosure counts. Never mutate source values."""
        a=np.ma.asarray(values,dtype=float).copy();raw=np.asarray(a.data);masked=np.ma.getmaskarray(a).copy()
        missing=masked|np.isnan(raw);invalid=np.isinf(raw)&~masked
        if self.spec.get('norm',{}).get('type')=='log':invalid|=(raw<=0)&~missing
        if invalid.any() and self.spec.get('invalid','error')=='error':raise ValueError('Invalid values for the declared scale; choose invalid: mask explicitly.')
        a.mask=missing|invalid
        lo,hi=self.spec['limits'];under=(raw<lo)&~a.mask;over=(raw>hi)&~a.mask
        policy=self.spec.get('out_of_range','extend')
        if policy=='error' and (under|over).any():raise ValueError('Values exceed reviewed limits.')
        if policy=='clip':a=np.ma.array(np.clip(a.data,lo,hi),mask=a.mask)
        if policy=='mask':a.mask|=under|over
        return a,dict(n=int(a.size),missing=int(missing.sum()),invalid=int(invalid.sum()),
            under=int(under.sum()),over=int(over.sum()),out_of_range=policy)

    def ticks(self,guide):
        t=self.spec.get('norm',{}).get('type','linear')
        if 'ticks' in guide:values=np.array(guide['ticks'],float)
        elif t=='boundary':values=np.array(self.spec['norm']['boundaries'],float)
        elif t=='two_slope':values=np.array([self.norm.vmin,self.norm.vcenter,self.norm.vmax])
        else:values=np.asarray(self.norm.inverse(np.linspace(0,1,guide.get('max_ticks',4))))
        if not np.isfinite(values).all() or np.any(np.diff(values)<=0) or values[0]<self.norm.vmin or values[-1]>self.norm.vmax:
            raise ValueError('Guide ticks must be finite, increasing and within the original-unit limits.')
        labels=guide.get('labels',[f'{v:.3g}' for v in values])
        if len(labels)!=len(values):raise ValueError('Tick/label length mismatch.')
        return values,list(labels)


def validate_visual_spec(spec, *,check_files=False,root='.'):
    issues=[dict(code='SCHEMA3',severity='error',message=e.message) for e in Draft7Validator(schema_v3()).iter_errors(spec)]
    if _has_nonfinite(spec):issues.append(dict(code='NONFINITE3',severity='error',message='Configuration contains NaN/Infinity.'))
    if issues:return dict(ok=False,issues=issues)
    r=validate_spec(legacy_view(spec),check_files=check_files,root=root);issues.extend(r['issues'])
    for sid,s in spec['scales'].items():
        if s['kind']=='continuous':
            try:VisualScale(s)
            except (ValueError,KeyError,TypeError) as e:issues.append(dict(code='SCALE3',severity='error',message=f'{sid}: {e}'))
    panels={p['id']:p for p in spec['panels']};used=set()
    for pid,p in panels.items():
        if p['renderer'] not in SUPPORTED_RENDERERS:issues.append(dict(code='RENDERER3',severity='error',message=f'{pid}: renderer is not implemented in the v3 pipeline.'))
        if 'marks' in p and p['renderer'] not in {'embedding','spatial'}:issues.append(dict(code='MARKS3',severity='error',message='marks.area_pt2 applies only to non-size-encoded scatter panels.'))
        for region in p.get('protected_regions',[]):
            if min(region['bounds_data'][2:])<=0:issues.append(dict(code='PROTECTED_REGION3',severity='error',message='Protected-region width and height must be positive.'))
    for gid,g in spec.get('guides',{}).items():
        try:
            if g['owner'] not in g['panels']:raise ValueError('Guide owner must be among its panels.')
            for pid in g['panels']:
                if pid not in panels:raise ValueError('Unknown guide panel.')
                ch=g['channel'];p=panels[pid]
                if ch not in p['channels']:raise ValueError('Guide channel absent from panel.')
                if (pid,ch) in used:raise ValueError('Duplicate guide for a panel channel.')
                used.add((pid,ch))
                if ch!='size' and p['scale_ids'].get(ch)!=g.get('scale_id'):raise ValueError('Shared guide requires identical scale_id and semantics.')
                if ch=='size' and (p['renderer']!='marker_dot' or 'scale_id' in g):raise ValueError('Size guide is only for the marker fraction/area renderer.')
            if g.get('font_pt',spec['design']['font_pt'])<spec['design']['min_font_pt']:raise ValueError('Guide type is below the project minimum.')
            if g['channel']=='color':
                VisualScale(spec['scales'][g['scale_id']]).ticks(g)
                if 'ncol' in g or 'max_area_pt2' in g:raise ValueError('ncol/area do not apply to colorbars.')
            elif any(k in g for k in ['length_mm','thickness_mm','max_ticks']) or g.get('orientation','auto')!='auto':raise ValueError('Colorbar-only settings on a category/size guide; use ncol for its arrangement.')
            if g['channel']!='size' and 'max_area_pt2' in g:raise ValueError('max_area_pt2 applies only to a fraction/area guide.')
            if g['channel']=='category' and spec['scales'][g['scale_id']]['kind']!='categorical':raise ValueError('Category guide requires a categorical scale.')
            if g['channel'] in ['category','size'] and 'labels' in g:raise ValueError('Category/size labels are derived from their registered values; labels override applies only to colorbar ticks.')
            if g['channel']=='size' and any(x<=0 or x>1 for x in g.get('ticks',[.25,.5,1])):raise ValueError('Size fractions must lie in (0,1].')
        except (KeyError,ValueError) as e:issues.append(dict(code='GUIDE3',severity='error',message=f'{gid}: {e}'))
    v=spec.get('visual',{})
    if 'reading_order' in v and set(v['reading_order'])!=set(panels):issues.append(dict(code='READING_ORDER',severity='error',message='Reading order must list each panel once.'))
    if 'lead_panel' in v and v['lead_panel'] not in panels:issues.append(dict(code='LEAD_PANEL',severity='error',message='Unknown lead panel.'))
    r.update(ok=not issues,issues=issues);return r


def lab(rgb):
    """D65 CIELAB, used as a screening metric (not CAM02-UCS or DeltaE2000)."""
    a=np.asarray(rgb,float);linear=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
    xyz=linear@np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.0721750],[.0193339,.1191920,.9503041]]).T
    xyz/=np.array([.95047,1.,1.08883]);d=6/29
    f=np.where(xyz>d**3,np.cbrt(xyz),xyz/(3*d*d)+4/29)
    return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],axis=-1)


# Numerical severity-100 matrices from Machado et al. (2009), DOI
# 10.1109/TVCG.2009.113; independently applied here in linear sRGB.
# Values read from the colorspacious/cvd.py transcription of that supplement. These numeric data are not a vendored library.
CVD_MATRICES={
 'protanomaly':[[.152286,1.052583,-.204868],[.114503,.786281,.099216],[-.003882,-.048116,1.051998]],
 'deuteranomaly':[[.367322,.860646,-.227968],[.280085,.672501,.047413],[-.011820,.042940,.968881]],
 'tritanomaly':[[1.255528,-.076749,-.178779],[-.078411,.930809,.147602],[.004733,.691367,.303900]]}


def cvd_simulate(rgb,kind):
    a=np.asarray(rgb,float)
    linear=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
    shifted=linear@np.asarray(CVD_MATRICES[kind]).T
    clipped=float(np.mean(np.any((shifted<0)|(shifted>1),axis=-1)))
    shifted=np.clip(shifted,0,1)
    return np.where(shifted<=.0031308,12.92*shifted,1.055*shifted**(1/2.4)-.055),clipped


def palette_audit(scale,policy=None):
    """Lightness/contrast/deltaE76 and three endpoint CVD screens; not accessibility certification."""
    p=dict(VISUAL_DEFAULTS,**(policy or {}));cat=scale['kind']=='categorical'
    if cat:rgba=np.array([mc.to_rgba(scale['colors'][x]) for x in scale['order']]);names=scale['order']
    else:rgba=VisualScale(scale).cmap(np.linspace(0,1,33));names=list(range(33))
    bg=np.array(mc.to_rgb(p['background']));rgb=rgba[:,:3]*rgba[:,3,None]+bg*(1-rgba[:,3,None])
    labs=lab(rgb);L=labs[:,0];issues=[]
    def contrast(a,b):
        def Y(x):return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)@np.array([.2126,.7152,.0722])
        ya,yb=Y(a),Y(b);return (np.maximum(ya,yb)+.05)/(np.minimum(ya,yb)+.05)
    c=contrast(rgb,bg)
    if np.min(c)<p['mark_contrast']:issues.append('LOW_BACKGROUND_CONTRAST: use keylines/direct labels where necessary.')
    def pairs(points):
        out=[]
        for i in range(len(points)):
            for j in range(i):
                distance=float(np.linalg.norm(points[i]-points[j]))
                if distance<p['min_delta_e']:out.append(dict(a=names[j],b=names[i],deltaE76=distance))
        return out
    close=pairs(labs) if cat else []
    if close:issues.append('SIMILAR_CATEGORIES')
    if not cat:
        role=scale.get('palette_role','diverging' if scale.get('norm',{}).get('type')=='two_slope' else 'sequential')
        parts=[L[:17],L[16:]] if role=='diverging' else [L]
        if role!='qualitative':
            for a in parts:
                delta=np.diff(a);direction=np.sign(a[-1]-a[0])
                if direction==0 or np.any(delta*direction < -p['lightness_tolerance']):issues.append('LIGHTNESS_REVERSAL')
            if role=='diverging' and np.sign(parts[0][-1]-parts[0][0])==np.sign(parts[1][-1]-parts[1][0]):issues.append('NO_DIVERGING_CENTER')
    cvd={'status':'screened','model':'Machado 2009; severity=100 only; clipped to display gamut','types':{}}
    for kind in CVD_MATRICES:
        sim,gamut_clipped=cvd_simulate(rgb,kind);near=pairs(lab(sim)) if cat else []
        cvd['types'][kind]={'rgb':sim.tolist(),'close_pairs':near,'gamut_clipped_fraction':gamut_clipped}
        if near:issues.append('CVD_SIMILAR_CATEGORIES')
    return dict(metric='D65 CIELAB / deltaE76 screening only',lightness=L.tolist(),
        background_contrast=c.tolist(),close_pairs=close,issues=sorted(set(issues)),cvd=cvd,
        thresholds={k:p[k] for k in ['min_delta_e','lightness_tolerance','mark_contrast']},
        release_approval=False)
