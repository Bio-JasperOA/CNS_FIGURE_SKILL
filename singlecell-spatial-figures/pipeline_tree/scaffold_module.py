#!/usr/bin/env python3
"""Generate conservative code scaffolds for registered pipeline modules.

Generated files are deliberately non-implementing stubs. They establish contracts and
locations without pretending a scientific renderer exists before it is implemented and
tested. Use `--all` to materialize the full registered tree.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = json.loads((HERE / "MODULE_REGISTRY.json").read_text(encoding="utf-8"))
CONTRACTS = json.loads((HERE / "RESULT_CONTRACTS.json").read_text(encoding="utf-8"))["contracts"]


def find_module(module_id: str) -> dict:
    rows = [m for m in REGISTRY["modules"] if m["id"] == module_id]
    if len(rows) != 1:
        raise ValueError(f"unknown or duplicate module id: {module_id}")
    return rows[0]


def safe_name(module_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", module_id.split(".", 1)[-1]).strip("_")


def python_stub(level: str, module: dict) -> str:
    plots = module[f"{level}_plots"] if level in {"required", "advanced"} else module["advanced_plots"]
    return f'''"""{level} rendering entry for {module['id']}.

This scaffold is not an implemented scientific renderer. Replace the explicit
NotImplementedError only after the declared contract and plot semantics are tested.
No subtitle renderer is permitted.
"""
from __future__ import annotations

PLOT_TARGETS = {plots!r}


def render(table, config):
    raise NotImplementedError(
        "{module['id']} {level} renderer is scaffolded but not yet implemented"
    )
'''


def adapter_stub(module: dict) -> str:
    contract = CONTRACTS[module["contract"]]
    required = contract["required"]
    return f'''"""Adapter contract for {module['id']}."""
from __future__ import annotations

REQUIRED_FIELDS = {required!r}


def adapt(table):
    missing = [name for name in REQUIRED_FIELDS if name not in table.columns]
    if missing:
        raise ValueError("missing canonical fields: " + ", ".join(missing))
    return table.copy()
'''


def test_stub(module: dict) -> str:
    return f'''from pathlib import Path
import json


def test_module_contract_is_declared():
    schema = json.loads((Path(__file__).resolve().parents[1] / "schema.json").read_text())
    assert schema["module_id"] == "{module['id']}"
    assert schema["subtitle_policy"] == "forbidden"
    assert schema["required_plots"]
    assert schema["advanced_plots"]


def test_renderer_implementation_must_be_explicit():
    # Generated scaffolds deliberately fail at runtime until a real renderer is supplied.
    text = (Path(__file__).resolve().parents[1] / "advanced.py").read_text()
    assert "NotImplementedError" in text
'''


def generate(module_id: str, root: Path, force: bool = False) -> Path:
    module = find_module(module_id)
    folder = root / module["domain"] / safe_name(module_id)
    if folder.exists() and any(folder.iterdir()) and not force:
        raise FileExistsError(f"refusing to overwrite non-empty module folder: {folder}")
    (folder / "tests").mkdir(parents=True, exist_ok=True)

    contract = CONTRACTS[module["contract"]]
    schema = {
        "module_id": module["id"],
        "domain": module["domain"],
        "priority": module["priority"],
        "contract": module["contract"],
        "required_fields": contract["required"],
        "optional_fields": contract.get("optional", []),
        "required_plots": module["required_plots"],
        "advanced_plots": module["advanced_plots"],
        "current_style_gallery_kinds": module.get("current_style_gallery_kinds", []),
        "subtitle_policy": "forbidden",
        "status": "scaffold_only"
    }
    (folder / "schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    (folder / "adapter.py").write_text(adapter_stub(module), encoding="utf-8")
    (folder / "minimal.py").write_text(python_stub("required", module), encoding="utf-8")
    (folder / "advanced.py").write_text(python_stub("advanced", module), encoding="utf-8")
    (folder / "panel.py").write_text(python_stub("panel", module), encoding="utf-8")
    (folder / "tests" / "test_module.py").write_text(test_stub(module), encoding="utf-8")
    (folder / "README.md").write_text(
        f"# {module['id']}\n\nStatus: scaffold only. Do not claim renderer implementation until code, fixtures and tests replace the explicit NotImplementedError paths.\n",
        encoding="utf-8",
    )
    return folder


def generate_all(root: Path, force: bool = False) -> list[Path]:
    return [generate(module["id"], root, force=force) for module in REGISTRY["modules"]]


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("module_id", nargs="?")
    group.add_argument("--all", action="store_true")
    parser.add_argument("--root", default=str(HERE.parent / "plots"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = Path(args.root)
    if args.all:
        paths = generate_all(root, args.force)
        for path in paths:
            print(path)
        print(f"generated {len(paths)} module scaffolds")
    else:
        print(generate(args.module_id, root, args.force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
