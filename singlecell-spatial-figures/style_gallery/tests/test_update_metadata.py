"""Metadata migration tests. These do not simulate or claim a GitHub push."""
import json,subprocess,sys,shutil,importlib.util
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[1]

def mock_checkout(tmp_path,major='3.1.0'):
    root=tmp_path/'repo';g=root/'singlecell-spatial-figures/style_gallery';g.mkdir(parents=True)
    for name in ['repository_update.py','catalogue_v32.json']:shutil.copy2(HERE/name,g/name)
    cap={'version':major,'palettes':{'count':52,'status':'preserve this exactly'},'renderers':['embedding','spatial','marker_dot','annotated_heatmap'],'style_gallery':{'version':'3.1.0','kinds':list(range(14))}}
    (g.parent/'CAPABILITIES.json').write_text(json.dumps(cap))
    old='<!-- STYLE_GALLERY_V3_1:START -->\nOld 14 kinds\n<!-- STYLE_GALLERY_V3_1:END -->\n'
    (root/'README.md').write_text('# Project\n\n'+old)
    (g.parent/'SKILL.md').write_text('---\nname: singlecell-spatial-figures\ndescription: preserved\n---\n# Main\n'+old)
    (g.parent/'QA_REPORT.md').write_text('# Historical QA\n'+old)
    return root,g,cap

def test_metadata_retains_palette_and_major_and_schema(tmp_path):
    root,g,old=mock_checkout(tmp_path)
    subprocess.run([sys.executable,str(g/'repository_update.py'),'metadata'],check=True)
    cap=json.loads((g.parent/'CAPABILITIES.json').read_text())
    assert cap['version']=='3.2.0'
    assert cap['palettes']==old['palettes']
    assert cap['renderers']==old['renderers']
    assert len(cap['style_gallery']['kinds'])==26
    text=(g.parent/'SKILL.md').read_text()
    assert text.startswith('---\nname: singlecell-spatial-figures')
    assert '所有绘图均不显示 subtitle' in text and 'Old 14 kinds' not in text

def test_metadata_is_idempotent(tmp_path):
    root,g,_=mock_checkout(tmp_path)
    cmd=[sys.executable,str(g/'repository_update.py'),'metadata']
    subprocess.run(cmd,check=True)
    paths=[root/'README.md',g.parent/'SKILL.md',g.parent/'QA_REPORT.md',g.parent/'CAPABILITIES.json']
    before=[p.read_bytes() for p in paths]
    subprocess.run(cmd,check=True)
    assert before==[p.read_bytes() for p in paths]

def test_metadata_refuses_major_change(tmp_path):
    _,g,_=mock_checkout(tmp_path,'4.0.0')
    p=subprocess.run([sys.executable,str(g/'repository_update.py'),'metadata'],capture_output=True)
    assert p.returncode!=0 and b'Major version' in p.stderr

def test_ci_does_not_unpack_stale_delivery():
    workflow=HERE.parents[1]/'.github/workflows/style-gallery.yml'
    if not workflow.is_file():pytest.skip('Standalone gallery without repository workflow')
    text=workflow.read_text()
    assert 'extractall' not in text and 'part_0' not in text
    assert '26 no-subtitle' in text

def test_no_parallel_stale_catalogue():
    p=HERE/'catalogue.py'
    assert 'catalogue_v32.json' in p.read_text()
    assert 'ROWS=' not in p.read_text()
