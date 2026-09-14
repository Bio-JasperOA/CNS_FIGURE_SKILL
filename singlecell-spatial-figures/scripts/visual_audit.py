"""Geometry, font, PDF-carrier and raster-regression checks shared across backends.

Bounding-box overlap is a conservative warning, not a glyph-level occlusion proof.
A render/PDF check cannot decide a biological claim or validate a statistical model.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib,json
import numpy as np
from matplotlib.text import Text
from matplotlib import font_manager,ft2font
from matplotlib.mathtext import MathTextParser


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def issue(code,message,*,severity='error',**context):
    payload=dict(code=code,message=message,severity=severity,**context)
    payload['id']=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
    return payload


def overlap(a,b):
    return max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))


def contained(a,b,tolerance=.2):
    return a[0]>=b[0]-tolerance and a[1]>=b[1]-tolerance and a[0]+a[2]<=b[0]+b[2]+tolerance and a[1]+a[3]<=b[1]+b[3]+tolerance


def geometry_audit(items,canvas,*,panels=None,protected=(),min_font_pt=6.,max_items=10000):
    issues=[];items=[i for i in items if i['box_mm'][2]>0 and i['box_mm'][3]>0]
    if len(items)>max_items:return [issue('GEOMETRY_BUDGET','Inspection budget exceeded; split the figure or explicitly increase the audit budget.')]
    for a in items:
        b=a['box_mm'];pid=a.get('panel')
        if not contained(b,canvas):issues.append(issue('TEXT_OUTSIDE_CANVAS',a['text'],element=a['id'],panel=pid))
        if a.get('font_pt',min_font_pt)<min_font_pt-1e-5:issues.append(issue('FINAL_FONT_TOO_SMALL',a['text'],element=a['id'],font_pt=a['font_pt'],panel=pid))
        for other,boxes in (panels or {}).items():
            target=boxes.get('plot_mm',boxes.get('content_mm'))
            if pid and other!=pid and overlap(b,target)>.05*b[2]*b[3]:issues.append(issue('CROSS_PANEL_INTRUSION',a['text'],element=a['id'],panel=pid,into=other))
        for r in protected:
            if overlap(b,r['box_mm'])>0:issues.append(issue('PROTECTED_REGION_OCCLUDED',a['text'],element=a['id'],region=r['id'],severity='warning'))
        if a.get('clip_mm') and not contained(b,a['clip_mm']):issues.append(issue('LOCAL_TEXT_CLIP',a['text'],element=a['id'],panel=pid))
    active=[]
    for a in sorted(items,key=lambda i:i['box_mm'][0]):
        b=a['box_mm'];active=[q for q in active if q['box_mm'][0]+q['box_mm'][2]>b[0]]
        for q in active:
            qb=q['box_mm'];ratio=overlap(b,qb)/min(b[2]*b[3],qb[2]*qb[3])
            if ratio>.12:issues.append(issue('TEXT_COLLISION',f"{a['text']} | {q['text']}",severity='warning',elements=sorted([a['id'],q['id']]),overlap_fraction=round(ratio,4)))
        active.append(a)
    return issues


def inspect_figure(fig,spec,layouts,results):
    fig.canvas.draw();renderer=fig.canvas.get_renderer();factor=25.4/fig.dpi;fw,fh=fig.get_size_inches()*25.4
    def box(bb):return [bb.x0*factor,fh-bb.y1*factor,bb.width*factor,bb.height*factor]
    excluded=set();issues=[];items=[];fonts={};math_fonts=set();charmaps={};parser=MathTextParser('path')
    for ax in fig.axes:
        for axis in [ax.xaxis,ax.yaxis]:
            lo,hi=sorted(axis.get_view_interval())
            for tick in list(axis.get_major_ticks())+list(axis.get_minor_ticks()):
                if not ax.axison or not axis.get_visible() or not(lo-1e-10<=tick.get_loc()<=hi+1e-10):excluded.update([id(tick.label1),id(tick.label2)])
            if not ax.axison:excluded.update([id(axis.label),id(axis.get_offset_text())])
    for index,t in enumerate(fig.findobj(match=Text)):
        if id(t) in excluded or not t.get_visible() or not t.get_text().strip():continue
        text=t.get_text();pid=getattr(t,'_v3_owner',getattr(t.axes,'_v3_owner',None));bb=t.get_window_extent(renderer)
        item=dict(id=f'text-{index}',text=text,panel=pid,box_mm=box(bb),font_pt=float(t.get_fontsize()))
        if t.get_clip_on() and t.get_clip_box() is not None:item['clip_mm']=box(t.get_clip_box())
        items.append(item)
        props=t.get_fontproperties();path=font_manager.findfont(props);name=ft2font.FT2Font(path).family_name
        fonts[name]=dict(file=Path(path).name,sha256=digest(path),requested=props.get_family())
        if '$' in text and t.get_parse_math():
            try:
                parsed=parser.parse(text,dpi=fig.dpi,prop=props)
                for font,size,code,*_ in parsed.glyphs:
                    math_fonts.add(font.family_name)
                    if font.get_char_index(code)==0:issues.append(issue('MISSING_MATH_GLYPH',text,codepoint=int(code),panel=pid))
            except (ValueError,RuntimeError) as e:issues.append(issue('MATH_PARSE',str(e),panel=pid))
        else:
            if path not in charmaps:charmaps[path]=ft2font.FT2Font(path).get_charmap()
            missing=sorted({ord(c) for c in text if not c.isspace() and ord(c) not in charmaps[path]})
            if missing:issues.append(issue('GLYPH_COVERAGE',text,codepoints=missing,font=name,panel=pid))
    protected=[]
    for r in results.values():
        for p in r.get('protected',[]):
            x,y,w,h=p['pixels'];protected.append(dict(id=p['id'],box_mm=[x*factor,fh-(y+h)*factor,w*factor,h*factor]))
    issues+=geometry_audit(items,[0,0,fw,fh],panels=layouts,protected=protected,min_font_pt=spec['design']['min_font_pt'])
    return dict(engine='Matplotlib artist inspection',issues=issues,fonts=fonts,math_fonts=sorted(math_fonts),elements=items,
        automatic_pass=not any(i['severity']=='error' for i in issues),review_pending=True,
        not_proven=['optical kerning','all glyph-level collisions','unregistered data/annotation occlusion','scientific validity'])


def audit_pdf(path,*,expected_mm=None,min_font_pt=6.,page_index=0,clip_mm=None):
    import fitz
    issues=[];items=[];fonts=[];path=Path(path)
    with fitz.open(path) as doc:
        page=doc[page_index];w,h=page.rect.width*25.4/72,page.rect.height*25.4/72
        canvas=clip_mm or [0,0,w,h]
        if expected_mm is not None and not np.allclose([w,h],expected_mm,atol=.15,rtol=0):issues.append(issue('PDF_PAGE_SIZE','Exported physical dimensions disagree.',observed_mm=[w,h],expected_mm=list(expected_mm)))
        # Raw spans retain final displayed font sizes; whole-page extraction lets us
        # flag partial clipping instead of silently discarding clipped text.
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for s in line['spans']:
                    x0,y0,x1,y1=s['bbox'];b=[x0*25.4/72,y0*25.4/72,(x1-x0)*25.4/72,(y1-y0)*25.4/72]
                    if clip_mm and not overlap(b,clip_mm):continue
                    if '\ufffd' in s['text']:issues.append(issue('PDF_REPLACEMENT_GLYPH',s['text']))
                    items.append(dict(id=f"span-{len(items)}",text=s['text'],box_mm=b,font_pt=s['size'],font=s['font']))
        # Font embedding is recorded, not guessed from the file suffix.
        for f in page.get_fonts(full=True):
            embedded=False
            if f[0]>0:
                try:embedded=bool(doc.extract_font(f[0])[3])
                except (ValueError,RuntimeError):pass
            fonts.append(dict(name=f[3],type=f[2],embedded=embedded))
            if not embedded:issues.append(issue('FONT_NOT_EMBEDDED',f[3],severity='warning'))
        if not items:issues.append(issue('NO_LIVE_TEXT','No auditable text in the selected artifact region; flattened/outlined text requires manual review.'))
        # Span envelopes overstate collisions in mathematical text: warnings only.
        issues+=geometry_audit(items,canvas,min_font_pt=min_font_pt)
    return dict(path=str(path),sha256=digest(path),page_index=page_index,dimensions_mm=[w,h],fonts=fonts,
        text=items,issues=issues,automatic_pass=not any(i['severity']=='error' for i in issues),
        native_backend='not_assumed',review_pending=True)


def audit_carrier(source_pdf,carrier_pdf,placement,*,min_font_pt=6.):
    """Verify actual final-PDF placement using unique-word anchors, not intent alone.

    placement: page_index (0-based), box_mm [left,top,width,height]. Supports
    nonrotated, vector-text-preserving insertion. Rasterized/ambiguous placements
    are blocked as unverified, rather than treated as a successful comparison.
    """
    import fitz
    b=placement['box_mm'];page_index=placement.get('page_index',0);issues=[]
    with fitz.open(source_pdf) as src,fitz.open(carrier_pdf) as dst:
        a=src[0];p=dst[page_index];rect=fitz.Rect(b[0],b[1],b[0]+b[2],b[1]+b[3])*(72/25.4)
        sw=a.get_text('words');tw=p.get_text('words',clip=rect)
        sc=Counter(x[4] for x in sw);tc=Counter(x[4] for x in tw)
        missing=sc-tc
        if missing:issues.append(issue('CARRIER_TEXT_LOSS','Source words are missing from the target region.',missing=dict(missing)))
        unique={x[4]:x for x in sw if sc[x[4]]==1 and tc[x[4]]==1};target={x[4]:x for x in tw}
        observed=None;expected=[rect.width/a.rect.width,rect.height/a.rect.height]
        if len(unique)<3:issues.append(issue('CARRIER_ANCHORS','Fewer than three unique matching anchors; actual placement cannot be verified.'))
        else:
            x=np.array([[(q[0]+q[2])/2,(q[1]+q[3])/2] for q in unique.values()]);y=np.array([[(target[k][0]+target[k][2])/2,(target[k][1]+target[k][3])/2] for k in unique])
            if min(np.ptp(x,axis=0))<10:issues.append(issue('CARRIER_ANCHOR_SPREAD','Anchors do not span both dimensions.'))
            else:
                fits=[np.linalg.lstsq(np.column_stack([x[:,i],np.ones(len(x))]),y[:,i],rcond=None)[0] for i in [0,1]]
                observed=[float(f[0]) for f in fits];residual=max(np.max(np.abs(y[:,i]-(fits[i][0]*x[:,i]+fits[i][1]))) for i in [0,1])
                if residual>.75 or not np.allclose(observed,expected,atol=.01,rtol=.02):issues.append(issue('CARRIER_PLACEMENT_MISMATCH','Observed anchor geometry differs from the declared placement.',observed_scale=observed,expected_scale=expected,residual_pt=float(residual)))
                if not np.isclose(observed[0],observed[1],rtol=.01):issues.append(issue('CARRIER_ASPECT_DISTORTION','Nonuniform scaling changes geometry.',observed_scale=observed))
    pdf=audit_pdf(carrier_pdf,min_font_pt=min_font_pt,page_index=page_index,clip_mm=b);issues+=pdf['issues']
    return dict(source_sha256=digest(source_pdf),carrier_sha256=digest(carrier_pdf),placement=placement,
        observed_scale=observed,expected_scale=expected,issues=issues,
        automatic_pass=not any(i['severity']=='error' for i in issues),review_pending=True)


def compare_rasters(reference,candidate,*,threshold=12.,max_fraction=.01):
    """Same-size RGB pixel regression. Never resize away a geometry regression."""
    from PIL import Image
    a=np.array(Image.open(reference).convert('RGB'),float);b=np.array(Image.open(candidate).convert('RGB'),float)
    if a.shape!=b.shape:return dict(pass_check=False,reason='DIMENSION_CHANGE',reference_shape=list(a.shape),candidate_shape=list(b.shape))
    delta=np.abs(a-b);fraction=float(np.mean(np.max(delta,axis=2)>threshold))
    return dict(pass_check=fraction<=max_fraction,changed_fraction=fraction,mean_absolute_error=float(delta.mean()),
        threshold=threshold,max_fraction=max_fraction,reference_sha256=digest(reference),candidate_sha256=digest(candidate),
        baseline_approval='external human review required; no automatic rebaseline')
