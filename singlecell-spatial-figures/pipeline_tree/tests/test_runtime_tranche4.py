from __future__ import annotations
import importlib.util,json
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/f"{name}.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
router=load("run_pipeline");fixtures=load("runtime_fixtures4")

@pytest.mark.parametrize("module_id",sorted(fixtures.FIXTURES))
def test_tranche4_real_renderers(module_id,tmp_path):
    inputs,cfg=fixtures.FIXTURES[module_id]();m=router.render_module(module_id,inputs,cfg,tmp_path/module_id.replace(".","_"));generated={r["target"] for r in m["generated"]};skipped={r["target"] for r in m["skipped"]};decl=router.IMPLEMENTED["modules"][module_id]
    assert m["subtitle_policy"]=="forbidden" and m["generated"]
    assert set(decl["required_targets"])|set(decl["advanced_targets"]) <= generated|skipped
    assert generated & set(decl["required_targets"]);assert generated & set(decl["advanced_targets"])
    assert "subtitle" not in json.dumps(m["generated"]).lower()
    for rec in m["generated"]:
        assert Path(rec["outputs"]["png"]).is_file();assert Path(rec["outputs"]["pdf"]).is_file()
        if rec["kind"]!="review_contact_sheet" and rec["engine"]!="alias":assert Path(rec["outputs"]["svg"]).is_file()
