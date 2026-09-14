"""Tests use software fixtures, not biological evidence."""
from copy import deepcopy
import json
from pathlib import Path
import numpy as np
import pytest
from matplotlib.colors import to_hex
import palette_presets as pp
from visual_contract import VisualScale, validate_visual_spec
from render_v3 import render

ROOT=Path(__file__).resolve().parents[1]
INV=pp.inventory()
IDS=[v['id'] for p in INV['presets'] for v in p.get('variants',[p])]

@pytest.mark.parametrize('pid',IDS)
def test_entry_roundtrip(pid):
    p,cols=pp._entry(pid)
    assert len(cols)==p['n_colors']
    assert all(len(c)==7 and to_hex(c).upper()==c for c in cols)
    assert p['grade'] in {'R','P','E','S','D'}
    if p['family']=='categorical':
        assert len(set(cols))==len(cols)
        with pytest.raises(ValueError):pp.palette_colors(pid,len(cols)+1)
    else:
        cm=pp.palette_colormap(pid)
        assert to_hex(cm(0.)).upper()==cols[0]
        assert to_hex(cm(1.)).upper()==cols[-1]
        assert pp.palette_colors(pid,5)[-1]==cols[-1]


def test_inventory_and_version():
    assert len(INV['presets'])==52 and len(IDS)==55
    assert INV['library_version']=='3.0.1' and INV['spec_version']=='3.0'
    assert sum(p['family']=='categorical' for p in INV['presets'])==21
    assert sum(p['grade']=='D' for p in INV['presets'])==1
    assert next(p for p in INV['presets'] if p['id']=='C21')['grade']=='D'
    assert len(pp.palette_colors('C18'))==102
    assert len(pp.palette_colors('C19'))==100
    assert pp.palette_colors('M01')[-1]=='#FDE725'
    assert pp.palette_colors('M07')[0]=='#FFFFFF'
    assert pp.palette_colors('M08')[0]=='#FFFFFF'

@pytest.mark.parametrize('pid',['C06','C06.wrong','C19.blue','C99','../../secrets',None,42])
def test_bad_id(pid):
    with pytest.raises((ValueError,KeyError)):pp.palette_colors(pid)

@pytest.mark.parametrize('n',[0,-1,True,1.5,'3'])
def test_bad_capacity(n):
    with pytest.raises(ValueError):pp.palette_colors('C19',n)


def test_identity_preserved():
    old=pp.categorical_map('C19',['beta','alpha'])
    grown=pp.categorical_map('C19',['alpha','new'],existing=old)
    assert grown['beta']==old['beta'] and grown['alpha']==old['alpha']
    assert list(grown)==['beta','alpha','new']
    assert len(set(grown.values()))==3
    with pytest.raises(ValueError):pp.categorical_map('M02',['alpha'])
    with pytest.raises(ValueError):pp.categorical_map('C19',['alpha','alpha'])
    with pytest.raises(ValueError):pp.categorical_map('C19','alpha')
    with pytest.raises(ValueError):pp.categorical_map('C19',['new'],existing={'old':'#FFFFFF'})
    with pytest.raises(ValueError):pp.categorical_map('C01',['a','b','c','d','e'])


def test_checksum_guard(tmp_path,monkeypatch):
    assets=tmp_path/'assets';assets.mkdir()
    for p in pp.ASSETS.glob('*.json'):(assets/p.name).write_bytes(p.read_bytes())
    index=assets/'index.json'; monkeypatch.setattr(pp,'ASSETS',assets);monkeypatch.setattr(pp,'INDEX',index)
    table=json.loads((assets/'categorical.json').read_text());table['C19']='010203'+table['C19'][6:]
    (assets/'categorical.json').write_text(json.dumps(table))
    with pytest.raises(ValueError,match='checksum'):pp.palette_colors('C19')


def test_resolve_copy_and_replay():
    spec={'scales':{'ct':{'kind':'categorical','order':['B','A'],'preset':'C19'},
                    'expr':{'kind':'continuous','limits':[0,1],'preset':'M02'}}}
    original=deepcopy(spec);resolved,bindings=pp.resolve_presets(spec)
    assert spec==original and 'preset' not in resolved['scales']['ct']
    assert resolved['scales']['ct']['colors']==pp.categorical_map('C19',['B','A'])
    assert bindings['ct']['n_colors']==100
    again,_=pp.resolve_presets(resolved)
    assert again==resolved
    assert VisualScale(resolved['scales']['expr']).cmap.N==256
    assert len(pp.dependency_paths(bindings))==4
    for sc in [dict(kind='continuous',preset='C19'),dict(kind='categorical',preset='M01',order=['x']),
               dict(kind='continuous',preset='M01',cmap='viridis'),dict(kind='categorical',preset='C19',order=['x'],colors={'x':'#111111'})]:
        with pytest.raises(ValueError):pp.resolve_presets({'scales':{'bad':sc}})

@pytest.mark.parametrize('norm,limits',[
    ({'type':'linear'},[0,10]),({'type':'log'},[.1,100]),
    ({'type':'power','gamma':.5},[0,10]),({'type':'two_slope','center':0},[-2,5]),
    ({'type':'symlog','linthresh':1},[-100,100]),
    ({'type':'boundary','boundaries':[0,1,3,10]},[0,10])])
def test_six_mechanisms(norm,limits):
    s,_=pp.resolve_presets({'scales':{'x':dict(kind='continuous',preset='D03',limits=limits,norm=norm)}})
    v=VisualScale(s['scales']['x']);a,disclosure=v.prepare(limits)
    assert np.isfinite(v.cmap(v.norm(a))).all()
    assert disclosure['missing']==0


def test_cyclic_is_not_sequential():
    s,_=pp.resolve_presets({'scales':{'phase':dict(kind='continuous',preset='Y01',limits=[0,360])}})
    assert s['scales']['phase']['palette_role']=='qualitative'
    assert s['scales']['phase'].get('norm',{'type':'linear'})=={'type':'linear'}


def test_render_integration(tmp_path):
    import yaml
    spec=yaml.safe_load((ROOT/'examples/v3_software_qa/figure.yaml').read_text())
    spec['scales']['signed'].pop('cmap');spec['scales']['signed']['preset']='D03'
    source=tmp_path/'figure.yaml';source.write_text(yaml.safe_dump(spec))
    result=render(source,ROOT/'examples/v3_software_qa',tmp_path/'out')
    assert result['release_ready'] is False
    out=tmp_path/'out';bindings=json.loads((out/'palette_bindings.json').read_text())
    assert bindings['signed']['id']=='D03'
    assert json.loads((out/'preflight.json').read_text())['ok']
    state=json.loads((out/'snapshot.json').read_text())
    assert '__palette__index.json' in state['inputs']
    assert '__palette__D03.json' in state['inputs']
    assert str(out/'palette_bindings.json') in state['artifacts']
    assert json.loads((out/'figure_spec.input.json').read_text())['scales']['signed']['preset']=='D03'
    for name in ['software_qa.pdf','software_qa.svg','software_qa.png']:assert (out/name).is_file()
    compiled=json.loads((out/'figure_spec.json').read_text())
    assert compiled['spec_version']=='3.0' and validate_visual_spec(compiled)['ok']
    spec['scales']['signed']['preset']='C99';source.write_text(yaml.safe_dump(spec))
    with pytest.raises(ValueError):render(source,ROOT/'examples/v3_software_qa',out)
    assert not json.loads((out/'preflight.json').read_text())['ok']
