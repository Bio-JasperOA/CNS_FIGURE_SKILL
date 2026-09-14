"""Deterministic SOFTWARE QA fixtures; never presented as biological results."""
from copy import deepcopy
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt
from matplotlib import colors
from visual_contract import VisualScale,validate_visual_spec,palette_audit,lab
from visual_layout import Measure,LayoutFailure,fit_panel,all_guides
from visual_audit import geometry_audit,audit_pdf,audit_carrier,compare_rasters,inspect_figure,digest
from review_gate import snapshot,impact,review_template,check_review,escalation
from render_v3 import render
from framework_contract import read_spec,panel_boxes
ROOT=Path(__file__).resolve().parents[1]


def scale(**kwargs):return dict(kind='continuous',limits=[0.,4.],label='SOFTWARE QA value',cmap='viridis',**kwargs)


def fixture_spec():
    s=read_spec(ROOT/'assets'/'atlas.yaml');s['spec_version']='3.0'
    s['figure'].update(id='software_qa',question='SOFTWARE QA ONLY',main_message='NO BIOLOGICAL RESULTS',width_mm=183,height_mm=105)
    s['layout'].update(rows=1,cols=1,row_weights=[1],col_weights=[1])
    s['panels']=s['panels'][:1];s['panels'][0]['slot']=[0,0,1,1]
    s['panels'][0].update(renderer='embedding',channels={'x':'x','y':'y','category':'cell_type'},scale_ids={'category':'identity'})
    s['datasets']={'data_a':dict(path='data.csv',grain='cell',keys=['id'],value_definition='Artificial software test',source='SOFTWARE QA ONLY')}
    s['design'].update(font_family='DejaVu Sans',fallback_font='DejaVu Sans')
    s['visual']={'reading_order':['a'],'lead_panel':'a'}
    return json.loads(json.dumps(s).replace('DRAFT:','SOFTWARE QA:'))


def fixture_table():return pd.DataFrame({'id':['qa1','qa2','qa3','qa4'],'x':[0.,1.,2.,3.],'y':[0.,1.,.5,2.],
    'cell_type':['Population_A','Population_B','Population_A','Population_B'],'value':[0.,1.,2.,np.nan],'section':['qa']*4})

@pytest.mark.parametrize('kind,params,limits,values,expected',[
 ('linear',{},[0,4],[0,2,4],[0,.5,1]),('two_slope',{'center':0},[-2,8],[-2,0,8],[0,.5,1]),
 ('log',{},[1,100],[1,10,100],[0,.5,1]),('symlog',{'linthresh':1},[-100,100],[-100,0,100],[0,.5,1]),
 ('power',{'gamma':2},[0,4],[0,2,4],[0,.25,1]),('boundary',{'boundaries':[0,1,4]},[0,4],[0,1,4],[0,1,1])])
def test_normalizers(kind,params,limits,values,expected):
    s=scale(norm={'type':kind,**params});s['limits']=limits;v=VisualScale(s)
    assert np.allclose(v.norm(values),expected)

@pytest.mark.parametrize('policy',['extend','clip','mask','error'])
def test_out_of_range_policy(policy):
    v=VisualScale(scale(out_of_range=policy));original=np.array([-1.,2.,5.,np.nan]);copy=original.copy()
    if policy=='error':
        with pytest.raises(ValueError):v.prepare(original)
    else:
        a,c=v.prepare(original);assert c['under']==1 and c['over']==1 and c['missing']==1
        if policy=='clip':assert a[0]==0 and a[2]==4
        if policy=='mask':assert a.mask.sum()==3
    assert np.array_equal(original,copy,equal_nan=True)

@pytest.mark.parametrize('values',[[0,1],[-1,2],[np.inf,2]])
def test_invalid_log(values):
    s=scale(norm={'type':'log'});s['limits']=[1,4]
    with pytest.raises(ValueError):VisualScale(s).prepare(values)
    s['invalid']='mask';assert np.ma.getmaskarray(VisualScale(s).prepare(values)[0]).sum()==1

@pytest.mark.parametrize('mutation',[{'norm':{'type':'linear','center':1}},{'norm':{'type':'two_slope','center':9}},
 {'norm':{'type':'boundary','boundaries':[0,2,1,4]}},{'norm':{'type':'power','gamma':0}}])
def test_invalid_norms(mutation):
    with pytest.raises((ValueError,KeyError)):VisualScale(scale(**mutation))


def test_ticks_are_original_units():
    s=scale(norm={'type':'log'});s['limits']=[1,100]
    ticks,labels=VisualScale(s).ticks({'max_ticks':3});assert np.allclose(ticks,[1,10,100]);assert labels==['1','10','100']
    with pytest.raises(ValueError):VisualScale(s).ticks({'ticks':[1,10,100],'labels':['oops']})


def test_lab_black_white_and_pair_screen():
    assert np.allclose(lab([[0,0,0],[1,1,1]])[:,0],[0,100],atol=.01)
    s=dict(kind='categorical',order=['a','b'],colors={'a':'#888888','b':'#898989'},label='QA')
    r=palette_audit(s);assert r['close_pairs'];assert 'SIMILAR_CATEGORIES' in r['issues'];assert not r['release_approval']
    r=palette_audit(scale());assert 'LIGHTNESS_REVERSAL' not in r['issues']
    assert r['cvd']['status'] in ['screened','not_run_missing_colorspacious']


def test_broken_palette_lightness():
    s=scale();s['cmap']='jet';assert 'LIGHTNESS_REVERSAL' in palette_audit(s)['issues']


def test_new_schema_and_shared_guide():
    s=fixture_spec();assert validate_visual_spec(s)['ok']
    s['guides']={'g':{'owner':'a','panels':['a'],'channel':'category','scale_id':'expression'}}
    assert not validate_visual_spec(s)['ok']
    s=fixture_spec();s['visual']['typo']=1;assert not validate_visual_spec(s)['ok']


def test_measured_long_labels_and_infeasible_layout():
    s=fixture_spec();table=fixture_table();fig=plt.figure(figsize=(183/25.4,105/25.4))
    m=Measure(fig,'DejaVu Sans',7);assert m('long label')[0]>m('x')[0]
    layout=fit_panel(fig,s,s['panels'][0],panel_boxes(s)['a'],{'data_a':table},all_guides(s),'DejaVu Sans')
    assert layout['guides'] and layout['plot_mm'][2]>18
    s['figure'].update(width_mm=40,height_mm=30)
    with pytest.raises(LayoutFailure):fit_panel(fig,s,s['panels'][0],panel_boxes(s)['a'],{'data_a':table},all_guides(s),'DejaVu Sans')
    plt.close(fig)


def test_geometry_failure_classes():
    items=[dict(id='x',text='qa',panel='a',box_mm=[40,5,20,5],font_pt=4),
           dict(id='y',text='qb',panel='b',box_mm=[45,5,20,5],font_pt=7,clip_mm=[45,5,10,5])]
    codes={i['code'] for i in geometry_audit(items,[0,0,50,30],panels={'b':{'plot_mm':[42,0,8,30]}},protected=[{'id':'roi','box_mm':[42,6,2,2]}])}
    assert {'TEXT_OUTSIDE_CANVAS','FINAL_FONT_TOO_SMALL','CROSS_PANEL_INTRUSION','TEXT_COLLISION','LOCAL_TEXT_CLIP','PROTECTED_REGION_OCCLUDED'}<=codes


def test_typography_math_and_missing_glyph():
    s=fixture_spec();fig=plt.figure(figsize=(4,3));fig.text(.1,.7,r'$\alpha + x^2$');fig.text(.1,.2,'\U0010ffff')
    r=inspect_figure(fig,s,{},{});assert r['math_fonts'];assert any(i['code']=='GLYPH_COVERAGE' for i in r['issues']);plt.close(fig)


def pdf_fixture(path):
    fig=plt.figure(figsize=(100/25.4,80/25.4));fig.text(.1,.8,'Alpha',fontsize=10);fig.text(.7,.6,'Beta',fontsize=10);fig.text(.3,.2,'Gamma',fontsize=10)
    fig.savefig(path);plt.close(fig)


def test_pdf_final_size_and_carrier(tmp_path):
    import fitz
    source=tmp_path/'source.pdf';pdf_fixture(source)
    r=audit_pdf(source,expected_mm=[100,80]);assert r['automatic_pass']
    assert not audit_pdf(source,expected_mm=[80,80])['automatic_pass']
    target=tmp_path/'report.pdf'
    with fitz.open(source) as src,fitz.open() as dst:
        p=dst.new_page(width=400,height=400);p.show_pdf_page(fitz.Rect(10,10,10+100*72/25.4,10+80*72/25.4),src,0);dst.save(target)
    b=[10*25.4/72,10*25.4/72,100,80];r=audit_carrier(source,target,{'box_mm':b});assert r['automatic_pass'],r
    tiny=tmp_path/'tiny.pdf'
    with fitz.open(source) as src,fitz.open() as dst:
        p=dst.new_page(width=400,height=400);p.show_pdf_page(fitz.Rect(10,10,10+50*72/25.4,10+40*72/25.4),src,0);dst.save(tiny)
    r=audit_carrier(source,tiny,{'box_mm':[b[0],b[1],50,40]});assert any(i['code']=='FINAL_FONT_TOO_SMALL' for i in r['issues'])


def test_raster_regression_detects_degradation(tmp_path):
    from PIL import Image
    a=np.full((100,100,3),255,np.uint8);b=a.copy();b[20:60,20:60]=0
    x,y=tmp_path/'a.png',tmp_path/'b.png';Image.fromarray(a).save(x);Image.fromarray(b).save(y)
    assert compare_rasters(x,x)['pass_check'];assert not compare_rasters(x,y)['pass_check']
    Image.fromarray(b[:50]).save(y);assert compare_rasters(x,y)['reason']=='DIMENSION_CHANGE'


def test_impact_and_stale_review(tmp_path):
    p=tmp_path/'artifact.txt';p.write_text('QA');s=fixture_spec();a=snapshot(s,{},[p]);b=deepcopy(a)
    b['spec']['scales']['identity']['colors']['Population_A']='#333333';assert impact(a,b)['affected_panels']==['a']
    r=review_template(a);assert not check_review(r,a,[])['release_ready']
    r.update(reviewer='SOFTWARE TEST ACTOR',reviewed_at='2026-09-14T00:00:00+00:00',carrier_mode='standalone')
    for row in r['criteria'].values():row.update(status='pass',evidence='Explicit software fixture assertion, not a scientific review.')
    assert check_review(r,a,[])['release_ready']
    p.write_text('modified');assert not check_review(r,a,[])['release_ready'];assert not check_review(r,b,[])['release_ready']


def test_repair_escalation():
    h=[dict(issue_codes=['TEXT_COLLISION'],touched_panels=['a'])]*2
    assert escalation(h)['action']=='restructure';assert escalation(h[:1])['action']=='local_repair'
    assert escalation([dict(touched_panels=['a','b'])])['action']=='restructure'

@pytest.mark.parametrize('kind',['embedding','spatial','marker_dot','annotated_heatmap'])
def test_v3_end_to_end(tmp_path,kind):
    import yaml
    s=fixture_spec();p=s['panels'][0];table=fixture_table();p['renderer']=kind
    if kind=='spatial':
        p.update(channels={'x':'x','y':'y','color':'value'},scale_ids={'color':'expression'},
            spatial={'unit':'um','section_column':'section','y_axis_down':True,'transform_applied':'SOFTWARE QA identity'})
    if kind in ['marker_dot','annotated_heatmap']:
        table=pd.DataFrame({'row':['R1','R1','R2','R2'],'col':['C1','C2','C1','C2'],'value':[0.,1.,2.,np.nan],
            'fraction':[.2,.5,.7,np.nan],'rm':[1.,1.,2.,2.],'cm':[1.,2.,1.,2.],'effect':['.1','.2','.3','']})
        s['datasets']['data_a'].update(keys=['row','col'],grain='matrix')
        p.update(channels={'x':'col','y':'row','color':'value'},scale_ids={'color':'expression'})
        if kind=='marker_dot':p['channels']['size']='fraction'
        else:p['channels'].update(row_metric='rm',col_metric='cm',effect='effect')
    table.to_csv(tmp_path/'data.csv',index=False);(tmp_path/'spec.yaml').write_text(yaml.safe_dump(s))
    r=render(tmp_path/'spec.yaml',tmp_path,tmp_path/'build')
    assert not r['release_ready'];assert (tmp_path/'build'/'snapshot.json').is_file()
    qa=json.loads((tmp_path/'build'/'qa.json').read_text());assert qa['pdf']['text'];assert 'palettes' in qa
    assert not any(i['code'] in ['TEXT_OUTSIDE_CANVAS','CROSS_PANEL_INTRUSION','PDF_PAGE_SIZE'] for i in qa['issues']),qa['issues']

@pytest.mark.parametrize('kind',['protanomaly','deuteranomaly','tritanomaly'])
def test_cvd_screen_numeric_boundaries(kind):
    from visual_contract import cvd_simulate
    rgb,clipped=cvd_simulate(np.array([[0.,0.,0.],[1.,1.,1.],[1.,0.,0.],[0.,1.,0.]]),kind)
    assert np.allclose(rgb[:2],[[0,0,0],[1,1,1]],atol=2e-5)
    assert np.isfinite(rgb).all() and np.all((rgb>=0)&(rgb<=1)) and 0<=clipped<=1

@pytest.mark.parametrize('kind,params,limits',[('linear',{},[0,4]),('two_slope',{'center':0},[-2,4]),
 ('log',{},[1,4]),('symlog',{'linthresh':1},[-2,4]),('power',{'gamma':2},[0,4]),
 ('boundary',{'boundaries':[0,1,4]},[0,4])])
def test_explicit_under_over_and_missing_colors(kind,params,limits):
    s=scale(norm={'type':kind,**params},under='#123456',over='#fedcba',bad='#abcdef');s['limits']=limits
    v=VisualScale(s);low=.5 if kind=='log' else limits[0]-1
    data,c=v.prepare([low,limits[-1]+1,np.nan]);actual=[colors.to_hex(x) for x in v.cmap(v.norm(data))]
    assert actual==['#123456','#fedcba','#abcdef']


def test_no_false_missing_for_existing_color(tmp_path):
    v=VisualScale(scale(bad='#440154'));a,c=v.prepare([0.,np.nan]);assert c['missing']==1
    assert colors.to_hex(v.cmap(v.norm(a))[0])==colors.to_hex(v.cmap(v.norm(a))[1])
    assert np.ma.getmaskarray(a).tolist()==[False,True]


def test_explicit_guide_length_and_nonlinear_tick_density():
    s=fixture_spec();p=s['panels'][0];p.update(renderer='spatial',channels={'x':'x','y':'y','color':'value'},scale_ids={'color':'expression'},
        spatial={'unit':'um','section_column':'section','y_axis_down':False,'transform_applied':'QA'})
    s['scales']['expression'].update(limits=[1,1000],norm={'type':'log'})
    s['guides']={'g':{'owner':'a','panels':['a'],'channel':'color','scale_id':'expression','position':'right','ticks':[1,1.001,1000],'length_mm':20.}}
    fig=plt.figure();t=fixture_table();t['value']=[1,10,100,np.nan]
    with pytest.raises(LayoutFailure):fit_panel(fig,s,p,panel_boxes(s)['a'],{'data_a':t},all_guides(s),'DejaVu Sans')
    plt.close(fig)


def test_shared_guide_is_drawn_once_and_change_propagates(tmp_path):
    import yaml
    s=fixture_spec();p=deepcopy(s['panels'][0]);p.update(id='b',slot=[0,1,1,1],depends_on=['a']);s['panels'].append(p)
    s['visual'].update(reading_order=['a','b']);s['layout'].update(cols=2,col_weights=[1,1])
    s['guides']={'identity':{'owner':'b','panels':['a','b'],'channel':'category','scale_id':'identity','position':'bottom'}}
    (tmp_path/'spec.yaml').write_text(yaml.safe_dump(s));fixture_table().to_csv(tmp_path/'data.csv',index=False)
    render(tmp_path/'spec.yaml',tmp_path,tmp_path/'build')
    plan=json.loads((tmp_path/'build/render_plan_v3.json').read_text());assert len(plan['layouts']['a']['guides'])==0 and len(plan['layouts']['b']['guides'])==1
    a=snapshot(s,{},[]);b=deepcopy(a);b['inputs']['data_a']={'sha256':'changed'}
    assert impact(a,b)['affected_panels']==['a','b']


def test_reject_crowded_legends_and_extreme_aspect():
    s=fixture_spec();t=fixture_table();s['figure'].update(width_mm=70,height_mm=50)
    s['scales']['identity']['order']=[f'Very_long_category_{i:03d}' for i in range(30)]
    s['scales']['identity']['colors']={n:'#336699' for n in s['scales']['identity']['order']}
    fig=plt.figure()
    with pytest.raises(LayoutFailure):fit_panel(fig,s,s['panels'][0],panel_boxes(s)['a'],{'data_a':t},all_guides(s),'DejaVu Sans')
    s=fixture_spec();t['x']*=100
    with pytest.raises(LayoutFailure):fit_panel(fig,s,s['panels'][0],panel_boxes(s)['a'],{'data_a':t},all_guides(s),'DejaVu Sans')
    plt.close(fig)


def test_configuration_changes_invalidate_existing_review(tmp_path):
    s=fixture_spec();f=tmp_path/'spec.json';f.write_text(json.dumps(s));a=snapshot(s,{'spec':{'resolved_path':str(f),'sha256':digest(f)}},[])
    r=review_template(a);r.update(reviewer='QA',reviewed_at='2026-09-14T00:00:00+00:00',carrier_mode='standalone')
    for row in r['criteria'].values():row.update(status='pass',evidence='SOFTWARE QA assertion')
    assert check_review(r,a,[])['release_ready'];f.write_text('{}');assert not check_review(r,a,[])['release_ready']


def test_required_warning_acknowledgement():
    from visual_audit import issue
    s=snapshot(fixture_spec(),{},[]);r=review_template(s);r.update(reviewer='QA',reviewed_at='2026-09-14T00:00:00+00:00',carrier_mode='standalone')
    for row in r['criteria'].values():row.update(status='pass',evidence='SOFTWARE QA assertion')
    w=issue('COLLISION','fixture',severity='warning');assert not check_review(r,s,[w])['release_ready']
    r['acknowledged_warnings'][w['id']]='Inspected artificial fixture.';assert check_review(r,s,[w])['release_ready']
    w['severity']='error';assert not check_review(r,s,[w])['release_ready']


def test_r_bridge_runtime_when_available(tmp_path):
    import shutil,subprocess,yaml
    if not shutil.which('Rscript'):pytest.skip('Rscript absent: native R behavior is NOT verified.')
    ok=subprocess.run(['Rscript','-e','quit(status=if(requireNamespace("jsonlite",quietly=TRUE)) 0 else 2)'],capture_output=True)
    if ok.returncode:pytest.skip('jsonlite absent in the available R runtime.')
    s=fixture_spec();(tmp_path/'spec.yaml').write_text(yaml.safe_dump(s));fixture_table().to_csv(tmp_path/'data.csv',index=False)
    render(tmp_path/'spec.yaml',tmp_path,tmp_path/'build')
    subprocess.run(['Rscript',str(ROOT/'scripts/render_v3.R'),str(tmp_path/'build/render_plan_v3.json'),str(tmp_path/'r.pdf')],check=True)
    assert audit_pdf(tmp_path/'r.pdf')['automatic_pass']


def test_two_pdf_rasterizers(tmp_path):
    import shutil,subprocess
    if not shutil.which('pdftoppm'):pytest.skip('Poppler is not installed.')
    pdfium=pytest.importorskip('pypdfium2')
    pdf=tmp_path/'fixture.pdf';pdf_fixture(pdf)
    subprocess.run(['pdftoppm','-r','144','-png','-singlefile',str(pdf),str(tmp_path/'poppler')],check=True,capture_output=True)
    doc=pdfium.PdfDocument(str(pdf));page=doc[0];bitmap=page.render(scale=2);bitmap.to_pil().save(tmp_path/'pdfium.png');bitmap.close();page.close();doc.close()
    result=compare_rasters(tmp_path/'poppler.png',tmp_path/'pdfium.png',threshold=32,max_fraction=.025)
    assert result['pass_check'],result


def test_operational_design_warnings():
    from visual_layout import design_audit
    s=fixture_spec();p=deepcopy(s['panels'][0]);p.update(id='b',slot=[0,1,1,1]);s['panels'].append(p)
    s['visual'].update(lead_panel='a',reading_order=['b','a'])
    layouts={'a':{'outer_mm':[0,0,40,40],'plot_mm':[1,1,20,20]},'b':{'outer_mm':[45,0,80,80],'plot_mm':[46,1,70,70]}}
    codes={i['code'] for i in design_audit(s,layouts,{'data_a':fixture_table()})}
    assert {'READING_ORDER_REVIEW','VISUAL_HIERARCHY_REVIEW'}<=codes


def test_guide_wrap_preserves_words_and_identifiers():
    fig=plt.figure();m=Measure(fig,'DejaVu Sans',7)
    text=m.wrap('log-normalized expression',24)
    assert 'log-normalized' in text and 'expression' in text
    assert ''.join(m.wrap('ABCDEFGHIJKLMNOPQRSTUVXYZ',10).splitlines())=='ABCDEFGHIJKLMNOPQRSTUVXYZ'
    plt.close(fig)


def test_title_mark_size_and_fraction_only_missing(tmp_path):
    import yaml
    s=fixture_spec();p=s['panels'][0];p.update(renderer='marker_dot',title='ARTIFICIAL SOFTWARE QA: marker matrix',
        channels={'x':'col','y':'row','color':'value','size':'fraction'},scale_ids={'color':'expression'})
    s['datasets']['data_a'].update(keys=['row','col'],grain='matrix')
    t=pd.DataFrame({'row':['R1','R1'],'col':['C1','C2'],'value':[0.,1.],'fraction':[.2,np.nan]})
    t.to_csv(tmp_path/'data.csv',index=False);(tmp_path/'spec.yaml').write_text(yaml.safe_dump(s))
    render(tmp_path/'spec.yaml',tmp_path,tmp_path/'build')
    qa=json.loads((tmp_path/'build/qa.json').read_text());assert qa['disclosure']['a']['missing_size']==1
    t=pd.read_csv(tmp_path/'build/prepared/a.csv');assert t['_v3_missing'].tolist()==[0,1]
    plan=json.loads((tmp_path/'build/render_plan_v3.json').read_text())
    assert plan['layouts']['a']['title'].startswith('ARTIFICIAL')
    assert next(g for g in plan['layouts']['a']['guides'] if g['channel']=='color')['missing']


def test_bind_export_report_invalidates_review(tmp_path):
    import yaml
    from review_gate import bind_report
    s=fixture_spec();(tmp_path/'spec.yaml').write_text(yaml.safe_dump(s));fixture_table().to_csv(tmp_path/'data.csv',index=False)
    render(tmp_path/'spec.yaml',tmp_path,tmp_path/'build')
    original=json.loads((tmp_path/'build/snapshot.json').read_text())
    report=tmp_path/'export_check.json';report.write_text(json.dumps(audit_pdf(tmp_path/'build/software_qa.pdf')))
    result=bind_report(tmp_path/'build',report,'export')
    assert result['status']=='report_bound_review_stale'
    state=json.loads((tmp_path/'build/snapshot.json').read_text());assert str(report) in state['artifacts']
    assert original!=state and (tmp_path/'build/review_pending.json').is_file()
    assert any(path.endswith('render_v3.R') for path in state['code'])


def test_shipped_example(tmp_path):
    example=ROOT/'examples/v3_software_qa'
    result=render(example/'figure.yaml',example,tmp_path/'build')
    assert result['automatic_pass'] and not result['release_ready']
    qa=json.loads((tmp_path/'build/qa.json').read_text())
    assert qa['disclosure']['a']['under']==1 and qa['disclosure']['a']['over']==1
    assert qa['disclosure']['a']['missing']==1
    assert any('ARTIFICIAL' in t['text'] for t in qa['pdf']['text'])


def test_unsupported_renderer_fails_before_drawing():
    s=fixture_spec();s['panels'][0]['renderer']='unimplemented_scientific_magic'
    assert not validate_visual_spec(s)['ok']
    s=fixture_spec();s['panels'][0]['marks']={'area_pt2':30.};assert validate_visual_spec(s)['ok']
    s['panels'][0]['protected_regions']=[{'id':'invalid','bounds_data':[0,0,-1,3]}]
    assert not validate_visual_spec(s)['ok']


def test_capability_registry():
    import ast
    from visual_contract import SUPPORTED_RENDERERS
    cap=json.loads((ROOT/'CAPABILITIES.json').read_text())
    assert {r['id'] for r in cap['issues']}==set(range(1,18))
    assert set(cap['python_v3_renderers'])==SUPPORTED_RENDERERS
    for row in cap['issues']:
        for path in row['implementation']:assert (ROOT/path).is_file(),path
        for ref in row['tests']:
            path,name=ref.split('::');tree=ast.parse((ROOT/path).read_text())
            assert name in {n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)},ref


def test_bind_actual_carrier(tmp_path):
    import yaml,fitz
    from review_gate import bind_report
    s=fixture_spec();(tmp_path/'spec.yaml').write_text(yaml.safe_dump(s));fixture_table().to_csv(tmp_path/'data.csv',index=False)
    render(tmp_path/'spec.yaml',tmp_path,tmp_path/'build')
    source=tmp_path/'build/software_qa.pdf';target=tmp_path/'report.pdf'
    src=fitz.open(source);doc=fitz.open();page=doc.new_page(width=src[0].rect.width+50,height=src[0].rect.height+50)
    page.show_pdf_page(src[0].rect+fitz.Rect(20,20,20,20),src,0);doc.save(target);doc.close();src.close()
    placement={'page_index':0,'box_mm':[20*25.4/72,20*25.4/72,183,105]}
    record=audit_carrier(source,target,placement);record.update(source_path=str(source),carrier_path=str(target))
    report=tmp_path/'carrier.json';report.write_text(json.dumps(record))
    result=bind_report(tmp_path/'build',report,'carrier')
    assert result['automatic_pass'] and not result['release_ready']


def test_raster_cli_exit_status(tmp_path,monkeypatch):
    from PIL import Image
    import render_v3
    a=tmp_path/'a.png';b=tmp_path/'b.png';Image.new('RGB',(20,20),'white').save(a);Image.new('RGB',(20,20),'black').save(b)
    monkeypatch.setattr('sys.argv',['render_v3.py','compare',str(a),str(b),'--out',str(tmp_path/'regression.json')])
    assert render_v3.main()==2


def test_irrelevant_guide_settings_rejected():
    s=fixture_spec();s['guides']={'g':{'owner':'a','panels':['a'],'channel':'category','scale_id':'identity','length_mm':20}}
    assert not validate_visual_spec(s)['ok']
    s['guides']['g'].pop('length_mm');s['guides']['g']['ncol']=2
    assert validate_visual_spec(s)['ok']
