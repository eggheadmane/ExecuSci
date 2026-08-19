"""Run the whole ExecuSci pipeline on one paper.

    01 src/01_input/target      the paper as Mathpix markdown (input)
      -> 02_extract_equations   equations.md + symbols.json
      -> 03_scrape_constants    constants.py (+ constants.md under log/)
      -> 04_latex2python        equations.py
      -> 05_plotting            figures comparing the model to the paper (optional)

Usage::

    python src/run_pipeline.py
    python src/run_pipeline.py --paper src/01_input/sample_2.md
    python src/run_pipeline.py --plot
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional, Sequence

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from execusci_paths import add_stages, paper_path, stage_dir  # noqa: E402

add_stages("Extract Equations", "Scrape Constants", "Latex2Python")

import extract_equations  # noqa: E402
import scrape_constants  # noqa: E402
import translate_equations  # noqa: E402


def _banner(step: int, title: str) -> None:
    print()
    print(f"=== Stage {step:02d}: {title} " + "=" * max(0, 46 - len(title)))


def run(paper: Optional[str] = None, plot: bool = False, quiet: bool = True) -> int:
    """Run every stage in order; returns a process exit code."""
    path = paper or paper_path()
    if not os.path.exists(path):
        print(f"Error: paper not found: {path}", file=sys.stderr)
        return 1

    _banner(2, "Extract equations")
    extraction = extract_equations.run(paper=path)

    _banner(3, "Scrape constants")
    scrape_constants.run(paper=path)

    _banner(4, "Translate equations to Python")
    equations_md = os.path.join(
        stage_dir("Extract Equations"), "output", extract_equations.EQUATIONS_FILENAME
    )
    status = translate_equations.run_document(equations_md, verbose=not quiet)

    if plot:
        _banner(5, "Compare against the paper's curves")
        add_stages("Plotting")
        import plot_compare  # noqa: E402  (optional: needs matplotlib/pandas)

        summary = plot_compare.run(show=False, paper=path)
        ssim_txt = (
            f"{summary['ssim']:.3f}" if summary.get("ssim") is not None else "n/a"
        )
        print(
            f"[{summary['tool']}] Eq. {summary.get('target_eq')}  "
            f"{summary.get('y_symbol')} vs {summary.get('x_symbol')}  "
            f"mean |err|={summary['mean_abs_pct_error']:.2f}%  "
            f"max |err|={summary['max_abs_pct_error']:.2f}%  "
            f"SSIM={ssim_txt}"
        )

    print()
    if extraction.failed or status != 0:
        print("Pipeline finished with unresolved equations -- see the output above.")
        return 1
    print("Pipeline complete.")
    return 0


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ExecuSci pipeline end to end.")
    parser.add_argument(
        "--paper",
        default=None,
        help="Paper markdown to process (default: the file in src/01_input/target/)",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Also run stage 05 (requires matplotlib and pandas).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print every translated equation, not just the summary.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    return run(paper=args.paper, plot=args.plot, quiet=not args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
