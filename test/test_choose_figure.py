"""Default figure picker ranks IHTC-vs-pressure plots above schematics."""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from execusci_paths import add_stages  # noqa: E402

add_stages("Extract Equations", "Translate2Python", "Scrape Constants", "Plotting")

from plot_compare import choose_figure, score_figure  # noqa: E402

_SAMPLE_PAPER = os.path.join(
    _SRC, "01_input", "target", "sample_paper_1", "sample_paper_1.md"
)


def test_score_figure_prefers_p20_ihtc_over_schematic():
    fig1 = "Fig_1_Overall_schematic_structure_of_the_IHTC_test_facility.jpg"
    fig8 = (
        "Fig_8_The_predicted_IHTC_evolutions_with_contact_pressure_"
        "using_P20_tools_under_dry_an.jpg"
    )
    fig4 = (
        "Fig_4_The_IHTC_evolutions_with_contact_pressure_using_H13_"
        "and_cast_iron_tools_under_dr.jpg"
    )
    assert score_figure(fig1) < 0
    assert score_figure(fig8) > score_figure(fig4) > 0
    assert score_figure(fig8) > score_figure(fig1)


def test_choose_figure_uses_paper_bundle_not_fig1(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    fig1 = images / "Fig_1_Overall_schematic_structure_of_the_IHTC_test_facility.jpg"
    fig8 = images / (
        "Fig_8_The_predicted_IHTC_evolutions_with_contact_pressure_"
        "using_P20_tools_under_dry_an.jpg"
    )
    fig1.write_bytes(b"x")
    fig8.write_bytes(b"y")
    paper = tmp_path / "sample.md"
    paper.write_text("# paper\n", encoding="utf-8")

    chosen = choose_figure(paper=str(paper))
    assert os.path.normcase(os.path.abspath(chosen)) == os.path.normcase(str(fig8))


def test_choose_figure_explicit_path_wins(tmp_path):
    other = tmp_path / "other.png"
    other.write_bytes(b"z")
    chosen = choose_figure(path=str(other), paper=str(tmp_path / "missing.md"))
    assert os.path.normcase(os.path.abspath(chosen)) == os.path.normcase(str(other))


def test_choose_figure_picks_fig8_from_sample_paper():
    if not os.path.isfile(_SAMPLE_PAPER):
        import pytest

        pytest.skip("sample_paper_1 is not in target/")
    chosen = choose_figure(paper=_SAMPLE_PAPER)
    assert os.path.basename(chosen).lower().startswith("fig_8_")
