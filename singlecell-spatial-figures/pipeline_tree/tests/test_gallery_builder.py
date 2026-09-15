from __future__ import annotations
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/f"{name}.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_every_executable_module_has_gallery_fixture():
    gallery=load("build_gallery")
    assert set(gallery.all_fixtures())==set(gallery.run_pipeline.IMPLEMENTED["modules"])
