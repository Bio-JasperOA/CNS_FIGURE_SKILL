"""Focused v3 rendering CLI. Run --help for rendering and post-export audits."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from copy import deepcopy
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.text import Text
import pandas as pd
import numpy as np
from figure_core import FigureStyle,apply_style,export_figure
from framework_contract import read_spec,panel_boxes
from composer import load_tables
from visual_contract import VISUAL_DEFAULTS,VisualScale,legacy_view,validate_visual_spec,palette_audit
from visual_layout import all_guides,fit_panel,draw_panel,figure_text,design_audit,LayoutFailure
from visual_audit import inspect_figure,audit_pdf,audit_carrier,compare_rasters,issue,digest
from review_gate import snapshot,review_template,check_review,impact,escalation,bind_report


def write_json(path,record):
    Path(path).write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def render(spec_path,root,output):
    spec=read_spec(spec_path);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    pre=validate_visual_spec(spec,check_files=True,root=root);write_json(out/'preflight.json',pre)
    if not pre['ok']:raise ValueError('Preflight failed; see preflight.json.')
    tab=load_tables(legacy_view(spec),root);guides=all_guides(spec);bounds=panel_boxes(spec)
    policy=dict(VISUAL_DEFAULTS,**spec.get('visual',{}));d=spec['design'];work=deepcopy(spec)
    with mpl.rc_context():
        font=apply_style(FigureStyle(font=d['font_family'],fallback_font=d['fallback_font'],font_pt=d['font_pt'],label_pt=d['tag_pt'],line_pt=d['line_pt']))
        mpl.rcParams.update({'mathtext.fontset':policy['math_fontset'],'figure.facecolor':policy['background'],'axes.facecolor':policy['background']})
        work['design']['font_family']=font
        fig=plt.figure(figsize=(spec['figure']['width_mm']/25.4,spec['figure']['height_mm']/25.4));layouts={};results={}
        try:
            for p in work['panels']:layouts[p['id']]=fit_panel(fig,work,p,bounds[p['id']],tab,guides,font)
            for p in work['panels']:
                results[p['id']]=draw_panel(fig,work,p,layouts[p['id']],tab,guides)
                x,y,_,_=bounds[p['id']]['outer_mm'];figure_text(fig,x,y+1,p['id'],d['tag_pt'],p['id'],fontweight='bold')
            for t in fig.findobj(match=Text):t.set_linespacing(policy['line_spacing'])
            artist_qa=inspect_figure(fig,work,layouts,results)
            palette_qa={sid:palette_audit(s,policy) for sid,s in spec['scales'].items()}
            files=export_figure(fig,out/spec['figure']['id'],source_tables=tab,provenance=dict(
                data_source=pre['input_manifest'],analysis_unit={k:v['grain'] for k,v in spec['datasets'].items()},
                value_definition={k:v['value_definition'] for k,v in spec['datasets'].items()},seed=0,
                requested_font=d['font_family'],actual_font=font,status='DRAFT; review gate not passed'))
            # Only plain reviewed data and explicit mapped colors are exchanged with R.
            prepared={};transforms={};(out/'prepared').mkdir(exist_ok=True)
            for p in work['panels']:
                pid=p['id'];a=tab[p['data_id']].copy();ch=p['channels']
                if any(c.startswith('_v3_') for c in a):raise ValueError('Reserved _v3_ columns in input.')
                if 'color' in ch:
                    vs=VisualScale(spec['scales'][p['scale_ids']['color']]);v,_=vs.prepare(pd.to_numeric(a[ch['color']],errors='raise').to_numpy(float))
                    if p['renderer']=='marker_dot':
                        v=np.ma.array(v,mask=np.ma.getmaskarray(v)|pd.to_numeric(a[ch['size']],errors='raise').isna().to_numpy())
                    a['_v3_color']=[mpl.colors.to_hex(c,keep_alpha=True) for c in vs.cmap(vs.norm(v))]
                    a['_v3_missing']=np.ma.getmaskarray(v).astype(int)
                elif 'category' in ch:a['_v3_color']=[spec['scales'][p['scale_ids']['category']]['colors'][str(c)] for c in a[ch['category']]]
                name=f'prepared/{pid}.csv';a.to_csv(out/name,index=False);prepared[pid]=name
                ax=results[pid]['axes'][0];transforms[pid]=dict(xlim=list(ax.get_xlim()),ylim=list(ax.get_ylim()))
                if p['renderer']=='annotated_heatmap':
                    for key,tax in zip(['column_track_mm','row_track_mm'],results[pid]['axes'][1:3]):
                        q=tax.get_position();fw,fh=fig.get_size_inches()*25.4
                        layouts[pid][key]=[float(q.x0*fw),float((1-q.y1)*fh),float(q.width*fw),float(q.height*fh)]
                    q=ax.get_position();fw,fh=fig.get_size_inches()*25.4
                    layouts[pid]['plot_mm']=[float(q.x0*fw),float((1-q.y1)*fh),float(q.width*fw),float(q.height*fh)]
        except LayoutFailure as e:
            write_json(out/'layout_failure.json',dict(status='restructure_required',message=str(e)))
            history_path=out/'repair_history.json';history=json.loads(history_path.read_text()) if history_path.exists() else []
            history.append(dict(issue_codes=['LAYOUT_INFEASIBLE'],touched_panels=[p['id']]))
            write_json(history_path,history);write_json(out/'repair_decision.json',dict(action='restructure',reasons=[str(e)]))
            raise
        finally:plt.close(fig)
    pdf_qa=audit_pdf(files['labelled_pdf'],expected_mm=[spec['figure']['width_mm'],spec['figure']['height_mm']],min_font_pt=d['min_font_pt'])
    issues=artist_qa['issues']+pdf_qa['issues']+design_audit(spec,layouts,tab)
    for sid,record in palette_qa.items():
        for message in record['issues']:issues.append(issue('PALETTE_SCREEN',message,severity='warning',scale=sid))
    qa=dict(version='3.0',artist=artist_qa,pdf=pdf_qa,palettes=palette_qa,
        disclosure={k:r['disclosure'] for k,r in results.items()},issues=issues,
        automatic_pass=not any(i['severity']=='error' for i in issues),release_ready=False,
        status='draft_requires_review',unverified=['R native execution','optical kerning','real biological dataset validation'])
    write_json(out/'qa.json',qa);write_json(out/'figure_spec.json',spec)
    history_path=out/'repair_history.json';history=json.loads(history_path.read_text()) if history_path.exists() else []
    local_codes={'TEXT_COLLISION','TEXT_OUTSIDE_CANVAS','CROSS_PANEL_INTRUSION','LOCAL_TEXT_CLIP','FINAL_FONT_TOO_SMALL','INFORMATION_DENSITY_REVIEW'}
    selected=[i for i in issues if i['code'] in local_codes]
    history.append(dict(issue_codes=sorted({i['code'] for i in selected}),touched_panels=sorted({i['panel'] for i in selected if i.get('panel')}),below_min_font=any(i['code']=='FINAL_FONT_TOO_SMALL' for i in selected)))
    write_json(history_path,history);write_json(out/'repair_decision.json',escalation(history,policy['max_repair_cycles']))
    lookup={}
    for sid,s in spec['scales'].items():
        if s['kind']=='continuous':
            vs=VisualScale(s);lookup[sid]=dict(colors=[mpl.colors.to_hex(c,keep_alpha=True) for c in vs.cmap(np.linspace(0,1,256))],bad=mpl.colors.to_hex(vs.cmap.get_bad(),keep_alpha=True),under=mpl.colors.to_hex(vs.cmap.get_under(),keep_alpha=True),over=mpl.colors.to_hex(vs.cmap.get_over(),keep_alpha=True),out_of_range=s.get('out_of_range','extend'))
    write_json(out/'render_plan_v3.json',dict(version='3.0',spec=work,layouts=layouts,prepared=prepared,coordinates=transforms,palettes=lookup))
    manifests=deepcopy(pre['input_manifest'])
    for did,record in manifests.items():record['resolved_path']=str((Path(root)/spec['datasets'][did]['path']).resolve())
    manifests['__figure_spec__']=dict(resolved_path=str(Path(spec_path).resolve()),sha256=digest(spec_path))
    artifacts=list(files.values())+[str(out/'qa.json'),str(out/'figure_spec.json'),str(out/'render_plan_v3.json')]+[str(out/v) for v in prepared.values()]
    state=snapshot(spec,manifests,artifacts,[p for p in Path(__file__).parent.iterdir() if p.suffix in {'.py','.R'}])
    previous=out/'snapshot.json'
    if previous.exists():write_json(out/'impact.json',impact(json.loads(previous.read_text()),state))
    write_json(previous,state)
    # Never overwrite an existing human review; a changed snapshot makes it stale.
    review_path=out/'review.json'
    if not review_path.exists():write_json(review_path,review_template(state))
    return dict(output=str(out),automatic_pass=qa['automatic_pass'],status=qa['status'],release_ready=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('render');p.add_argument('spec');p.add_argument('--root',default='.');p.add_argument('--out',required=True)
    p=sub.add_parser('inspect-pdf');p.add_argument('pdf');p.add_argument('--min-font',type=float,default=6.);p.add_argument('--out',required=True)
    p=sub.add_parser('carrier');p.add_argument('source');p.add_argument('target');p.add_argument('placement');p.add_argument('--out',required=True);p.add_argument('--min-font',type=float,default=6.)
    p=sub.add_parser('review');p.add_argument('directory')
    p=sub.add_parser('bind-report');p.add_argument('directory');p.add_argument('report');p.add_argument('--kind',choices=['carrier','export'],required=True)
    p=sub.add_parser('impact');p.add_argument('before');p.add_argument('after');p.add_argument('--out',required=True)
    p=sub.add_parser('escalate');p.add_argument('history');p.add_argument('--max-cycles',type=int,default=2)
    p=sub.add_parser('compare');p.add_argument('reference');p.add_argument('candidate');p.add_argument('--out',required=True)
    a=ap.parse_args()
    if a.command=='render':r=render(a.spec,a.root,a.out)
    elif a.command=='inspect-pdf':r=audit_pdf(a.pdf,min_font_pt=a.min_font);write_json(a.out,r)
    elif a.command=='carrier':
        r=audit_carrier(a.source,a.target,json.loads(Path(a.placement).read_text()),min_font_pt=a.min_font)
        r.update(source_path=str(Path(a.source).resolve()),carrier_path=str(Path(a.target).resolve()));write_json(a.out,r)
    elif a.command=='bind-report':r=bind_report(a.directory,a.report,a.kind)
    elif a.command=='review':
        d=Path(a.directory);issues=json.loads((d/'qa.json').read_text())['issues']
        if not json.loads((d/'preflight.json').read_text()).get('ok'):issues.append(issue('LATEST_PREFLIGHT_FAILED','The most recent requested build failed preflight.'))
        r=check_review(json.loads((d/'review.json').read_text()),json.loads((d/'snapshot.json').read_text()),issues);write_json(d/'release_gate.json',r)
    elif a.command=='impact':r=impact(json.loads(Path(a.before).read_text()),json.loads(Path(a.after).read_text()));write_json(a.out,r)
    elif a.command=='escalate':r=escalation(json.loads(Path(a.history).read_text()),a.max_cycles)
    else:r=compare_rasters(a.reference,a.candidate);write_json(a.out,r)
    print(json.dumps({k:v for k,v in r.items() if k in ['status','automatic_pass','release_ready','action','errors']},ensure_ascii=False))
    return 2 if r.get('release_ready') is False and a.command=='review' else (2 if r.get('automatic_pass') is False or r.get('pass_check') is False else 0)

if __name__=='__main__':raise SystemExit(main())
