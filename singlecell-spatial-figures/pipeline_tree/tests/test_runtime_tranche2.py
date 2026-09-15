from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parents[1]

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/f"{name}.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

router=load("run_pipeline")
fixtures=load("runtime_fixtures2")

@pytest.mark.parametrize("module_id",sorted(fixtures.FIXTURES))
def test_tranche2_real_renderers(module_id,tmp_path):
    inputs,cfg=fixtures.FIXTURES[module_id]()
    manifest=router.render_module(module_id,inputs,cfg,tmp_path/module_id.replace(".","_"))
    assert manifest["module_id"]==module_id
    assert manifest["subtitle_policy"]=="forbidden"
    assert manifest["generated"]
    targets={r["target"] for r in manifest["generated"]}
    declared=router.IMPLEMENTED["modules"][module_id]
    assert targets & set(declared["required_targets"])
    assert targets & set(declared["advanced_targets"])
    assert "subtitle" not in json.dumps(manifest["generated"]).lower()
    for rec in manifest["generated"]:
        for ext in ("png","pdf"):
            assert ext in rec["outputs"] and Path(rec["outputs"][ext]).is_file()
        if rec["kind"]!="review_contact_sheet" and rec["engine"]!="alias":
            assert Path(rec["outputs"]["svg"]).is_file()


def test_trajectory_interval_requires_explicit_program(tmp_path):
    inputs,cfg=fixtures.trajectory();cfg=dict(cfg);cfg["trend_feature"]="SOX2"
    m=router.render_module("scrna.trajectory",inputs,cfg,tmp_path/"trajectory")
    assert "trend_with_interval" in {r["target"] for r in m["generated"]}


def test_trajectory_without_program_does_not_average_features(tmp_path):
    inputs,cfg=fixtures.trajectory()
    m=router.render_module("scrna.trajectory",inputs,cfg,tmp_path/"trajectory")
    assert "trend_with_interval" not in {r["target"] for r in m["generated"]}
    assert any(x["target"]=="trend_with_interval" for x in m["skipped"])


def test_router_rejects_missing_named_input(tmp_path):
    inputs,cfg=fixtures.annotation();inputs.pop("markers")
    with pytest.raises(ValueError):router.render_module("scrna.annotation",inputs,cfg,tmp_path/"x")


def test_router_keeps_roadmap_boundary(tmp_path):
    inputs,cfg=fixtures.annotation()
    with pytest.raises(NotImplementedError):router.render_module("spatial.communication",inputs,cfg,tmp_path/"x")
