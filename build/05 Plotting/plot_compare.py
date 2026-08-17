"""Stage 05 -- compare the translated IHTC model against digitized paper curves.

Evaluates the Eq. 6 chain from stage 04's ``equations.py`` (h = h_a + h_c + h_l)
with stage 03's scraped constants over contact pressure, and overlays the result
on the paper's P20 IHTC curve.

Usage
-----
    python "build/05 Plotting/plot_compare.py"
    python "build/05 Plotting/plot_compare.py" --tool P20 --delta 1.5e-5
    python "build/05 Plotting/plot_compare.py" --no-show
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Generated equations / scraped constants live in the numbered stage folders.
_BUILD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BUILD not in sys.path:
    sys.path.insert(0, _BUILD)

from execusci_paths import BUILD, add_stages, stage_dir  # noqa: E402

add_stages("Latex2Python", "Scrape Constants")

import equations  # noqa: E402
from constants import (  # noqa: E402
    DEFAULT_DELTA,
    DEFAULT_TOOL,
    available_tools,
    get_constants,
)

DEFAULT_DATA = os.path.join(stage_dir("Plotting", root=BUILD), "data", "p20.csv")
DEFAULT_OUTPUT = os.path.join(stage_dir("Plotting"), "output")


def load_paper_curve(path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load digitized paper data: columns P (MPa), h (kW/m²K)."""
    df = pd.read_csv(path, header=None, names=["P", "h"])
    P = pd.to_numeric(df["P"], errors="coerce").to_numpy(dtype=float)
    h = pd.to_numeric(df["h"], errors="coerce").to_numpy(dtype=float)
    mask = np.isfinite(P) & np.isfinite(h)
    return P[mask], h[mask]


def compute_h(P: float, consts: Dict[str, float]) -> float:
    """Evaluate the translated Eq. 6 chain at a single pressure."""
    K_st = equations.eq_8(consts["k_s"], consts["k_t"])
    R = equations.eq_9(consts["R_s"], consts["R_t"])
    N_P = equations.eq_10(P, consts["lamda"], consts["sigma_U"])
    h_c = equations.eq_7(K_st, N_P, R, consts["alpha"])

    K_stl = equations.eq_12(consts["k_l"], consts["k_s"], consts["k_t"])
    N_L = equations.eq_13(consts["delta"], consts["gamma"])
    h_l = equations.eq_11(K_stl, N_L, R, consts["beta"])

    return float(equations.eq_6(consts["h_a"], h_c, h_l))


def predict_curve(P: Sequence[float], consts: Dict[str, float]) -> np.ndarray:
    """Vector of predicted IHTC values for each pressure in ``P``."""
    return np.array([compute_h(float(p), consts) for p in P], dtype=float)


def percent_error(y_pred: np.ndarray, y_true: np.ndarray) -> np.ndarray:
    y_pred = np.asarray(y_pred, dtype=float)
    y_true = np.asarray(y_true, dtype=float)
    return np.abs((y_pred - y_true) / y_true) * 100.0


def plot_comparison(
    P: np.ndarray,
    h_pred: np.ndarray,
    h_paper: np.ndarray,
    tool: str,
    out_dir: str,
    show: bool = True,
) -> List[str]:
    """Save comparison and error plots; return paths of written files."""
    os.makedirs(out_dir, exist_ok=True)
    saved: List[str] = []

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(P, h_pred, label="h from ExecuSci", linewidth=2)
    ax.plot(P, h_paper, label="h from paper", linewidth=2)
    ax.set_xlabel("Contact Pressure (MPa)")
    ax.set_ylabel("IHTC (kW/m²K)")
    ax.set_title(f"IHTC vs Contact Pressure ({tool})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path_cmp = os.path.join(out_dir, f"ihtc_compare_{tool}.svg")
    fig.savefig(path_cmp)
    saved.append(path_cmp)

    err = percent_error(h_pred, h_paper)
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(P, err, linewidth=2)
    ax2.set_xlabel("Contact Pressure (MPa)")
    ax2.set_ylabel("Percentage Error (%)")
    ax2.set_title(f"Error Analysis ({tool})")
    ax2.grid(True, alpha=0.3)
    fig2.tight_layout()
    path_err = os.path.join(out_dir, f"ihtc_error_{tool}.svg")
    fig2.savefig(path_err)
    saved.append(path_err)

    if show:
        plt.show()
    else:
        plt.close("all")

    return saved


def run(
    data_path: str = DEFAULT_DATA,
    tool: str = DEFAULT_TOOL,
    delta: float = DEFAULT_DELTA,
    out_dir: str = DEFAULT_OUTPUT,
    show: bool = True,
) -> dict:
    consts = get_constants(tool=tool, delta=delta)
    P, h_paper = load_paper_curve(data_path)
    h_pred = predict_curve(P, consts)
    paths = plot_comparison(P, h_pred, h_paper, tool=tool, out_dir=out_dir, show=show)

    err = percent_error(h_pred, h_paper)
    summary = {
        "tool": tool,
        "delta": delta,
        "n_points": int(len(P)),
        "mean_abs_pct_error": float(np.mean(err)),
        "max_abs_pct_error": float(np.max(err)),
        "outputs": paths,
    }
    return summary


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot translated IHTC equations against the paper curve."
    )
    parser.add_argument(
        "--data",
        default=DEFAULT_DATA,
        help=f"CSV of digitized paper curve (default: {DEFAULT_DATA})",
    )
    parser.add_argument(
        "--tool",
        default=DEFAULT_TOOL,
        choices=available_tools(),
        help=f"Tool material constants (default: {DEFAULT_TOOL})",
    )
    parser.add_argument(
        "--delta",
        type=float,
        default=DEFAULT_DELTA,
        help=f"Lubricant film thickness δ in metres (default: {DEFAULT_DELTA})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Directory for saved figures (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Save figures without opening an interactive window.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run(
        data_path=args.data,
        tool=args.tool,
        delta=args.delta,
        out_dir=args.output,
        show=not args.no_show,
    )
    print(
        f"[{summary['tool']}] n={summary['n_points']}  "
        f"mean |err|={summary['mean_abs_pct_error']:.2f}%  "
        f"max |err|={summary['max_abs_pct_error']:.2f}%"
    )
    for path in summary["outputs"]:
        print(f"  wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
