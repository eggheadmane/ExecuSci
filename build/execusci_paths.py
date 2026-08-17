"""Locate the ExecuSci pipeline stage folders.

The stage folders carry a numeric prefix (``01 PDF2Latex``, ``02 Extract
Equations``, ...) that changes whenever a stage is inserted or reordered.
Modules therefore look folders up by their *name* -- ``stage_dir("Latex2Python")``
-- instead of hard-coding the prefix, and add them to ``sys.path`` with
:func:`add_stages`.

Runnable source lives under ``build/`` in the same numbered folders.  Papers
stay in ``01 PDF2Latex`` at the repo root; generated outputs for later stages
live under ``generated/``.  This module lives in ``build/``, so :data:`ROOT`
is the parent of that folder.

Stage scripts bootstrap this module with::

    import os, sys
    _BUILD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _BUILD not in sys.path:
        sys.path.insert(0, _BUILD)
    from execusci_paths import add_stages, stage_dir
"""

from __future__ import annotations

import os
import re
import sys
from typing import Dict, List, Optional, Sequence

__all__ = [
    "BUILD",
    "ROOT",
    "GENERATED",
    "stage_dir",
    "stage_dirs",
    "add_stages",
    "paper_path",
    "PAPER_NAME",
]

BUILD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD)

#: Folder holding generated stage outputs (equations.md, constants.py, ...).
GENERATED = os.path.join(ROOT, "generated")

#: Default source document for the whole pipeline (lives in the PDF2Latex stage).
PAPER_NAME = "target_paper.md"

#: Numbered stage folders only, e.g. ``01 PDF2Latex``.  Excludes ``build/``,
#: ``test/``, ``generated/``, ``legacy_code/``, and year-prefixed archives.
_STAGE_DIR_RE = re.compile(r"^\d{2}[\s._-]")
_PREFIX_RE = re.compile(r"^\s*\d+[\s._-]*")


def _strip_prefix(name: str) -> str:
    return _PREFIX_RE.sub("", name).strip()


def io_roots() -> List[str]:
    """Directories that may hold papers and generated stage outputs."""
    roots = [ROOT]
    if os.path.isdir(GENERATED) and os.path.abspath(GENERATED) != os.path.abspath(ROOT):
        roots.append(GENERATED)
    return roots


def stage_dirs(root: str = ROOT) -> Dict[str, str]:
    """Map each stage's prefix-free lowercase name to its absolute path."""
    found: Dict[str, str] = {}
    if not os.path.isdir(root):
        return found
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if not os.path.isdir(path) or not _STAGE_DIR_RE.match(entry):
            continue
        found[_strip_prefix(entry).lower()] = path
    return found


def stage_dir(keyword: str, root: Optional[str] = None) -> str:
    """Return the absolute path of the stage folder named ``keyword``.

    The numeric prefix and case are ignored, so ``stage_dir("scrape
    constants")`` finds ``03 Scrape Constants``.  A unique partial match is
    accepted too (``stage_dir("plotting")``).  Pass ``root=BUILD`` to find
    the matching source folder under ``build/``.

    With no ``root``, papers are sought at the repo root and generated
    outputs under :data:`GENERATED`.
    """
    bases: Sequence[str] = (root,) if root is not None else io_roots()
    last_error: Optional[LookupError] = None
    for base in bases:
        try:
            return _stage_dir_in(keyword, base)
        except LookupError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def _stage_dir_in(keyword: str, root: str) -> str:
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


def add_stages(*keywords: str, root: Optional[str] = None) -> List[str]:
    """Put the named source (``build/``) and output folders on ``sys.path``.

    Each keyword is looked up first under :data:`BUILD` (runnable source) and
    then under the I/O roots (repo root and :data:`GENERATED`) so generated
    artefacts such as ``equations.py`` resolve.  Missing matches are skipped.
    """
    added: List[str] = []
    bases: List[str] = [BUILD]
    if root is not None:
        bases.append(root)
    else:
        bases.extend(io_roots())
    paths = [BUILD]
    for keyword in keywords:
        for base in bases:
            try:
                paths.append(stage_dir(keyword, root=base))
            except LookupError:
                continue
    for path in paths:
        if path not in sys.path:
            sys.path.insert(0, path)
        added.append(path)
    return added


def paper_path(name: Optional[str] = None, root: Optional[str] = None) -> str:
    """Absolute path of a source document inside the PDF2Latex stage."""
    return os.path.join(stage_dir("PDF2Latex", root), name or PAPER_NAME)
