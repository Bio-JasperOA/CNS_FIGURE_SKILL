"""Artifact-bound human review, conservative impact propagation and repair escalation."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import hashlib,json
from visual_audit import digest

CRITERIA={
 'question_answer':'Point to the marks and comparison that answer the question; fail if only topic labels are supplied.',
 'claim_strength':'State the strongest justified claim and a plausible alternative explanation; fail on causal overstatement.',
 'independent_unit':'Identify donor/animal/sample units and denominators; fail on unacknowledged pseudoreplication.',
 'scales_missing':'Verify units, centers, transformations, clipping and missing-value symbols against source values.',
 'reading_order':'Trace the intended reading order; fail if the primary comparison cannot be found without narration.',
 'density_layout':'Inspect at final physical size; fail on unreadable labels, hidden categories or misleading area hierarchy.',
 'guides':'Locate each encoding in a readable guide; fail on ambiguous sharing, missing units or indistinguishable categories.',
 'color_perception':'Review full color and grayscale/CVD evidence; fail on color-only essential distinctions that disappear.',
 'typography':'Check glyphs, math, optical spacing and line spacing in the exported artifact, not only the source code.',
 'occlusion':'Inspect collision/protected-region warnings; fail on data-obscuring annotations or local/cross-panel clipping.',
 'final_carrier':'Inspect the actual final PDF placement and displayed font sizes; standalone figures must be explicitly declared.',
 'provenance':'Confirm source data, parameters, rendering code and artifact hashes correspond to the reviewed output.'}


def hash_value(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def snapshot(spec,inputs,artifacts,code_paths=()):
    return dict(version='3.0',spec=deepcopy(spec),spec_sha256=hash_value(spec),inputs=deepcopy(inputs),
        code={str(p):digest(p) for p in sorted(Path(q).resolve() for q in code_paths)},
        artifacts={str(p):digest(p) for p in sorted(Path(q).resolve() for q in artifacts)})


def impact(before,after):
    """Transitive closure is conservative. Unknown/global code changes affect all."""
    old,new=before['spec'],after['spec'];panels={p['id']:p for p in new['panels']}
    affected=set();reasons={};changed_scales={k for k in set(old['scales'])|set(new['scales']) if old['scales'].get(k)!=new['scales'].get(k)}
    data={k for k in set(before['inputs'])|set(after['inputs']) if before['inputs'].get(k)!=after['inputs'].get(k)}
    previous={p['id']:p for p in old['panels']}
    global_change=any(old.get(k)!=new.get(k) for k in ['figure','layout','design','visual']) or before.get('code')!=after.get('code')
    for pid,p in panels.items():
        r=[]
        if global_change:r.append('global style/layout/code')
        if p!=previous.get(pid):r.append('panel definition')
        if p['data_id'] in data or old['datasets'].get(p['data_id'])!=new['datasets'].get(p['data_id']):r.append('input data')
        if changed_scales&set(p['scale_ids'].values()):r.append('scale')
        if r:affected.add(pid);reasons[pid]=r
    for gid in set(old.get('guides',{}))|set(new.get('guides',{})):
        a,b=old.get('guides',{}).get(gid),new.get('guides',{}).get(gid)
        if a!=b:affected.update((a or {}).get('panels',[]));affected.update((b or {}).get('panels',[]))
    # A shared guide needs all its panels rechecked even when the source scale is unchanged.
    while True:
        previous_set=set(affected)
        for pid,p in panels.items():
            if affected&set(p['depends_on']):affected.add(pid)
        for g in new.get('guides',{}).values():
            if affected&set(g['panels']):affected.update(g['panels'])
        if affected==previous_set:break
    changed_artifacts=[k for k in set(before['artifacts'])|set(after['artifacts']) if before['artifacts'].get(k)!=after['artifacts'].get(k)]
    return dict(affected_panels=sorted(affected),reasons=reasons,changed_scales=sorted(changed_scales),
        changed_inputs=sorted(data),externally_changed_artifacts=sorted(changed_artifacts),
        invalidate_all_assembled_outputs=bool(affected or changed_artifacts or set(previous)-set(panels)),
        review_stale=before!=after)


def escalation(history,max_cycles=2):
    """history entries: issue_codes, touched_panels, below_min_font (optional)."""
    reasons=[]
    if history:
        last=history[-1]
        if last.get('below_min_font') or 'CROSS_PANEL_INTRUSION' in last.get('issue_codes',[]):reasons.append('Semantic/physical boundary was compromised.')
        if len(set(last.get('touched_panels',[])))>1:reasons.append('The local repair changes more than one panel.')
    if len(history)>=max_cycles:
        repeated=set.intersection(*(set(x.get('issue_codes',[])) for x in history[-max_cycles:]))
        if repeated:reasons.append('Repeated unresolved issues: '+', '.join(sorted(repeated)))
    return dict(action='restructure' if reasons else 'local_repair',reasons=reasons,
        never_allowed=['shrink below declared minimum','hide data/labels','change normalization to fit','move content across panel boundaries'])


def review_template(state):
    return dict(version='3.0',snapshot_sha256=hash_value(state),reviewer='',reviewed_at='',
        criteria={k:dict(status='pending',evidence='',failure_condition=v) for k,v in CRITERIA.items()},
        acknowledged_warnings={},carrier_mode='pending',carrier_reports=[])


def check_review(review,state,issues,*,verify_files=True):
    errors=[]
    if 'DRAFT:' in json.dumps(state['spec']):errors.append('Planning placeholders remain in the FigureSpec.')
    if review.get('snapshot_sha256')!=hash_value(state):errors.append('STALE_REVIEW: inputs/config/code/output hashes changed.')
    if not str(review.get('reviewer','')).strip():errors.append('Reviewer required.')
    try:
        stamp=datetime.fromisoformat(review.get('reviewed_at','').replace('Z','+00:00'))
        if stamp.tzinfo is None:errors.append('Review timestamp needs a timezone.')
    except (TypeError,ValueError):errors.append('A valid review timestamp is required.')
    for k in CRITERIA:
        row=review.get('criteria',{}).get(k,{})
        if row.get('status') not in ['pass','not_applicable'] or not str(row.get('evidence','')).strip():errors.append('Incomplete criterion: '+k)
    for i in issues:
        if i['severity']=='error':errors.append('Unresolved hard error: '+i['code'])
        elif i['severity']=='warning' and not review.get('acknowledged_warnings',{}).get(i['id'],'').strip():errors.append('Warning needs evidence/rationale: '+i['id'])
    if review.get('carrier_mode') not in ['standalone','placed']:errors.append('Declare the actual final carrier.')
    if review.get('carrier_mode')=='placed':
        reports=review.get('carrier_reports',[])
        if not reports:errors.append('Actual placement report required.')
        for path in reports:
            if path not in state['artifacts']:errors.append('Carrier report must be bound into snapshot.')
            try:
                record=json.loads(Path(path).read_text())
                if not record.get('automatic_pass'):errors.append('Carrier verification did not pass.')
                for key,hkey in [('source_path','source_sha256'),('carrier_path','carrier_sha256')]:
                    if key not in record or digest(record[key])!=record[hkey]:errors.append('Carrier artifact missing/stale.')
            except (OSError,ValueError,KeyError):errors.append('Unreadable carrier report.')
    if verify_files:
        for key in ['artifacts','code']:
            for path,expected in state.get(key,{}).items():
                if not Path(path).is_file() or digest(path)!=expected:errors.append('Changed/missing '+key+': '+path)
        for d in state.get('inputs',{}).values():
            if 'resolved_path' in d and (not Path(d['resolved_path']).is_file() or digest(d['resolved_path'])!=d['sha256']):errors.append('Input file changed since rendering.')
    return dict(release_ready=not errors,errors=errors,
        qualification='Records human review completeness, not an automated scientific endorsement.')


def bind_report(directory,report_path,kind):
    """Bind an audited native export or final placement to the current build.

    Reports are re-audited instead of trusting an edited automatic_pass field.
    The current review is deliberately preserved and becomes stale.
    """
    from visual_audit import audit_pdf,audit_carrier
    directory=Path(directory);report_path=Path(report_path).resolve()
    state_path=directory/'snapshot.json';state=json.loads(state_path.read_text())
    qa_path=directory/'qa.json';qa=json.loads(qa_path.read_text())
    record=json.loads(report_path.read_text());minimum=state['spec']['design']['min_font_pt']
    if kind=='carrier':
        source=Path(record['source_path']).resolve();target=Path(record['carrier_path']).resolve()
        if state['artifacts'].get(str(source))!=digest(source):raise ValueError('Carrier source must be a currently bound export; bind an R export first.')
        checked=audit_carrier(source,target,record['placement'],min_font_pt=minimum)
        checked.update(source_path=str(source),carrier_path=str(target));artifacts=[source,target]
    elif kind=='export':
        target=Path(record['path']).resolve()
        checked=audit_pdf(target,expected_mm=[state['spec']['figure']['width_mm'],state['spec']['figure']['height_mm']],min_font_pt=minimum)
        artifacts=[target]
    else:raise ValueError('Unknown report kind.')
    report_path.write_text(json.dumps(checked,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    qa['issues']+=checked['issues'];qa['automatic_pass']=not any(i['severity']=='error' for i in qa['issues'])
    qa.setdefault('attached_reports',[]).append(dict(kind=kind,path=str(report_path)))
    qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    for path in artifacts+[report_path,qa_path.resolve()]:state['artifacts'][str(path)]=digest(path)
    state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    # No approval is copied. The reviewer has to use the new expected snapshot hash.
    (directory/'review_pending.json').write_text(json.dumps(review_template(state),ensure_ascii=False,indent=2)+'\n')
    return dict(status='report_bound_review_stale',expected_review_sha256=hash_value(state),automatic_pass=qa['automatic_pass'],release_ready=False)
