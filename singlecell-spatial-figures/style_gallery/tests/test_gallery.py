import sys, json, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt
from render import KINDS,render,validate,audit,export,_palette,_cmap
from fixtures import generate
from catalogue import CATALOG,SOURCES

@pytest.mark.parametrize('kind',KINDS)
@pytest.mark.parametrize('mode',['minimal','advanced'])
def test_render_no_mutation_or_crop(kind,mode):
    d,c=generate()[kind];before=d.copy(deep=True);config=json.dumps(c,sort_keys=True)
    fig=render(kind,d,c,mode)
    assert not audit(fig)['outside_canvas']
    assert abs(fig.get_figwidth()*25.4-183)<1e-9
    pd.testing.assert_frame_equal(d,before); assert config==json.dumps(c,sort_keys=True)
    assert any('ILLUSTRATIVE DATA' in t.get_text() for t in fig.texts)
    plt.close(fig)

@pytest.mark.parametrize('kind',KINDS)
def test_exports_actual_images_and_pdf(kind,tmp_path):
    fitz=pytest.importorskip('fitz')
    d,c=generate()[kind]; p=tmp_path/kind; export(render(kind,d,c),p)
    assert p.with_suffix('.png').stat().st_size>3000
    assert '<text' in p.with_suffix('.svg').read_text()
    doc=fitz.open(p.with_suffix('.pdf'))
    assert len(doc)==1
    assert abs(doc[0].rect.width/72*25.4-183)<.01
    assert 'ILLUSTRATIVE DATA' in doc[0].get_text()
    doc.close()

@pytest.mark.parametrize('kind',KINDS)
def test_duplicate_keys_rejected(kind):
    d,c=generate()[kind]
    with pytest.raises(ValueError,match='identity'):validate(kind,pd.concat([d,d.iloc[[0]]]),c)

@pytest.mark.parametrize('kind',KINDS)
def test_provenance_required_for_real_data(kind):
    d,c=generate()[kind];c['demo']=False
    with pytest.raises(ValueError,match='provenance'):validate(kind,d,c)

def test_catalogue_coverage():
    assert set(c['kind'] for c in CATALOG)==set(KINDS)
    assert all(c['source_id'] in SOURCES and c['difference'] and c['fail_rule'] for c in CATALOG)
    assert {'Nature','Cell','Science'}<=set(s['journal'] for s in SOURCES.values())

def test_palette_capacity_and_order():
    with pytest.raises(ValueError,match='capacity|capacity|high-capacity'):_palette(list(map(str,range(11))),{})
    assert list(_palette(['a','b'],{}))==['a','b']
    with pytest.raises(ValueError,match='Repeated'):_palette(['a','b'],{'colors':{'a':'red','b':'#FF0000'}})

def test_palette_conflict_and_endpoints():
    with pytest.raises(ValueError):_cmap({'continuous_preset':'D03','continuous_colors':['red','blue']})
    from render import PALETTE_SNAPSHOT
    from matplotlib.colors import to_hex
    c=_cmap({'continuous_preset':'M02'})
    assert to_hex(c(0.)).upper()==PALETTE_SNAPSHOT['M02']['colors'][0]
    assert to_hex(c(1.)).upper()==PALETTE_SNAPSHOT['M02']['colors'][-1]

def test_paired_missing_condition():
    d,c=generate()['paired']
    with pytest.raises(ValueError):validate('paired',d.iloc[1:],c)

def test_composition_sum_and_metadata():
    d,c=generate()['composition'];d.loc[0,'fraction']+=.1
    with pytest.raises(ValueError,match='sum'):validate('composition',d,c)
    d,c=generate()['composition'];d.loc[0,'n']=1
    with pytest.raises(ValueError,match='Inconsistent'):validate('composition',d,c)

def test_no_fake_spatial_units_or_cross_section():
    d,c=generate()['spatial'];c.pop('coordinate_unit')
    with pytest.raises(ValueError):validate('spatial',d,c)
    d,c=generate()['spatial'];d.loc[0,'section']='other'
    with pytest.raises(ValueError):validate('spatial',d,c)

def test_q_floor_must_be_declared_upstream():
    d,c=generate()['volcano'];d.loc[0,'q']=0
    with pytest.raises(ValueError,match='positive q'):validate('volcano',d,c)

def test_network_no_zero_denominator():
    d,c=generate()['network'];d['weight']=0
    with pytest.raises(ValueError,match='positive'):validate('network',d,c)

def test_flow_source_mass_not_normalized():
    d,c=generate()['flow'];fig=render('flow',d,c)
    assert sum(d.mass)==400
    text=' '.join(t.get_text() for ax in fig.axes for t in ax.texts)
    assert '400' in text and '135' in text and '115' in text
    plt.close(fig)

def test_trajectory_intervals_in_both_modes():
    d,c=generate()['trajectory']
    for mode in ['minimal','advanced']:
        fig=render('trajectory',d,c,mode)
        from matplotlib.collections import FillBetweenPolyCollection
        assert sum(isinstance(x,FillBetweenPolyCollection) for x in fig.axes[0].collections)==3
        plt.close(fig)

def test_dot_area_exact():
    d,c=generate()['dotplot'];fig=render('dotplot',d,c)
    np.testing.assert_allclose(fig.axes[0].collections[0].get_sizes(),90*d.fraction)
    plt.close(fig)

def test_export_rejects_off_canvas(tmp_path):
    d,c=generate()['paired'];fig=render('paired',d,c);fig.text(1.2,.5,'bad')
    with pytest.raises(ValueError,match='Layout'):export(fig,tmp_path/'bad')
    plt.close(fig)

def test_deterministic_fixtures():
    a,b=generate(),generate()
    for k in KINDS:pd.testing.assert_frame_equal(a[k][0],b[k][0])

def test_non_symmetric_not_triangle():
    d,c=generate()['correlation'];d.loc[1,'value']=.111
    with pytest.raises(ValueError,match='symmetric'):render('correlation',d,c)
    plt.close('all')

def test_missing_matrix_value_not_zero():
    d,c=generate()['heatmap'];d.loc[0,'value']=np.nan
    fig=render('heatmap',d,c);assert np.ma.getmaskarray(fig.axes[0].images[0].get_array())[0,0]
    plt.close(fig)

def test_high_capacity_example_and_external_key(tmp_path):
    from fixtures import high_capacity
    d,c=high_capacity();fig=render('embedding',d,c)
    assert len(fig._external_color_key)==100
    p=tmp_path/'hundred';export(fig,p)
    key=pd.read_csv(p.with_suffix('.colors.csv'))
    assert key.color.nunique()==100
    assert p.with_suffix('.key.pdf').is_file()

def test_shared_cell_identity():
    sets=generate()
    for k in ['embedding','composition','network']:
        assert sets[k][1]['colors']['T cells']=='#729ECE'
