from __future__ import annotations
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
roadmap=json.loads((HERE/"MODULE_REGISTRY.json").read_text())
implemented=json.loads((HERE/"IMPLEMENTED_MODULES.json").read_text())


def test_implemented_modules_are_roadmap_modules():
    allmods={m["id"]:m for m in roadmap["modules"]}
    assert implemented["skill_major_version"]==3
    assert implemented["subtitle_policy"]=="forbidden"
    for mid,spec in implemented["modules"].items():
        assert mid in allmods
        module=allmods[mid]
        assert set(spec["required_targets"])<=set(module["required_plots"])
        assert set(spec["advanced_targets"])<=set(module["advanced_plots"])
        assert spec["inputs"]


def test_runtime_dispatch_matches_registry():
    spec=importlib.util.spec_from_file_location("runtime",HERE/"runtime.py")
    runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
    assert set(runtime.DISPATCH)==set(implemented["modules"])
