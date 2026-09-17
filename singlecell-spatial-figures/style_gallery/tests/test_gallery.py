"""v3.2 semantic/display regressions; fixture-specific v3.1 sizes are not requirements."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.collections import PathCollection,FillBetweenPolyCollection
from render import KINDS,render,validate,audit,export,_palette,_cmap,PALETTE_SNAPSHOT
from chart_core import normalization
from fixtures import generate,high_capacity

@pytest.fixture(scope='module')
def fixtures():return generate()

@pytest.mark.parametrize('kind',KINDS)
@pytest.mark.parametrize('mode',['minimal','advanced'])
def test_all_renderings_preserve_input_and_have_no_subtitle(kind,mode,fixtures):
    d,c=fixtures[kind];before=d.copy(deep=True);original=copy.deepcopy(c)
    fig=render(kind,d,c,mode);report=audit(fig)
    assert report['outside_canvas']==[]
    assert report['subtitle_count']==0
    assert not any('THIS MUST NEVER' in t.get_text() for t in fig.findobj(Text))
    assert len(fig.texts)<=2 # Only a main title and the synthetic-data disclosure.
    assert abs(fig.get_figwidth()*25.4-c['width_mm'])<1e-8
    assert any('SYNTHETIC' in t.get_text() for t in fig.texts)
    pd.testing.assert_frame_equal(d,before);assert c==original
    plt.close(fig)

@pytest.mark.parametrize('kind',KINDS)
def test_actual_export_formats_and_text(kind,tmp_path,fixtures):
    import fitz
    d,c=fixtures[kind];out=tmp_path/kind;report=export(render(kind,d,c),out)
    assert '<text' in out.with_suffix('.svg').read_text()
    assert out.with_suffix('.png').stat().st_size>3000
    with fitz.open(out.with_suffix('.pdf')) as doc:
        assert len(doc)==1
        assert 'THIS MUST NEVER' not in doc[0].get_text()
        assert 'SYNTHETIC' in doc[0].get_text()
        assert abs(doc[0].rect.width/72*25.4-c['width_mm'])<.02
    assert set(report['outputs'])=={'png','pdf','svg'}

@pytest.mark.parametrize('kind',KINDS)
def test_duplicate_identity_rejected(kind,fixtures):
    d,c=fixtures[kind];dup=pd.concat([d,d.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match='identity'):validate(kind,dup,c)

@pytest.mark.parametrize('kind',KINDS)
def test_real_data_needs_provenance(kind,fixtures):
    d,c=fixtures[kind];c=copy.deepcopy(c);c['demo']=False
    with pytest.raises(ValueError,match='provenance'):render(kind,d,c)

@pytest.mark.parametrize('kind',KINDS)
def test_advanced_has_auditable_information_not_just_title(kind,fixtures):
    d,c=fixtures[kind];a=render(kind,d,c,'advanced');m=render(kind,d,c,'minimal')
    assert len(a._semantic_layers)>len(m._semantic_layers)
    assert all(x['fields'] for x in a._semantic_layers)
    assert a._input_sha256==m._input_sha256
    plt.close(a);plt.close(m)

def test_registry_and_catalogue_agree():
    catalog=json.loads((Path(__file__).resolve().parents[1]/'catalogue_v32.json').read_text())
    assert len(KINDS)==26 and set(KINDS)=={r['kind'] for r in catalog}
    assert sum(r['new_family'] for r in catalog)==12

def test_palette_identity_stable_across_subset():
    c={'categorical_preset':'C19','palette_order':['A','B','C','D']}
    whole=_palette(['A','B','C','D'],c);part=_palette(['D','B'],c)
    assert part=={'D':whole['D'],'B':whole['B']}

def test_capacity_never_cycles_or_interpolates():
    with pytest.raises(ValueError,match='capacity'):_palette([str(i) for i in range(11)],{})
    with pytest.raises(ValueError,match='Duplicate'):_palette(['a','b'],{'colors':{'a':'red','b':'#FF0000'}})

def test_continuous_endpoints_and_conflict():
    from matplotlib.colors import to_hex
    cm=_cmap({'continuous_preset':'M02'})
    assert to_hex(cm(0.0)).upper()==PALETTE_SNAPSHOT['M02']['colors'][0]
    assert to_hex(cm(1.0)).upper()==PALETTE_SNAPSHOT['M02']['colors'][-1]
    with pytest.raises(ValueError):_cmap({'continuous_preset':'M02','continuous_colors':['red','blue']})

@pytest.mark.parametrize('norm', ['linear','two_slope','log','symlog','power','boundary'])
def test_normalizations(norm):
    c={'norm':norm,'limits':[-3,4] if norm in ['two_slope','symlog'] else [1,8],'boundaries':[1,2,4,8]}
    n=normalization(c,[-1,2,3] if norm in ['two_slope','symlog'] else [1,2,4])
    assert np.isfinite(n([2.,3.])).all()

def test_dot_area_is_proportional_to_fraction(fixtures):
    d,c=fixtures['dotplot'];f=render('dotplot',d,c)
    observed=np.concatenate([x.get_sizes() for x in f.axes[0].collections if isinstance(x,PathCollection)])
    expected=d.fraction.to_numpy()*150/np.sqrt(d.condition.nunique())
    np.testing.assert_allclose(np.sort(observed),np.sort(expected));plt.close(f)

def test_unobserved_matrix_value_is_not_zero(fixtures):
    d,c=fixtures['heatmap'];d=d.copy();d.loc[0,'value']=np.nan;f=render('heatmap',d,c)
    assert np.ma.getmaskarray(f.axes[0].images[0].get_array())[0,0];plt.close(f)

def test_no_inferred_spatial_segmentation(fixtures):
    from matplotlib.collections import PolyCollection
    d,c=fixtures['spatial'];f=render('spatial',d.drop(columns=['vertices']),c)
    assert not any(isinstance(x,PolyCollection) for x in f.axes[0].collections);plt.close(f)

def test_spatial_scope_and_geometry(fixtures):
    d,c=fixtures['spatial'];d=d.copy();d.loc[0,'section']='different'
    with pytest.raises(ValueError):render('spatial',d,c)
    d,c=fixtures['spatial'];c=dict(c);c.pop('coordinate_unit')
    with pytest.raises(ValueError):render('spatial',d,c)

def test_fraction_and_count_metadata(fixtures):
    d,c=fixtures['composition'];v=d.copy();v.loc[0,'fraction']+=.1
    with pytest.raises(ValueError):render('composition',v,c)
    v=d.copy();v.loc[0,'n']+=5
    with pytest.raises(ValueError,match='Inconsistent'):render('composition',v,c)

def test_pairing_and_differences(fixtures):
    d,c=fixtures['paired']
    with pytest.raises(ValueError):render('paired',d.iloc[1:],c)
    f=render('paired',d,c)
    p=d.pivot(index='sample',columns='condition',values='value');expected=np.sort(p.After-p.Before)
    np.testing.assert_allclose(f.axes[0].collections[-1].get_offsets()[:,0],expected);plt.close(f)

def test_multistage_mass_conservation(fixtures):
    d,c=fixtures['flow'];v=d.copy();v.loc[v.stage.eq(1).idxmax(),'mass']+=5
    with pytest.raises(ValueError,match='conserved'):render('flow',v,c)
    f=render('flow',d,c);assert any('300 coupling' in t.get_text() for t in f.axes[0].texts);plt.close(f)

def test_upset_is_exclusive_and_conserves_item_total(fixtures):
    d,c=fixtures['upset'];f=render('upset',d,c)
    assert sum(x['n'] for x in f._intersections)==d.item.nunique()
    assert len({tuple(x['membership']) for x in f._intersections})==len(f._intersections);plt.close(f)

def test_intervals_remain_in_both_curve_modes(fixtures):
    for kind in ['trajectory','roc','precision_recall']:
        d,c=fixtures[kind]
        counts=[]
        for mode in ['minimal','advanced']:
            f=render(kind,d,c,mode);counts.append(sum(isinstance(x,FillBetweenPolyCollection) for x in f.axes[0].collections));plt.close(f)
        assert counts[0]==counts[1] and counts[0]>0

def test_confusion_raw_counts_and_row_sums(fixtures):
    d,c=fixtures['confusion'];f=render('confusion',d,c)
    m=f.axes[0].images[0].get_array();np.testing.assert_allclose(m.sum(axis=1),1)
    assert any('(n=' in t.get_text() for t in f.axes[0].get_yticklabels());plt.close(f)

def test_ridge_is_not_faked_with_single_observation(fixtures):
    d,c=fixtures['ridge'];v=d.groupby('group',sort=False).head(1)
    with pytest.raises(ValueError):render('ridge',v,c)

def test_roc_order_and_real_steps(fixtures):
    d,c=fixtures['roc'];v=d.copy();v.loc[2,'fpr']=0
    with pytest.raises(ValueError):render('roc',v,c)

def test_no_false_abstract_edges(fixtures):
    d,c=fixtures['embedding'];c=copy.deepcopy(c);c.pop('edge_definition')
    with pytest.raises(ValueError):render('embedding',d,c)

def test_export_stops_on_off_canvas(tmp_path,fixtures):
    d,c=fixtures['paired'];f=render('paired',d,c);f.text(1.2,.5,'OFF')
    with pytest.raises(ValueError,match='Outside'):export(f,tmp_path/'bad')
    plt.close(f)

def test_high_capacity_and_full_key(tmp_path):
    d,c=high_capacity();f=render('embedding',d,c);assert len(f._external_color_key)==100
    p=tmp_path/'hundred';export(f,p)
    assert pd.read_csv(p.with_suffix('.colors.csv')).color.nunique()==100
    assert p.with_suffix('.key.pdf').is_file()

def test_deterministic_fixtures():
    a,b=generate(),generate()
    for k in KINDS:pd.testing.assert_frame_equal(a[k][0],b[k][0])


def test_calibration_area_is_linear_and_shared_across_models():
    d,c=generate()['calibration'];f=render('calibration',d,c,'advanced')
    cols=[x for x in f.axes[0].collections if isinstance(x,PathCollection)]
    for coll,(_,g) in zip(cols,d.groupby('model',sort=False)):
        np.testing.assert_allclose(coll.get_sizes(),g.sort_values('predicted').n/d.n.max()*100)
    plt.close(f)

def test_zero_enrichment_counts_do_not_create_infinite_legend():
    d,c=generate()['enrichment'];d['count']=0
    with pytest.raises(ValueError,match='positive gene'):render('enrichment',d,c,'advanced')

def test_top_k_upset_keeps_omitted_mass_in_audit_but_not_canvas_microcopy():
    d,c=generate()['upset'];c.update(max_intersections=3,allow_top_k=True)
    f=render('upset',d,c);r=audit(f)
    assert r['omitted_intersections']['items']>0
    assert not any('not displayed' in x['text'] for x in r['rendered_text'])
    assert any('not displayed' in x for x in f._removed_explanatory_text)
    plt.close(f)

def test_partial_optional_interval_is_rejected():
    d,c=generate()['roc'];d=d.drop(columns=['upper'])
    with pytest.raises(ValueError,match='both interval'):render('roc',d,c)

def test_export_qa_binds_source_table(tmp_path):
    d,c=generate()['heatmap'];f=render('heatmap',d,c)
    r=export(f,tmp_path/'heatmap');assert len(r['input_csv_sha256'])==64
