"""Nested target-paper discovery and Mathpix-bundle normalisation."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import execusci_paths as paths  # noqa: E402


def _write_bundle(target: Path, folder: str = "my_paper") -> Path:
    bundle = target / folder
    images = bundle / "images"
    images.mkdir(parents=True)
    (images / "foo.jpg").write_bytes(b"x")
    (images / "orphan.png").write_bytes(b"y")
    (images / "bar.jpg").write_bytes(b"z")
    (bundle / "uuid-1234.md").write_text(
        "![](./images/foo.jpg)\n"
        "Fig. 1. Overall schematic structure of the IHTC test facility.\n"
        "\n"
        "![](./images/bar.jpg)\n"
        "Fig. 10. Predicted IHTC evolutions as a function of conductivity.\n"
        "\n"
        "![](./images/orphan.png)\n"
        "Some prose without a caption.\n",
        encoding="utf-8",
    )
    return bundle


def test_nested_bundle_is_renamed_and_idempotent(tmp_path, monkeypatch):
    target = tmp_path / "target"
    bundle = _write_bundle(target)
    monkeypatch.setattr(paths, "TARGET", str(target))

    result = paths.paper_path()
    assert os.path.basename(result) == "my_paper.md"
    assert os.path.isfile(result)
    assert not (bundle / "uuid-1234.md").exists()

    fig1 = bundle / "images" / "Fig_1_Overall_schematic_structure_of_the_IHTC_test_facility.jpg"
    fig10 = bundle / "images" / "Fig_10_Predicted_IHTC_evolutions_as_a_function_of_conductivity.jpg"
    assert fig1.is_file()
    assert fig10.is_file()
    assert (bundle / "images" / "orphan.png").is_file()
    assert not (bundle / "images" / "foo.jpg").exists()

    text = (bundle / "my_paper.md").read_text(encoding="utf-8")
    assert "./images/Fig_1_Overall_schematic_structure_of_the_IHTC_test_facility.jpg" in text
    assert "./images/Fig_10_Predicted_IHTC_evolutions_as_a_function_of_conductivity.jpg" in text
    assert "foo.jpg" not in text
    assert "./images/orphan.png" in text

    again = paths.paper_path()
    assert os.path.normcase(again) == os.path.normcase(result)
    names = sorted(p.name for p in (bundle / "images").iterdir())
    assert names == [
        "Fig_10_Predicted_IHTC_evolutions_as_a_function_of_conductivity.jpg",
        "Fig_1_Overall_schematic_structure_of_the_IHTC_test_facility.jpg",
        "orphan.png",
    ]

    figs = [os.path.basename(p) for p in paths.target_figure_paths()]
    assert figs[0] == fig1.name
    assert figs[1] == fig10.name
    assert "orphan.png" in figs


def test_explicit_path_inside_bundle_is_normalised(tmp_path, monkeypatch):
    target = tmp_path / "target"
    bundle = _write_bundle(target)
    monkeypatch.setattr(paths, "TARGET", str(target))
    uuid_md = str(bundle / "uuid-1234.md")
    result = paths.paper_path(uuid_md)
    assert os.path.basename(result) == "my_paper.md"
    assert os.path.isfile(result)


def test_loose_paper_in_target_still_works(tmp_path, monkeypatch):
    target = tmp_path / "target"
    target.mkdir()
    paper = target / "sample.md"
    paper.write_text("# hello\n", encoding="utf-8")
    monkeypatch.setattr(paths, "TARGET", str(target))
    result = paths.paper_path()
    assert os.path.normcase(result) == os.path.normcase(str(paper))


def test_multiple_bundles_are_an_error(tmp_path, monkeypatch):
    target = tmp_path / "target"
    _write_bundle(target, "paper_a")
    _write_bundle(target, "paper_b")
    monkeypatch.setattr(paths, "TARGET", str(target))
    with pytest.raises(LookupError, match="Expected one paper folder"):
        paths.paper_path()


def test_nested_bundle_preferred_over_loose_file(tmp_path, monkeypatch):
    target = tmp_path / "target"
    _write_bundle(target)
    (target / "leftover.mmd").write_text("ignore me\n", encoding="utf-8")
    monkeypatch.setattr(paths, "TARGET", str(target))
    result = paths.paper_path()
    assert os.path.basename(result) == "my_paper.md"
