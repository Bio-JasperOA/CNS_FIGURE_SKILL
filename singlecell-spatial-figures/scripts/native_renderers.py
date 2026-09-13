"""Three ready-to-register renderers; other blueprints need project adapters."""
from __future__ import annotations
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from composer import PanelContext,PanelResult
from figure_core import plot_embedding,plot_spatial_values,plot_marker_dot

def embedding(ctx: PanelContext, table: pd.DataFrame) -> PanelResult:
    p=ctx.panel;ch=p['channels'];s=ctx.scale('category')
    ax=ctx.add_axes((0,0,.72,1))
    plot_embedding(ax,table[[ch['x'],ch['y']]].to_numpy(dtype=float),
                   table[ch['category']].astype(str),s['colors'],seed=0)
    handles=[Line2D([],[],marker='o',linestyle='none',color=s['colors'][k],markersize=3,label=k) for k in s['order']]
    ax.legend(handles=handles,title=s['label'],loc='center left',bbox_to_anchor=(1.02,.5),frameon=False,borderaxespad=0)
    return PanelResult([ax],['Legend order is taken from the named scale registry.'])

def spatial(ctx: PanelContext, table: pd.DataFrame) -> PanelResult:
    p=ctx.panel;ch=p['channels'];s=ctx.scale('color');geo=p['spatial']
    ax=ctx.add_axes((0,0,.76,1));cax=ctx.add_axes((.83,.15,.04,.70))
    artist=plot_spatial_values(ax,table[[ch['x'],ch['y']]].to_numpy(dtype=float),
           table[ch['color']].to_numpy(dtype=float),section_ids=table[geo['section_column']],
           coordinate_unit=geo['unit'],y_axis_down=geo['y_axis_down'],norm=ctx.norm('color'),cmap=s['cmap'])
    ctx.figure.colorbar(artist,cax=cax,label=s['label'])
    return PanelResult([ax,cax],mappables={'color':artist})

def marker_dot(ctx: PanelContext, table: pd.DataFrame) -> PanelResult:
    ch=ctx.panel['channels'];s=ctx.scale('color')
    tab=table.rename(columns={ch['x']:'gene',ch['y']:'group',ch['color']:'mean_expression',ch['size']:'fraction_detected'})
    # Explicit table order is retained; callers must export an upstream reviewed order.
    groups=list(pd.unique(tab['group']));genes=list(pd.unique(tab['gene']))
    ax=ctx.add_axes((0,0,.72,1));cax=ctx.add_axes((.81,.30,.04,.70))
    artist=plot_marker_dot(ax,tab,groups,genes,value='mean_expression',norm=ctx.norm('color'),cmap=s['cmap'])
    ctx.figure.colorbar(artist,cax=cax,label=s['label'])
    handles=[ax.scatter([],[],s=45*f,facecolors='none',edgecolors='black',label=f'{f:.0%}') for f in [.25,.5,1.]]
    ax.legend(handles=handles,title='Detected cells',loc='upper left',bbox_to_anchor=(1.02,.25),frameon=False,borderaxespad=0)
    return PanelResult([ax,cax],['Input row order controls group and gene order; no renderer-side clustering.'],{'color':artist})

REGISTRY={'embedding':embedding,'spatial':spatial,'marker_dot':marker_dot}

def annotated_heatmap(ctx: PanelContext, table: pd.DataFrame) -> PanelResult:
    from composer import BoundedFigure
    from complex_recipes import annotated_heatmap as draw_heatmap
    ch=ctx.panel['channels'];s=ctx.scale('color')
    required={'x','y','color','row_metric','col_metric'}
    if required-set(ch): raise ValueError(f'Annotated heatmap requires channels {sorted(required)}.')
    if table.duplicated([ch['y'],ch['x']]).any(): raise ValueError('Duplicate heatmap cell.')
    for group,metric in [('y','row_metric'),('x','col_metric')]:
        if (table.groupby(ch[group])[ch[metric]].nunique(dropna=False)>1).any():
            raise ValueError(f'{metric} is inconsistent across the same identifier.')
    rows=list(pd.unique(table[ch['y']]));cols=list(pd.unique(table[ch['x']]))
    mat=table.pivot(index=ch['y'],columns=ch['x'],values=ch['color']).reindex(index=rows,columns=cols)
    rm=table.drop_duplicates(ch['y']).set_index(ch['y'])[ch['row_metric']]
    cm=table.drop_duplicates(ch['x']).set_index(ch['x'])[ch['col_metric']]
    effect=None
    if 'effect' in ch:
        effect=table.pivot(index=ch['y'],columns=ch['x'],values=ch['effect']).reindex(index=rows,columns=cols)
    axes=draw_heatmap(BoundedFigure(ctx),mat,column_metric=cm,row_metric=rm,
                     norm=ctx.norm('color'),cmap=s['cmap'],effect_labels=effect,value_label=s['label'])
    return PanelResult(list(axes.values()),['One row/column order is shared across matrix, metrics and labels.'],
                       {'color':axes['heatmap'].images[0]})

REGISTRY['annotated_heatmap']=annotated_heatmap
