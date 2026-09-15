import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image

spec = importlib.util.spec_from_file_location("finalize_style_docs", Path(__file__).with_name("finalize_style_docs.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

@pytest.mark.parametrize("wrapper", [None, "plots", "entries", "catalogue"])
def test_catalogue_wrapper(tmp_path, wrapper):
    rows = [{"kind": "forest", "title": "Forest"}]
    (tmp_path / "catalogue.json").write_text(json.dumps(rows if wrapper is None else {wrapper: rows}))
    assert module.load_rows(tmp_path) == rows

@pytest.mark.parametrize("in_figures", [True, False])
def test_preview_publication(tmp_path, in_figures):
    images = tmp_path / "figures" if in_figures else tmp_path
    images.mkdir(exist_ok=True)
    Image.new("RGB", (100, 60), "#336699").save(images / "forest_advanced.png")
    output = tmp_path / "docs" / "preview.png"
    module.build_preview([{"kind": "forest"}], tmp_path, output)
    with Image.open(output) as actual:
        assert actual.size == (2248, 564)
        assert actual.getpixel((100, 100)) != (0, 0, 0)


def test_missing_image_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        module.build_preview([{"kind": "forest"}], tmp_path, tmp_path / "out.png")


def test_empty_catalogue_fails(tmp_path):
    (tmp_path / "catalogue.json").write_text("[]")
    with pytest.raises(ValueError):
        module.load_rows(tmp_path)


def test_markdown_links(tmp_path):
    module.write_readme([{"kind": "forest", "title": "Forest"}], tmp_path)
    text = (tmp_path / "GALLERY.md").read_text()
    assert "forest_minimal.pdf" in text and "forest_advanced.png" in text
    assert "1 families" in text
