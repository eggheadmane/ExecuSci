"""ExecuSci -- LaTeX equation to Python translator (command line entry point).

Examples
--------
Translate a single equation given on the command line::

    python main.py --latex "h=1.45 k \\frac{\\tan \\theta}{\\sigma}\\left(\\frac{p}{H}\\right)^{0.985}"

Translate every equation found in a document and print them::

    python main.py "markdown equation.md"

Translate a document and write a runnable Python module of functions::

    python main.py "markdown equation.md" --module equations.py

If no arguments are given, it runs on ``markdown equation.md`` when present.
"""

from __future__ import annotations

import argparse
import os
import sys

from latex2python import (
    LatexParseError,
    generate_module,
    translate,
    translate_document,
)

DEFAULT_DOC = "markdown equation.md"


def _print_equation(eq, tag=None):
    label = f"Eq. {tag}" if tag else "Equation"
    print(f"[{label}]")
    print(f"  LaTeX : {eq.latex}")
    print(f"  Python: {eq.python}")
    if eq.inputs:
        print(f"  Inputs: {', '.join(s.name for s in eq.inputs)}")
    print()


def run_single(latex: str) -> int:
    try:
        eq = translate(latex)
    except LatexParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    _print_equation(eq)
    print("Generated function:\n")
    print(eq.function_source())
    return 0


def run_document(path: str, module_path: str | None) -> int:
    if not os.path.exists(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    results = translate_document(text)
    if not results:
        print(f"No equations found in {path}.")
        return 0

    ok = 0
    for raw, eq, error in results:
        if eq is None:
            print(f"[Eq. {raw.tag}]  COULD NOT TRANSLATE")
            print(f"  LaTeX : {raw.latex}")
            print(f"  Reason: {error}\n")
            continue
        ok += 1
        _print_equation(eq, tag=raw.tag)

    print(f"Translated {ok}/{len(results)} equations from {path}.")

    if module_path:
        source = generate_module(
            text, module_doc=f"Executable equations extracted from {os.path.basename(path)}."
        )
        with open(module_path, "w", encoding="utf-8") as fh:
            fh.write(source)
        print(f"Wrote runnable module to {module_path}.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Translate LaTeX mathematical equations into Python.",
    )
    parser.add_argument(
        "document",
        nargs="?",
        help="Path to a .tex/.md document containing equations.",
    )
    parser.add_argument(
        "--latex",
        help="Translate a single LaTeX equation passed directly on the command line.",
    )
    parser.add_argument(
        "--module",
        metavar="OUTPUT.py",
        help="Write a runnable Python module of functions for a document.",
    )
    args = parser.parse_args(argv)

    if args.latex:
        return run_single(args.latex)

    path = args.document or DEFAULT_DOC
    if not args.document and not os.path.exists(DEFAULT_DOC):
        parser.print_help()
        return 0
    return run_document(path, args.module)


if __name__ == "__main__":
    raise SystemExit(main())
