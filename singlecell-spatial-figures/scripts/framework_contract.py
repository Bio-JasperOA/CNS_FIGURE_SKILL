"""FigureSpec 2.0: schema, semantic preflight and deterministic physical layout.

No plotting, model fitting or dynamic code execution occurs in this module.
A successful preflight is NOT a scientific or visual review.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path
from typing import Any
import yaml
from jsonschema import Draft7Validator

SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'assets' / 'figure_spec.schema.json'

def read_spec(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding='utf-8') as handle:
        doc = yaml.safe_load(handle)
    if not isinstance(doc, dict):
        raise ValueError('FigureSpec must be a mapping, not an empty file or a list.')
    return doc

def _error(code: str, message: str, panel: str | None = None) -> dict:
    return {'severity': 'error', 'code': code, 'panel': panel, 'message': message}

def _has_nonfinite(value: Any) -> bool:
    if isinstance(value, float): return not math.isfinite(value)
    if isinstance(value, dict): return any(_has_nonfinite(v) for v in value.values())
    if isinstance(value, (tuple, list)): return any(_has_nonfinite(v) for v in value)
    return False

def panel_boxes(spec: dict) -> dict[str, dict]:
    """Return outer/content boxes [left, top, width, height] in millimetres.

    Slots are zero-based [row, col, row_span, col_span]. Padding/margins are
    [top, right, bottom, left]. Physical geometry is shared by both backends.
    """
    lay=spec['layout']; width=spec['figure']['width_mm']; height=spec['figure']['height_mm']
    t,r,b,l=lay['margin_mm']; gap=lay['gap_mm']
    usable_w=width-l-r-gap*(lay['cols']-1)
    usable_h=height-t-b-gap*(lay['rows']-1)
    if min(usable_w,usable_h)<=0: raise ValueError('Margins and gaps consume the canvas.')
    cw=[usable_w*x/sum(lay['col_weights']) for x in lay['col_weights']]
    rh=[usable_h*x/sum(lay['row_weights']) for x in lay['row_weights']]
    boxes={}
    for panel in spec['panels']:
        row,col,rs,cs=panel['slot']
        x=l+sum(cw[:col])+gap*col; y=t+sum(rh[:row])+gap*row
        w=sum(cw[col:col+cs])+gap*(cs-1); h=sum(rh[row:row+rs])+gap*(rs-1)
        pt,pr,pb,pl=panel.get('padding_mm',spec['design']['panel_padding_mm'])
        if min(w-pl-pr,h-pt-pb)<=0: raise ValueError(f"{panel['id']}: padding consumes the panel.")
        boxes[panel['id']]={'outer_mm':[x,y,w,h],'content_mm':[x+pl,y+pt,w-pl-pr,h-pt-pb]}
    return boxes

def _resolve_data_path(root: Path, path: str) -> Path:
    relative=Path(path)
    if relative.is_absolute(): raise ValueError('Use a project-relative input path.')
    target=(root/relative).resolve()
    if not target.is_relative_to(root.resolve()): raise ValueError('Input path escapes the declared project root.')
    return target

def validate_spec(spec: dict, *, check_files: bool=False, root: str | Path='.') -> dict:
    schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    issues=[]
    if _has_nonfinite(spec): issues.append(_error('NONFINITE','NaN/Infinity is not valid configuration.'))
    for err in sorted(Draft7Validator(schema).iter_errors(spec),key=lambda e:str(list(e.path))):
        issues.append(_error('SCHEMA',f"{'.'.join(map(str,err.path)) or '$'}: {err.message}"))
    if issues: return {'ok':False,'stage':'schema','issues':issues,'files_checked':False}
    lay=spec['layout']; panels=spec['panels']; ids=[p['id'] for p in panels]
    if len(ids)!=len(set(ids)): issues.append(_error('DUPLICATE_PANEL','Panel IDs must be unique.'))
    if len(lay['row_weights'])!=lay['rows'] or len(lay['col_weights'])!=lay['cols']:
        issues.append(_error('GRID_WEIGHTS','Weight lengths must match rows/cols.'))
    occupied={}
    for p in panels:
        pid=p['id']; row,col,rs,cs=p['slot']
        if rs<1 or cs<1 or row+rs>lay['rows'] or col+cs>lay['cols']:
            issues.append(_error('SLOT_BOUNDS','Slot is empty or outside the layout.',pid));continue
        for r in range(row,row+rs):
            for c in range(col,col+cs):
                if (r,c) in occupied: issues.append(_error('SLOT_OVERLAP',f"Slot overlaps {occupied[r,c]}.",pid))
                occupied[r,c]=pid
        if p['data_id'] not in spec['datasets']: issues.append(_error('DATA_REF',f"Unknown data_id {p['data_id']}",pid))
        for channel,sid in p['scale_ids'].items():
            if channel not in p['channels']: issues.append(_error('SCALE_CHANNEL',f'{channel} has no mapped data column.',pid))
            if sid not in spec['scales']: issues.append(_error('SCALE_REF',f'Unknown scale {sid}.',pid))
        stat=p['statistics']
        if stat['inferential']:
            if stat['independent_unit'] not in {'donor','animal','biological_sample'}:
                issues.append(_error('PSEUDOREPLICATION','Conventional sample-comparison inference requires a biological replicate unit.',pid))
            if stat['n_biological']<2: issues.append(_error('REPLICATES','Fewer than two biological replicates: block conventional replicated-group inference.',pid))
            if not stat.get('source_table'): issues.append(_error('STAT_SOURCE','Inferential panels require a reviewed statistics source_table.',pid))
        if p['renderer'].startswith('spatial') and 'spatial' not in p:
            issues.append(_error('SPATIAL_CONTRACT','Spatial rendering requires units, section and orientation.',pid))
        for parent in p['depends_on']:
            if parent not in ids: issues.append(_error('DEPENDENCY',f'Unknown dependency {parent}.',pid))
    for sid,s in spec['scales'].items():
        if s['kind']=='continuous' and s['limits'][0]>=s['limits'][1]: issues.append(_error('SCALE_RANGE',f'{sid}: limits must increase.'))
        if s['kind']=='categorical' and set(s['order'])!=set(s['colors']): issues.append(_error('PALETTE_KEYS',f'{sid}: order and palette keys differ.'))
    # A comparison group declares identical encodings, not merely visually similar guides.
    comparisons={}
    for p in panels:
        if 'comparison_group' in p:
            g=p['comparison_group']; signature=p['scale_ids']
            if g in comparisons and comparisons[g]!=signature: issues.append(_error('COMPARISON_SCALE',f'{g}: comparable panels use different scale registries.',p['id']))
            comparisons[g]=signature
    # Topological scheduling independent of panel display order.
    remaining={p['id']:set(p['depends_on']) for p in panels}; order=[]
    while remaining:
        ready=[k for k,v in remaining.items() if v.issubset(order)]
        if not ready: issues.append(_error('DEPENDENCY_CYCLE','Dependencies contain a cycle or an unknown reference.'));break
        for k in ready: order.append(k);remaining.pop(k)
    boxes={}
    if not any(i['code'] in {'GRID_WEIGHTS','SLOT_BOUNDS','DUPLICATE_PANEL'} for i in issues):
        try: boxes=panel_boxes(spec)
        except ValueError as e: issues.append(_error('PANEL_SIZE',str(e)))
    if spec['design']['font_pt']<spec['design']['min_font_pt']:
        issues.append(_error('FONT_MIN','Configured text size is below the declared minimum.'))
    manifest={}
    if check_files:
        root=Path(root)
        for did,d in spec['datasets'].items():
            try:
                path=_resolve_data_path(root,d['path'])
                if not path.is_file(): raise ValueError(f'Missing file: {d["path"]}')
                # This implementation audits tabular exchange inputs, not native AnnData/Seurat objects.
                if path.suffix.lower() not in {'.csv','.tsv'}: raise ValueError('Exchange data must be CSV/TSV; use a documented upstream native-object adapter.')
                with path.open(encoding='utf-8-sig',newline='') as handle:
                    reader=csv.DictReader(handle,delimiter='\t' if path.suffix.lower()=='.tsv' else ',')
                    columns=reader.fieldnames or []
                    if len(columns)!=len(set(columns)): raise ValueError('Duplicate column headers.')
                    required=set(d['keys'])
                    for p in panels:
                        if p['data_id']==did:
                            required.update(p['channels'].values())
                            if 'spatial' in p: required.add(p['spatial']['section_column'])
                    if required-set(columns): raise ValueError(f'Missing columns: {sorted(required-set(columns))}')
                    seen=set(); count=0
                    for row in reader:
                        key=tuple(row[k] for k in d['keys'])
                        if any(x is None or not str(x).strip() for x in key): raise ValueError('Missing primary key.')
                        if key in seen: raise ValueError(f'Duplicate primary key {key}.')
                        seen.add(key);count+=1
                    if count==0: raise ValueError('No data rows.')
                digest=hashlib.sha256()
                with path.open('rb') as handle:
                    for block in iter(lambda:handle.read(1024*1024),b''):digest.update(block)
                manifest[did]={'path':d['path'],'sha256':digest.hexdigest(),'rows':count,'columns':columns}
            except (OSError,ValueError,csv.Error) as e: issues.append(_error('INPUT_FILE',f'{did}: {e}'))
        for p in panels:
            stat=p['statistics']
            if stat['inferential'] and stat.get('source_table'):
                try:
                    if not _resolve_data_path(root,stat['source_table']).is_file(): raise ValueError('Statistics source_table does not exist.')
                except (ValueError,OSError) as e: issues.append(_error('STAT_FILE',str(e),p['id']))
    warnings=[]
    if 'DRAFT:' in json.dumps(spec): warnings.append('Planning placeholders remain; this is not a release-ready specification.')
    if not check_files: warnings.append('Files, values and primary-key uniqueness have not been inspected.')
    return {'ok':not issues,'stage':'preflight','files_checked':check_files,'issues':issues,
            'warnings':warnings,'render_order':order,'boxes':boxes,'input_manifest':manifest,
            'scientific_review':'not_performed','visual_review':'not_performed'}

def compile_plan(spec: dict, report: dict) -> dict:
    if not report['ok']: raise ValueError('Cannot compile a failed specification.')
    return {'plan_version':'2.0','spec':spec,'render_order':report['render_order'],
            'boxes':report['boxes'],'input_manifest':report['input_manifest'],
            'spec_sha256':hashlib.sha256(json.dumps(spec,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest(),
            'status':'preflight_passed_not_reviewed'}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec');parser.add_argument('--root',default='.')
    parser.add_argument('--check-files',action='store_true');parser.add_argument('--out',required=True)
    args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    try: spec=read_spec(args.spec);report=validate_spec(spec,check_files=args.check_files,root=args.root)
    except (ValueError,OSError,yaml.YAMLError) as e: report={'ok':False,'stage':'read','issues':[_error('READ',str(e))]}
    (out/'preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if report['ok']:
        (out/'render_plan.json').write_text(json.dumps(compile_plan(spec,report),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else: (out/'render_plan.json').unlink(missing_ok=True)
    print(json.dumps({'ok':report['ok'],'report':str(out/'preflight.json')},ensure_ascii=False))
    return 0 if report['ok'] else 2

if __name__=='__main__': raise SystemExit(main())
