"""Physical-layout composer with an explicit, trusted local renderer registry.

YAML never names Python modules to import or code to evaluate. Callers supply
functions explicitly. Renderers receive reviewed data, never fit models here.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib, json
from pathlib import Path
from typing import Any, Callable
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.text import Text
import numpy as np
import pandas as pd
from framework_contract import validate_spec, compile_plan, _resolve_data_path
from figure_core import FigureStyle, apply_style, export_figure

@dataclass
class PanelResult:
    axes: list[Axes]
    notes: list[str]=field(default_factory=list)
    mappables: dict[str,Any]=field(default_factory=dict)

@dataclass
class PanelContext:
    figure: Figure
    spec: dict
    panel: dict
    box: dict
    axes: list[Axes]=field(default_factory=list)

    def add_axes(self, bounds=(0.,0.,1.,1.)) -> Axes:
        """Bounds are relative [left,bottom,width,height] inside the content box."""
        u,v,w,h=map(float,bounds)
        if min(u,v)<0 or min(w,h)<=0 or u+w>1.000001 or v+h>1.000001:
            raise ValueError('A child Axes must remain within the panel content box.')
        x,top,cw,ch=self.box['content_mm']; fw=self.spec['figure']['width_mm'];fh=self.spec['figure']['height_mm']
        bottom=fh-top-ch
        ax=self.figure.add_axes([(x+u*cw)/fw,(bottom+v*ch)/fh,w*cw/fw,h*ch/fh])
        self.axes.append(ax);return ax

    def scale(self, channel: str) -> dict:
        return self.spec['scales'][self.panel['scale_ids'][channel]]

    def norm(self, channel: str):
        s=self.scale(channel)
        if s['kind']!='continuous':raise ValueError(f'{channel} is not a continuous scale.')
        return mpl.colors.Normalize(*s['limits'],clip=False)

@dataclass
class ComposedFigure:
    figure: Figure
    spec: dict
    results: dict[str,PanelResult]
    tables: dict[str,pd.DataFrame]
    actual_font: str
    qa: dict


def _style(spec: dict) -> FigureStyle:
    d=spec['design'];f=spec['figure']
    return FigureStyle(font=d['font_family'],fallback_font=d['fallback_font'],font_pt=d['font_pt'],
                       label_pt=d['tag_pt'],line_pt=d['line_pt'],width_mm=f['width_mm'],height_mm=f['height_mm'])

def load_tables(spec: dict, root: str | Path) -> dict[str,pd.DataFrame]:
    report=validate_spec(spec,check_files=True,root=root)
    if not report['ok']: raise ValueError(json.dumps(report['issues'],ensure_ascii=False))
    tables={}
    for did,d in spec['datasets'].items():
        path=_resolve_data_path(Path(root),d['path'])
        tables[did]=pd.read_csv(path,sep='\t' if path.suffix=='.tsv' else ',',
                               dtype={k:'string' for k in d['keys']},keep_default_na=False)
    return tables


def inspect_canvas(fig: Figure, spec: dict, results: dict[str,PanelResult]) -> dict:
    """Check text outside the canvas and minimum type size, not scientific validity.

    This deliberately does NOT claim to detect every label-label collision,
    color-vision deficiency or incorrect inferential interpretation.
    """
    fig.canvas.draw();renderer=fig.canvas.get_renderer();fb=fig.bbox;issues=[]
    # Matplotlib retains out-of-view Tick objects with visible=True even when
    # Axis.draw excludes them. Do not report these undrawn labels as clipping.
    excluded=set()
    for ax in fig.axes:
        for axis in (ax.xaxis,ax.yaxis):
            ticks=list(axis.get_major_ticks())+list(axis.get_minor_ticks())
            lo,hi=sorted(axis.get_view_interval());tol=max(abs(lo),abs(hi),1)*1e-10
            for tick in ticks:
                if (not ax.get_visible() or not ax.axison or not axis.get_visible()
                        or tick.get_loc()<lo-tol or tick.get_loc()>hi+tol):
                    excluded.update([id(tick.label1),id(tick.label2)])
            if not ax.get_visible() or not ax.axison or not axis.get_visible():
                excluded.update([id(axis.label),id(axis.get_offset_text())])
    for text in fig.findobj(match=Text):
        if id(text) in excluded or not text.get_visible() or not text.get_text().strip():continue
        bb=text.get_window_extent(renderer)
        if bb.width<=0 or bb.height<=0:continue
        if bb.x0<fb.x0-1 or bb.y0<fb.y0-1 or bb.x1>fb.x1+1 or bb.y1>fb.y1+1:
            issues.append({'code':'TEXT_OUTSIDE_CANVAS','text':text.get_text()})
        if text.get_fontsize()<spec['design']['min_font_pt']-1e-6:
            issues.append({'code':'TEXT_TOO_SMALL','text':text.get_text(),'size_pt':text.get_fontsize()})
    for p in spec['panels']:
        result=results[p['id']]
        for channel,artist in result.mappables.items():
            if channel not in p['scale_ids']:continue
            s=spec['scales'][p['scale_ids'][channel]]
            if s['kind']=='continuous' and not np.allclose([artist.norm.vmin,artist.norm.vmax],s['limits']):
                issues.append({'code':'MAPPABLE_SCALE_MISMATCH','panel':p['id'],'channel':channel})
    return {'automated_render_checks_passed':not issues,'issues':issues,
            'manual_visual_review':'pending','scientific_review':'pending','release_ready':False,
            'not_checked':['all label-label collisions','color-vision deficiency','statistical model correctness','biological claims']}


def compose(spec: dict, tables: dict[str,pd.DataFrame], registry: dict[str,Callable]) -> ComposedFigure:
    report=validate_spec(spec)
    if not report['ok']:raise ValueError(json.dumps(report['issues'],ensure_ascii=False))
    plan=compile_plan(spec,report)
    missing=set(spec['datasets'])-tables.keys()
    if missing:raise ValueError(f'Missing reviewed tables: {sorted(missing)}')
    unknown={p['renderer'] for p in spec['panels']}-registry.keys()
    if unknown:raise ValueError(f'Renderers require explicit local registration: {sorted(unknown)}. No package will be auto-installed.')
    for did,d in spec['datasets'].items():
        table=tables[did]
        if table.empty or not table.columns.is_unique:raise ValueError(f'{did}: empty table or duplicate columns.')
        required=set(d['keys'])
        for p in spec['panels']:
            if p['data_id']==did:
                required.update(p['channels'].values())
                if 'spatial' in p:required.add(p['spatial']['section_column'])
        if required-set(table.columns):raise ValueError(f'{did}: missing required columns.')
        blank=table[d['keys']].map(lambda x:isinstance(x,str) and not x.strip()).any().any()
        if blank or table[d['keys']].isna().any().any() or table.duplicated(d['keys']).any():raise ValueError(f'{did}: invalid primary key.')
    with mpl.rc_context():
        font=apply_style(_style(spec));fig=plt.figure(figsize=(spec['figure']['width_mm']/25.4,spec['figure']['height_mm']/25.4))
        results={};panels={p['id']:p for p in spec['panels']}
        try:
            for pid in plan['render_order']:
                p=panels[pid];ctx=PanelContext(fig,spec,p,plan['boxes'][pid])
                result=registry[p['renderer']](ctx,tables[p['data_id']].copy(deep=True))
                if not isinstance(result,PanelResult) or not result.axes:raise TypeError(f'{pid}: renderer must return PanelResult with Axes.')
                if any(ax.figure is not fig for ax in result.axes):raise ValueError(f'{pid}: renderer created an unrelated Figure.')
                results[pid]=result
                x,y,w,h=plan['boxes'][pid]['outer_mm'];fw=spec['figure']['width_mm'];fh=spec['figure']['height_mm']
                fig.text(x/fw,1-(y+1)/fh,pid,ha='left',va='top',fontweight='bold',fontsize=spec['design']['tag_pt'])
            qa=inspect_canvas(fig,spec,results)
        except Exception:
            plt.close(fig);raise
    return ComposedFigure(fig,spec,results,tables,font,qa)


def write_bundle(composed: ComposedFigure, output: str | Path, *, input_manifest: dict | None=None) -> dict:
    """Export a draft/review bundle. This function never approves publication."""
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    spec=composed.spec;stem=output/spec['figure']['id']
    provenance={'data_source':{k:v['source'] for k,v in spec['datasets'].items()},
                'analysis_unit':{k:v['grain'] for k,v in spec['datasets'].items()},
                'value_definition':{k:v['value_definition'] for k,v in spec['datasets'].items()},
                'seed':0,'actual_font':composed.actual_font,'input_manifest':input_manifest or {},
                'spec_sha256':hashlib.sha256(json.dumps(spec,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                'review_status':'DRAFT: scientific and manual visual review pending'}
    # Restore export settings locally; do not leak style into subsequent projects.
    with mpl.rc_context():
        apply_style(_style(spec))
        files=export_figure(composed.figure,stem,provenance=provenance,source_tables=composed.tables)
    (output/'figure_spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
    (output/'qa.json').write_text(json.dumps(composed.qa,ensure_ascii=False,indent=2)+'\n')
    return files

class BoundedFigure:
    """Adapt a legacy GridSpec recipe to one physical panel, without screenshots.

    Supported interface is deliberately small. Recipes that require a complete
    standalone Figure need a dedicated adapter rather than silent rescaling.
    """
    def __init__(self, context: PanelContext): self.context=context
    def add_gridspec(self, *args, **kwargs):
        if set(kwargs)&{'left','right','bottom','top','figure'}:
            raise ValueError('A bounded recipe cannot override its physical panel bounds.')
        x,t,w,h=self.context.box['content_mm'];f=self.context.spec['figure']
        return self.context.figure.add_gridspec(*args,left=x/f['width_mm'],right=(x+w)/f['width_mm'],
                bottom=1-(t+h)/f['height_mm'],top=1-t/f['height_mm'],**kwargs)
    def add_subplot(self, *args, **kwargs):
        ax=self.context.figure.add_subplot(*args,**kwargs);self.context.axes.append(ax);return ax
    def colorbar(self, *args, **kwargs): return self.context.figure.colorbar(*args,**kwargs)
