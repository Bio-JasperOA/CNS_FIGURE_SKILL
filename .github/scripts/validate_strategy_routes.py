#!/usr/bin/env python3
"""Check repository-local invocation definitions without importing plotting packages."""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from urllib.parse import unquote

REQUIRED_ROUTES = {
    'research-design': 'agent_planning',
    'analysis-plan': 'agent_planning',
    'analysis-code': 'agent_code_authoring',
    'plot-single': 'python_renderer',
    'plot-pipeline': 'python_renderer',
    'figure-audit': 'python_audit',
    'end-to-end': 'agent_orchestration',
}
EXECUTION = {'plan_only', 'write_code', 'run_approved'}
CATALOG_FIELDS = ('analysis_catalog', 'pipeline_registry', 'plot_catalog', 'research_plan_schema')


def validate(root: Path, definition: dict | None = None) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    def path_for(value, label):
        if not isinstance(value, str) or not value:
            errors.append(f'{label}: expected a nonempty repository-relative path')
            return None
        path = Path(value)
        if path.is_absolute() or '..' in path.parts:
            errors.append(f'{label}: path must stay inside the repository')
            return None
        target = root / path
        if not target.resolve().is_relative_to(root) or not target.is_file():
            errors.append(f'{label}: missing or unsafe file {value}')
            return None
        return target

    def read_json(path, label):
        if path is None:
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            errors.append(f'{label}: {exc}')
            return {}

    if definition is None:
        definition = read_json(path_for('STRATEGY_ROUTES.json', 'routes'), 'routes')
    if not isinstance(definition, dict):
        return ['routes: expected an object']
    if definition.get('skill_major_version') != 3:
        errors.append('skill_major_version must remain 3')
    if definition.get('path_base') != 'repository_root':
        errors.append('path_base must be repository_root')
    catalogs = {key: read_json(path_for(definition.get(key), key), key) for key in CATALOG_FIELDS}
    analysis = catalogs['analysis_catalog'].get('modules', {}) if isinstance(catalogs['analysis_catalog'], dict) else {}
    pipeline = catalogs['pipeline_registry'].get('modules', {}) if isinstance(catalogs['pipeline_registry'], dict) else {}
    if not isinstance(analysis, dict) or not analysis:
        errors.append('analysis catalog has no module dictionary')
        analysis = {}
    if not isinstance(pipeline, dict) or not pipeline:
        errors.append('pipeline registry has no module dictionary')
        pipeline = {}
    plots = catalogs['plot_catalog']
    if not isinstance(plots, list) or not plots or any(not isinstance(x, dict) or not x.get('kind') for x in plots):
        errors.append('plot catalogue must contain kind definitions')
    elif len({x['kind'] for x in plots}) != len(plots):
        errors.append('plot catalogue contains duplicate kinds')

    routes = definition.get('routes')
    if not isinstance(routes, dict):
        return errors + ['routes must be an object']
    if set(routes) != set(REQUIRED_ROUTES):
        errors.append('route IDs differ from the reviewed seven-route contract')
    for rid, spec in routes.items():
        if not isinstance(spec, dict):
            errors.append(f'{rid}: expected an object')
            continue
        if spec.get('execution_kind') != REQUIRED_ROUTES.get(rid):
            errors.append(f'{rid}: invalid execution_kind')
        if spec.get('default_execution') not in EXECUTION:
            errors.append(f'{rid}: invalid default_execution')
        path_for(spec.get('entry'), f'{rid}.entry')
        for key in ('read_after', 'required_inputs', 'outputs'):
            values = spec.get(key)
            if not isinstance(values, list) or not values or any(not isinstance(x, str) or not x.strip() for x in values):
                errors.append(f'{rid}.{key}: expected a nonempty string list')
                continue
            if len(values) != len(set(values)):
                errors.append(f'{rid}.{key}: duplicate entries')
            if key == 'read_after':
                for value in values:
                    path_for(value, f'{rid}.read_after')
        if not isinstance(spec.get('boundary'), str) or not spec['boundary'].strip():
            errors.append(f'{rid}: capability boundary is required')
        if spec.get('execution_kind') in {'python_renderer', 'python_audit'}:
            path_for(spec.get('cli'), f'{rid}.cli')
        elif 'cli' in spec:
            errors.append(f'{rid}: an agent-only route must not claim a bundled CLI')

    handoffs = definition.get('analysis_to_plot')
    if not isinstance(handoffs, dict):
        return errors + ['analysis_to_plot must be an object']
    if set(handoffs) != set(analysis):
        errors.append('analysis_to_plot keys must cover exactly the live analysis catalog')
    for aid, destinations in handoffs.items():
        if not isinstance(destinations, list) or not destinations or any(not isinstance(x, str) for x in destinations):
            errors.append(f'{aid}: invalid plotting handoff list')
            continue
        if len(destinations) != len(set(destinations)):
            errors.append(f'{aid}: duplicate plotting handoffs')
        for destination in destinations:
            if destination not in pipeline:
                errors.append(f'{aid}: unknown plotting module {destination}')

    for name in ('README.md', 'AGENTS.md'):
        doc = path_for(name, name)
        if doc is None:
            continue
        text = doc.read_text(encoding='utf-8')
        for rid in REQUIRED_ROUTES:
            if f'`{rid}`' not in text:
                errors.append(f'{name}: missing documented route {rid}')
        if 'STRATEGY_ROUTES.json' not in text:
            errors.append(f'{name}: no registry link')
        for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)', text):
            if target.startswith(('https://', 'http://', 'mailto:', '#')):
                continue
            relative = unquote(target.split('#', 1)[0])
            candidate = root / relative
            if not candidate.resolve().is_relative_to(root) or not candidate.exists():
                errors.append(f'{name}: broken local link {target}')
    return errors


def self_test(root: Path, definition: dict) -> int:
    """Negative cases must fail; do not weaken the production checks to pass tests."""
    cases = []
    bad = copy.deepcopy(definition)
    bad['routes']['analysis-plan']['entry'] = 'missing_route_entry.md'
    cases.append(('missing entry', bad, 'missing_route_entry.md'))
    bad = copy.deepcopy(definition)
    bad['routes']['analysis-plan']['cli'] = 'fake_analysis.py'
    cases.append(('fictional analysis executable', bad, 'agent-only route'))
    bad = copy.deepcopy(definition)
    aid = next(iter(bad['analysis_to_plot']))
    bad['analysis_to_plot'][aid] = ['not.a.plot.module']
    cases.append(('unknown renderer', bad, 'unknown plotting module'))
    bad = copy.deepcopy(definition)
    bad['analysis_to_plot']['not.an.analysis'] = ['scrna.qc']
    cases.append(('unknown analysis', bad, 'exactly the live analysis catalog'))
    bad = copy.deepcopy(definition)
    del bad['analysis_to_plot'][next(iter(bad['analysis_to_plot']))]
    cases.append(('missing handoff', bad, 'exactly the live analysis catalog'))
    bad = copy.deepcopy(definition)
    bad['routes']['plot-single']['entry'] = '../outside.md'
    cases.append(('path traversal', bad, 'inside the repository'))
    bad = copy.deepcopy(definition)
    bad['routes']['end-to-end']['default_execution'] = 'silently_run_everything'
    cases.append(('undefined execution mode', bad, 'invalid default_execution'))
    for label, candidate, expected in cases:
        errors = validate(root, candidate)
        if not any(expected in error for error in errors):
            raise RuntimeError(f'Negative regression did not detect {label}: {errors}')
    return len(cases)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print('ERROR:', error)
        return 1
    definition = json.loads((args.root / 'STRATEGY_ROUTES.json').read_text(encoding='utf-8'))
    print(f"PASS: {len(definition['routes'])} invocation routes; {len(definition['analysis_to_plot'])} analysis handoffs; referenced files and README/AGENTS links exist")
    if args.self_test:
        count = self_test(args.root, definition)
        print(f'PASS: {count} negative routing regressions')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
