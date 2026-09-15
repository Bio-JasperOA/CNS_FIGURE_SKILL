"""One-time checked delivery and repeatable v3.2 publication verification.
The obsolete 24-family delivery is never executed. No secrets or user data needed.
"""
from pathlib import Path, PurePosixPath
import argparse, datetime as dt, hashlib, io, json, os, re, tarfile

ROOT = Path.cwd().resolve()
SKILL = ROOT / 'singlecell-spatial-figures'
GALLERY = SKILL / 'style_gallery'
DELIVERY = ROOT / '.delivery/style-gallery-v32-26'
STATE = Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'cns-style-publish-state.json'
DIGEST = '98cbc446b1daa3c237847a88265c1842e40996a9e519b60f2fa4f751b884b874'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def protected():
    paths = list((SKILL / 'assets').rglob('*')) + list((SKILL / 'scripts').rglob('*'))
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(paths)
            if p.is_file() and '__pycache__' not in p.parts}

def install():
    caps = json.loads((SKILL / 'CAPABILITIES.json').read_text())
    assert str(caps['version']).split('.')[0] == '3', 'Major version changed'
    state = {'protected': protected(),
             'capabilities': {k: v for k, v in caps.items() if k not in ('version', 'style_gallery')},
             'source_sha256': {}}
    if DELIVERY.exists():
        paths = [DELIVERY / f'chunk_{i:02d}.xz' for i in range(19)]
        raw = b''.join(p.read_bytes() for p in paths)
        assert len(raw) == 41616 and hashlib.sha256(raw).hexdigest() == DIGEST, 'Delivery checksum mismatch'
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:xz') as archive:
            members = archive.getmembers()
            assert len(members) == 20 and sum(m.size for m in members) == 144602
            assert len({m.name for m in members}) == len(members), 'Repeated source path'
            staged = []
            for member in members:
                rel = PurePosixPath(member.name)
                assert member.isfile() and not rel.is_absolute() and '..' not in rel.parts
                assert rel.parts[:2] == ('singlecell-spatial-figures', 'style_gallery')
                target = ROOT / str(rel)
                assert target.resolve().is_relative_to(ROOT)
                assert not any(p.is_symlink() for p in [target, *target.parents] if p != ROOT)
                data = archive.extractfile(member).read()
                assert len(data) == member.size
                staged.append((target, data))
            for target, data in staged:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                state['source_sha256'][target.relative_to(ROOT).as_posix()] = hashlib.sha256(data).hexdigest()
        for path in paths:
            path.unlink()
        DELIVERY.rmdir()
    else:
        assert (GALLERY / 'catalogue_v32.json').is_file(), 'No v3.2 sources installed'
    STATE.write_text(json.dumps(state, indent=2))
    print('Verified v3.2 source delivery; saved protected palette, schema and script hashes')

def verify():
    import fitz
    import pandas as pd
    state = json.loads(STATE.read_text())
    assert state['protected'] == protected(), 'Palette, schema or legacy script changed'
    caps = json.loads((SKILL / 'CAPABILITIES.json').read_text())
    assert state['capabilities'] == {k: v for k, v in caps.items() if k not in ('version', 'style_gallery')}
    assert caps['version'] == '3.2.0' and len(caps['style_gallery']['kinds']) == 26
    for rel, sha in state['source_sha256'].items():
        assert digest(ROOT / rel) == sha, 'Delivered source modified: ' + rel
    root = GALLERY / 'examples'
    manifest = json.loads((root / 'manifest.json').read_text())
    assert manifest['version'] == '3.2.0' and len(manifest['pairs']) == 26
    prefixes = [root / 'figures' / f'{row["kind"]}_{mode}'
                for row in manifest['pairs'] for mode in ('minimal', 'advanced')]
    prefixes += [root / 'figures' / f'embedding_100_{mode}' for mode in ('minimal', 'advanced')]
    checked = []
    for prefix in prefixes:
        qa = json.loads(prefix.with_suffix('.qa.json').read_text())
        assert qa['subtitle_count'] == 0 and not qa['outside_canvas'], prefix.name
        for ext in ('png', 'pdf', 'svg'):
            path = prefix.with_suffix('.' + ext)
            assert path.stat().st_size > 1000
            assert digest(path) == qa['outputs'][ext], 'Output hash mismatch: ' + path.name
        assert '<text' in prefix.with_suffix('.svg').read_text()
        with fitz.open(prefix.with_suffix('.pdf')) as doc:
            assert len(doc) == 1
            assert abs(doc[0].rect.width * 25.4 / 72 - qa['width_mm']) < .03
            assert abs(doc[0].rect.height * 25.4 / 72 - qa['height_mm']) < .03
            text = doc[0].get_text()
            assert 'SYNTHETIC EXAMPLE' in text and 'SUBTITLE' not in text
        checked.append({'figure': prefix.name, 'subtitle_count': 0, 'outside_canvas': [],
                        'outputs': qa['outputs']})
    with fitz.open(root / 'paired_gallery.pdf') as doc:
        assert len(doc) == 26
    for mode in ('minimal', 'advanced'):
        key = pd.read_csv(root / 'figures' / f'embedding_100_{mode}.colors.csv')
        assert len(key) == 100 and key.color.nunique() == 100
    for row in manifest['pairs']:
        csv = root / 'source_data' / (row['kind'] + '.csv')
        assert digest(csv) == row['data_sha256']
        assert digest(csv.with_suffix('.json')) == row['config_sha256']
    log = (GALLERY / 'CI_REPORT.txt').read_text()
    summary = next((line for line in reversed(log.splitlines()) if re.search(r'\d+ passed', line)), '')
    assert summary and not re.search(r'\d+ failed|\d+ error', summary), summary
    report = {'version': '3.2.0', 'status': 'verified_before_generated_commit',
              'source_commit': os.environ.get('GITHUB_SHA'),
              'workflow_url': os.environ.get('GITHUB_SERVER_URL', 'https://github.com') + '/' + os.environ.get('GITHUB_REPOSITORY', 'Bio-JasperOA/CNS_FIGURE_SKILL') + '/actions/runs/' + os.environ.get('GITHUB_RUN_ID', ''),
              'checked_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'ci_summary': summary, 'chart_families': 26, 'standalone_figures': 54,
              'paired_pdf_pages': 26, 'palette_schema_legacy_scripts_unchanged': True,
              'source_archive_sha256': DIGEST, 'source_sha256': state['source_sha256'],
              'figures': checked,
              'limits': ['Synthetic style fixtures, not biological results',
                         'No native R validation', 'No universal visual or scientific certification']}
    (GALLERY / 'PUBLISH_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    # Keep the original authoring QA intact, with its historical scope explicit.
    p = GALLERY / 'QA_REPORT.md'
    old = p.read_text()
    start, end = '<!-- REMOTE_PUBLICATION:START -->', '<!-- REMOTE_PUBLICATION:END -->'
    old = re.sub(re.escape(start) + r'.*?' + re.escape(end) + r'\s*', '', old, flags=re.S)
    header = (start + '\n# GitHub publication verification\n\n' + summary + '\n\n'
              '26 families; 54 no-subtitle figures; 26-page paired PDF; existing palette, schema and legacy script hashes unchanged.\n\n'
              '[Build run](' + report['workflow_url'] + ') | [Machine-readable report](PUBLISH_REPORT.json). '
              'The authoring report below is historical; its earlier not-uploaded status does not describe this publication.\n'
              + end + '\n\n')
    p.write_text(header + old)
    print(summary)
    print('Verified 54 no-subtitle exports and 26 paired PDF pages; protected files unchanged')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['install', 'verify'])
    args = parser.parse_args()
    {'install': install, 'verify': verify}[args.command]()
