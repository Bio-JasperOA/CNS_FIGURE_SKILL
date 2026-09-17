#!/usr/bin/env python3
"""Validate a declared evidence bundle and write a source-bound review packet.

No models are fitted, images interpreted, p-values reconstructed, external URLs
fetched, or scientific conclusions automatically accepted by this program.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / 'RESULT_BUNDLE_SCHEMA.json').read_text(encoding='utf-8'))
ASSAYS = json.loads((HERE / 'ASSAY_RULES.json').read_text(encoding='utf-8'))['assays']


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    def invalid_constant(value: str):
        raise ValueError(f'Non-finite JSON constant: {value}')
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=invalid_constant)


def _numbers_finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_numbers_finite(x) for x in value.values())
    if isinstance(value, list):
        return all(_numbers_finite(x) for x in value)
    return True


def _get(data: dict, path: str):
    value = data
    for part in path.split('.'):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _unit_ids(obs: dict) -> set[str]:
    return {str(x) for ids in obs['design'].get('unit_ids_by_group', {}).values() for x in ids}


def validate(bundle: dict, root: Path | None = None, verify_files: bool = False) -> dict:
    issues: list[dict] = []
    checked: dict[str, str] = {}

    def add(code: str, message: str, severity: str = 'error', **where):
        issues.append(dict(code=code, severity=severity, message=message, **where))

    def result():
        errors = sum(x['severity'] == 'error' for x in issues)
        return dict(schema_version='1.0', status='input_errors' if errors else 'checks_passed_requires_review',
                    errors=errors, warnings=sum(x['severity'] == 'warning' for x in issues), issues=issues,
                    file_verification_requested=verify_files, verified_source_hashes=checked,
                    scientific_review='pending', scientific_certification=False,
                    scope='Schema, declared-evidence consistency and optional local hashes/CSV numeric bindings; not biological truth or prose entailment.')

    if not _numbers_finite(bundle):
        add('NONFINITE', 'NaN and Infinity cannot be interpreted as experimental measurements.')
        return result()
    for e in sorted(Draft202012Validator(SCHEMA).iter_errors(bundle), key=lambda x: str(list(x.absolute_path))):
        add('SCHEMA', e.message, path='.'.join(map(str, e.absolute_path)))
    if issues:
        return result()

    def index(rows: list[dict], name: str) -> dict:
        ids = [x['id'] for x in rows]
        if len(ids) != len(set(ids)):
            add('DUPLICATE_ID', f'Duplicate {name} IDs.')
        return {x['id']: x for x in rows}

    sources = index(bundle['sources'], 'source')
    observations = index(bundle['observations'], 'result')
    claims = index(bundle['claims'], 'claim')
    known_literature = {x['id'] for x in load_json(HERE / 'SOURCES.json')['sources']}
    for rid in bundle['narrative']['literature_refs']:
        if rid not in known_literature:
            add('UNKNOWN_LITERATURE', f'Add a verified source record before citing {rid}.')
    resolved: dict[str, Path] = {}
    if verify_files and root is None:
        add('SOURCE_ROOT', 'A project root is required for local source verification.')
    root = Path(root).resolve() if root is not None else None
    for sid, s in sources.items():
        if s['synthetic'] != bundle['example_only']:
            add('SYNTHETIC_SCOPE', 'Do not silently mix synthetic and real evidence.', source=sid)
        if s['read_scope'] == 'not_read':
            add('UNREAD_SOURCE', 'The source is declared unread.', 'warning', source=sid)
        p = Path(s['path'])
        if p.is_absolute() or '..' in p.parts or '://' in s['path']:
            add('SOURCE_PATH', 'Source paths must be local and project-root relative.', source=sid)
            continue
        if verify_files and root is not None:
            target = (root / p).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                add('MISSING_SOURCE', 'Source is missing, not a regular file or escapes the project root.', source=sid)
                continue
            digest = sha256(target)
            checked[sid] = digest
            resolved[sid] = target
            if 'sha256' in s and s['sha256'] != digest:
                add('STALE_SOURCE', 'Source content changed after the declared evidence was bound.', source=sid)

    for rid, r in observations.items():
        if r['assay'] not in ASSAYS:
            add('UNKNOWN_ASSAY', 'Use a registered assay or the explicit other route.', result=rid)
        for sid in r['source_refs']:
            if sid not in sources:
                add('UNKNOWN_SOURCE', f'Unknown source {sid}.', result=rid)
        readable = [sources[s] for s in r['source_refs'] if s in sources and sources[s]['read_scope'] != 'not_read']
        if not readable:
            add('NO_READ_EVIDENCE', 'No read source supports this observation.', result=rid)
        st, d, details = r['statistics'], r['design'], r['assay_details']
        if r['origin'] == 'visual_only' and st is not None:
            add('IMAGE_NUMBERS', 'Visual-only evidence cannot carry reconstructed exact statistics.', result=rid)
        if st is not None and readable and all(s['kind'] == 'image' and s['read_scope'] == 'image_only' for s in readable):
            add('IMAGE_ONLY_STATS', 'Supply a quantitative source/legend rather than image-only access for exact statistics.', result=rid)
        if st is not None:
            scale, null, est = st['scale'], st['null_value'], st['estimate']
            if scale == 'ratio' and (null != 1 or est <= 0):
                add('RATIO_SCALE', 'Ratios need null=1 and a positive estimate.', result=rid)
            if scale in {'difference', 'log2_fold_change', 'log_ratio', 'correlation'} and null != 0:
                add('NULL_SCALE', 'The declared effect scale uses a zero null.', result=rid)
            if scale == 'correlation' and not -1 <= est <= 1:
                add('CORRELATION_RANGE', 'Correlation must lie in [-1,1].', result=rid)
            ci = st['ci']
            if ci:
                if ci['lower'] > ci['upper']:
                    add('INTERVAL_ORDER', 'Interval lower bound exceeds upper bound.', result=rid)
                if not ci['lower'] <= est <= ci['upper']:
                    add('ESTIMATE_OUTSIDE_INTERVAL', 'Check scale/estimator: point estimate lies outside supplied interval.', 'warning', result=rid)
                if scale == 'ratio' and ci['lower'] <= 0:
                    add('RATIO_INTERVAL', 'A ratio-scale interval must be positive.', result=rid)
                if scale == 'correlation' and not -1 <= ci['lower'] <= ci['upper'] <= 1:
                    add('CORRELATION_INTERVAL', 'Correlation interval outside [-1,1].', result=rid)
                if ci['kind'] in {'sd', 'sem', 'range'}:
                    add('NOT_INFERENTIAL_INTERVAL', 'Do not interpret SD/SEM/range as a confidence interval.', 'warning', result=rid)
            if st['q_value'] is not None and st['multiplicity'].strip().lower() in {'unknown', 'none', 'na', 'n/a', 'not_applicable'}:
                add('Q_WITHOUT_METHOD', 'An adjusted value needs its actual correction definition.', result=rid)
            eq = st.get('equivalence')
            if eq:
                if not eq['lower_margin'] < eq['upper_margin']:
                    add('EQUIVALENCE_MARGINS', 'Equivalence margins must be ordered.', result=rid)
                if eq['decision'] == 'established' and ci and ci['kind'] == 'confidence' and 'ci-based' in eq['method'].lower():
                    if not eq['lower_margin'] < ci['lower'] <= ci['upper'] < eq['upper_margin']:
                        add('EQUIVALENCE_CONFLICT', 'The CI-based equivalence claim conflicts with its supplied margins.', result=rid)
            if st.get('practical_threshold') is not None and st['practical_threshold'] < 0:
                add('PRACTICAL_THRESHOLD', 'Practical threshold must be a nonnegative magnitude.', result=rid)
        if d['population_claim'] and d['biological_unit'] != d['inferential_unit'] and not d['hierarchy_accounted']:
            add('PSEUDOREPLICATION', 'Population claim ignores the declared nesting of measurements.', result=rid)
        if d['population_claim'] and any(n is None or n < 2 for n in d['n_biological'].values()):
            add('REPLICATION_REVIEW', 'Replication/precision needs review; no universal power claim follows from a count.', 'warning', result=rid)
        if r['contrast']['test'] == r['contrast']['reference'] and d['kind'] != 'technical':
            add('IDENTICAL_CONTRAST', 'Test and reference labels are identical.', result=rid)
        groups = d.get('unit_ids_by_group', {})
        for group, ids in groups.items():
            n = d['n_biological'].get(group)
            if n is not None and len(ids) != n:
                add('REPLICATE_COUNT', 'Listed independent IDs do not match declared biological n.', result=rid, group=group)
        if len(groups) >= 2:
            sets = [set(x) for x in groups.values()]
            overlap = any(a & b for i, a in enumerate(sets) for b in sets[i + 1:])
            if not d['paired'] and overlap:
                add('PAIRING_MISMATCH', 'Repeated biological IDs were declared unpaired.', result=rid)
            if d['paired'] and any(a != sets[0] for a in sets[1:]):
                add('INCOMPLETE_PAIRING', 'Unequal paired ID sets require an explicit incomplete-pair design.', 'warning', result=rid)
        if r['quality']['status'] != 'passed':
            add('QUALITY_REVIEW', f"Diagnostic status is {r['quality']['status']}.", 'warning', result=rid)
        if r['assay'] in {'spatial_localization', 'spatial_mapping', 'spatial_communication'}:
            for key in ('observation_unit', 'coordinate_unit'):
                if not details.get(key):
                    add('SPATIAL_METADATA', f'Missing {key}; restrict interpretation to the known resolution.', 'warning', result=rid)
        if r['assay'] == 'model_prediction':
            for key in ('split_unit', 'baseline_comparison', 'leakage_check'):
                if not details.get(key):
                    add('PREDICTION_REVIEW', f'Unverified {key}.', 'warning', result=rid)

        for b in r.get('numeric_bindings', []):
            sid = b['source_id']
            if sid not in r['source_refs']:
                add('BINDING_SOURCE', 'Numeric binding must reference an observation source.', result=rid)
                continue
            if st is None:
                add('BINDING_WITHOUT_STATS', 'Numeric binding has no statistics to bind.', result=rid)
                continue
            if not verify_files:
                continue
            if sid not in resolved:
                add('BINDING_UNVERIFIED', 'Cannot verify binding without its local source.', result=rid)
                continue
            path = resolved[sid]
            suffix = path.name.lower()
            if not suffix.endswith(('.csv', '.tsv', '.csv.gz', '.tsv.gz')):
                add('BINDING_FORMAT', 'Numeric binding supports CSV/TSV only; export a reviewed table for other formats.', result=rid)
                continue
            opener = gzip.open if suffix.endswith('.gz') else open
            try:
                with opener(path, 'rt', encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f, delimiter='\t' if '.tsv' in suffix else ',')
                    fields = reader.fieldnames or []
                    if len(fields) != len(set(fields)):
                        raise ValueError('Duplicate column names')
                    if set(b['row_key']) - set(fields) or b['column'] not in fields:
                        raise ValueError('Missing bound column/key')
                    rows = [x for x in reader if all(x.get(k) == str(v) for k, v in b['row_key'].items())]
                if len(rows) != 1:
                    raise ValueError(f'Expected one matching row, found {len(rows)}')
                raw = rows[0][b['column']]
                expected = _get(st, b['statistic'])
                if expected is None:
                    match = raw.strip().lower() in {'', 'na', 'n/a', 'null'}
                else:
                    actual = float(raw)
                    match = math.isfinite(actual) and math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-12)
                if not match:
                    raise ValueError(f"Source {raw!r} differs from declared {b['statistic']}={expected!r}")
            except (OSError, ValueError, TypeError, csv.Error) as e:
                add('NUMERIC_BINDING', str(e), result=rid)

    for link in bundle['evidence_links']:
        a, b = link['from'], link['to']
        if a not in observations or b not in observations or a == b:
            add('LINK_ID', 'Evidence link needs two distinct known result IDs.')
            continue
        ra, rb = observations[a], observations[b]
        if link['independence'] == 'independent_specimens':
            if ra['provenance_group'] == rb['provenance_group'] or (_unit_ids(ra) & _unit_ids(rb)):
                add('FALSE_INDEPENDENCE', 'Same underlying provenance or overlapping biological IDs cannot be independent specimens.', link=f'{a}->{b}')
            elif not _unit_ids(ra) or not _unit_ids(rb):
                add('INDEPENDENCE_UNVERIFIED', 'Independent-specimen status is declared but IDs are incomplete.', 'warning', link=f'{a}->{b}')
        if link['relationship'] == 'contradicts' and not link['same_estimand']:
            add('APPARENT_CONTRADICTION', 'Different estimands may be complementary rather than logically contradictory.', 'warning', link=f'{a}->{b}')

    assigned: set[str] = set()
    for cid, c in claims.items():
        groups = [set(c[k]) for k in ('supporting_results', 'contradicting_results', 'unresolved_results')]
        if any(a & b for i, a in enumerate(groups) for b in groups[i + 1:]):
            add('CLAIM_ROLE_CONFLICT', 'A result has conflicting roles in one claim.', claim=cid)
        refs = set.union(*groups)
        assigned |= refs
        for rid in refs - observations.keys():
            add('CLAIM_RESULT_ID', f'Unknown result {rid}.', claim=cid)
        support = [observations[r] for r in c['supporting_results'] if r in observations]
        if c['status'] == 'supported' and not support:
            add('UNSUPPORTED_CLAIM', 'A supported claim needs actual supporting results.', claim=cid)
        if c['status'] == 'contradicted' and not c['contradicting_results']:
            add('CONTRADICTION_REQUIRED', 'Contradicted status needs contrary result references.', claim=cid)
        if c['status'] == 'supported':
            if any(r['quality']['status'] == 'failed' for r in support):
                add('FAILED_EVIDENCE', 'Failed-quality results cannot carry an unqualified supported claim.', claim=cid)
            if c['contradicting_results']:
                add('MIXED_EVIDENCE', 'Supported status has contrary evidence; review the scoped conclusion.', 'warning', claim=cid)
            if c['type'] in {'mechanistic', 'causal'} and all(r['origin'] in {'inferred', 'visual_only'} for r in support):
                add('INFERENCE_ONLY_MECHANISM', 'Inferred/image-only results do not establish a mechanism.', claim=cid)
            if c['type'] == 'causal':
                identification = c.get('causal_identification')
                if not identification:
                    add('CAUSAL_DESIGN', 'Document the identifying design, assumptions and diagnostics.', claim=cid)
                else:
                    for rid in identification['diagnostic_results']:
                        if rid not in observations:
                            add('CAUSAL_DIAGNOSTIC_ID', f'Unknown diagnostic result {rid}.', claim=cid)
                if not any(r['design']['kind'] in {'controlled_perturbation', 'randomized', 'quasi_experimental'} for r in support):
                    add('CAUSAL_EVIDENCE', 'No supporting result has an identifying experimental/quasi-experimental design.', claim=cid)
                add('CAUSAL_HUMAN_REVIEW', 'Design declarations are not proof of causal identification or direct mechanism.', 'warning', claim=cid)
            if c['type'] == 'generalization':
                external = [r for r in support if r['design']['validation_role'] in {'independent_replication', 'heldout'}]
                if not external:
                    add('NO_HOLDOUT', 'Generalization needs an appropriate heldout or independent result.', claim=cid)
                for r in external:
                    against = r['design'].get('validation_against')
                    if against not in observations:
                        add('HOLDOUT_REFERENCE', 'Link validation to its discovery result.', claim=cid)
                    elif _unit_ids(r) & _unit_ids(observations[against]):
                        add('HOLDOUT_LEAKAGE', 'Overlapping specimen IDs need a narrower than specimen-generalization claim.', claim=cid)
            if c['type'] == 'equivalence':
                if not any(r['statistics'] and (r['statistics'].get('equivalence') or {}).get('decision') == 'established' for r in support):
                    add('NONSIGNIFICANCE_NOT_EQUIVALENCE', 'No actual equivalence analysis establishes the stated claim.', claim=cid)
            if c['type'] == 'predictive' and not any(r['assay'] == 'model_prediction' and r['assay_details'].get('heldout') is True for r in support):
                add('PREDICTION_NO_TEST', 'A supported prediction claim requires a declared heldout prediction result.', claim=cid)
        if len(support) > 1 and len({r['provenance_group'] for r in support}) == 1:
            add('SHARED_DATA', 'Supporting analyses share provenance; this is not independent replication.', 'warning', claim=cid)

    excluded: set[str] = set()
    for x in bundle['excluded_results']:
        rid = x['result_id']
        if rid not in observations or rid in excluded:
            add('EXCLUSION_ID', 'Exclusion references an unknown or repeated result.')
        excluded.add(rid)
        if x['reason'].strip().lower() in {'not significant', 'negative result', 'does not fit the story', '不显著', '不符合预期'}:
            add('SELECTIVE_REPORTING', 'Statistical direction/story fit alone is not a defensible exclusion.', result=rid)
    for rid in observations.keys() - assigned - excluded:
        add('UNACCOUNTED_RESULT', 'Account for this result in a claim or a justified scope exclusion.', result=rid)
    for section in bundle['narrative']['results_sections']:
        for cid in set(section['claim_ids']) - claims.keys():
            add('NARRATIVE_CLAIM', f'Unknown claim {cid}.')
        for rid in set(section['result_ids']) - observations.keys():
            add('NARRATIVE_RESULT', f'Unknown result {rid}.')
        connected = set()
        for cid in section['claim_ids']:
            if cid in claims:
                for key in ('supporting_results', 'contradicting_results', 'unresolved_results'):
                    connected.update(claims[cid][key])
        if section['claim_ids'] and not connected.intersection(section['result_ids']):
            add('NARRATIVE_DISCONNECTED', 'Narrative section has no evidence connected to its stated claims.')
    return result()


def _cell(x: Any) -> str:
    return str(x).replace('|', '\\|').replace('\n', '<br>')


def packet(bundle: dict, audit: dict) -> str:
    synthetic = 'SYNTHETIC TEACHING EXAMPLE — NOT BIOLOGICAL FINDINGS' if bundle['example_only'] else 'DRAFT INTERPRETATION — HUMAN REVIEW PENDING'
    lines = ['# Result interpretation review packet', '', synthetic, '', bundle['question'], '',
             f"Automated status: `{audit['status']}`. This is not scientific acceptance.", '', '## Actual observations', '',
             '| Result | Assay | Finding | Test / reference | Effect and interval | Biological n | Source |', '|---|---|---|---|---|---|---|']
    for r in bundle['observations']:
        st = r['statistics']
        stat = 'Not quantitatively supplied'
        if st:
            stat = f"{st['estimate']} ({st['scale']}; {st['unit']}); null={st['null_value']}"
            if st['ci']:
                ci = st['ci']; stat += f"; {ci['kind']} [{ci['lower']}, {ci['upper']}]"
            if st['p_value'] is not None: stat += f"; p={st['p_value']}"
            if st['q_value'] is not None: stat += f"; adjusted={st['q_value']} ({st['multiplicity']})"
        lines.append('| ' + ' | '.join(map(_cell, [r['id'], r['assay'], r['finding'],
            f"{r['contrast']['test']} / {r['contrast']['reference']}", stat, r['design']['n_biological'], ', '.join(r['source_refs'])])) + ' |')
    lines += ['', '## Claim ledger']
    for c in bundle['claims']:
        lines += ['', f"### {c['id']}: {c['text']}", f"Type: {c['type']}; declared status: {c['status']}; scope: {c['scope']}.", '', c['reasoning'],
                  f"Support: {', '.join(c['supporting_results']) or 'none'}; contrary: {', '.join(c['contradicting_results']) or 'none'}; unresolved: {', '.join(c['unresolved_results']) or 'none'}.",
                  'Unsupported extension: ' + c['unsupported_extension']]
        for a in c['alternatives']:
            lines += ['Alternative: ' + a['explanation'], 'Distinguishing prediction: ' + a['predicted_observation'], 'Test: ' + a['discriminating_test']]
    lines += ['', '## Evidence connections']
    for link in bundle['evidence_links']:
        lines.append(f"{link['from']} → {link['to']}: {link['relationship']}; {link['independence']}. {link['explanation']}")
    lines += ['', '## Proposed Results text — not automatically endorsed']
    for s in bundle['narrative']['results_sections']:
        lines += ['', '### ' + s['heading'], s['text'], 'Trace: ' + ', '.join(s['result_ids'])]
    lines += ['', '## Proposed Discussion — not automatically endorsed', bundle['narrative']['discussion'], '', '## Discriminating next steps']
    for n in bundle['next_steps']:
        lines += ['', f"**{n['priority']} / proposed:** {n['question']}", n['test'],
                  'Competing predictions: ' + ' | '.join(n['predictions']), 'Required input: ' + n['required_input']]
    lines += ['', '## Automated issues']
    for issue in audit['issues']:
        lines.append(f"- {issue['severity'].upper()} {issue['code']}: {issue['message']}")
    if not audit['issues']: lines.append('No implemented check failed. Biology and prose entailment remain unverified.')
    lines += ['', '## Source receipt']
    for s in bundle['sources']:
        digest = audit['verified_source_hashes'].get(s['id'], 'not verified in this run')
        lines.append(f"- {s['id']}: `{s['path']}`; scope={s['read_scope']}; locator={s['locator']}; SHA256={digest}")
    lines += ['', '## Review boundary', 'Read the actual assays, source data and literature before accepting this interpretation. Hash checks bind files; they do not prove the observation or the prose. No image was interpreted or new analysis executed by this helper.', '']
    return '\n'.join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['validate', 'packet'])
    p.add_argument('bundle', type=Path)
    p.add_argument('--root', type=Path, help='Root for project-relative evidence files.')
    p.add_argument('--verify-files', action='store_true', help='Verify hashes and explicit CSV/TSV numeric bindings.')
    p.add_argument('--out', type=Path, help='Output directory; packet requires it.')
    p.add_argument('--overwrite', action='store_true', help='Replace generated audit/packet, never input evidence.')
    a = p.parse_args()
    try:
        b = load_json(a.bundle)
        report = validate(b, a.root, a.verify_files)
        if a.command == 'packet' and a.out is None:
            raise ValueError('packet requires --out')
        if a.out:
            targets = [a.out / 'audit.json']
            if a.command == 'packet' and report['errors'] == 0:
                targets.append(a.out / 'review_packet.md')
            protected = {a.bundle.resolve()}
            if a.root and isinstance(b, dict):
                protected |= {(a.root / s['path']).resolve() for s in b.get('sources', []) if isinstance(s, dict) and isinstance(s.get('path'), str)}
            if any(t.resolve() in protected for t in targets):
                raise ValueError('Output collides with input evidence.')
            if not a.overwrite and any(t.exists() for t in targets):
                raise ValueError('Output exists; choose a new destination or explicit --overwrite.')
            a.out.mkdir(parents=True, exist_ok=True)
            report['bundle_sha256'] = sha256(a.bundle)
            (a.out / 'audit.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
            if len(targets) == 2:
                targets[1].write_text(packet(b, report), encoding='utf-8')
        print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
        return 1 if report['errors'] else 0
    except (ValueError, OSError, TypeError, KeyError) as e:
        print('ERROR:', str(e))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
