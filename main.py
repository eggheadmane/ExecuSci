"""ExecuSci -- translate LaTeX equations from a markdown document into Python.

Reads ``markdown equation.md``, prints each translated equation, and writes a
runnable module to ``equations.py``.
"""

import os
import sys

from latex2python import generate_module, translate_document

# DEFAULT_DOC = "markdown equation.md"
DEFAULT_DOC = "test_eq.md"
DEFAULT_MODULE = "test_equations.py"


def _print_equation(eq, tag=None):
    label = f"Eq. {tag}" if tag else "Equation"
    print(f"[{label}]")
    print(f"  LaTeX : {eq.latex}")
    print(f"  Python: {eq.python}")
    if eq.inputs:
        print(f"  Inputs: {', '.join(s.name for s in eq.inputs)}")
    print()


def run_document(path: str, module_path: str) -> int:
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

    source = generate_module(
        text, module_doc=f"Executable equations extracted from {os.path.basename(path)}."
    )
    with open(module_path, "w", encoding="utf-8") as fh:
        fh.write(source)
    print(f"Wrote runnable module to {module_path}.")
    return 0


def main() -> int:
    return run_document(DEFAULT_DOC, DEFAULT_MODULE)


if __name__ == "__main__":
    raise SystemExit(main())
