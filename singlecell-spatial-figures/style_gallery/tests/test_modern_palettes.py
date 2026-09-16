from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from matplotlib.colors import to_rgb
from modern_palettes import palette,cmap,CATEGORICAL,SEQUENTIAL,DIVERGING


def _lightness(hex_color):
    r,g,b=to_rgb(hex_color)
    return 0.2126*r+0.7152*g+0.0722*b


def test_editorial_inventory_is_complete_and_light_background_friendly():
    assert len(CATEGORICAL)==12
    assert len(SEQUENTIAL)==6
    assert len(DIVERGING)==4
    colors=[c for row in CATEGORICAL.values() for c in row['colors']]
    assert min(_lightness(c) for c in colors)>.30


def test_default_small_category_routing_is_low_saturation_editorial():
    levels=['A','B','C','D','E','F']
    p=palette(levels,{})
    assert list(p.values())==CATEGORICAL['E01']['colors']
    assert len(set(p.values()))==len(levels)


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
    assert _lightness(seq(0.0))>.85
    assert _lightness(seq(1.0))>.30
    assert _lightness(div(0.5))>.85
    assert _lightness(div(0.0))>.25 and _lightness(div(1.0))>.25
