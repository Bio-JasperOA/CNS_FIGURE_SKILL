"""Render a FigureSpec project with the bundled registry or explicit local adapters."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import matplotlib.pyplot as plt
from framework_contract import read_spec, validate_spec, compile_plan
from composer import load_tables, compose, write_bundle
from native_renderers import REGISTRY

def render_project(spec_path, root, output, registry=None):
    spec=read_spec(spec_path)
    report=validate_spec(spec,check_files=True,root=root)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/'preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if not report['ok']:raise ValueError('Preflight failed; inspect preflight.json. No rendering performed.')
    plan=compile_plan(spec,report)
    tables=load_tables(spec,root)
    registry=dict(REGISTRY) if registry is None else registry
    composed=compose(spec,tables,registry)
    try: files=write_bundle(composed,out,input_manifest=report['input_manifest'])
    finally:plt.close(composed.figure)
    (out/'render_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    return {'files':files,'qa':composed.qa,'status':'rendered_review_pending'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec');parser.add_argument('--root',default='.')
    parser.add_argument('--out',required=True);a=parser.parse_args()
    result=render_project(a.spec,a.root,a.out)
    print(json.dumps({'status':result['status'],'output':a.out,'automated_checks_passed':result['qa']['automated_render_checks_passed']}))
