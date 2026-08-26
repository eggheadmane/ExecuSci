"""Stage 05 figure digitizer: axes, symbols, and curve extraction."""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from execusci_paths import TARGET, add_stages, paper_path, target_figure_paths  # noqa: E402

add_stages("Extract Equations", "Translate2Python", "Plotting")

from digitize_figure import (  # noqa: E402
    OcrBox,
    Series,
    choose_plot_frame,
    digitize_figure,
    extract_captions,
    fill_missing_deltas,
    find_plot_frames,
    match_axis_symbol,
    normalise_ocr_text,
    parse_thicknesses,
    parse_tool,
    split_label_unit,
    stitch_legend_rows,
    thickness_to_metres,
)
from extract_equations import extract  # noqa: E402

easyocr = pytest.importorskip("easyocr")
cv2 = pytest.importorskip("cv2")

PAPER = paper_path()


def _sample_figure() -> str:
    for path in target_figure_paths():
        if os.path.basename(path).lower().startswith("fig_8_"):
            return path
    figures = target_figure_paths()
    return figures[0] if figures else os.path.join(TARGET, "sample_pic1.jpg")


SAMPLE_FIG = _sample_figure()


@pytest.fixture(scope="module")
def symbol_dict() -> dict:
    with open(PAPER, "r", encoding="utf-8") as fh:
        return extract(fh.read(), source=PAPER).to_json()["symbols"]


@pytest.fixture(scope="module")
def captions() -> list:
    with open(PAPER, "r", encoding="utf-8") as fh:
        return extract_captions(fh.read())


def test_target_folder_contains_the_sample_figure():
    found = target_figure_paths()
    assert found, "expected raster figures in the target paper bundle"
    assert all(os.path.isfile(p) for p in found)
    if os.path.isfile(SAMPLE_FIG):
        assert os.path.normcase(SAMPLE_FIG) in [os.path.normcase(p) for p in found]


def test_split_label_unit_and_aliases():
    label, unit = split_label_unit("Contact pressure, MPa")
    assert "pressure" in label.lower()
    assert unit.lower() == "mpa"
    assert thickness_to_metres(0.015, "mm") == pytest.approx(1.5e-5)
    assert parse_thicknesses("lube conditions (0.015 mm)") == [pytest.approx(1.5e-5)]
    assert normalise_ocr_text("P2O tools: model predictions") == "P20 tools: model predictions"
    assert parse_tool("P2O tools: dry conditions", ["P20", "H13"]) == "P20"


def _ocr_box(text: str, cx: float, cy: float, width: float = 50.0, height: float = 12.0) -> OcrBox:
    x0, y0 = cx - width / 2.0, cy - height / 2.0
    x1, y1 = cx + width / 2.0, cy + height / 2.0
    pts = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=float)
    return OcrBox(
        text=text,
        conf=0.9,
        pts=pts,
        cx=cx,
        cy=cy,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
    )


def test_stitch_legend_rows_joins_fragments_and_fixes_p20():
    rows = stitch_legend_rows(
        [
            _ocr_box("P2O tools:", 100, 50),
            _ocr_box("model", 160, 51),
            _ocr_box("dry", 210, 50),
            _ocr_box("conditions", 280, 52),
            _ocr_box("P20 tools:", 110, 78),
            _ocr_box("lube conditions (0.015 mm)", 250, 79),
        ]
    )
    blob = " ".join(row.text for row in rows)
    assert "dry" in blob.lower()
    assert "P20" in blob
    assert "P2O" not in blob
    dry_rows = [row for row in rows if "dry" in row.text.lower()]
    assert dry_rows, blob
    assert "P20" in dry_rows[0].text
    messy = stitch_legend_rows(
        [
            _ocr_box("predictions:", 100, 40),
            _ocr_box("redictions:", 170, 40),
            _ocr_box("dry", 230, 40),
            _ocr_box("conditions", 290, 41),
        ]
    )
    assert len(messy) == 1
    tokens = messy[0].text.lower().replace(":", " ").split()
    assert "redictions" not in tokens
    assert "predictions" in tokens
    assert "dry" in messy[0].text.lower()


def test_choose_plot_frame_prefers_subplot_with_ticks():
    """A full-figure fallback crop must lose to the subplot that owns the ticks."""
    fallback = (50, 40, 900, 700)
    panel = (100, 80, 400, 350)
    ocr = [
        _ocr_box("0", 180, 365),
        _ocr_box("10", 250, 365),
        _ocr_box("20", 320, 365),
        _ocr_box("0", 85, 300),
        _ocr_box("8", 85, 200),
        _ocr_box("16", 85, 120),
    ]
    frame, x_ticks, y_ticks = choose_plot_frame([fallback, panel], ocr)
    assert frame == panel
    assert len(x_ticks) >= 2
    assert len(y_ticks) >= 2


def test_fill_missing_deltas_uses_intercepts():
    x = np.linspace(0.0, 20.0, 40)
    dry = Series("grey line", x, 0.8 + 10.0 * (1.0 - np.exp(-0.28 * x)), (120, 120, 120))
    lube = Series("yellow series", x, 4.6 + 10.0 * (1.0 - np.exp(-0.28 * x)), (0, 180, 240))
    filled = fill_missing_deltas([dry, lube], thicknesses=[1.5e-5])
    by_name = {item.name: item.delta for item in filled}
    assert by_name["grey line"] == pytest.approx(0.0)
    assert by_name["yellow series"] == pytest.approx(1.5e-5)


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


def _save_two_curve_plot(path: str) -> None:
    x = np.linspace(0.0, 20.0, 200)
    y_dry = 0.8 + 10.2 * (1.0 - np.exp(-0.28 * x))
    y_lube = 4.6 + 10.2 * (1.0 - np.exp(-0.28 * x))
    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=120)
    ax.plot(x, y_dry, color="#6e6e6e", linewidth=2.5, label="P20 tools: model predictions: dry conditions")
    ax.plot(x, y_lube, color="#f0a202", linewidth=2.5, label="P20 tools: model predictions: lube conditions (0.015 mm)")
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


def _save_four_panel_plot(path: str) -> None:
    x = np.linspace(0.0, 30.0, 120)
    y = 2.0 + 12.0 * (1.0 - np.exp(-0.12 * x))
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 8.0), dpi=120)
    for ax in axes.ravel():
        ax.plot(x, y, color="#d62728", linewidth=2.0)
        ax.set_xlabel("Contact pressure, MPa")
        ax.set_ylabel("IHTC, kW/m²K")
        ax.set_xlim(0, 30)
        ax.set_ylim(0, 16)
        ax.set_xticks([0, 10, 20, 30])
        ax.set_yticks([0, 4, 8, 12, 16])
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


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


def test_synthetic_four_panel_calibrates_one_subplot(tmp_path, symbol_dict, captions):
    image = tmp_path / "four_panel.png"
    _save_four_panel_plot(str(image))
    frames = find_plot_frames(cv2.imread(str(image)))
    assert len(frames) >= 2, f"expected subplot frames, got {frames}"
    digitized = digitize_figure(
        str(image), symbols=symbol_dict, captions=captions, tools=["P20"]
    )
    assert digitized.x_symbol == "P"
    assert digitized.y_symbol == "h"
    assert digitized.calib.xmin == pytest.approx(0.0, abs=2.0)
    assert digitized.calib.xmax == pytest.approx(30.0, abs=3.0)
    assert digitized.calib.ymin == pytest.approx(0.0, abs=2.0)
    assert digitized.calib.ymax == pytest.approx(16.0, abs=2.0)
    assert digitized.model_series(), "expected a model curve in one subplot"


def test_synthetic_dry_and_lube_deltas(tmp_path, symbol_dict, captions):
    image = tmp_path / "synthetic_two.png"
    _save_two_curve_plot(str(image))
    digitized = digitize_figure(
        str(image), symbols=symbol_dict, captions=captions, tools=["P20", "H13"]
    )
    models = [s for s in digitized.model_series() if s.kind == "line"]
    assert len(models) >= 2, f"expected two model lines, got {[s.name for s in digitized.series]}"
    deltas = [s.delta for s in models if s.delta is not None]
    assert any(abs(d) < 1e-12 for d in deltas), deltas
    assert any(abs(d - 1.5e-5) < 1e-9 for d in deltas), deltas


@pytest.mark.skipif(not os.path.isfile(SAMPLE_FIG), reason="no raster figure in the target paper bundle")
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
