"""Locate the ExecuSci pipeline stage folders.

The stage folders carry a numeric prefix (``01_input``, ``02_extract_equations``,
...) that changes whenever a stage is inserted or reordered.  Modules therefore
look folders up by their *name* -- ``stage_dir("translate2python")`` -- instead of
hard-coding the prefix, and add them to ``sys.path`` with :func:`add_stages`.

Runnable source and the artefacts later stages import live under ``src/`` in
the numbered folders.  Papers live in ``src/01_input/``; the default paper is
whichever markdown/LaTeX file sits in ``src/01_input/target/`` (any filename).
Every generated artefact is also copied under ``log/`` (including duplicates
of files that stay in ``src/`` so later stages can import them).  This module
lives in ``src/``, so :data:`ROOT` is the parent of that folder.

Stage scripts (e.g.) bootstrap this module with::

    import os, sys
    _SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _SRC not in sys.path:
        sys.path.insert(0, _SRC)
    from execusci_paths import add_stages, stage_dir
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from typing import Dict, List, Optional

# Can remove - only serves as additional feature
__all__ = [
    "SRC",
    "ROOT",
    "LOG",
    "INPUT",
    "TARGET",
    "stage_dir",
    "stage_dirs",
    "mirror_to_log",
    "add_stages",
    "paper_path",
    "target_figure_paths",
]

SRC = os.path.dirname(os.path.abspath(__file__))    # SRC is /src folder
ROOT = os.path.dirname(SRC)     # ROOT is parent of /src folder

#: Full copy of every generated artefact (including files also kept in ``src/``).
LOG = os.path.join(ROOT, "log")

_PAPER_EXTS = {".md", ".mmd"}   # Markdown or Mathpix markdown
_FIGURE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

#: Numbered stage folders only, e.g. ``02_extract_equations``.
_STAGE_DIR_RE = re.compile(r"^\d{2}[\s._-]")
_PREFIX_RE = re.compile(r"^\s*\d+[\s._-]*")
_SEP_RE = re.compile(r"[\s._-]+")       # Separators to fold to ``_`` in normalised names


'''Find the stage directory'''

def _normalise(name: str) -> str:
    """Prefix-free lowercase name with spaces and hyphens folded to ``_``."""
    prefix_free = _PREFIX_RE.sub("", name).strip().lower()
    return _SEP_RE.sub("_", prefix_free).strip("_")     #.strip removes leading/trailing underscores


def stage_dirs(root: str = SRC) -> Dict[str, str]:
    """Map each stage's prefix-free lowercase name to its absolute path."""
    found: Dict[str, str] = {}

    # If src is not a directory, return an empty dictionary
    if not os.path.isdir(root):
        return found

    # Match each entry in the root directory against the _STAGE_DIR_RE regex pattern. 
    # If it matches, add it to the found dictionary with the normalised name as the key and the absolute path as the value.
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if not os.path.isdir(path) or not _STAGE_DIR_RE.match(entry):
            continue
        found[_normalise(entry)] = path
    return found


def stage_dir(keyword: str, root: Optional[str] = None) -> str:
    """Return the absolute path of the stage folder named ``keyword``.

    The numeric prefix, case, and spaces vs underscores are ignored, so
    ``stage_dir("scrape constants")`` finds ``03_scrape_constants``.  A unique
    partial match is accepted too (``stage_dir("plotting")``).  Pass
    ``root=SRC`` (the default) to look under ``src/``.
    """
    stages = stage_dirs(SRC if root is None else root)
    key = _normalise(keyword)
    # If the key is in the stages dictionary, return the corresponding path
    if key in stages:
        return stages[key]

    # If the key is not in the stages dictionary, look for partial matches by checking if the key is a substring of any of the stage names.
    partial = [path for name, path in stages.items() if key in name]
    # If there is exactly one partial match, return the corresponding path. 
    if len(partial) == 1:
        return partial[0]
    # If there are multiple partial matches, raise a LookupError indicating that the stage is ambiguous. 
    known = ", ".join(sorted(stages)) or "<none>"
    if partial:
        raise LookupError(f"Stage {keyword!r} is ambiguous; candidates: {known}")

    # If there are no partial matches, raise a LookupError indicating that no stage folder matching the keyword was found.
    raise LookupError(f"No stage folder matching {keyword!r}. Known stages: {known}")


def mirror_to_log(path: str) -> Optional[str]:
    """Copy ``path`` from ``src/`` to the same relative location under ``log/``."""
    try:
        rel = os.path.relpath(os.path.abspath(path), SRC)
    except ValueError:
        return None
    if rel.startswith("..") or os.path.isabs(rel):
        return None
    dest = os.path.join(LOG, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(path, dest)
    return dest

'''Add stage files to sys.path so that modules can be imported around'''

def add_stages(*keywords: str, root: Optional[str] = None) -> List[str]:
    """Put the named ``src/`` stage folders on ``sys.path``.

    Each keyword is looked up under :data:`SRC` (runnable source and the
    artefacts later stages import).  An extra ``root`` is searched as well.
    Missing matches are skipped.
    """
    added: List[str] = []
    bases: List[str] = [SRC]
    
    # root is additional directory to look at. If it is not the same as \src then add to bases
    if root is not None and os.path.abspath(root) != os.path.abspath(SRC):
        bases.append(root)
    paths = [SRC]
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


'''Find papers (md files) in folder'''

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

'''Hard code input folder, and under that the target folder'''
INPUT = os.path.join(SRC, "01_input")
#: Papers: extras live directly in ``01_input/``; the default paper is in ``target/``.
TARGET = os.path.join(INPUT, "target")


def paper_path(name: Optional[str] = None) -> str:
    """Absolute path of a source document.

    With no ``name``, returns the single markdown/LaTeX file in
    :data:`TARGET` (any filename).  Drop a different paper into that folder
    to switch the default without renaming it.

    With ``name``, looks in :data:`INPUT` first (e.g. ``sample_2.md``),
    then in :data:`TARGET`.
    """
    # If no specific paper is given --> Look into target folder
    # Error when there is 0 papers or more than 1 paper
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

    # If given the file path in CLI
    if os.path.exists(name):
        return os.path.abspath(name)
    
    # If given just a file name --> Look in input and target folders
    for folder in (INPUT, TARGET):
        candidate = os.path.join(folder, name)
        if os.path.exists(candidate):
            return candidate
    
    # If you still can't find the file, just say that it's in the input folder and let the error happen later on
    return os.path.join(INPUT, name)


''' For figures '''
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