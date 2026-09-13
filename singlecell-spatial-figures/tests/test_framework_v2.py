"""Software fixtures only. No data here are biological observations."""
from pathlib import Path
from copy import deepcopy
import json
import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from framework_contract import read_spec, validate_spec, compile_plan, panel_boxes
from composer import compose, PanelResult, write_bundle, inspect_canvas, load_tables
from native_renderers import REGISTRY
ROOT=Path(__file__).resolve().parents[1]

def draft():
    return read_spec(ROOT/'assets'/'atlas.yaml')

def simple_spec():
    s=draft(); s['figure'].update(question='SOFTWARE QA ONLY',main_message='NO BIOLOGICAL RESULTS',width_mm=183,height_mm=110)
    s['layout'].update(rows=1,cols=2,row_weights=[1],col_weights=[1,1])
    s['panels']=s['panels'][:2];s['panels'][0]['slot']=[0,0,1,1];s['panels'][1]['slot']=[0,1,1,1]
    s['datasets']={k:v for k,v in s['datasets'].items() if k in ['data_a','data_b']}
    for p in s['panels']:
        p.update(renderer='fixture',channels={'x':'x','y':'y'},scale_ids={})
    return s

@pytest.mark.parametrize('name',['atlas','spatial_niche','development','model_benchmark'])
def test_templates(name):
    s=read_spec(ROOT/'assets'/f'{name}.yaml');r=validate_spec(s)
    assert r['ok'] and r['warnings'] and not r['files_checked']
    assert r['scientific_review']=='not_performed'

def mutate(s,case):
    if case=='overlap':s['panels'][1]['slot']=s['panels'][0]['slot']
    if case=='outbound':s['panels'][0]['slot']=[4,0,1,1]
    if case=='zero_span':s['panels'][0]['slot']=[0,0,0,1]
    if case=='duplicate_id':s['panels'][1]['id']='a'
    if case=='unknown_data':s['panels'][0]['data_id']='missing'
    if case=='unknown_scale':s['panels'][0]['scale_ids']['category']='missing'
    if case=='palette':del s['scales']['identity']['colors']['Population_A']
    if case=='limits':s['scales']['expression']['limits']=[4,0]
    if case=='pseudorep':s['panels'][0]['statistics'].update(inferential=True,independent_unit='cell',n_biological=5,source_table='x.csv')
    if case=='no_n':s['panels'][0]['statistics'].update(inferential=True,independent_unit='donor',n_biological=1,source_table='x.csv')
    if case=='no_stat_source':s['panels'][0]['statistics'].update(inferential=True,independent_unit='donor',n_biological=5)
    if case=='cycle':s['panels'][0]['depends_on']=['b']
    if case=='unknown_parent':s['panels'][0]['depends_on']=['z']
    if case=='weights':s['layout']['row_weights']=[1]
    if case=='padding':s['design']['panel_padding_mm']=[100]*4
    if case=='spatial':del s['panels'][2]['spatial']
    if case=='nan':s['figure']['width_mm']=float('nan')
    if case=='smallfont':s['design']['font_pt']=5
    if case=='unknown_field':s['figure']['typo_field']='yes'
    if case=='comparison':
        for p in s['panels'][:2]:p['comparison_group']='same'
    return s

@pytest.mark.parametrize('case',['overlap','outbound','zero_span','duplicate_id','unknown_data','unknown_scale',
 'palette','limits','pseudorep','no_n','no_stat_source','cycle','unknown_parent','weights','padding','spatial','nan',
 'smallfont','unknown_field','comparison'])
def test_invalid_specs(case):
    r=validate_spec(mutate(draft(),case));assert not r['ok'],case

def test_physical_boxes():
    s=simple_spec();b=panel_boxes(s)
    assert b['a']['outer_mm'][0]==4
    assert b['b']['outer_mm'][0]>b['a']['outer_mm'][0]+b['a']['outer_mm'][2]
    for bb in b.values():
        x,t,w,h=bb['outer_mm'];assert x+w<=183 and t+h<=110
        x,t,w,h=bb['content_mm'];assert w>0 and h>0

def test_dependency_execution_order():
    s=simple_spec();s['panels']=list(reversed(s['panels']))
    r=validate_spec(s);assert r['render_order']==['a','b']
    assert compile_plan(s,r)['status']=='preflight_passed_not_reviewed'

def test_input_csv_keys_and_hash(tmp_path):
    s=simple_spec()
    for k in s['datasets']:
        s['datasets'][k]['path']=k+'.csv'
        (tmp_path/(k+'.csv')).write_text('id,x,y\n001,1,3\n002,2,4\n')
    r=validate_spec(s,check_files=True,root=tmp_path)
    assert r['ok'] and r['input_manifest']['data_a']['rows']==2
    assert len(r['input_manifest']['data_a']['sha256'])==64
    tables=load_tables(s,tmp_path);assert tables['data_a']['id'][0]=='001'
    (tmp_path/'data_a.csv').write_text('id,x,y\n001,1,3\n001,2,4\n')
    assert not validate_spec(s,check_files=True,root=tmp_path)['ok']

def test_no_path_escape(tmp_path):
    s=simple_spec();s['datasets']['data_a']['path']='../secret.csv'
    r=validate_spec(s,check_files=True,root=tmp_path)
    assert not r['ok'] and any('escapes' in x['message'] for x in r['issues'])

def tables_fixture():
    return {k:pd.DataFrame({'id':['T1','T2','T3'],'x':[0.,1.,2.],'y':[0.,1.,0.]}) for k in ['data_a','data_b']}

def fixture(ctx,table):
    ax=ctx.add_axes();ax.plot(table.x,table.y);ax.set_xlabel('Software test x');ax.set_ylabel('Software test y')
    table.loc[0,'x']=999
    return PanelResult([ax])

def test_composition_and_source_copy():
    tables=tables_fixture();c=compose(simple_spec(),tables,{'fixture':fixture})
    assert len(c.figure.axes)==2 and len(c.results)==2
    assert c.qa['automated_render_checks_passed'], c.qa
    assert tables['data_a'].loc[0,'x']==0
    assert c.qa['manual_visual_review']=='pending' and not c.qa['release_ready']
    assert np.allclose(c.figure.get_size_inches()*25.4,[183,110]);plt.close(c.figure)

def test_registry_does_not_dynamic_import():
    with pytest.raises(ValueError,match='Register|registration'):compose(simple_spec(),tables_fixture(),{})

def test_orphan_figure_rejected():
    def bad(ctx,table):
        fig,ax=plt.subplots();return PanelResult([ax])
    with pytest.raises(ValueError,match='unrelated'):compose(simple_spec(),tables_fixture(),{'fixture':bad})
    plt.close('all')

def test_canvas_check_identifies_bad_text():
    c=compose(simple_spec(),tables_fixture(),{'fixture':fixture})
    c.figure.text(1.2,0.5,'OFF CANVAS');c.figure.text(.5,.5,'too small',fontsize=3)
    qa=inspect_canvas(c.figure,c.spec,c.results)
    codes={x['code'] for x in qa['issues']}
    assert {'TEXT_OUTSIDE_CANVAS','TEXT_TOO_SMALL'}<=codes;plt.close(c.figure)

def test_export_draft_bundle(tmp_path):
    c=compose(simple_spec(),tables_fixture(),{'fixture':fixture})
    paths=write_bundle(c,tmp_path)
    assert {'labelled_pdf','labelled_svg','labelled_png','provenance'}<=set(paths)
    assert not json.loads((tmp_path/'qa.json').read_text())['release_ready']
    assert (tmp_path/'figure_spec.json').exists();plt.close(c.figure)

def test_composable_complex_heatmap():
    s=simple_spec();p=s['panels'][0];p.update(renderer='annotated_heatmap',
      channels={'x':'column','y':'row','color':'value','row_metric':'rm','col_metric':'cm','effect':'effect'},
      scale_ids={'color':'expression'})
    s['datasets']['data_a']['keys']=['row','column']
    t=tables_fixture();t['data_a']=pd.DataFrame({'row':['R1','R1','R2','R2'], 'column':['C1','C2','C1','C2'],
           'value':[1.,2.,3.,4.],'rm':[2.,2.,3.,3.],'cm':[1.,2.,1.,2.],'effect':['.1','.2','.3','.4']})
    registry=dict(REGISTRY,fixture=fixture);c=compose(s,t,registry)
    assert len(c.results['a'].axes)==4
    assert len(c.figure.axes)==5
    assert not any(x['code']=='MAPPABLE_SCALE_MISMATCH' for x in c.qa['issues']);plt.close(c.figure)

def test_native_spatial_single_section():
    s=simple_spec();p=s['panels'][0];p.update(renderer='spatial',channels={'x':'x','y':'y','color':'value'},scale_ids={'color':'expression'},
      spatial={'unit':'um','y_axis_down':True,'section_column':'section_id','transform_applied':'Identity transform; software test.'})
    t=tables_fixture();t['data_a']['value']=[0.,1.,2.];t['data_a']['section_id']='S1'
    c=compose(s,t,dict(REGISTRY,fixture=fixture));assert c.results['a'].axes[0].yaxis_inverted();plt.close(c.figure)
    t['data_a'].loc[1,'section_id']='S2'
    with pytest.raises(ValueError,match='exactly one'):compose(s,t,dict(REGISTRY,fixture=fixture))

def test_native_embedding_and_dot():
    s=simple_spec();s['panels'][0].update(renderer='embedding',channels={'x':'x','y':'y','category':'cell_type'},scale_ids={'category':'identity'})
    s['panels'][1].update(renderer='marker_dot',channels={'x':'gene','y':'group','color':'mean_expression','size':'fraction_detected'},scale_ids={'color':'expression'})
    s['datasets']['data_b']['keys']=['gene','group']
    t=tables_fixture();t['data_a']['cell_type']=['Population_A','Population_B','Population_A']
    t['data_b']=pd.DataFrame({'gene':['G1','G2'],'group':['Population_A','Population_A'],'mean_expression':[1.,2.],'fraction_detected':[.2,.8]})
    c=compose(s,t,REGISTRY);assert len(c.results)==2;plt.close(c.figure)


def test_end_to_end_project(tmp_path):
    import yaml
    from render_project import render_project
    s=simple_spec()
    for p in s['panels']:
        p.update(renderer='embedding',channels={'x':'x','y':'y','category':'cell_type'},scale_ids={'category':'identity'})
    for did in s['datasets']:
        s['datasets'][did]['path']=did+'.csv'
        pd.DataFrame({'id':['QA1','QA2'], 'x':[0,1], 'y':[0,1],
           'cell_type':['Population_A','Population_B']}).to_csv(tmp_path/(did+'.csv'),index=False)
    path=tmp_path/'spec.yaml';path.write_text(yaml.safe_dump(s,sort_keys=False))
    out=tmp_path/'build';r=render_project(path,tmp_path,out)
    assert r['status']=='rendered_review_pending'
    assert (out/'preflight.json').exists() and (out/'render_plan.json').exists()
    provenance=json.loads((out/(s['figure']['id']+'_provenance.json')).read_text())
    assert len(provenance['input_manifest']['data_a']['sha256'])==64


def test_direct_table_empty_key_is_rejected():
    tables=tables_fixture();tables['data_a'].loc[0,'id']='  '
    with pytest.raises(ValueError,match='primary key'):
        compose(simple_spec(),tables,{'fixture':fixture})
