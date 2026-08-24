"""Stage 05 -- compare a reduced model against a paper figure.

Discovers a plot image in the target paper's ``images/`` folder, digitizes its axes and curves,
reduces the extracted equations to the last definition of the y-axis symbol,
evaluates that DAG over the digitized x values, and writes numeric error
plots plus a visual overlay of the prediction on the original figure to
``log/plotting/``.

Usage
-----
    python src/05_plotting/plot_compare.py
    python src/05_plotting/plot_compare.py --eq 6 --target h --x P
    python src/05_plotting/plot_compare.py --no-show
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from execusci_paths import PLOTTING_LOG, add_stages, paper_path, stage_dir, target_figure_paths  # noqa: E402

add_stages("Translate2Python", "Scrape Constants", "Plotting")

import equations  # noqa: E402
from constants import (  # noqa: E402
    DEFAULT_DELTA,
    DEFAULT_TOOL,
    available_tools,
    get_constants,
)

try:
    from constants import DEFAULT_MATERIAL, available_materials  # noqa: E402
except ImportError:  # older generated modules
    DEFAULT_MATERIAL = None
    available_materials = lambda: []  # noqa: E731
from digitize_figure import (  # noqa: E402
    DigitizedFigure,
    DigitizeError,
    Series,
    digitize_figure,
    extract_captions,
    save_digitized,
)
from equation_graph import EquationGraph  # noqa: E402

try:
    from skimage.metrics import structural_similarity as ssim_metric
except ImportError:  # pragma: no cover
    ssim_metric = None

DEFAULT_SYMBOLS = os.path.join(stage_dir("Extract Equations"), "output", "symbols.json")
DEFAULT_OUTPUT = PLOTTING_LOG

_FIGURE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}
_FIG_NUM_RE = re.compile(r"^Fig_(\d+[a-z]?)_", re.IGNORECASE)
_FIG_CAPTION_RE = re.compile(
    r"^Fig(?:ure)?\.?\s*(\d+[a-z]?)\.\s*(.+)$", re.IGNORECASE | re.MULTILINE
)
_SKIP_FIG = re.compile(
    r"schematic|fe_model|fe model|pam_stamp|pam-stamp|facility|"
    r"cross_sectional|cross-sectional|loading_condition",
    re.I,
)
_SCORE_PATTERNS: Tuple[Tuple[re.Pattern[str], int], ...] = (
    (re.compile(r"ihtc|interfacial[\s_]+heat", re.I), 4),
    (re.compile(r"contact[\s_]+pressure", re.I), 4),
    (re.compile(r"\bp20\b", re.I), 2),
    (re.compile(r"predict", re.I), 1),
    (re.compile(r"dry|lube|lubricat", re.I), 1),
)


def percent_error(y_pred: np.ndarray, y_true: np.ndarray) -> np.ndarray:
    y_pred = np.asarray(y_pred, dtype=float)
    y_true = np.asarray(y_true, dtype=float)
    denom = np.maximum(np.abs(y_true), 1e-12)
    return np.abs((y_pred - y_true) / denom) * 100.0


def axis_title(label: str, unit: str) -> str:
    label = (label or "").strip()
    unit = (unit or "").strip()
    if label and unit:
        return f"{label} ({unit})" if unit not in label else label
    return label or unit or ""


def _slug(text: str, fallback: str = "series") -> str:
    slug = re.sub(r"[^\w]+", "_", text or "").strip("_")
    return slug[:48] or fallback


def load_symbols(path: str = DEFAULT_SYMBOLS) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_captions(paper: Optional[str] = None) -> List[str]:
    path = paper or paper_path()
    with open(path, "r", encoding="utf-8") as fh:
        return extract_captions(fh.read())


def _list_local_figures(folder: str) -> List[str]:
    if not os.path.isdir(folder):
        return []
    found: List[str] = []
    for entry in os.listdir(folder):
        path = os.path.join(folder, entry)
        if os.path.isfile(path) and os.path.splitext(entry)[1].lower() in _FIGURE_EXTS:
            found.append(os.path.abspath(path))
    return found


def _figures_for_paper(paper: Optional[str]) -> List[str]:
    """Raster files in the paper folder and its ``images/`` directory."""
    if not paper:
        return []
    abs_paper = os.path.abspath(paper)
    bundle = abs_paper if os.path.isdir(abs_paper) else os.path.dirname(abs_paper)
    found = _list_local_figures(bundle) + _list_local_figures(os.path.join(bundle, "images"))
    return list(dict.fromkeys(found))


def _captions_by_number(paper: Optional[str]) -> Dict[str, str]:
    if not paper or not os.path.isfile(paper):
        return {}
    with open(paper, "r", encoding="utf-8") as fh:
        text = fh.read()
    return {match.group(1): match.group(2).strip() for match in _FIG_CAPTION_RE.finditer(text)}


def _caption_for_figure(path: str, captions: Dict[str, str]) -> str:
    match = _FIG_NUM_RE.match(os.path.basename(path))
    if not match:
        return ""
    number = match.group(1)
    if number in captions:
        return captions[number]
    if number.isdigit():
        return captions.get(str(int(number)), "")
    return ""


def score_figure(path: str, extra: str = "") -> int:
    """Higher scores are better x-y comparison plots (IHTC vs pressure, P20, …)."""
    blob = f"{os.path.basename(path).replace('_', ' ')} {extra}"
    if _SKIP_FIG.search(blob):
        return -100
    return sum(weight for pattern, weight in _SCORE_PATTERNS if pattern.search(blob))


def choose_figure(path: Optional[str] = None, paper: Optional[str] = None) -> str:
    """Pick an explicit path, else the best comparison plot for ``paper``."""
    if path:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Figure not found: {path}")
        return path

    figures = _figures_for_paper(paper)
    if not figures:
        try:
            figures = target_figure_paths()
        except LookupError:
            figures = []
    if not figures:
        raise FileNotFoundError(
            "No plot image in the target paper bundle. Put figures in that folder's images/ directory."
        )

    captions = _captions_by_number(paper)
    ranked = sorted(
        figures,
        key=lambda p: (-score_figure(p, _caption_for_figure(p, captions)), os.path.basename(p).lower()),
    )
    return ranked[0]


def resolve_constants(
    tool: Optional[str],
    delta: float,
    captions: Optional[Sequence[str]] = None,
) -> Tuple[Optional[str], Dict[str, float]]:
    tools = list(available_tools() or [])
    chosen = tool
    if tools:
        chosen = tool if tool in tools else (DEFAULT_TOOL if DEFAULT_TOOL in tools else tools[0])
    kwargs: Dict[str, Any] = {"delta": delta}
    if chosen:
        kwargs["tool"] = chosen
    materials = list(available_materials() or [])
    blob = " ".join(captions or [])
    blanks = [name for name in materials if name.startswith("AA")]
    mentioned = [name for name in blanks if name.lower() in blob.lower()]
    material = mentioned[-1] if mentioned else None
    if material:
        kwargs["material"] = material
    elif DEFAULT_MATERIAL:
        kwargs["material"] = DEFAULT_MATERIAL
    coating = next(
        (
            name
            for name in materials
            if name in {"CrN", "TiN", "AlCrN", "WC-Co"} and name.lower() in blob.lower()
        ),
        None,
    )
    if coating:
        kwargs["coating"] = coating
    return chosen, get_constants(**kwargs)


def extras_from_captions(captions: Sequence[str]) -> Dict[str, float]:
    """Operating inputs the figure states but stage 03 does not tabulate."""
    blob = " ".join(captions or [])
    extras: Dict[str, float] = {}
    thick = re.search(r"(\d+(?:\.\d+)?)\s*mm", blob, re.I)
    if thick:
        extras["l"] = float(thick.group(1)) * 1e-3
    temp = re.search(r"(\d+(?:\.\d+)?)\s*°\s*C", blob)
    if temp:
        extras["T"] = float(temp.group(1)) + 273.15
    # Eq. 7 was OCR'd as sigma_U(T x)/sigma_U(T 6); T6 temper ⇒ x=6 ⇒ f=1.
    extras["x"] = 6.0
    return extras


def interpolate_to(x_src: np.ndarray, y_src: np.ndarray, x_dst: np.ndarray) -> np.ndarray:
    x_src = np.asarray(x_src, dtype=float)
    y_src = np.asarray(y_src, dtype=float)
    order = np.argsort(x_src)
    return np.interp(x_dst, x_src[order], y_src[order])


def curve_masks(
    figure: DigitizedFigure,
    paper: Series,
    y_pred: np.ndarray,
    thickness: int = 2,
) -> Tuple[np.ndarray, np.ndarray]:
    """Binary rasters of the digitized and predicted curves in plot-crop space."""
    h = max(int(round(figure.calib.height)), 1)
    w = max(int(round(figure.calib.width)), 1)
    origin = np.array([figure.calib.x0, figure.calib.y0], dtype=float)

    def draw(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        mask = np.zeros((h, w), dtype=np.uint8)
        pts = figure.calib.polyline_pixels(x, y).astype(float) - origin
        pts[:, 0] = np.clip(pts[:, 0], 0, w - 1)
        pts[:, 1] = np.clip(pts[:, 1], 0, h - 1)
        if len(pts) >= 2:
            cv2.polylines(mask, [pts.astype(np.int32)], False, 255, thickness)
        return mask

    return draw(paper.x, paper.y), draw(paper.x, y_pred)


def curve_ssim(true_mask: np.ndarray, pred_mask: np.ndarray) -> Optional[float]:
    if ssim_metric is None:
        return None
    if true_mask.size == 0 or pred_mask.size == 0:
        return None
    return float(ssim_metric(true_mask, pred_mask))


def mean_polyline_distance(y_pred: np.ndarray, y_true: np.ndarray) -> float:
    return float(np.nanmean(np.abs(np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float))))


def plot_comparison(
    figure: DigitizedFigure,
    results: Sequence[dict],
    out_dir: str,
    show: bool = True,
) -> List[str]:
    os.makedirs(out_dir, exist_ok=True)
    saved: List[str] = []
    x_title = axis_title(figure.x_label, figure.x_unit) or (figure.x_symbol or "x")
    y_title = axis_title(figure.y_label, figure.y_unit) or (figure.y_symbol or "y")

    fig, ax = plt.subplots(figsize=(8, 5))
    for row in results:
        ax.plot(row["x"], row["y_pred"], linewidth=2, label=f"{row['label']} (ExecuSci)")
        ax.plot(row["x"], row["y_paper"], linewidth=2, linestyle="--", label=f"{row['label']} (paper)")
    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title)
    ax.set_title(f"{y_title} vs {x_title}" if x_title or y_title else "Model vs paper")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path_cmp = os.path.join(out_dir, "compare.svg")
    fig.savefig(path_cmp)
    saved.append(path_cmp)

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    for row in results:
        ax2.plot(row["x"], row["error"], linewidth=2, label=row["label"])
    ax2.set_xlabel(x_title)
    ax2.set_ylabel("Percentage Error (%)")
    ax2.set_title("Error analysis")
    if len(results) > 1:
        ax2.legend()
    ax2.grid(True, alpha=0.3)
    fig2.tight_layout()
    path_err = os.path.join(out_dir, "error.svg")
    fig2.savefig(path_err)
    saved.append(path_err)

    if show:
        plt.show()
    else:
        plt.close("all")
    return saved


def _draw_dashed(
    image: np.ndarray,
    pts: np.ndarray,
    colour: Tuple[int, int, int],
    thickness: int = 2,
    dash: float = 8.0,
    gap: float = 6.0,
) -> None:
    """Draw a dashed polyline; OpenCV ``polylines`` is solid-only."""
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 2:
        return
    seg_on = True
    leftover = dash
    for start, end in zip(pts[:-1], pts[1:]):
        vec = end - start
        length = float(np.linalg.norm(vec))
        if length < 1e-6:
            continue
        direction = vec / length
        travelled = 0.0
        while travelled < length:
            step = min(leftover, length - travelled)
            p0 = start + direction * travelled
            p1 = start + direction * (travelled + step)
            if seg_on:
                cv2.line(
                    image,
                    (int(round(p0[0])), int(round(p0[1]))),
                    (int(round(p1[0])), int(round(p1[1]))),
                    colour,
                    thickness,
                    lineType=cv2.LINE_AA,
                )
            travelled += step
            leftover -= step
            if leftover <= 1e-9:
                seg_on = not seg_on
                leftover = dash if seg_on else gap


def overlay_predictions(
    figure: DigitizedFigure,
    results: Sequence[dict],
    out_dir: str,
) -> str:
    if figure.image_bgr is None:
        raise DigitizeError("Digitized figure has no image to overlay")
    overlay = figure.image_bgr.copy()
    colours = [(255, 0, 0), (255, 0, 255), (0, 255, 255), (0, 140, 255)]
    for i, row in enumerate(results):
        pts = figure.calib.polyline_pixels(row["x"], row["y_pred"])
        if len(pts) >= 2:
            _draw_dashed(overlay, pts, colours[i % len(colours)])
    path = os.path.join(out_dir, "overlay.png")
    cv2.imwrite(path, overlay)
    return path


def _series_delta(series: Series, fallback: float) -> float:
    if series.delta is not None:
        return float(series.delta)
    if re.search(r"\bdry\b", series.name, re.I):
        return 0.0
    return float(fallback)


def _series_label(series: Series, tool: Optional[str]) -> str:
    name = series.name.strip() or series.kind
    if tool and tool.lower() not in name.lower():
        return f"{tool}: {name}"
    return name


def run(
    figure_path: Optional[str] = None,
    symbols_path: str = DEFAULT_SYMBOLS,
    tool: Optional[str] = DEFAULT_TOOL,
    delta: float = DEFAULT_DELTA,
    eq_tag: Optional[str] = None,
    target: Optional[str] = None,
    x_symbol: Optional[str] = None,
    out_dir: str = DEFAULT_OUTPUT,
    show: bool = True,
    paper: Optional[str] = None,
) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    payload = load_symbols(symbols_path)
    graph = EquationGraph.from_json(payload)
    captions = load_captions(paper)
    extras = extras_from_captions(captions)
    image_path = choose_figure(figure_path, paper=paper)
    digitized = digitize_figure(
        image_path,
        symbols=payload.get("symbols") or {},
        captions=captions,
        tools=available_tools(),
    )
    artefact_paths = save_digitized(digitized, out_dir)

    y_symbol = target or digitized.y_symbol
    x_name = x_symbol or digitized.x_symbol
    if not y_symbol:
        raise LookupError(
            "Could not identify the y-axis symbol. Pass --target (e.g. --target h)."
        )
    if not x_name:
        raise LookupError(
            "Could not identify the x-axis symbol. Pass --x (e.g. --x P)."
        )

    system = graph.reduce(y_symbol=y_symbol, eq_tag=eq_tag)
    graph_path = os.path.join(out_dir, "equation_graph.svg")
    try:
        graph.plot(system, path=graph_path, show=False)
    except Exception:
        graph_path = None

    results: List[dict] = []
    ssim_scores: List[float] = []
    evaluate_error: Optional[str] = None
    for series in digitized.model_series():
        series_delta = _series_delta(series, delta)
        series_tool, consts = resolve_constants(
            series.tool or tool, series_delta, captions=captions
        )
        y_pred = graph.evaluate_curve(
            equations,
            consts,
            x_name,
            series.x,
            y_symbol=system.y_symbol,
            eq_tag=system.target.tag,
            extras=extras,
        )
        finite = np.isfinite(y_pred) & np.isfinite(series.y)
        if not np.any(finite):
            if evaluate_error is None and len(series.x):
                try:
                    graph.evaluate(
                        equations,
                        consts,
                        x_name,
                        float(series.x[0]),
                        y_symbol=system.y_symbol,
                        eq_tag=system.target.tag,
                        extras=extras,
                    )
                except Exception as exc:
                    evaluate_error = str(exc)
            continue
        x = series.x[finite]
        y_paper = series.y[finite]
        y_hat = y_pred[finite]
        err = percent_error(y_hat, y_paper)
        true_mask, pred_mask = curve_masks(digitized, series, y_pred)
        score = curve_ssim(true_mask, pred_mask)
        if score is not None:
            ssim_scores.append(score)
        results.append(
            {
                "label": _series_label(series, series_tool),
                "tool": series_tool,
                "delta": series_delta,
                "x": x,
                "y_pred": y_hat,
                "y_paper": y_paper,
                "error": err,
                "mean_abs_pct_error": float(np.mean(err)),
                "max_abs_pct_error": float(np.max(err)),
                "mean_polyline_distance": mean_polyline_distance(y_hat, y_paper),
                "ssim": score,
                "n_points": int(len(x)),
            }
        )

    if not results:
        detail = f": {evaluate_error}" if evaluate_error else ""
        raise RuntimeError(
            "Digitized the figure but could not evaluate any model series" + detail
        )

    plot_paths = plot_comparison(digitized, results, out_dir=out_dir, show=show)
    overlay_path = overlay_predictions(digitized, results, out_dir)

    primary = results[0]
    outputs = list(artefact_paths.values()) + plot_paths + [overlay_path]
    if graph_path:
        outputs.append(graph_path)

    summary = {
        "tool": primary["tool"],
        "delta": primary["delta"],
        "x_symbol": x_name,
        "y_symbol": system.y_symbol,
        "target_eq": system.target.tag,
        "reduced_eqs": system.tags,
        "x_label": digitized.x_label,
        "y_label": digitized.y_label,
        "n_points": primary["n_points"],
        "mean_abs_pct_error": primary["mean_abs_pct_error"],
        "max_abs_pct_error": primary["max_abs_pct_error"],
        "ssim": float(np.mean(ssim_scores)) if ssim_scores else None,
        "series": [
            {
                "label": row["label"],
                "tool": row["tool"],
                "delta": row["delta"],
                "n_points": row["n_points"],
                "mean_abs_pct_error": row["mean_abs_pct_error"],
                "max_abs_pct_error": row["max_abs_pct_error"],
                "mean_polyline_distance": row["mean_polyline_distance"],
                "ssim": row["ssim"],
            }
            for row in results
        ],
        "outputs": outputs,
        "figure": image_path,
    }
    summary_path = os.path.join(out_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")
    summary["outputs"] = outputs + [summary_path]
    return summary


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reduce equations to a target and compare against a paper figure."
    )
    parser.add_argument(
        "--figure",
        default=None,
        help="Plot image (default: image in the target paper's images/ folder)",
    )
    parser.add_argument("--symbols", default=DEFAULT_SYMBOLS, help="Stage 02 symbols.json")
    parser.add_argument("--paper", default=None, help="Markdown used for figure captions")
    parser.add_argument("--eq", dest="eq_tag", default=None, help="Paper equation tag to reduce from")
    parser.add_argument("--target", default=None, help="Dependent symbol (y-axis), e.g. h")
    parser.add_argument("--x", dest="x_symbol", default=None, help="Independent symbol (x-axis), e.g. P")
    tools = available_tools()
    tool_kwargs: Dict[str, Any] = {}
    if tools:
        tool_kwargs["choices"] = tools
    parser.add_argument(
        "--tool",
        default=DEFAULT_TOOL,
        help="Material / tool constants (default: scraped default)",
        **tool_kwargs,
    )
    parser.add_argument(
        "--delta",
        type=float,
        default=DEFAULT_DELTA,
        help=f"Fallback lubricant thickness in metres (default: {DEFAULT_DELTA})",
    )
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Directory for saved figures")
    parser.add_argument("--no-show", action="store_true", help="Save figures without opening a window")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run(
        figure_path=args.figure,
        symbols_path=args.symbols,
        tool=args.tool,
        delta=args.delta,
        eq_tag=args.eq_tag,
        target=args.target,
        x_symbol=args.x_symbol,
        out_dir=args.output,
        show=not args.no_show,
        paper=args.paper,
    )
    ssim_txt = f"{summary['ssim']:.3f}" if summary.get("ssim") is not None else "n/a"
    print(
        f"[{summary['tool']}] Eq. {summary['target_eq']}  "
        f"{summary['y_symbol']} vs {summary['x_symbol']}  "
        f"mean |err|={summary['mean_abs_pct_error']:.2f}%  "
        f"max |err|={summary['max_abs_pct_error']:.2f}%  "
        f"SSIM={ssim_txt}"
    )
    for path in summary["outputs"]:
        print(f"  wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
