"""Stage 02 -- pull every equation out of a paper into a self-contained document.

Reads the Mathpix markdown produced by stage 01 and writes:

``output/equations_raw.md``
    Display-equation blocks only.  Stage 04 reads this file to generate
    ``equations.py``.  It is not copied to ``log/``.

``output/symbols.json``
    Machine-readable extraction.  Stage 03 uses it to report which symbols
    still need a numeric value; stage 04 uses the descriptions to document
    the arguments of the generated Python functions.

``log/02_extract_equations/equations.md``
    Human-readable report: each display equation (with the paper's ``\\tag``),
    the sentence that introduces it, and the symbol dictionary.  Nothing in
    the pipeline imports this file.

Symbol descriptions come from the "where ``x`` is ..." clauses that follow the
equations in the paper, so the dictionary uses the authors' own wording.

Run it with::

    python src/02_extract_equations/extract_equations.py
    python src/02_extract_equations/extract_equations.py --paper src/01_input/sample_2.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HERE = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from execusci_paths import LOG, mirror_to_log, paper_path, stage_dir  # noqa: E402

from translator import (  # noqa: E402
    LatexParseError,
    latex_to_name,
    name_to_latex,
    translate,
)

__all__ = [
    "ExtractedEquation",
    "RawLatexEquation",
    "SymbolEntry",
    "ExtractedResult",
    "extract",
    "extract_latex_equations",
    "find_definitions",
    "render_markdown",
    "render_raw_markdown",
    "run",
]

_STAGE = stage_dir("Extract Equations")
DEFAULT_OUTPUT_DIR = os.path.join(_STAGE, "output")
EQUATIONS_FILENAME = "equations.md"
EQUATIONS_RAW_FILENAME = "equations_raw.md"
SYMBOLS_FILENAME = "symbols.json"
DEFAULT_REPORT_PATH = os.path.join(LOG, os.path.basename(_STAGE), EQUATIONS_FILENAME)

''' For the regexes below, see https://regex101.com/r/0g1k3F/1 for a live playground. '''

#: Inline math span, e.g. ``$k_{s}$``.
_INLINE_MATH = r"\$[^$]+\$"
#: "``$x$``, ``$y$`` and ``$z$`` are ..." -- the paper's definition clauses.
_DEFINITION_RE = re.compile(
    r"(?P<syms>" + _INLINE_MATH + r"(?:\s*(?:,\s*and|,|and)\s*" + _INLINE_MATH + r")*)"
    r"\s*(?:is|are|represents?|denotes?|refers? to)\s+",
    re.IGNORECASE,
)
#: Fallback for equations without a "where" clause: "the <description> $x$".
_APPOSITION_RE = re.compile(
    r"\bthe\s+(?P<desc>[a-z][a-z0-9 .()/-]{4,70}?)\s*(?P<sym>" + _INLINE_MATH + r")"
)

#: Where the prose after an equation stops being about that equation.
_CONTEXT_STOP_RE = re.compile(
    r"\n\s*(?:#{1,6}\s|\$\$|\\begin\{|!\[|\||Table\s+\d|Fig\.\s*\d)"
)

# Recognize a full stop that ends a sentence, ignoring abbreviations and single-letter initials.
_SENTENCE_END_RE = re.compile(r"\.(\s+|$)")
# Abbreviations whose full stop does not end a sentence.
_ABBREVIATIONS = {
    "e.g", "i.e", "et al", "cf", "eq", "eqs", "fig", "figs", "ref", "refs",
    "approx", "vs", "no", "al", "r.m.s", "etc", "min", "max",
}

_CONTEXT_WINDOW = 2000

_PARAMETER_RE = re.compile(r"model (?:parameter|constant|coefficient)", re.IGNORECASE)

_EQ_ENV_RE = re.compile(
    r"\\begin\{(equation\*?|align\*?|gather\*?|displaymath|math)\}"
    r"(?P<body>.*?)"
    r"\\end\{\1\}",
    re.DOTALL,
)
_DOLLAR_BLOCK_RE = re.compile(r"\$\$(?P<body>.+?)\$\$", re.DOTALL)
_TAG_RE = re.compile(r"\\tag\{(?P<tag>[^}]*)\}")
_LABEL_RE = re.compile(r"\\label\{[^}]*\}")


# --------------------------------------------------------------------------- #
# Display-equation finder
# --------------------------------------------------------------------------- #

@dataclass
class RawLatexEquation:
    """A LaTeX equation extracted from a document, before translation.

    ``source_line`` is the 1-based line of the document the equation was found
    on; the extraction report written by this stage cites it so a reader can
    trace every equation back to the paper.
    """

    latex: str
    tag: Optional[str] = None
    source_line: Optional[int] = None





def extract_latex_equations(text: str) -> List[RawLatexEquation]:
    """Return every LaTeX display equation found in ``text``.

    Handles ``\\begin{equation*}`` style environments (optionally wrapped in
    ``$$ ... $$``) as well as bare ``$$ ... $$`` blocks.  The ``\\tag{...}``
    number, if present, is captured separately and stripped from the math.
    """
    found: List[RawLatexEquation] = []
    consumed: List[Tuple[int, int]] = []

    for m in _EQ_ENV_RE.finditer(text):
        body = m.group("body")      # .group is how you access the matched text from the regex
        tag_m = _TAG_RE.search(body)
        tag = tag_m.group("tag").strip() if tag_m else None
        found.append(
            RawLatexEquation(latex=_clean_body(body), tag=tag, source_line=_line_of(text, m.start()))
        )
        consumed.append((m.start(), m.end()))   # Keep track of the start and end indices of the matched environment to avoid double counting in the next step

    # Bare $$ ... $$ blocks that did not contain an environment we already read.
    for m in _DOLLAR_BLOCK_RE.finditer(text):
        if any(start <= m.start() < end for start, end in consumed):
            continue
        body = m.group("body")
        if "\\begin{" in body:
            continue
        tag_m = _TAG_RE.search(body)
        tag = tag_m.group("tag").strip() if tag_m else None
        cleaned = _clean_body(body)
        if cleaned:
            found.append(
                RawLatexEquation(latex=cleaned, tag=tag, source_line=_line_of(text, m.start()))
            )

    # Order by the paper's own equation number when every equation carries a
    # numeric \tag (note this is a numeric sort, so Eq. (10) follows Eq. (9)).
    # Otherwise fall back to the order the equations appear in the document.
    numbers = [_tag_number(e.tag) for e in found]
    if found and all(n is not None for n in numbers):
        found.sort(key=lambda e: (_tag_number(e.tag), e.source_line or 0))
    else:
        found.sort(key=lambda e: (e.source_line or 0))
    return found


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1       # Counts how many \n before the index, +1 for 1-based line number

def _tag_number(tag: Optional[str]) -> Optional[float]:
    """Numeric value of a ``\\tag{...}``, or ``None`` if it is not a number."""
    if tag is None:
        return None
    try:
        return float(tag)
    except ValueError:
        return None

def _clean_body(body: str) -> str:
    """Remove ``\\tag`` / ``\\label`` from a body and strip whitespace."""
    body = _TAG_RE.sub("", body)
    body = _LABEL_RE.sub("", body)
    return body.strip()










@dataclass
class ExtractedEquation:
    """One display equation together with everything known about it."""

    tag: Optional[str]
    latex: str
    source_line: Optional[int]
    output: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    context: str = ""
    python: Optional[str] = None
    error: Optional[str] = None

    @property
    def label(self) -> str:
        return f"Eq. ({self.tag})" if self.tag else "Equation"

    @property
    def symbols(self) -> List[str]:
        names = list(self.inputs)
        if self.output and self.output not in names:
            names.append(self.output)
        return names

    def to_json(self) -> dict:
        return {
            "tag": self.tag,
            "latex": self.latex,
            "source_line": self.source_line,
            "output": self.output,
            "inputs": list(self.inputs),
            "python": self.python,
            "context": self.context,
            "error": self.error,
        }


@dataclass
class SymbolEntry:
    """A variable or constant used by the extracted equations like h_g or k_s."""

    name: str
    latex: str
    details: List[Tuple[str, str]] = field(default_factory=list)  # (description, tag)
    defined_by: List[str] = field(default_factory=list)  # equation tags
    used_in: List[str] = field(default_factory=list)  # equation tags

    @property
    def description(self) -> Optional[str]:
        return self.details[0][0] if self.details else None

    @property
    def kind(self) -> str:
        """``derived`` (an equation defines it), ``parameter`` or ``input``."""
        if self.defined_by:
            return "derived"
        # If every description mentions "model parameter" or similar, call it a parameter.
        if any(_PARAMETER_RE.search(text) for text, _ in self.details):
            return "parameter"
        return "input"  # Else used in an equation but not defined by one, and not described as a parameter. It requires input from the user or stage 03 scraping.

    def to_json(self) -> dict:
        return {
            "latex": self.latex,
            "description": self.description,
            "kind": self.kind,
            "definitions": [
                {"description": text, "equation": tag} for text, tag in self.details
            ],
            "defined_by": list(self.defined_by),
            "used_in": list(self.used_in),
        }


@dataclass
class ExtractedResult:
    """Result of reading one paper."""

    source: str
    equations: List[ExtractedEquation]
    symbols: Dict[str, SymbolEntry]

    @property
    def failed(self) -> List[ExtractedEquation]:
        return [e for e in self.equations if e.error]

    def descriptions(self) -> Dict[str, str]:
        """Flat ``name -> description`` mapping for downstream docstrings."""
        return {
            name: entry.description
            for name, entry in self.symbols.items()
            if entry.description
        }

    def to_json(self) -> dict:
        return {
            "source": os.path.basename(self.source),
            "equation_count": len(self.equations),
            "symbol_count": len(self.symbols),
            "equations": [e.to_json() for e in self.equations],
            "symbols": {name: s.to_json() for name, s in sorted(self.symbols.items())},
        }


# --------------------------------------------------------------------------- #
# Context / description mining
# --------------------------------------------------------------------------- #

# Finds the string index of the start of a 1-based line number format that markdown uses.
# Inverse of _line_of
def _offset_of_line(text: str, line: Optional[int]) -> int:
    """Character offset of the start of a 1-based line number."""
    if not line or line <= 1:
        return 0
    offset = 0
    for count, raw_line in enumerate(text.splitlines(keepends=True), start=1):
        if count == line:
            return offset
        offset += len(raw_line)
    return offset


def _end_of_equation_block(text: str, start: int) -> int:
    """Offset just past the ``$$``/``\\end{...}`` that closes a display block."""
    if text.startswith("$$", start):
        closing = text.find("$$", start + 2)
        if closing != -1:
            return closing + 2
    env_end = re.compile(r"\\end\{[^}]*\}").search(text, start)
    if env_end:
        closing = text.find("$$", env_end.end())
        if closing != -1 and closing - env_end.end() < 10:
            return closing + 2
        return env_end.end()
    return start


def context_after(text: str, raw: RawLatexEquation) -> str:
    """The prose that follows an equation, up to the next block-level element."""
    start = _offset_of_line(text, raw.source_line)
    end = _end_of_equation_block(text, start)
    window = text[end : end + _CONTEXT_WINDOW]
    stop = _CONTEXT_STOP_RE.search(window)
    if stop:
        window = window[: stop.start()]
    return window.strip()


def _cut_at_sentence_end(text: str) -> str:
    """Truncate at the first real sentence end, ignoring abbreviations.

    A full stop after a single letter only continues the sentence when the
    letter is part of a dotted abbreviation (``r.m.s.``); ``490 °C.`` ends one.
    """
    for match in _SENTENCE_END_RE.finditer(text):
        before = text[: match.start()]
        word = re.search(r"([A-Za-z.]+)$", before)
        token = (word.group(1) if word else "").strip(".").lower()
        if token in _ABBREVIATIONS:
            continue
        if len(token) == 1 and before[: -len(token)].endswith("."):
            continue
        return text[: match.start()]
    return text


# Collapse all new lines to spaces.
def _tidy_context(text: str) -> str:
    """One-line version of a paragraph, with the paper's inline math intact."""
    return _cut_at_sentence_end(re.sub(r"\s+", " ", text).strip())
# Make the description one line, and remove trailing "and" or commas.  Also strip trailing punctuation and whitespace, and unwrap inline math (like $k$ to k) for readability.
def _tidy_description(text: str) -> str:
    desc = _tidy_context(text)
    desc = re.sub(r"[,;]?\s*(?:and|,)\s*$", "", desc).strip()
    desc = desc.rstrip(".,;: ").strip()
    # Inline math reads better unwrapped inside a one-line description.
    desc = re.sub(r"\$\s*([^$]+?)\s*\$", r"\1", desc)
    return desc


def _names_in_math_group(group: str) -> List[str]:
    """Symbol names inside a run of inline math, e.g. ``$k_{s}, k_{t}$ and $k_{l}$``."""
    names: List[str] = []
    for fragment in re.findall(r"\$([^$]+)\$", group):
        # Mathpix often packs a list into one span; try it whole, then split.
        candidates = [fragment]
        if "," in fragment:
            candidates = [fragment, *fragment.split(",")]
        for candidate in candidates:
            name = latex_to_name(candidate)
            if name is None:
                continue
            if name not in names:
                names.append(name)
            if candidate is fragment:
                break
    return names


def where_clause(context: str) -> Optional[str]:
    """The paper's ``where ...`` sentence, which defines an equation's symbols.

    Only that one sentence is returned: the sentences that follow it discuss the
    equation ("the solid-contact IHTC $h_c$ is thus correlated positively with
    ...") rather than define its notation.
    """
    match = re.search(r"\bwhere\b", context, re.IGNORECASE)
    if match is None:
        return None
    end = context.find("\n\n", match.start())
    clause = context[match.end() : end if end != -1 else len(context)]
    return _cut_at_sentence_end(re.sub(r"\s+", " ", clause).strip()).strip()


def find_definitions(context: str, strict: bool = True) -> List[Tuple[List[str], str]]:
    """Extract ``([symbol names], description)`` pairs from a definition clause.

    Handles both single definitions ("``$P$`` is the contact pressure") and
    shared ones ("``$h_g$`` and ``$h_c$`` are the heat transfer coefficients
    across the air gap and for the solid contact respectively"), in which case
    the shared wording is recorded for every symbol in the group.

    With ``strict`` (the default) only the ``where ...`` clause is read, because
    that is where the paper actually defines its notation; ordinary prose such
    as "the solid-contact IHTC $h_c$ is thus correlated positively with ..." is
    a statement about a symbol, not a definition of it.
    """
    scope = where_clause(context) if strict else context
    if not scope:
        return []
    matches = list(_DEFINITION_RE.finditer(scope))
    out: List[Tuple[List[str], str]] = []
    for index, match in enumerate(matches):
        names = _names_in_math_group(match.group("syms"))
        if not names:
            continue
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(scope)
        description = _tidy_description(scope[match.end() : stop])
        if description:
            out.append((names, description))
    return out


def find_appositions(context: str) -> List[Tuple[List[str], str]]:
    """Fallback definitions of the form "the harmonic mean conductivity ``$K$``"."""
    out: List[Tuple[List[str], str]] = []
    for match in _APPOSITION_RE.finditer(context):
        names = _names_in_math_group(match.group("sym"))
        if not names:
            continue
        description = _tidy_description("the " + match.group("desc"))
        if description:
            out.append((names, description))
    return out


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #

def _record_definitions(
    symbols: Dict[str, SymbolEntry],
    definitions: Iterable[Tuple[List[str], str]],
    tag: Optional[str],
    only: Optional[Iterable[str]] = None,
) -> None:
    allowed = set(only) if only is not None else None
    for names, description in definitions:
        for name in names:
            entry = symbols.get(name)
            if entry is None:
                continue  # Only document symbols that appear in an equation.
            if allowed is not None and name not in allowed:
                continue
            if not any(text == description for text, _ in entry.details):
                entry.details.append((description, tag or "-"))


def _entry_for(symbols: Dict[str, SymbolEntry], name: str) -> SymbolEntry:
    if name not in symbols:
        symbols[name] = SymbolEntry(name=name, latex=name_to_latex(name))
    return symbols[name]


def extract(text: str, source: str = "") -> ExtractedResult:
    """Extract equations, their context and their symbol dictionary from ``text``."""
    equations: List[ExtractedEquation] = []
    symbols: Dict[str, SymbolEntry] = {}
    pending: List[Tuple[Optional[str], str]] = []

    for raw in extract_latex_equations(text):
        record = ExtractedEquation(
            tag=raw.tag,
            latex=raw.latex,
            source_line=raw.source_line,
            context=context_after(text, raw),
        )
        try:
            equation = translate(raw.latex, tag=raw.tag)
        except LatexParseError as exc:
            record.error = str(exc)
        else:
            record.output = equation.output.name if equation.output else None
            record.inputs = [s.name for s in equation.inputs]
            record.python = equation.python

            tag = raw.tag or str(len(equations) + 1)
            if record.output:
                entry = _entry_for(symbols, record.output)
                if tag not in entry.defined_by:
                    entry.defined_by.append(tag)
            for name in record.inputs:
                entry = _entry_for(symbols, name)
                if tag not in entry.used_in:
                    entry.used_in.append(tag)

        equations.append(record)
        pending.append((raw.tag, record.context))

    # Descriptions are recorded once every symbol is known, so a clause that
    # mentions a symbol used by a later equation is still picked up.  The
    # authors' "where ..." clauses come first; looser prose patterns only fill
    # the gaps they leave.
    for tag, context in pending:
        _record_definitions(symbols, find_definitions(context, strict=True), tag)
    for finder in (
        lambda ctx: find_definitions(ctx, strict=False),
        find_appositions,
    ):
        for tag, context in pending:
            undescribed = {n for n, e in symbols.items() if not e.details}
            if not undescribed:
                break
            gap_fillers = [
                (names, desc)
                for names, desc in finder(context)
                if any(name in undescribed for name in names)
            ]
            _record_definitions(symbols, gap_fillers, tag, only=undescribed)

    return ExtractedResult(source=source, equations=equations, symbols=symbols)


# --------------------------------------------------------------------------- #
# Outputting equations_raw.md, equations.md and symbols.json
# --------------------------------------------------------------------------- #

def _inline_safe(text: str) -> str:
    """Keep inline math from ever forming a ``$$`` display delimiter."""
    return re.sub(r"\$\s*\$", "$ $", text)


def _table_cell(text: str) -> str:
    return _inline_safe(re.sub(r"\s+", " ", text).replace("|", "\\|").strip())


def _context_quote(context: str) -> str:
    """The line quoted under an equation: its ``where`` clause, or plain context."""
    if not context:
        return ""
    clause = where_clause(context)
    if clause:
        return f"where {_tidy_context(clause)}."
    first = _tidy_context(context.split("\n\n")[0])
    return f"Context: {first}." if first else ""


def _equation_block(record: ExtractedEquation) -> str:
    body = record.latex.strip()
    if record.tag:
        body = f"{body} \\tag{{{record.tag}}}"
    return "$$\n\\begin{equation*}\n" + body + "\n\\end{equation*}\n$$"


def render_raw_markdown(extraction: ExtractedResult) -> str:
    """Display-equation blocks only -- the input stage 04 re-parses."""
    if not extraction.equations:
        return ""
    return "\n\n".join(_equation_block(record) for record in extraction.equations) + "\n"


def _symbol_sort_key(entry: SymbolEntry) -> Tuple[str, str]:
    return (entry.name.lstrip("\\").lower(), entry.name)


def render_markdown(extraction: ExtractedResult) -> str:
    """Render the extraction as the ``equations.md`` deliverable."""
    source = os.path.basename(extraction.source) or "the source document"
    ok = len(extraction.equations) - len(extraction.failed)
    lines: List[str] = [
        f"# Equations extracted from `{source}`",
        "",
        "Generated by ExecuSci stage 02 (`extract_equations.py`). Do not edit by hand.",
        "",
        f"- Equations found: **{len(extraction.equations)}** "
        f"({ok} translated, {len(extraction.failed)} unparsed)",
        f"- Distinct symbols: **{len(extraction.symbols)}**",
        "- The paper's `\\tag{n}` numbering is preserved, so stage 04 names the "
        "generated functions `eq_n`.",
        "",
        "## Equations",
        "",
    ]

    for record in extraction.equations:
        heading = record.label
        if record.output:
            heading += f" — defines `{record.output}`"
        lines.append(f"### {heading}")
        lines.append("")
        lines.append(_equation_block(record))
        lines.append("")
        if record.source_line:
            lines.append(f"- Paper line: {record.source_line}")
        if record.python:
            lines.append(f"- Python: `{record.python}`")
        if record.inputs:
            lines.append(f"- Inputs: {', '.join(f'`{n}`' for n in record.inputs)}")
        if record.error:
            lines.append(f"- **Could not translate**: {record.error}")
        lines.append("")
        quote = _context_quote(record.context)
        if quote:
            lines.append(f"> {_inline_safe(quote)}")
            lines.append("")

    lines.extend(
        [
            "## Symbol dictionary",
            "",
            "Every variable and constant used above, described in the paper's own "
            "wording. `derived` symbols are defined by an equation, `parameter` "
            "symbols are fitted model parameters, and `input` symbols are supplied "
            "by the user or scraped in stage 03.",
            "",
            "| Symbol | Name | Kind | Description | Defined by | Used in |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    for entry in sorted(extraction.symbols.values(), key=_symbol_sort_key):
        description = entry.description or "—"
        for text, tag in entry.details[1:]:
            description += f" *(Eq. {tag}: {text})*"
        defined = ", ".join(entry.defined_by) or "—"
        used = ", ".join(entry.used_in) or "—"
        lines.append(
            f"| ${_table_cell(entry.latex)}$ | `{entry.name}` | {entry.kind} "
            f"| {_table_cell(description)} | {defined} | {used} |"
        )

    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def run(
    paper: Optional[str] = None,
    out_dir: str = DEFAULT_OUTPUT_DIR,
    report_path: str = DEFAULT_REPORT_PATH,
    verbose: bool = True,
) -> ExtractedResult:
    """Extract from ``paper`` and write ``equations_raw.md`` / ``symbols.json``.

    The human-readable report is written to ``report_path`` (log only by
    default) and is not mirrored from ``src/``.
    """
    path = paper or paper_path()
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    extraction = extract(text, source=path)
    os.makedirs(out_dir, exist_ok=True)

    raw_path = os.path.join(out_dir, EQUATIONS_RAW_FILENAME)
    with open(raw_path, "w", encoding="utf-8") as fh:
        fh.write(render_raw_markdown(extraction))

    json_path = os.path.join(out_dir, SYMBOLS_FILENAME)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(extraction.to_json(), fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    mirror_to_log(json_path)

    os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(extraction))

    if verbose:
        ok = len(extraction.equations) - len(extraction.failed)
        print(f"Read {os.path.basename(path)}")
        print(f"  {ok}/{len(extraction.equations)} equations translated")
        for record in extraction.failed:
            print(f"  ! {record.label}: {record.error}")
        described = sum(1 for s in extraction.symbols.values() if s.description)
        print(f"  {described}/{len(extraction.symbols)} symbols described by the paper")
        undescribed = sorted(n for n, s in extraction.symbols.items() if not s.description)
        if undescribed:
            print(f"  ? no description found for: {', '.join(undescribed)}")
        print(f"  wrote {raw_path}")
        print(f"  wrote {json_path}")
        print(f"  wrote {report_path}")

    return extraction


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract equations and their symbol dictionary from a paper."
    )
    parser.add_argument(
        "--paper",
        default=None,
        help="Markdown/LaTeX source (default: the file in src/01_input/target/)",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for equations_raw.md and symbols.json (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--report",
        default=DEFAULT_REPORT_PATH,
        help=f"Human-readable equations.md path (default: {DEFAULT_REPORT_PATH})",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    extraction = run(paper=args.paper, out_dir=args.output, report_path=args.report)
    return 0 if extraction.equations and not extraction.failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
