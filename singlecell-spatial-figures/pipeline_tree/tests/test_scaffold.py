from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scaffold_module", HERE / "scaffold_module.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_generate_scaffold(tmp_path):
    folder = module.generate("scrna.qc", tmp_path)
    expected = {
        "schema.json",
        "adapter.py",
        "minimal.py",
        "advanced.py",
        "panel.py",
        "README.md",
    }
    assert expected <= {p.name for p in folder.iterdir() if p.is_file()}
    assert (folder / "tests" / "test_module.py").is_file()
    schema = json.loads((folder / "schema.json").read_text())
    assert schema["status"] == "scaffold_only"
    assert schema["subtitle_policy"] == "forbidden"
    assert schema["required_plots"]
    assert schema["advanced_plots"]


def test_generate_all_scaffolds(tmp_path):
    paths = module.generate_all(tmp_path)
    assert len(paths) == len(module.REGISTRY["modules"])
    assert len({p.as_posix() for p in paths}) == len(paths)
    for folder in paths:
        schema = json.loads((folder / "schema.json").read_text())
        assert schema["required_plots"]
        assert schema["advanced_plots"]
        assert schema["subtitle_policy"] == "forbidden"


def test_refuses_to_overwrite(tmp_path):
    module.generate("scrna.qc", tmp_path)
    try:
        module.generate("scrna.qc", tmp_path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("scaffold generator overwrote an existing module")


def test_unknown_module_fails(tmp_path):
    try:
        module.generate("not.real", tmp_path)
    except ValueError:
        pass
    else:
        raise AssertionError("unknown module ID was accepted")
