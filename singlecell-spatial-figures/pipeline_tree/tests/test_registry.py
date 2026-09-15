from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pipeline_registry", HERE / "validate_registry.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def docs():
    return module.load_json(HERE / "MODULE_REGISTRY.json"), module.load_json(HERE / "RESULT_CONTRACTS.json")


def test_shipped_registry_is_valid():
    registry, contracts = docs()
    result = module.validate(registry, contracts)
    assert result["ok"], result["errors"]
    assert result["summary"]["modules"] >= 30
    assert result["summary"]["required_plot_assignments"] > 100
    assert result["summary"]["advanced_plot_assignments"] > 70


def test_every_module_has_both_figure_levels():
    registry, _ = docs()
    for item in registry["modules"]:
        assert item["required_plots"]
        assert item["advanced_plots"]


def test_all_contracts_resolve():
    registry, contracts = docs()
    known = set(contracts["contracts"])
    assert all(item["contract"] in known for item in registry["modules"])


def test_subtitle_policy_is_hard_failure():
    registry, contracts = docs()
    broken = copy.deepcopy(registry)
    broken["subtitle_policy"] = "optional"
    result = module.validate(broken, contracts)
    assert not result["ok"]
    assert any("subtitle" in message for message in result["errors"])


def test_missing_advanced_plot_is_hard_failure():
    registry, contracts = docs()
    broken = copy.deepcopy(registry)
    broken["modules"][0]["advanced_plots"] = []
    result = module.validate(broken, contracts)
    assert not result["ok"]
    assert any("advanced_plots" in message for message in result["errors"])


def test_unknown_contract_is_hard_failure():
    registry, contracts = docs()
    broken = copy.deepcopy(registry)
    broken["modules"][0]["contract"] = "does_not_exist"
    result = module.validate(broken, contracts)
    assert not result["ok"]
    assert any("unknown result contract" in message for message in result["errors"])


def test_duplicate_module_ids_are_rejected():
    registry, contracts = docs()
    broken = copy.deepcopy(registry)
    broken["modules"][1]["id"] = broken["modules"][0]["id"]
    result = module.validate(broken, contracts)
    assert not result["ok"]
    assert any("duplicate module IDs" in message for message in result["errors"])
