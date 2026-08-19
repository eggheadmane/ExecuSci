"""Locate the ExecuSci pipeline stage folders.

The stage folders carry a numeric prefix (``02 Extract Equations``,
``03 Scrape Constants``, ...) that changes whenever a stage is inserted or
reordered.  Modules therefore look folders up by their *name* --
``stage_dir("Latex2Python")`` -- instead of hard-coding the prefix, and add
them to ``sys.path`` with :func:`add_stages`.

Runnable source lives under ``build/`` in the same numbered folders.  Papers
live in ``input/``; the default paper is whichever markdown/LaTeX file sits
in ``input/target/`` (any filename).  Generated outputs live under
``generated/``.  This module lives in ``build/``, so :data:`ROOT` is the
parent of that folder.

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
    "INPUT",
    "TARGET",
    "stage_dir",
    "stage_dirs",
    "add_stages",
    "paper_path",
    "target_figure_paths",
]

BUILD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD)

#: Folder holding generated stage outputs (equations.md, constants.py, ...).
GENERATED = os.path.join(ROOT, "generated")

#: Papers: extras live directly in ``input/``; the default paper is in ``target/``.
INPUT = os.path.join(ROOT, "input")
TARGET = os.path.join(INPUT, "target")

_PAPER_EXTS = {".md", ".tex"}
_FIGURE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

#: Numbered stage folders only, e.g. ``02 Extract Equations``.  Excludes
#: ``build/``, ``test/``, ``input/``, ``generated/``, ``legacy_code/``.
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

    With no ``root``, generated outputs are sought under :data:`GENERATED`
    (and numbered leftovers at the repo root, if any).
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


def _list_papers(folder: str) -> List[str]:
    """Basenames of markdown/LaTeX files directly inside ``folder``."""
    if not os.path.isdir(folder):
        return []
    found: List[str] = []
    for entry in os.listdir(folder):
        path = os.path.join(folder, entry)
        if os.path.isfile(path) and os.path.splitext(entry)[1].lower() in _PAPER_EXTS:
            found.append(entry)
    return sorted(found)


def paper_path(name: Optional[str] = None, root: Optional[str] = None) -> str:
    """Absolute path of a source document.

    With no ``name``, returns the single markdown/LaTeX file in
    :data:`TARGET` (any filename).  Drop a different paper into that folder
    to switch the default without renaming it.

    With ``name``, looks in :data:`INPUT` first (e.g. ``Sample Paper 2.md``),
    then in :data:`TARGET`.  ``root`` is unused and kept for call-site
    compatibility.
    """
    del root  # papers are no longer looked up as a numbered stage folder
    if name is None:
        papers = _list_papers(TARGET)
        if not papers:
            raise LookupError(
                f"No markdown/LaTeX paper in {TARGET}. "
                "Put the file you want to run into that folder (any name)."
            )
        if len(papers) > 1:
            raise LookupError(
                f"Expected one paper in {TARGET}, found: {', '.join(papers)}. "
                "Leave only the file you want to run."
            )
        return os.path.join(TARGET, papers[0])

    if os.path.isabs(name) and os.path.exists(name):
        return name
    for folder in (INPUT, TARGET):
        candidate = os.path.join(folder, name)
        if os.path.exists(candidate):
            return candidate
    return os.path.join(INPUT, name)


def target_figure_paths() -> List[str]:
    """Absolute paths of raster figures sitting in :data:`TARGET`.

    Stage 05 compares the reduced model against these images.  Markdown/LaTeX
    papers are ignored; any ``.jpg``/``.png``/``.webp`` (and similar) counts.
    """
    if not os.path.isdir(TARGET):
        return []
    found: List[str] = []
    for entry in sorted(os.listdir(TARGET)):
        path = os.path.join(TARGET, entry)
        if os.path.isfile(path) and os.path.splitext(entry)[1].lower() in _FIGURE_EXTS:
            found.append(path)
    return found
