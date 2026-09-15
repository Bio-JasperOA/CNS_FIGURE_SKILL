#!/usr/bin/env python3
"""Validate and inspect the pipeline-first figure registry.

This tool validates architecture only. A named plot target is not automatically an
implemented renderer; current reusable backends are listed separately in each module.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / "MODULE_REGISTRY.json"
CONTRACTS_PATH = HERE / "RESULT_CONTRACTS.json"


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def validate(registry: dict, contracts_doc: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if registry.get("skill_major_version") != 3:
        errors.append("pipeline registry must remain on Skill major version 3")
    if registry.get("figure_spec_version") != "3.0":
        errors.append("FigureSpec version must remain 3.0 for this additive architecture")
    if registry.get("subtitle_policy") != "forbidden":
        errors.append("subtitle policy must be forbidden")

    contracts = contracts_doc.get("contracts", {})
    if not isinstance(contracts, dict) or not contracts:
        errors.append("RESULT_CONTRACTS.json has no contracts")
        contracts = {}

    domains = registry.get("domains", [])
    modules = registry.get("modules", [])
    if not isinstance(domains, list) or not domains:
        errors.append("registry has no domains")
    if not isinstance(modules, list) or not modules:
        errors.append("registry has no modules")
        modules = []

    ids = [m.get("id") for m in modules if isinstance(m, dict)]
    duplicate_ids = sorted(k for k, n in Counter(ids).items() if k and n > 1)
    if duplicate_ids:
        errors.append("duplicate module IDs: " + ", ".join(duplicate_ids))

    required_plot_count = 0
    advanced_plot_count = 0
    all_plots: set[str] = set()
    domain_counts = Counter()
    priority_counts = Counter()

    for index, module in enumerate(modules):
        prefix = f"module[{index}]"
        if not isinstance(module, dict):
            errors.append(prefix + " is not an object")
            continue
        mid = module.get("id") or prefix
        domain = module.get("domain")
        contract = module.get("contract")
        required = module.get("required_plots")
        advanced = module.get("advanced_plots")
        ready = module.get("current_style_gallery_kinds", [])
        priority = module.get("priority")

        if domain not in domains:
            errors.append(f"{mid}: unknown domain {domain!r}")
        else:
            domain_counts[domain] += 1
        if contract not in contracts:
            errors.append(f"{mid}: unknown result contract {contract!r}")
        if priority not in {1, 2, 3}:
            errors.append(f"{mid}: priority must be 1, 2 or 3")
        else:
            priority_counts[priority] += 1

        for label, plots in (("required_plots", required), ("advanced_plots", advanced)):
            if not isinstance(plots, list) or not plots:
                errors.append(f"{mid}: {label} must be a non-empty list")
                continue
            if len(plots) != len(set(plots)):
                errors.append(f"{mid}: duplicate names in {label}")
            bad = [p for p in plots if not isinstance(p, str) or not p.strip()]
            if bad:
                errors.append(f"{mid}: invalid plot name in {label}")
            if any("subtitle" in str(p).lower() for p in plots):
                errors.append(f"{mid}: subtitle-oriented plot target is forbidden")
            all_plots.update(str(p) for p in plots)

        required_plot_count += len(required or []) if isinstance(required, list) else 0
        advanced_plot_count += len(advanced or []) if isinstance(advanced, list) else 0
        if not isinstance(ready, list):
            errors.append(f"{mid}: current_style_gallery_kinds must be a list")
        elif not ready:
            warnings.append(f"{mid}: no existing style_gallery backend; entirely new renderer work")

    panels = registry.get("panel_templates", {})
    if not isinstance(panels, dict) or not panels:
        errors.append("panel_templates must be a non-empty object")
    else:
        for name, slots in panels.items():
            if not isinstance(slots, list) or not slots:
                errors.append(f"panel template {name!r} has no slots")

    result = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "domains": len(domain_counts),
            "modules": len(modules),
            "required_plot_assignments": required_plot_count,
            "advanced_plot_assignments": advanced_plot_count,
            "unique_plot_targets": len(all_plots),
            "modules_by_domain": dict(sorted(domain_counts.items())),
            "modules_by_priority": {str(k): priority_counts[k] for k in sorted(priority_counts)},
            "contracts": len(contracts),
            "panel_templates": len(panels) if isinstance(panels, dict) else 0,
        },
    }
    return result


def print_tree(registry: dict) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for module in registry["modules"]:
        grouped[module["domain"]].append(module)
    for domain in registry["domains"]:
        rows = grouped.get(domain, [])
        print(domain)
        for i, module in enumerate(rows):
            branch = "└─" if i == len(rows) - 1 else "├─"
            print(f"  {branch} {module['id']} [P{module['priority']}] -> {len(module['required_plots'])} required / {len(module['advanced_plots'])} advanced")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "tree", "report"], nargs="?", default="validate")
    args = parser.parse_args()

    registry = load_json(REGISTRY_PATH)
    contracts = load_json(CONTRACTS_PATH)
    result = validate(registry, contracts)

    if args.command == "tree":
        print_tree(registry)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    if not result["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
