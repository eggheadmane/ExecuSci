"""Locate the ExecuSci pipeline stage folders.

The stage folders carry a numeric prefix (``01 PDF2Latex``, ``02 Extract
Equations``, ...) that changes whenever a stage is inserted or reordered.
Modules therefore look folders up by their *name* -- ``stage_dir("Latex2Python")``
-- instead of hard-coding the prefix, and add them to ``sys.path`` with
:func:`add_stages`.

Stage scripts bootstrap this module with::

    import os, sys
    _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from execusci_paths import add_stages, stage_dir
"""

from __future__ import annotations

import os
import re
import sys
from typing import Dict, List, Optional

__all__ = [
    "ROOT",
    "stage_dir",
    "stage_dirs",
    "add_stages",
    "paper_path",
    "PAPER_NAME",
]

ROOT = os.path.dirname(os.path.abspath(__file__))

#: Default source document for the whole pipeline (lives in the PDF2Latex stage).
PAPER_NAME = "target_paper.md"

_PREFIX_RE = re.compile(r"^\s*\d+[\s._-]*")


def _strip_prefix(name: str) -> str:
    return _PREFIX_RE.sub("", name).strip()


def stage_dirs(root: str = ROOT) -> Dict[str, str]:
    """Map each stage's prefix-free lowercase name to its absolute path."""
    found: Dict[str, str] = {}
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if not os.path.isdir(path) or entry.startswith((".", "__")):
            continue
        found[_strip_prefix(entry).lower()] = path
    return found


def stage_dir(keyword: str, root: str = ROOT) -> str:
    """Return the absolute path of the stage folder named ``keyword``.

    The numeric prefix and case are ignored, so ``stage_dir("scrape
    constants")`` finds ``03 Scrape Constants``.  A unique partial match is
    accepted too (``stage_dir("plotting")``).
    """
    stages = stage_dirs(root)
    key = _strip_prefix(keyword).lower()
    if key in stages:
        return stages[key]
    partial = [path for name, path in stages.items() if key in name]
    if len(partial) == 1:
        return partial[0]
    known = ", ".join(sorted(stages)) or "<none>"
    if partial:
        raise LookupError(f"Stage {keyword!r} is ambiguous; candidates: {known}")
    raise LookupError(f"No stage folder matching {keyword!r}. Known stages: {known}")


def add_stages(*keywords: str, root: str = ROOT) -> List[str]:
    """Put the named stage folders (and the repo root) on ``sys.path``."""
    added: List[str] = []
    for path in (root, *(stage_dir(k, root) for k in keywords)):
        if path not in sys.path:
            sys.path.insert(0, path)
        added.append(path)
    return added


def paper_path(name: Optional[str] = None, root: str = ROOT) -> str:
    """Absolute path of a source document inside the PDF2Latex stage."""
    return os.path.join(stage_dir("PDF2Latex", root), name or PAPER_NAME)
