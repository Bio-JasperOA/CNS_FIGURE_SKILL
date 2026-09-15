from __future__ import annotations
import importlib.util,json
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/f"{name}.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
router=load("run_pipeline");fixtures=load("runtime_fixtures3")

@pytest.mark.parametrize("module_id",sorted(fixtures.FIXTURES))
def test_tranche3_real_renderers(module_id,tmp_path):
    inputs,cfg=fixtures.FIXTURES[module_id]();m=router.render_module(module_id,inputs,cfg,tmp_path/module_id.replace(".","_"))
    assert m["subtitle_policy"]=="forbidden" and m["generated"]
    targets={r["target"] for r in m["generated"]};decl=router.IMPLEMENTED["modules"][module_id]
    assert targets & set(decl["required_targets"]);assert targets & set(decl["advanced_targets"])
    assert "subtitle" not in json.dumps(m["generated"]).lower()
    for rec in m["generated"]:
        assert Path(rec["outputs"]["png"]).is_file();assert Path(rec["outputs"]["pdf"]).is_file()
        if rec["kind"]!="review_contact_sheet" and rec["engine"]!="alias":assert Path(rec["outputs"]["svg"]).is_file()


def test_mapping_entropy_is_labeled_as_derived_not_posterior(tmp_path):
    inputs,cfg=fixtures.reference_mapping();m=router.render_module("cross_modal.reference_mapping",inputs,cfg,tmp_path/"mapping")
    targets={r["target"] for r in m["generated"]};assert "mapping_composition_entropy" in targets
    assert "posterior" not in json.dumps(m["generated"]).lower()


def test_latent_consistency_requires_supplied_score(tmp_path):
    inputs,cfg=fixtures.latent_embedding();inputs["main"]=inputs["main"].drop(columns="confidence")
    m=router.render_module("fm.latent_embedding",inputs,cfg,tmp_path/"latent")
    assert "neighborhood_consistency" not in {r["target"] for r in m["generated"]}
    assert any(x["target"]=="neighborhood_consistency" for x in m["skipped"])
