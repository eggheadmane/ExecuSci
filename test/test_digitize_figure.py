"""Stage 05 figure digitizer: axes, symbols, and curve extraction."""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BUILD = os.path.join(_ROOT, "build")
if _BUILD not in sys.path:
    sys.path.insert(0, _BUILD)

from execusci_paths import TARGET, add_stages, paper_path, target_figure_paths  # noqa: E402

add_stages("Extract Equations", "Latex2Python", "Plotting")

from digitize_figure import (  # noqa: E402
    digitize_figure,
    extract_captions,
    match_axis_symbol,
    parse_thicknesses,
    split_label_unit,
    thickness_to_metres,
)
from extract_equations import extract  # noqa: E402

easyocr = pytest.importorskip("easyocr")
cv2 = pytest.importorskip("cv2")

PAPER = paper_path()
SAMPLE_FIG = os.path.join(TARGET, "sample_pic1.jpg")


@pytest.fixture(scope="module")
def symbol_dict() -> dict:
    with open(PAPER, "r", encoding="utf-8") as fh:
        return extract(fh.read(), source=PAPER).to_json()["symbols"]


@pytest.fixture(scope="module")
def captions() -> list:
    with open(PAPER, "r", encoding="utf-8") as fh:
        return extract_captions(fh.read())


def test_target_folder_contains_the_sample_figure():
    paths = [os.path.normcase(p) for p in target_figure_paths()]
    assert os.path.normcase(SAMPLE_FIG) in paths


def test_split_label_unit_and_aliases():
    label, unit = split_label_unit("Contact pressure, MPa")
    assert "pressure" in label.lower()
    assert unit.lower() == "mpa"
    assert thickness_to_metres(0.015, "mm") == pytest.approx(1.5e-5)
    assert parse_thicknesses("lube conditions (0.015 mm)") == [pytest.approx(1.5e-5)]


def test_axis_labels_map_to_symbols(symbol_dict):
    assert match_axis_symbol("IHTC, kW/m²K", symbol_dict) == "h"
    assert match_axis_symbol("Contact pressure, MPa", symbol_dict) == "P"


def test_fig8_caption_is_extracted(captions):
    blob = " ".join(captions)
    assert "IHTC" in blob
    assert "contact pressure" in blob.lower()


def _save_synthetic_plot(path: str) -> np.ndarray:
    x = np.linspace(0.0, 20.0, 200)
    y = 4.6 + 10.2 * (1.0 - np.exp(-0.28 * x))
    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=120)
    ax.plot(x, y, color="#f0a202", linewidth=2.5, label="P20 tools: model predictions: lube conditions (0.015 mm)")
    ax.set_xlabel("Contact pressure, MPa")
    ax.set_ylabel("IHTC, kW/m²K")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 16)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_yticks([0, 2, 4, 6, 8, 10, 12, 14, 16])
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return y


def test_synthetic_figure_axes_and_model_curve(tmp_path, symbol_dict, captions):
    image = tmp_path / "synthetic.png"
    _save_synthetic_plot(str(image))
    digitized = digitize_figure(
        str(image), symbols=symbol_dict, captions=captions, tools=["P20", "H13"]
    )
    assert digitized.x_symbol == "P"
    assert digitized.y_symbol == "h"
    assert digitized.calib.xmin == pytest.approx(0.0, abs=1.5)
    assert digitized.calib.xmax == pytest.approx(20.0, abs=1.5)
    assert digitized.calib.ymin == pytest.approx(0.0, abs=1.5)
    assert digitized.calib.ymax == pytest.approx(16.0, abs=1.5)
    models = digitized.model_series()
    assert models, "expected at least one model series"
    series = models[0]
    assert len(series.x) >= 20
    assert series.x.min() == pytest.approx(0.0, abs=2.0)
    assert series.x.max() == pytest.approx(20.0, abs=2.0)


@pytest.mark.skipif(not os.path.isfile(SAMPLE_FIG), reason="sample_pic1.jpg is missing")
def test_sample_pic1_axis_ranges(symbol_dict, captions):
    digitized = digitize_figure(
        SAMPLE_FIG, symbols=symbol_dict, captions=captions, tools=["P20"]
    )
    labels = f"{digitized.x_label} {digitized.y_label} {' '.join(digitized.legend_text)} {' '.join(captions)}"
    assert "pressure" in labels.lower() or digitized.x_symbol == "P"
    assert "ihtc" in labels.lower() or digitized.y_symbol == "h"
    assert digitized.calib.xmin == pytest.approx(0.0, abs=3.0)
    assert digitized.calib.xmax == pytest.approx(20.0, abs=3.0)
    assert digitized.calib.ymin == pytest.approx(0.0, abs=3.0)
    assert digitized.calib.ymax == pytest.approx(16.0, abs=3.0)
    assert digitized.model_series(), "expected a model curve on Fig. 8"
