"""Stage 04 -- turn the extracted equations into an executable Python module.

Reads ``02 Extract Equations/output/equations.md`` (falling back to the paper
itself if that stage has not been run), translates every equation with
``latex2python`` and writes ``equations.py`` into the Latex2Python stage folder.
The symbol dictionary from stage 02 is used to document each generated
function's arguments in the paper's own words.

Run it with::

    python "build/04 Latex2Python/translate_equations.py"
    python "build/04 Latex2Python/translate_equations.py" --source "01 PDF2Latex/target_paper.md"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Optional, Sequence

_BUILD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BUILD not in sys.path:
    sys.path.insert(0, _BUILD)

from execusci_paths import add_stages, paper_path, stage_dir  # noqa: E402

add_stages("Latex2Python")

from latex2python import generate_module, translate_document  # noqa: E402

DEFAULT_MODULE = os.path.join(stage_dir("Latex2Python"), "equations.py")
_EXTRACTED = os.path.join(stage_dir("Extract Equations"), "output")
DEFAULT_SOURCE = os.path.join(_EXTRACTED, "equations.md")
DEFAULT_SYMBOLS = os.path.join(_EXTRACTED, "symbols.json")


def load_symbol_dictionary(path: str = DEFAULT_SYMBOLS) -> dict:
    """Stage 02's ``symbols.json``, or ``{}`` if that stage has not run."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def descriptions_from(dictionary: dict) -> Dict[str, str]:
    """``name -> description`` for every symbol the paper describes."""
    return {
        name: info["description"]
        for name, info in dictionary.get("symbols", {}).items()
        if info.get("description")
    }


def load_descriptions(path: str = DEFAULT_SYMBOLS) -> Dict[str, str]:
    """``name -> description`` from stage 02, or ``{}`` if it has not run."""
    return descriptions_from(load_symbol_dictionary(path))


def _print_equation(eq, tag=None) -> None:
    label = f"Eq. {tag}" if tag else "Equation"
    print(f"[{label}]")
    print(f"  LaTeX : {eq.latex}")
    print(f"  Python: {eq.python}")
    if eq.inputs:
        print(f"  Inputs: {', '.join(s.name for s in eq.inputs)}")
    print()


def run_document(
    path: str = DEFAULT_SOURCE,
    module_path: str = DEFAULT_MODULE,
    symbols_path: str = DEFAULT_SYMBOLS,
    verbose: bool = True,
) -> int:
    """Translate every equation in ``path`` and write the equations module."""
    if not os.path.exists(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    results = translate_document(text)
    if not results:
        print(f"No equations found in {path}.")
        return 1

    ok = 0
    for raw, eq, error in results:
        if eq is None:
            print(f"[Eq. {raw.tag}]  COULD NOT TRANSLATE")
            print(f"  LaTeX : {raw.latex}")
            print(f"  Reason: {error}\n")
            continue
        ok += 1
        if verbose:
            _print_equation(eq, tag=raw.tag)

    dictionary = load_symbol_dictionary(symbols_path)
    descriptions = descriptions_from(dictionary)
    origin = dictionary.get("source") or os.path.basename(path)
    source = generate_module(
        text,
        module_doc=f"Executable equations extracted from {origin}.",
        descriptions=descriptions,
    )
    with open(module_path, "w", encoding="utf-8") as fh:
        fh.write(source)

    print(f"Translated {ok}/{len(results)} equations from {os.path.basename(path)}.")
    if descriptions:
        print(f"Documented arguments using {len(descriptions)} symbol descriptions.")
    print(f"Wrote runnable module to {module_path}.")
    return 0 if ok == len(results) else 1


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate extracted LaTeX equations into a Python module."
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help=f"Document holding the equations (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--module",
        default=DEFAULT_MODULE,
        help=f"Generated module path (default: {DEFAULT_MODULE})",
    )
    parser.add_argument(
        "--symbols",
        default=DEFAULT_SYMBOLS,
        help="Stage 02 symbol dictionary used to document arguments.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print the summary, not every translated equation.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    source = args.source
    if not os.path.exists(source) and source == DEFAULT_SOURCE:
        print(
            f"{os.path.basename(source)} not found -- run stage 02 first. "
            "Falling back to the paper itself.",
            file=sys.stderr,
        )
        source = paper_path()
    return run_document(
        source,
        module_path=args.module,
        symbols_path=args.symbols,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    raise SystemExit(main())
