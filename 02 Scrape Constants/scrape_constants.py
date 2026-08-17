"""Scrape numeric constants from paper LaTeX / Mathpix markdown.

Runs alongside equation extraction: the same document text yields both
``equations.py`` (via ``latex2python``) and a ``constants.py`` module that
callers can import to supply values to the generated ``eq_*`` functions.

Sources
-------
1. **Markdown tables** whose headers are math symbols (e.g. Table 3 in
   ``mathpix_pdf.md``): header cell → symbol name, value cell → float.
2. **Prose** patterns such as ``$h_a$ ... approximately $0.8$``.

Symbol names are normalised with the same rules as ``latex2python``
(``\\lambda`` → ``lamda``, ``k_{s}`` → ``k_s``, …) so keys line up with
equation argument names.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from latex2python import LatexParseError, translate

__all__ = [
    "Constant",
    "extract_constants",
    "extract_tables",
    "generate_constants_module",
    "latex_to_name",
    "parse_number",
]

# Tool / material labels that appear in Table 3 headers like ``k_t (H13)``.
_TOOL_ALIASES = {
    "h13": "H13",
    "p20": "P20",
    "cast iron": "CastIron",
    "castiron": "CastIron",
}

# Parenthetical labels that are descriptive, not tool variants.
_NON_TOOL_LABELS = {"lubricant", "blank", "specimen"}

_MD_TABLE_ROW_RE = re.compile(r"^\|(?P<cells>.+)\|\s*$", re.MULTILINE)
_SEPARATOR_RE = re.compile(r"^[\s:|\-]+$")
_TABLE_CAPTION_RE = re.compile(
    r"(?:^|\n)\s*Table\s+(?P<num>\d+)\s*\n(?P<title>[^\n|]+)?",
    re.IGNORECASE,
)

# Prose: $symbol$ ... approximately|of|=|≈ ... number (optionally in $...$).
# Captions that are material data sheets, not model-constant tables.
_SKIP_CAPTION_RE = re.compile(r"composition|propert(?:y|ies)", re.I)
_KEEP_CAPTION_RE = re.compile(r"constant|parameter", re.I)

# Prose: $symbol$ ... approximately|of|=|≈ ... number (optionally in $...$).
_PROSE_CONST_RE = re.compile(
    r"\$\s*(?P<sym>[^$=]+?)\s*\$"
    r"(?P<bridge>.{0,120}?)"
    r"(?:approximately|approx\.?|of|equal(?:s| to)?|≈|=|:)\s*"
    r"(?:\$\s*)?(?P<val>[0-9][0-9eE+.\-\\mathrm\{\}\s~]*)",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class Constant:
    """One scraped numeric constant."""

    name: str
    value: float
    unit: Optional[str] = None
    variant: Optional[str] = None  # tool material, e.g. "H13"
    source: str = "table"  # "table" | "prose"
    table: Optional[str] = None  # e.g. "3"
    caption: Optional[str] = None
    source_line: Optional[int] = None
    raw_header: Optional[str] = None
    raw_value: Optional[str] = None


@dataclass
class _MarkdownTable:
    headers: List[str]
    rows: List[List[str]]
    start: int
    table_num: Optional[str] = None
    caption: Optional[str] = None


# --------------------------------------------------------------------------- #
# Number / symbol helpers
# --------------------------------------------------------------------------- #

def parse_number(text: str) -> Optional[float]:
    """Parse a Mathpix / LaTeX numeric cell into a Python float.

    Handles ``3.4e-7``, ``3.4 \\mathrm{e}-7``, ``2.01 e-4``, ``7.85 e 03``.
    """
    if text is None:
        return None
    s = text.strip()
    if not s or s.lower() in {"bal.", "bal", "-", "—", "–"}:
        return None

    # Drop math wrappers and unit fragments so digits remain.
    s = s.replace("$", " ")
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)  # \quad, \times, …
    s = s.replace("{", " ").replace("}", " ").replace("~", " ")
    s = re.sub(r"\s+", " ", s).strip()

    # Scientific: "3.4 e -7" / "3.4e-7" / "2e5"
    m = re.search(
        r"([+-]?\d+(?:\.\d+)?)\s*[eE]\s*([+-]?\d+)",
        s,
    )
    if m:
        try:
            return float(f"{m.group(1)}e{m.group(2)}")
        except ValueError:
            return None

    m = re.search(r"([+-]?\d+(?:\.\d+)?)", s)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def latex_to_name(latex: str) -> Optional[str]:
    """Map a LaTeX symbol fragment to the ASCII name used by ``latex2python``."""
    frag = latex.strip()
    if not frag:
        return None
    try:
        eq = translate(frag)
    except LatexParseError:
        return None
    expr = eq.expr
    # Bare symbol.
    if hasattr(expr, "is_Symbol") and expr.is_Symbol:
        return str(expr.name)
    # Equality or expression with a single free symbol — take that name.
    free = list(getattr(expr, "free_symbols", []) or [])
    if len(free) == 1:
        return free[0].name
    if eq.output is not None and not eq.inputs:
        return eq.output.name
    return None


def _normalize_tool(label: str) -> Optional[str]:
    key = re.sub(r"\s+", " ", label.strip().lower())
    if key in _NON_TOOL_LABELS:
        return None
    return _TOOL_ALIASES.get(key)


def _split_header(cell: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Return ``(symbol_name, tool_variant, unit)`` from a table header cell."""
    raw = cell.strip()
    if not raw:
        return None, None, None

    # Bare text like ``H13``, ``Property``, ``AA7075`` is not a math symbol header.
    # Model-constant headers from Mathpix always contain ``$`` / ``\`` / ``_``.
    if not re.search(r"[\\_$]", raw):
        return None, None, None

    # Pure numeric / scientific-notation cells are values, never headers.
    if re.search(r"\d\s*(?:\\mathrm\{e\}|[eE])\s*[+\-]?\s*\d", raw):
        return None, None, None
    if re.fullmatch(r"\$?\s*[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\s*\$?", raw):
        return None, None, None

    variant: Optional[str] = None
    unit: Optional[str] = None
    work = raw

    # Normalise \left(...\right) before scanning parentheses.
    work = re.sub(r"\\left\s*", "", work)
    work = re.sub(r"\\right\s*", "", work)

    # Tool labels and unit / dimensionless parentheses.
    for m in list(re.finditer(r"\(([^)]+)\)", work)):
        inner = m.group(1).strip()
        tool = _normalize_tool(inner)
        if tool is not None:
            variant = tool
            work = work[: m.start()] + work[m.end() :]
            continue
        if inner.lower() in _NON_TOOL_LABELS or inner in {"-", "—", "–"}:
            work = work[: m.start()] + " " + work[m.end() :]
            continue
        # Unit parenthetical: (\mathrm{~kW}/mK), (m^{-1}), …
        if re.search(r"\\mathrm|kW|[/^]|\\?\b m\b|K\b|-1|~\w", inner, re.I):
            cleaned = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", inner)
            cleaned = re.sub(r"[~$\\\s]", "", cleaned)
            unit = (unit + cleaned) if unit else cleaned
            work = work[: m.start()] + " " + work[m.end() :]

    # Unwrap identity \mathrm{t} inside subscripts — but never \mathrm{e} (sci note).
    work = re.sub(r"\\mathrm\{([A-Za-df-z]+)\}", r"\1", work)

    # Trailing unit fragments still attached: \mathrm{~kW}, ^{-1}, …
    for um in list(re.finditer(r"\\mathrm\{([^}]*)\}", work)):
        content = um.group(1)
        if re.search(r"kW|m|K|[/^~]|-1|\d", content, re.I):
            cleaned = re.sub(r"[~$\\\s]", "", content)
            unit = (unit + cleaned) if unit else cleaned
            work = work[: um.start()] + " " + work[um.end() :]

    work = re.sub(r"\^{[^}]*}", " ", work)
    work = re.sub(r"\^[+\-]?\d+", " ", work)

    work = work.replace("$", " ")
    work = re.sub(r"\\text\{[^}]*\}", " ", work)
    work = re.sub(r"[()]", " ", work)
    work = re.sub(r"\s+", " ", work).strip()
    work = re.sub(r"\s*-\s*$", "", work).strip()

    if not work or work.lower() in {"property", "element"}:
        return None, variant, unit

    name = latex_to_name(work)
    return name, variant, unit or None


# --------------------------------------------------------------------------- #
# Table extraction
# --------------------------------------------------------------------------- #

def extract_tables(text: str) -> List[_MarkdownTable]:
    """Find pipe-style markdown tables and attach nearby ``Table N`` captions."""
    captions: List[Tuple[int, str, str]] = []
    for m in _TABLE_CAPTION_RE.finditer(text):
        title = (m.group("title") or "").strip()
        captions.append((m.start(), m.group("num"), title))

    tables: List[_MarkdownTable] = []
    lines = text.splitlines(keepends=True)
    # Rebuild with absolute offsets.
    offset = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if not _MD_TABLE_ROW_RE.match(line.rstrip("\n")):
            offset += len(line)
            i += 1
            continue

        block_start = offset
        row_lines: List[str] = []
        while i < len(lines) and _MD_TABLE_ROW_RE.match(lines[i].rstrip("\n")):
            row_lines.append(lines[i].rstrip("\n"))
            offset += len(lines[i])
            i += 1

        parsed_rows: List[List[str]] = []
        for rl in row_lines:
            m = _MD_TABLE_ROW_RE.match(rl)
            if not m:
                continue
            cells = [c.strip() for c in m.group("cells").split("|")]
            # Separator row (| :--- | :--- |).
            if all(_SEPARATOR_RE.match(c.replace(":", "-")) or not c for c in cells):
                continue
            if all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells if c):
                continue
            parsed_rows.append(cells)

        if len(parsed_rows) < 2:
            continue

        headers = parsed_rows[0]
        data = parsed_rows[1:]
        # Nearest caption before this table.
        table_num = caption = None
        for cap_pos, num, title in reversed(captions):
            if cap_pos < block_start:
                table_num, caption = num, title
                break
        tables.append(
            _MarkdownTable(
                headers=headers,
                rows=data,
                start=block_start,
                table_num=table_num,
                caption=caption,
            )
        )
    return tables


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _parse_header_row(
    cells: List[str],
) -> List[Tuple[Optional[str], Optional[str], Optional[str], str]]:
    return [(*_split_header(h), h) for h in cells]


def _row_symbol_score(cells: List[str]) -> Tuple[int, int]:
    """Return ``(symbol_hits, numeric_hits)`` for classifying header vs value rows."""
    symbols = 0
    numbers = 0
    for cell in cells:
        if not cell or not cell.strip():
            continue
        name, _, _ = _split_header(cell)
        num = parse_number(cell)
        # A pure number cell is a value; a parseable symbol (even if a number
        # substring exists inside units) counts as a header when named.
        if name is not None and not re.fullmatch(
            r"\$?\s*[+-]?\d+(?:\.\d+)?(?:\s*[eE]\s*[+-]?\d+)?\s*\$?",
            cell.strip(),
        ):
            # Prefer symbol if the cell is clearly math/identifier-heavy.
            if re.search(r"[\\_A-Za-z]", cell):
                symbols += 1
                continue
        if num is not None:
            numbers += 1
        elif name is not None:
            symbols += 1
    return symbols, numbers


def _row_is_header_like(cells: List[str]) -> bool:
    symbols, numbers = _row_symbol_score(cells)
    return symbols > 0 and symbols >= numbers


def _row_is_value_like(cells: List[str]) -> bool:
    symbols, numbers = _row_symbol_score(cells)
    return numbers > 0 and numbers >= symbols


def _emit_row_constants(
    parsed_headers: List[Tuple[Optional[str], Optional[str], Optional[str], str]],
    row: List[str],
    table: _MarkdownTable,
    text: str,
) -> List[Constant]:
    out: List[Constant] = []
    for col, (name, variant, unit, raw_h) in enumerate(parsed_headers):
        if name is None or col >= len(row):
            continue
        raw_v = row[col]
        value = parse_number(raw_v)
        if value is None:
            continue
        out.append(
            Constant(
                name=name,
                value=value,
                unit=unit,
                variant=variant,
                source="table",
                table=table.table_num,
                caption=table.caption,
                source_line=_line_of(text, table.start),
                raw_header=raw_h,
                raw_value=raw_v,
            )
        )
    return out


def _constants_from_table(table: _MarkdownTable, text: str) -> List[Constant]:
    """Pair symbol headers with numeric cells.

    Mathpix often emits "stacked" constant tables as **one** markdown table
    with alternating header / value rows (see Table 3).  Detect that pattern
    instead of treating every non-first row as values for the top header.
    """
    if table.caption and _SKIP_CAPTION_RE.search(table.caption):
        if not _KEEP_CAPTION_RE.search(table.caption):
            return []

    # Build the sequence: markdown header row + body rows.
    all_rows: List[List[str]] = [table.headers, *table.rows]
    out: List[Constant] = []
    parsed_headers: Optional[
        List[Tuple[Optional[str], Optional[str], Optional[str], str]]
    ] = None
    symbol_header_blocks = 0

    for row in all_rows:
        if _row_is_header_like(row) and not _row_is_value_like(row):
            parsed_headers = _parse_header_row(row)
            named = sum(1 for n, _, _, _ in parsed_headers if n is not None)
            if named >= max(1, len([c for c in row if c.strip()]) // 2):
                symbol_header_blocks += 1
            else:
                parsed_headers = None
            continue

        if parsed_headers is None:
            continue

        if _row_is_value_like(row):
            out.extend(_emit_row_constants(parsed_headers, row, table, text))
            # Keep headers for a possible second value row; stacked tables
            # usually alternate, so the next header-like row will replace them.

    # Skip composition / property tables that never looked symbol-keyed.
    if symbol_header_blocks == 0:
        return []
    return out

# --------------------------------------------------------------------------- #
# Prose extraction
# --------------------------------------------------------------------------- #

def _constants_from_prose(text: str) -> List[Constant]:
    out: List[Constant] = []
    seen: set = set()
    for m in _PROSE_CONST_RE.finditer(text):
        bridge = m.group("bridge")
        # Avoid matching equation definitions like $h = h_a + ...$.
        if "=" in bridge and "approximately" not in bridge.lower():
            # Allow "= approximately" style; skip pure equation bridges.
            if not re.search(r"approximately|approx|≈", bridge, re.I):
                continue
        name = latex_to_name(m.group("sym"))
        value = parse_number(m.group("val"))
        if name is None or value is None:
            continue
        key = (name, value)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            Constant(
                name=name,
                value=value,
                source="prose",
                source_line=_line_of(text, m.start()),
                raw_header=m.group("sym").strip(),
                raw_value=m.group("val").strip(),
            )
        )
    return out


def extract_constants(text: str, *, include_prose: bool = True) -> List[Constant]:
    """Scrape constants from markdown tables (and optionally prose) in ``text``."""
    found: List[Constant] = []
    for table in extract_tables(text):
        found.extend(_constants_from_table(table, text))
    if include_prose:
        # Prefer table values when the same name already exists without a variant.
        table_names = {c.name for c in found if c.variant is None}
        for c in _constants_from_prose(text):
            if c.name in table_names:
                continue
            found.append(c)
    return found


# --------------------------------------------------------------------------- #
# Module generation
# --------------------------------------------------------------------------- #

def _organise(constants: List[Constant]) -> Tuple[Dict[str, Constant], Dict[str, Dict[str, Constant]]]:
    """Split into shared scalars and per-tool overrides."""
    shared: Dict[str, Constant] = {}
    tools: Dict[str, Dict[str, Constant]] = {}
    for c in constants:
        if c.variant:
            tools.setdefault(c.variant, {})[c.name] = c
        else:
            # First occurrence wins (tables usually precede prose).
            shared.setdefault(c.name, c)
    return shared, tools


def _fmt_float(x: float) -> str:
    """Render a float for generated source (keep scientific where natural)."""
    if x == 0:
        return "0.0"
    ax = abs(x)
    if ax >= 1e5 or (ax < 1e-3 and ax != 0):
        return f"{x:.6g}"
    # Prefer ordinary decimals for typical model params.
    s = f"{x:.12g}"
    if "." not in s and "e" not in s and "E" not in s:
        s += ".0"
    return s


def generate_constants_module(
    text: str,
    *,
    module_doc: str = "",
    include_prose: bool = True,
    default_tool: Optional[str] = None,
    default_delta: float = 1.5e-5,
) -> str:
    """Build a runnable ``constants.py`` source string from document ``text``.

    Layout mirrors the hand-authored plotting helper: ``_SHARED``, ``_TOOL``,
    and ``get_constants(tool, delta)`` so generated ``eq_*`` functions can be
    called with ``**get_constants()`` (or selected keys).
    """
    constants = extract_constants(text, include_prose=include_prose)
    shared, tools = _organise(constants)

    doc = module_doc or "Auto-generated constants scraped from the paper by ExecuSci."
    lines: List[str] = [
        f'"""{doc}',
        "",
        "Names match symbols in the companion equations module (e.g. ``lamda``,",
        "``sigma_U``). Tool-specific values are grouped under ``_TOOL``.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Dict",
        "",
        "# Shared blank / lubricant / model parameters (independent of tool material).",
        "_SHARED = {",
    ]

    for name in sorted(shared):
        c = shared[name]
        comment_bits = []
        if c.unit:
            comment_bits.append(c.unit)
        if c.table:
            comment_bits.append(f"Table {c.table}")
        elif c.source == "prose":
            comment_bits.append("prose")
        comment = f"  # {' — '.join(comment_bits)}" if comment_bits else ""
        lines.append(f'    "{name}": {_fmt_float(c.value)},{comment}')
    lines.append("}")
    lines.append("")

    lines.append("# Tool thermal conductivity and roughness by material.")
    lines.append("_TOOL = {")
    for tool in sorted(tools):
        lines.append(f'    "{tool}": {{')
        for name in sorted(tools[tool]):
            c = tools[tool][name]
            comment = f"  # Table {c.table}" if c.table else ""
            lines.append(f'        "{name}": {_fmt_float(c.value)},{comment}')
        lines.append("    },")
    lines.append("}")
    lines.append("")

    if default_tool is None:
        default_tool = "P20" if "P20" in tools else (next(iter(sorted(tools)), "P20"))

    lines.extend(
        [
            f'DEFAULT_TOOL = "{default_tool}"',
            f"DEFAULT_DELTA = {_fmt_float(default_delta)}  # m — lubricant film thickness (user-supplied)",
            "",
            "",
            "def available_tools() -> list[str]:",
            "    return list(_TOOL.keys())",
            "",
            "",
            "def get_constants(tool: str = DEFAULT_TOOL, delta: float = DEFAULT_DELTA) -> Dict[str, float]:",
            '    """Return a flat constant dict for the given tool material."""',
            "    if tool not in _TOOL:",
            "        raise ValueError(",
            '            f"Unknown tool {tool!r}. Choose from: {\', \'.join(available_tools())}"',
            "        )",
            '    consts = {**_SHARED, **_TOOL[tool], "delta": float(delta)}',
            "    return consts",
            "",
            "",
            "def as_dict() -> Dict[str, float]:",
            '    """All shared constants plus every tool-qualified name (``k_t_H13``, …)."""',
            "    out = {k: float(v) for k, v in _SHARED.items()}",
            "    for tool, vals in _TOOL.items():",
            '        for name, value in vals.items():',
            '            out[f"{name}_{tool}"] = float(value)',
            "    return out",
            "",
        ]
    )
    return "\n".join(lines)
