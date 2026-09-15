from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/f"{name}.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
runtime=load("runtime");fixtures=load("runtime_fixtures")

@pytest.mark.parametrize("module_id",sorted(fixtures.FIXTURES))
def test_runtime_generates_figures(module_id,tmp_path):
    table,cfg=fixtures.FIXTURES[module_id]();manifest=runtime.render_module(module_id,{"main":table},cfg,tmp_path/module_id.replace(".","_"));assert manifest["module_id"]==module_id;assert manifest["subtitle_policy"]=="forbidden";assert manifest["generated"]
    assert all("subtitle" not in json.dumps(rec).lower() for rec in manifest["generated"])
    for rec in manifest["generated"]:
        outs=rec["outputs"];assert Path(outs["png"]).is_file();assert Path(outs["pdf"]).is_file()
        if rec["kind"]!="review_contact_sheet" and rec["engine"]!="alias":assert "svg" in outs and Path(outs["svg"]).is_file()

def test_unknown_module_refuses_runtime(tmp_path):
    table,cfg=fixtures.scrna_qc()
    with pytest.raises(NotImplementedError):runtime.render_module("not.registered",{"main":table},cfg,tmp_path/"x")

def test_real_data_requires_explicit_provenance(tmp_path):
    table,cfg=fixtures.scrna_qc();cfg=dict(cfg);cfg["demo"]=False;cfg.pop("provenance",None)
    with pytest.raises(ValueError):runtime.render_module("scrna.qc",{"main":table},cfg,tmp_path/"x")

def test_legacy_subtitle_is_ignored(tmp_path):
    table,cfg=fixtures.scrna_qc();cfg=dict(cfg);cfg["subtitle"]="THIS MUST NOT RENDER";manifest=runtime.render_module("scrna.qc",{"main":table},cfg,tmp_path/"x");assert "THIS MUST NOT RENDER" not in json.dumps(manifest)
