"""Locate the ExecuSci pipeline stage folders.

The stage folders carry a numeric prefix (``01_input``, ``02_extract_equations``,
...) that changes whenever a stage is inserted or reordered.  Modules therefore
look folders up by their *name* -- ``stage_dir("translate2python")`` -- instead of
hard-coding the prefix, and add them to ``sys.path`` with :func:`add_stages`.

Runnable source and the artefacts later stages import live under ``src/`` in
the numbered folders.  Papers live in ``src/01_input/``.  The default paper is
the Mathpix export folder in ``src/01_input/target/`` (markdown plus
``images/``); the markdown is renamed to the folder name and figures to their
``Fig. N.`` captions.  A single loose markdown file in ``target/`` still works.
Every generated artefact is also copied under ``log/`` as a flat file
(``log/symbols.json``, ``log/equations.py``, …).  Plotting figures go in
``log/plotting/``.  This module lives in ``src/``, so :data:`ROOT` is the
parent of that folder.

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
from typing import Dict, List, Optional, Tuple

# Can remove - only serves as additional feature
__all__ = [
    "SRC",
    "ROOT",
    "LOG",
    "PLOTTING_LOG",
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

#: Copies of generated artefacts and human-only reports (no per-stage folders).
LOG = os.path.join(ROOT, "log")
#: Plotting figures and related artefacts.  The only subdirectory under ``log/``.
PLOTTING_LOG = os.path.join(LOG, "plotting")

_PAPER_EXTS = {".md", ".mmd"}   # Markdown or Mathpix markdown
_FIGURE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}
_CAPTION_SLUG_LEN = 80
#: ``![](./images/foo.jpg)`` immediately followed by ``Fig. N. caption``.
_IMAGE_CAPTION_RE = re.compile(
    r"!\[.*?\]\(([^)\s]+)\)[ \t]*\r?\n[ \t]*Fig(?:ure)?\.?\s*(\d+[a-z]?)\.\s*([^\r\n]+)",
    re.IGNORECASE,
)
_FIG_FILENAME_RE = re.compile(r"^Fig_(\d+)([a-z]?)_", re.IGNORECASE)

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
    """Copy ``path`` from ``src/`` into ``log/`` under its basename.

    Plotting artefacts go in :data:`PLOTTING_LOG`; everything else sits
    directly in :data:`LOG` (no numbered stage folders).
    """
    try:
        abs_path = os.path.abspath(path)
        rel = os.path.relpath(abs_path, SRC)
    except ValueError:
        return None
    if rel.startswith("..") or os.path.isabs(rel):
        return None
    name = os.path.basename(abs_path)
    top = rel.replace("\\", "/").split("/")[0]
    dest_dir = PLOTTING_LOG if _normalise(top) == "plotting" else LOG
    dest = os.path.join(dest_dir, name)
    os.makedirs(dest_dir, exist_ok=True)
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


def _paper_bundle_dirs(root: str) -> List[str]:
    """Subdirectories of ``root`` that contain a markdown/LaTeX paper."""
    if not os.path.isdir(root):
        return []
    found: List[str] = []
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if os.path.isdir(path) and _list_papers(path):
            found.append(path)
    return found


def _same_file(left: str, right: str) -> bool:
    return os.path.normcase(os.path.abspath(left)) == os.path.normcase(os.path.abspath(right))


def _is_under(path: str, root: str) -> bool:
    try:
        rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    except ValueError:
        return False
    return rel != os.pardir and not rel.startswith(".." + os.sep) and not os.path.isabs(rel)


def _target_bundle_dir(root: Optional[str] = None) -> Optional[str]:
    """The single Mathpix export folder under ``root`` (default :data:`TARGET`).

    Loose files at the root are ignored when a nested bundle exists.  ``None``
    means fall back to a paper sitting directly in ``root``.
    """
    folder = TARGET if root is None else root
    bundles = _paper_bundle_dirs(folder)
    if len(bundles) > 1:
        names = ", ".join(os.path.basename(path) for path in bundles)
        raise LookupError(
            f"Expected one paper folder in {folder}, found: {names}. "
            "Leave only the folder you want to run."
        )
    if len(bundles) == 1:
        return bundles[0]
    return None


def _slug_caption(text: str, max_len: int = _CAPTION_SLUG_LEN) -> str:
    slug = re.sub(r"[^\w]+", "_", text or "", flags=re.UNICODE).strip("_")
    slug = slug[:max_len].rstrip("_")
    return slug or "figure"


def _unique_dest(path: str) -> str:
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    n = 2
    candidate = f"{stem}_{n}{ext}"
    while os.path.exists(candidate):
        n += 1
        candidate = f"{stem}_{n}{ext}"
    return candidate


def _paired_figures(markdown: str) -> List[Tuple[str, str, str, str]]:
    """``(full_match, image_src, fig_number, caption)`` from Mathpix markdown."""
    found: List[Tuple[str, str, str, str]] = []
    for match in _IMAGE_CAPTION_RE.finditer(markdown or ""):
        found.append((match.group(0), match.group(1), match.group(2), match.group(3).strip()))
    return found


def _rewrite_image_src(src_ref: str, new_basename: str) -> str:
    posix = src_ref.replace("\\", "/")
    parent = posix.rsplit("/", 1)[0] if "/" in posix else ""
    return f"{parent}/{new_basename}" if parent else new_basename


def _rename_captioned_images(bundle: str, markdown: str) -> str:
    """Rename each captioned raster to ``Fig_N_slug.ext`` and rewrite ``![]()`` srcs."""
    updated = markdown
    for full, src_ref, number, caption in _paired_figures(markdown):
        old_path = os.path.normpath(os.path.join(bundle, src_ref.replace("/", os.sep)))
        if not os.path.isfile(old_path):
            continue
        ext = os.path.splitext(old_path)[1]
        dest = os.path.join(os.path.dirname(old_path), f"Fig_{number}_{_slug_caption(caption)}{ext}")
        if not _same_file(old_path, dest):
            dest = _unique_dest(dest)
            os.rename(old_path, dest)
        new_ref = _rewrite_image_src(src_ref, os.path.basename(dest))
        if new_ref != src_ref:
            updated = updated.replace(full, full.replace(src_ref, new_ref, 1), 1)
    return updated


def _normalize_paper_bundle(bundle: str) -> str:
    """Rename the paper to the folder name, caption-name its images, return the md path."""
    papers = _list_papers(bundle)
    if not papers:
        raise LookupError(f"No markdown/LaTeX paper in {bundle}.")
    if len(papers) > 1:
        raise LookupError(
            f"Expected one paper in {bundle}, found: {', '.join(papers)}. "
            "Leave only the file you want to run."
        )
    src = os.path.join(bundle, papers[0])
    dest = os.path.join(bundle, os.path.basename(bundle) + os.path.splitext(papers[0])[1])
    if not _same_file(src, dest):
        if os.path.exists(dest):
            raise LookupError(
                f"Cannot rename {papers[0]} to {os.path.basename(dest)}: that file already exists."
            )
        os.rename(src, dest)
        src = dest

    with open(src, "r", encoding="utf-8") as fh:
        text = fh.read()
    rewritten = _rename_captioned_images(bundle, text)
    if rewritten != text:
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(rewritten)
    return src


def _maybe_normalize_paper(path: str) -> str:
    """If ``path`` is inside a target holding folder, normalise that bundle."""
    abs_path = os.path.abspath(path)
    if os.path.isdir(abs_path):
        if (
            os.path.abspath(os.path.dirname(abs_path)) == os.path.abspath(TARGET)
            and _list_papers(abs_path)
        ):
            return _normalize_paper_bundle(abs_path)
        return abs_path
    parent = os.path.dirname(abs_path)
    if (
        os.path.abspath(os.path.dirname(parent)) == os.path.abspath(TARGET)
        and _is_under(parent, TARGET)
        and _list_papers(parent)
    ):
        return _normalize_paper_bundle(parent)
    return abs_path


'''Hard code input folder, and under that the target folder'''
INPUT = os.path.join(SRC, "01_input")
#: Papers: extras live directly in ``01_input/``; the default is a bundle in ``target/``.
TARGET = os.path.join(INPUT, "target")


def paper_path(name: Optional[str] = None) -> str:
    """Absolute path of a source document.

    With no ``name``, prefers the single subdirectory of :data:`TARGET` that
    contains a paper (a Mathpix export folder).  That bundle is normalised in
    place: the markdown is renamed to the folder name and captioned images are
    renamed to ``Fig_N_caption``.  If there is no nested folder, the single
    markdown file sitting directly in ``target/`` is used (legacy layout).

    With ``name``, looks in :data:`INPUT` first (e.g. ``sample_2.md``),
    then in :data:`TARGET`.  A path inside a target bundle is normalised too.
    """
    if name is None:
        bundle = _target_bundle_dir()
        if bundle is not None:
            return _normalize_paper_bundle(bundle)
        papers = _list_papers(TARGET)
        if not papers:
            raise LookupError(
                f"No markdown/LaTeX paper in {TARGET}. "
                "Put a paper file, or a folder containing the paper and images/, into that folder."
            )
        if len(papers) > 1:
            raise LookupError(
                f"Expected one paper in {TARGET}, found: {', '.join(papers)}. "
                "Leave only the file you want to run."
            )
        return os.path.join(TARGET, papers[0])

    if os.path.exists(name):
        return _maybe_normalize_paper(name)

    for folder in (INPUT, TARGET):
        candidate = os.path.join(folder, name)
        if os.path.exists(candidate):
            return _maybe_normalize_paper(candidate)

    return os.path.join(INPUT, name)


def _list_figures(folder: str) -> List[str]:
    if not os.path.isdir(folder):
        return []
    found: List[str] = []
    for entry in os.listdir(folder):
        path = os.path.join(folder, entry)
        if os.path.isfile(path) and os.path.splitext(entry)[1].lower() in _FIGURE_EXTS:
            found.append(path)
    return found


def _figure_sort_key(path: str) -> Tuple[int, int, str, str]:
    name = os.path.basename(path)
    match = _FIG_FILENAME_RE.match(name)
    if match:
        return (0, int(match.group(1)), match.group(2).lower(), name.lower())
    return (1, 0, "", name.lower())


''' For figures '''
def target_figure_paths() -> List[str]:
    """Absolute paths of raster figures for the default target paper.

    When ``target/`` holds a Mathpix export folder, rasters are collected from
    that folder and its ``images/`` subdirectory.  Otherwise files sitting
    directly in :data:`TARGET` are used.  Names ``Fig_N_...`` sort by figure
    number so ``Fig_2`` comes before ``Fig_10``.
    """
    found: List[str] = []
    try:
        bundle = _target_bundle_dir()
    except LookupError:
        bundle = None
    if bundle is not None:
        found.extend(_list_figures(bundle))
        found.extend(_list_figures(os.path.join(bundle, "images")))
    elif os.path.isdir(TARGET):
        found.extend(_list_figures(TARGET))
    unique = list(dict.fromkeys(os.path.abspath(path) for path in found))
    unique.sort(key=_figure_sort_key)
    return unique