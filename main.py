"""ExecuSci -- translate LaTeX equations and scrape constants from a document.

Reads a Mathpix / markdown paper, prints each translated equation, and writes
runnable modules for both equations and scraped constants automatically.
"""

import os
import sys

from latex2python import generate_module, translate_document
from scrape_constants import extract_constants, generate_constants_module

DEFAULT_DOC = "test_eq.md"
DEFAULT_MODULE = "test_equations.py"
DEFAULT_CONSTANTS = "constants.py"


def _print_equation(eq, tag=None):
    label = f"Eq. {tag}" if tag else "Equation"
    print(f"[{label}]")
    print(f"  LaTeX : {eq.latex}")
    print(f"  Python: {eq.python}")
    if eq.inputs:
        print(f"  Inputs: {', '.join(s.name for s in eq.inputs)}")
    print()


def _print_constants(constants) -> None:
    if not constants:
        print("No constants scraped.")
        return
    print(f"Scraped {len(constants)} constant(s):")
    for c in constants:
        where = f"Table {c.table}" if c.table else c.source
        variant = f" [{c.variant}]" if c.variant else ""
        print(f"  {c.name}{variant} = {c.value}  ({where})")
    print()


def run_document(
    path: str,
    module_path: str = DEFAULT_MODULE,
    constants_path: str = DEFAULT_CONSTANTS,
) -> int:
    if not os.path.exists(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    results = translate_document(text)
    if not results:
        print(f"No equations found in {path}.")
    else:
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

        source = generate_module(
            text,
            module_doc=f"Executable equations extracted from {os.path.basename(path)}.",
        )
        with open(module_path, "w", encoding="utf-8") as fh:
            fh.write(source)
        print(f"Wrote runnable module to {module_path}.")

    constants = extract_constants(text)
    _print_constants(constants)
    if constants:
        const_src = generate_constants_module(
            text,
            module_doc=f"Constants scraped from {os.path.basename(path)}.",
        )
        with open(constants_path, "w", encoding="utf-8") as fh:
            fh.write(const_src)
        print(f"Wrote constants module to {constants_path}.")

    return 0


def main() -> int:
    return run_document(DEFAULT_DOC, DEFAULT_MODULE, DEFAULT_CONSTANTS)


if __name__ == "__main__":
    raise SystemExit(main())
