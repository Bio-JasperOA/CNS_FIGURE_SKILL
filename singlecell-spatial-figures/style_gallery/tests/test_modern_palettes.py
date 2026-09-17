from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb,to_hex
from matplotlib.collections import PathCollection
from matplotlib.text import Text
from modern_palettes import palette,cmap,CATEGORICAL,SEQUENTIAL,DIVERGING
from render import render,_prepare_demo_config
from chart_core import INK,MUTED
from fixtures import generate


def _lightness(color):
    r,g,b=to_rgb(color)
    return 0.2126*r+0.7152*g+0.0722*b


def _hexset(rows):
    return {to_hex(x,keep_alpha=False).upper() for x in rows}


def _safe_hex(color):
    try:return to_hex(color,keep_alpha=False).upper()
    except Exception:return ''


def test_editorial_inventory_is_complete_and_high_lightness():
    assert len(CATEGORICAL)==12
    assert len(SEQUENTIAL)==6
    assert len(DIVERGING)==4
    colors=[c for row in CATEGORICAL.values() for c in row['colors']]
    assert min(_lightness(c) for c in colors)>.55
    assert sum(_lightness(c) for c in colors)/len(colors)>.65


def test_default_small_category_routing_is_light_editorial():
    levels=['A','B','C','D','E','F']
    p=palette(levels,{})
    assert list(p.values())==CATEGORICAL['E01']['colors']
    assert len(set(p.values()))==len(levels)
    assert min(_lightness(c) for c in p.values())>.55


def test_subset_identity_is_stable_under_editorial_routing():
    cfg={'palette_order':['A','B','C','D','E','F']}
    whole=palette(['A','B','C','D','E','F'],cfg)
    part=palette(['F','B'],cfg)
    assert part=={'F':whole['F'],'B':whole['B']}


def test_large_atlas_uses_existing_high_capacity_palette_without_recycling():
    levels=[f'c{i:03d}' for i in range(100)]
    p=palette(levels,{})
    assert len(p)==100 and len(set(p.values()))==100


def test_explicit_real_data_colors_are_preserved_unless_auto_requested():
    explicit={'A':'#112233','B':'#445566'}
    assert palette(['A','B'],{'colors':explicit})==explicit


def test_legacy_and_locked_routes_remain_available():
    p=palette(['A','B'],{'categorical_preset':'C19','palette_lock':True})
    assert len(p)==2
    q=palette(['A','B'],{'categorical_preset':'C19','palette_policy':'legacy'})
    assert p==q


def test_continuous_defaults_are_light_and_never_black():
    seq=cmap({'title':'Spatial expression'})
    div=cmap({'title':'Differential expression effect'},signed=True)
    assert _lightness(seq(0.0))>.90
    assert _lightness(seq(1.0))>.55
    assert _lightness(div(0.5))>.90
    assert _lightness(div(0.0))>.55 and _lightness(div(1.0))>.55


def test_demo_config_removes_legacy_palette_hints():
    _,c=generate()['embedding']
    prepared=_prepare_demo_config(c)
    assert prepared['palette_policy']=='modern_editorial'
    assert 'colors' not in prepared
    assert 'categorical_preset' not in prepared
    _,c=generate()['benchmark']
    prepared=_prepare_demo_config(c)
    assert 'continuous_preset' not in prepared


def test_rendered_embedding_artist_uses_editorial_palette():
    d,c=generate()['embedding']
    legacy={x.upper() for x in c['colors'].values()}
    fig=render('embedding',d,c,'minimal')
    try:
        coll=next(x for x in fig.axes[0].collections if isinstance(x,PathCollection))
        actual=_hexset(coll.get_facecolors())
        expected={x.upper() for x in CATEGORICAL['E01']['colors']}
        assert actual==expected
        assert actual.isdisjoint(legacy)
        assert fig._palette_policy=='modern_editorial'
        assert fig._palette_router=='modern_palettes'
    finally:
        plt.close(fig)


def test_rendered_spatial_artist_uses_editorial_sequential_cmap():
    d,c=generate()['spatial']
    fig=render('spatial',d,c,'minimal')
    try:
        im=fig.axes[0].collections[0]
        assert to_hex(im.cmap(0.0)).upper()==SEQUENTIAL['L01']['colors'][0]
        assert to_hex(im.cmap(1.0)).upper()==SEQUENTIAL['L01']['colors'][-1]
    finally:
        plt.close(fig)


def test_rendered_heatmap_artist_uses_editorial_diverging_cmap():
    d,c=generate()['heatmap']
    fig=render('heatmap',d,c,'minimal')
    try:
        im=fig.axes[0].images[0]
        assert to_hex(im.cmap(0.0)).upper()==DIVERGING['V02']['colors'][0]
        assert to_hex(im.cmap(1.0)).upper()==DIVERGING['V02']['colors'][-1]
    finally:
        plt.close(fig)


def test_legends_are_left_aligned_consistently():
    for kind,mode in [('embedding','minimal'),('heatmap','advanced'),('calibration','advanced')]:
        d,c=generate()[kind]
        fig=render(kind,d,c,mode)
        try:
            legends=[ax.get_legend() for ax in fig.axes if ax.get_legend() is not None]
            assert legends
            for legend in legends:
                assert getattr(legend,'_legend_box').align=='left'
                assert legend.get_title().get_ha()=='left'
                assert all(t.get_ha()=='left' for t in legend.get_texts())
        finally:
            plt.close(fig)


def test_no_gray_small_explanatory_text_remains_on_canvas():
    muted=to_hex(MUTED).upper()
    for kind in ['dotplot','network','benchmark','calibration']:
        d,c=generate()[kind]
        fig=render(kind,d,c,'advanced')
        try:
            visible=[t for t in fig.findobj(Text) if t.get_visible() and (t.get_text() or '').strip()]
            gray_small=[t.get_text() for t in visible if t.get_fontsize()<=7.5 and _safe_hex(t.get_color())==muted]
            assert gray_small==[]
            texts=[t.get_text() for t in visible]
            assert not any(x.startswith(('Row order:','Cell text:','Cell text =','Node values:','Total ','Area ∝','Point area ∝','Fixed point area')) for x in texts)
            assert not any(' not displayed' in x for x in texts)
        finally:
            plt.close(fig)


def test_synthetic_disclosure_is_not_gray_microcopy():
    d,c=generate()['embedding']
    fig=render('embedding',d,c,'minimal')
    try:
        disclosure=next(t for t in fig.findobj(Text) if t.get_gid()=='synthetic_disclosure')
        assert disclosure.get_visible()
        assert _safe_hex(disclosure.get_color())==to_hex(INK).upper()
        assert disclosure.get_fontsize()>=7
    finally:
        plt.close(fig)
