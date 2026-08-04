"""LaTeX math -> Python / SymPy translator for ExecuSci.

This module turns the mathematical equations embedded in scientific papers
(as produced by tools such as Mathpix, i.e. ``\\begin{equation*} ... \\end{equation*}``
blocks) into executable Python.

It is deliberately self contained and does **not** rely on SymPy's own
``parse_latex`` (whose ANTLR/Lark backends choke on the real-world LaTeX found
in papers -- multi-character subscripts like ``k_{s t}``, placeholder
superscripts like ``R_{s}{ }^{2}``, bare ``\\tan \\theta``, ``\\left( ... \\right)``
and accents like ``\\bar{\\lambda}``).

Pipeline
--------
1. ``extract_equations`` pulls the raw LaTeX math out of a ``.tex`` / ``.md`` file.
2. ``preprocess`` normalises the Mathpix quirks.
3. ``tokenize`` splits the math into tokens.
4. ``Parser`` builds a SymPy expression via recursive descent.
5. ``translate`` / ``Equation`` expose the result as a SymPy ``Eq``, a Python
   source string, and a ready-to-call numeric function.

Typical use::

    from latex2python import translate
    eq = translate(r"h=1.45 k \\frac{\\tan \\theta}{\\sigma}"
                   r"\\left(\\frac{p}{H}\\right)^{0.985}")
    print(eq.python)          # h = 1.45*k*(p/H)**0.985*tan(theta)/sigma
    print(eq.evaluate(k=1, theta=0.1, sigma=2, p=3, H=4))
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import sympy as sp

__all__ = [
    "Equation",
    "translate",
    "translate_document",
    "extract_equations",
    "preprocess",
    "tokenize",
    "Parser",
    "generate_module",
    "MATH_NAMESPACE",
    "LatexParseError",
]

# Names that the generated Python expressions/functions rely on being in scope.
# NumPy is used so the generated code works on scalars *and* arrays.
_NAMESPACE_IMPORT = (
    "from numpy import (\n"
    "    exp, log, sqrt, sin, cos, tan, sinh, cosh, tanh, pi,\n"
    "    arcsin as asin, arccos as acos, arctan as atan, abs as Abs,\n"
    ")\n"
)


def MATH_NAMESPACE() -> Dict[str, Callable]:
    """Return a dict of the math names used by generated expressions."""
    import numpy as np

    return {
        "exp": np.exp, "log": np.log, "sqrt": np.sqrt,
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
        "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
        "Abs": np.abs, "pi": np.pi,
    }


class LatexParseError(ValueError):
    """Raised when a LaTeX fragment cannot be parsed into a Python expression."""


# --------------------------------------------------------------------------- #
# Symbol / command tables
# --------------------------------------------------------------------------- #

# Greek letters -> plain-ASCII SymPy symbol names.  ``lambda`` is a Python
# keyword, so it is mapped to ``lamda`` (the same spelling SymPy uses).
_GREEK = {
    "alpha": "alpha", "beta": "beta", "gamma": "gamma", "delta": "delta",
    "epsilon": "epsilon", "varepsilon": "epsilon", "zeta": "zeta", "eta": "eta",
    "theta": "theta", "vartheta": "theta", "iota": "iota", "kappa": "kappa",
    "lambda": "lamda", "mu": "mu", "nu": "nu", "xi": "xi", "pi": "pi",
    "rho": "rho", "varrho": "rho", "sigma": "sigma", "varsigma": "sigma",
    "tau": "tau", "upsilon": "upsilon", "phi": "phi", "varphi": "phi",
    "chi": "chi", "psi": "psi", "omega": "omega",
    "Gamma": "Gamma", "Delta": "Delta", "Theta": "Theta", "Lambda": "Lamda",
    "Xi": "Xi", "Pi": "Pi", "Sigma": "Sigma", "Upsilon": "Upsilon",
    "Phi": "Phi", "Psi": "Psi", "Omega": "Omega",
}

# LaTeX functions -> SymPy callables.
_FUNCTIONS: Dict[str, Callable] = {
    "exp": sp.exp,
    "log": sp.log,
    "ln": sp.log,
    "sqrt": sp.sqrt,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "sec": sp.sec, "csc": sp.csc, "cot": sp.cot,
    "arcsin": sp.asin, "arccos": sp.acos, "arctan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "abs": sp.Abs,
}

# Accent commands that decorate the following symbol (``\bar{\lambda}`` -> lamda_bar).
_ACCENTS = {
    "bar": "bar", "overline": "bar", "hat": "hat", "widehat": "hat",
    "tilde": "tilde", "widetilde": "tilde", "vec": "vec", "dot": "dot",
    "ddot": "ddot", "overrightarrow": "vec", "mathbf": "", "boldsymbol": "",
    "mathrm": "", "text": "", "operatorname": "",
}

# Spacing / cosmetic commands that carry no mathematical meaning.
_SPACING = [
    r"\,", r"\;", r"\:", r"\!", r"\quad", r"\qquad", r"\ ", r"\medspace",
    r"\thinspace", r"\thickspace", r"\negthinspace", r"\displaystyle",
    r"\limits", r"\nolimits",
]


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #

_EQ_ENV_RE = re.compile(
    r"\\begin\{(equation\*?|align\*?|gather\*?|displaymath|math)\}"
    r"(?P<body>.*?)"
    r"\\end\{\1\}",
    re.DOTALL,
)
_DOLLAR_BLOCK_RE = re.compile(r"\$\$(?P<body>.+?)\$\$", re.DOTALL)
_TAG_RE = re.compile(r"\\tag\{(?P<tag>[^}]*)\}")
_LABEL_RE = re.compile(r"\\label\{[^}]*\}")


@dataclass
class RawEquation:
    """A LaTeX equation extracted from a document, before translation."""

    latex: str
    tag: Optional[str] = None
    source_line: Optional[int] = None


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def extract_equations(text: str) -> List[RawEquation]:
    """Return every LaTeX display equation found in ``text``.

    Handles ``\\begin{equation*}`` style environments (optionally wrapped in
    ``$$ ... $$``) as well as bare ``$$ ... $$`` blocks.  The ``\\tag{...}``
    number, if present, is captured separately and stripped from the math.
    """
    found: List[RawEquation] = []
    consumed: List[Tuple[int, int]] = []

    for m in _EQ_ENV_RE.finditer(text):
        body = m.group("body")
        tag_m = _TAG_RE.search(body)
        tag = tag_m.group("tag").strip() if tag_m else None
        found.append(
            RawEquation(latex=_clean_body(body), tag=tag, source_line=_line_of(text, m.start()))
        )
        consumed.append((m.start(), m.end()))

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
                RawEquation(latex=cleaned, tag=tag, source_line=_line_of(text, m.start()))
            )

    found.sort(key=lambda e: (e.source_line or 0))
    return found


def _clean_body(body: str) -> str:
    body = _TAG_RE.sub("", body)
    body = _LABEL_RE.sub("", body)
    return body.strip()


# --------------------------------------------------------------------------- #
# Preprocessing
# --------------------------------------------------------------------------- #

def preprocess(latex: str) -> str:
    """Normalise real-world LaTeX so the tokenizer can handle it."""
    s = latex.strip()

    # Strip surrounding math delimiters.
    s = s.replace("$$", " ").replace("$", " ")
    s = _TAG_RE.sub("", s)
    s = _LABEL_RE.sub("", s)

    # Environment wrappers, if a raw environment string is passed in directly.
    s = re.sub(r"\\(begin|end)\{[^}]*\}", " ", s)

    # \left( ... \right) -> ( ... ); also \left. / \right. and \left\{ etc.
    s = re.sub(r"\\left\s*\\?", " ", s)
    s = re.sub(r"\\right\s*\\?", " ", s)
    s = re.sub(r"\\(bigl|bigr|Bigl|Bigr|biggl|biggr|Biggl|Biggr|big|Big|bigg|Bigg)\s*", " ", s)

    # Explicit multiplication dots.
    s = s.replace(r"\cdot", " * ").replace(r"\times", " * ")

    # Cosmetic spacing commands.
    for cmd in _SPACING:
        s = s.replace(cmd, " ")

    # Mathpix placeholder groups: R_{s}{ }^{2}  ->  R_{s}^{2}
    s = re.sub(r"\{\s*\}", " ", s)

    return s.strip()


# --------------------------------------------------------------------------- #
# Tokenizer
# --------------------------------------------------------------------------- #

@dataclass
class Token:
    kind: str  # 'num', 'sym', 'cmd', 'op'
    value: str


_NUMBER_RE = re.compile(r"\d+\.\d+|\.\d+|\d+")
_COMMAND_RE = re.compile(r"\\[A-Za-z]+|\\.")
_OPS = set("+-*/^_(){}=[]")


def tokenize(latex: str) -> List[Token]:
    """Split preprocessed LaTeX math into a flat token stream."""
    s = latex
    i = 0
    n = len(s)
    tokens: List[Token] = []
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        m = _NUMBER_RE.match(s, i)
        if m:
            tokens.append(Token("num", m.group()))
            i = m.end()
            continue
        if c == "\\":
            m = _COMMAND_RE.match(s, i)
            if not m:
                raise LatexParseError(f"Dangling backslash at position {i}: {s[i:i+10]!r}")
            tokens.append(Token("cmd", m.group()[1:]))  # store name without backslash
            i = m.end()
            continue
        if c in _OPS:
            tokens.append(Token("op", c))
            i += 1
            continue
        if c.isalpha():
            tokens.append(Token("sym", c))
            i += 1
            continue
        # Unknown punctuation such as ',' or '.' between structures -> skip.
        if c in ",.;":
            i += 1
            continue
        raise LatexParseError(f"Unexpected character {c!r} at position {i}")
    return tokens


# --------------------------------------------------------------------------- #
# Parser (recursive descent)
# --------------------------------------------------------------------------- #

class Parser:
    r"""Recursive-descent parser turning a token stream into a SymPy expression.

    Grammar (informal)::

        equation := expr ('=' expr)?
        expr     := term (('+' | '-') term)*
        term     := factor ( ('/' | '*') factor | <implicit> factor )*
        factor   := ('+' | '-')* power
        power    := atom ('^' atom)?
        atom     := number | symbol | '(' expr ')' | '{' expr '}'
                  | \frac{expr}{expr} | \sqrt[expr]{expr} | func atom | accent atom
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.symbols: Dict[str, sp.Symbol] = {}

    # -- token helpers ---------------------------------------------------- #
    def _peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _next(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, kind: str, value: str) -> Token:
        tok = self._peek()
        if tok is None or tok.kind != kind or tok.value != value:
            raise LatexParseError(f"Expected {value!r} but found {tok}")
        return self._next()

    def _sym(self, name: str) -> sp.Symbol:
        if name not in self.symbols:
            self.symbols[name] = sp.Symbol(name)
        return self.symbols[name]

    # -- entry point ------------------------------------------------------ #
    def parse(self):
        lhs = self._parse_expr()
        tok = self._peek()
        if tok is not None and tok.kind == "op" and tok.value == "=":
            self._next()
            rhs = self._parse_expr()
            # Keep the sides exactly as written (do not move terms around).
            result = sp.Eq(lhs, rhs, evaluate=False)
        else:
            result = lhs
        if self._peek() is not None:
            raise LatexParseError(f"Unexpected trailing token {self._peek()}")
        return result

    # -- grammar rules ---------------------------------------------------- #
    def _parse_expr(self):
        node = self._parse_term()
        while True:
            tok = self._peek()
            if tok and tok.kind == "op" and tok.value in "+-":
                self._next()
                rhs = self._parse_term()
                node = node + rhs if tok.value == "+" else node - rhs
            else:
                break
        return node

    def _parse_term(self):
        node = self._parse_factor()
        while True:
            tok = self._peek()
            if tok is None:
                break
            if tok.kind == "op" and tok.value == "/":
                self._next()
                node = node / self._parse_factor()
            elif tok.kind == "op" and tok.value == "*":
                self._next()
                node = node * self._parse_factor()
            elif self._starts_factor(tok):
                node = node * self._parse_factor()
            else:
                break
        return node

    def _starts_factor(self, tok: Token) -> bool:
        if tok.kind in ("num", "sym"):
            return True
        if tok.kind == "op" and tok.value in "({":
            return True
        if tok.kind == "cmd":
            return True
        return False

    def _parse_factor(self):
        sign = 1
        while True:
            tok = self._peek()
            if tok and tok.kind == "op" and tok.value in "+-":
                if tok.value == "-":
                    sign = -sign
                self._next()
            else:
                break
        node = self._parse_power()
        return -node if sign == -1 else node

    def _parse_power(self):
        base = self._parse_atom()
        tok = self._peek()
        if tok and tok.kind == "op" and tok.value == "^":
            self._next()
            exponent = self._parse_atom()
            base = base ** exponent
        return base

    def _parse_atom(self):
        tok = self._peek()
        if tok is None:
            raise LatexParseError("Unexpected end of expression")

        if tok.kind == "num":
            self._next()
            return sp.Number(tok.value)

        if tok.kind == "op" and tok.value == "(":
            self._next()
            node = self._parse_expr()
            self._expect("op", ")")
            return node

        if tok.kind == "op" and tok.value == "[":
            self._next()
            node = self._parse_expr()
            self._expect("op", "]")
            return node

        if tok.kind == "op" and tok.value == "{":
            self._next()
            node = self._parse_expr()
            self._expect("op", "}")
            return node

        if tok.kind == "cmd":
            return self._parse_command()

        if tok.kind == "sym":
            self._next()
            return self._finish_symbol(tok.value)

        raise LatexParseError(f"Unexpected token {tok}")

    def _parse_command(self):
        name = self._next().value

        if name == "frac" or name == "dfrac" or name == "tfrac":
            numer = self._parse_group()
            denom = self._parse_group()
            return numer / denom

        if name == "sqrt":
            index = None
            tok = self._peek()
            if tok and tok.kind == "op" and tok.value == "[":
                self._next()
                index = self._parse_expr()
                self._expect("op", "]")
            radicand = self._parse_group()
            if index is None:
                return sp.sqrt(radicand)
            return radicand ** (1 / index)

        if name in _FUNCTIONS:
            func = _FUNCTIONS[name]
            arg = self._parse_atom()
            return func(arg)

        if name in _ACCENTS:
            suffix = _ACCENTS[name]
            base_name = self._read_name_group()
            full = f"{base_name}_{suffix}" if suffix else base_name
            return self._finish_symbol(full, already_named=True)

        if name == "pi":
            return sp.pi

        if name in _GREEK:
            return self._finish_symbol(_GREEK[name], already_named=True)

        # Unknown command: treat its name as a symbol base.
        return self._finish_symbol(name, already_named=True)

    # -- helpers for symbols / groups ------------------------------------ #
    def _parse_group(self):
        """Parse a mandatory ``{ ... }`` argument (or a single atom)."""
        tok = self._peek()
        if tok and tok.kind == "op" and tok.value == "{":
            self._next()
            node = self._parse_expr()
            self._expect("op", "}")
            return node
        return self._parse_atom()

    def _finish_symbol(self, base: str, already_named: bool = False):
        """Attach an optional ``_subscript`` to a symbol base and build it."""
        name = base
        tok = self._peek()
        if tok and tok.kind == "op" and tok.value == "_":
            self._next()
            sub = self._read_name_group()
            name = f"{base}_{sub}"
        return self._sym(name)

    def _read_name_group(self) -> str:
        """Read a group/atom purely as an identifier string (for sub/superscripts).

        ``{s t}`` -> ``st``, ``{U}`` -> ``U``, ``\\lambda`` -> ``lamda``.
        """
        tok = self._peek()
        if tok is None:
            raise LatexParseError("Expected a name group")

        if tok.kind == "op" and tok.value == "{":
            self._next()
            parts: List[str] = []
            while True:
                inner = self._peek()
                if inner is None:
                    raise LatexParseError("Unterminated '{' in name group")
                if inner.kind == "op" and inner.value == "}":
                    self._next()
                    break
                parts.append(self._read_name_token())
            return "".join(parts)

        return self._read_name_token()

    def _read_name_token(self) -> str:
        tok = self._next()
        if tok.kind == "num":
            return tok.value
        if tok.kind == "sym":
            return tok.value
        if tok.kind == "cmd":
            if tok.value in _GREEK:
                return _GREEK[tok.value]
            return tok.value
        if tok.kind == "op":
            if tok.value == "{":
                self.pos -= 1
                return self._read_name_group()
            if tok.value == "-":
                return "m"  # e.g. superscript -1 handled elsewhere; defensive
            # ignore other punctuation inside identifiers
            return ""
        raise LatexParseError(f"Cannot use {tok} inside an identifier")


# --------------------------------------------------------------------------- #
# High level API
# --------------------------------------------------------------------------- #

def _to_python_source(expr) -> str:
    """Render a SymPy expression as Python source using bare function names.

    SymPy's default string printer already emits ``sqrt(x)``, ``exp(x)``,
    ``tan(x)`` and ``a**b`` -- i.e. valid Python -- as long as those names are in
    scope (see :data:`MATH_NAMESPACE`).  This avoids the ``math.``/``numpy.``
    prefixes that the code printers add.
    """
    return sp.sstr(expr, full_prec=False)


@dataclass
class Equation:
    """A translated equation with SymPy, Python-source and callable views."""

    latex: str
    expr: object  # sympy Eq or Expr
    symbols: Dict[str, sp.Symbol]
    tag: Optional[str] = None
    lhs: object = field(default=None)
    rhs: object = field(default=None)

    def __post_init__(self):
        if isinstance(self.expr, sp.Equality):
            self.lhs, self.rhs = self.expr.lhs, self.expr.rhs
        else:
            self.lhs, self.rhs = None, self.expr

    # -- views ------------------------------------------------------------ #
    @property
    def inputs(self) -> List[sp.Symbol]:
        """Free symbols on the right-hand side, i.e. the function arguments."""
        target = self.rhs if self.rhs is not None else self.expr
        result = self.lhs if isinstance(self.lhs, sp.Symbol) else None
        syms = sorted(target.free_symbols, key=lambda s: s.name)
        return [s for s in syms if s is not result]

    @property
    def output(self) -> Optional[sp.Symbol]:
        return self.lhs if isinstance(self.lhs, sp.Symbol) else None

    @property
    def python(self) -> str:
        """A single-line ``lhs = rhs`` (or just ``rhs``) Python expression."""
        rhs_src = _to_python_source(self.rhs if self.rhs is not None else self.expr)
        if self.output is not None:
            return f"{self.output.name} = {rhs_src}"
        return rhs_src

    def function_source(self, name: Optional[str] = None) -> str:
        """Return the source of a stand-alone Python function for this equation."""
        fname = name or self._default_name()
        args = ", ".join(s.name for s in self.inputs)
        rhs_src = _to_python_source(self.rhs if self.rhs is not None else self.expr)
        doc = self.latex.replace("\\", "\\\\")
        lines = [
            f"def {fname}({args}):",
            f'    """{self.output.name if self.output else "value"} '
            f'= {rhs_src}',
            f"",
            f"    LaTeX: {doc}",
            f'    """',
            f"    return {rhs_src}",
        ]
        return "\n".join(lines)

    def _default_name(self) -> str:
        if self.tag:
            slug = re.sub(r"\W+", "_", self.tag).strip("_")
            return f"eq_{slug}" if slug else "equation"
        if self.output is not None:
            return self.output.name.replace(".", "_")
        return "equation"

    def evaluate(self, **values):
        """Numerically evaluate the right-hand side given keyword values."""
        func = self.callable()
        missing = [s.name for s in self.inputs if s.name not in values]
        if missing:
            raise TypeError(f"Missing values for: {', '.join(missing)}")
        return func(*[values[s.name] for s in self.inputs])

    def callable(self) -> Callable:
        """A NumPy-backed callable ``f(*inputs)`` for the right-hand side."""
        target = self.rhs if self.rhs is not None else self.expr
        return sp.lambdify(self.inputs, target, modules=["numpy"])

    def __str__(self) -> str:
        tag = f" (Eq. {self.tag})" if self.tag else ""
        return f"{self.python}{tag}"


def translate(latex: str, tag: Optional[str] = None) -> Equation:
    """Translate a single LaTeX math fragment into an :class:`Equation`."""
    cleaned = preprocess(latex)
    if not cleaned:
        raise LatexParseError("Empty expression after preprocessing")
    tokens = tokenize(cleaned)
    parser = Parser(tokens)
    try:
        expr = parser.parse()
    except LatexParseError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise LatexParseError(f"Failed to parse {latex!r}: {exc}") from exc
    return Equation(latex=latex.strip(), expr=expr, symbols=parser.symbols, tag=tag)


def translate_document(text: str) -> List[Tuple[RawEquation, Optional[Equation], Optional[str]]]:
    """Translate every equation in a document.

    Returns a list of ``(raw, equation, error)`` triples so callers can report
    on fragments that could not be parsed instead of aborting the whole run.
    """
    results = []
    for raw in extract_equations(text):
        try:
            eq = translate(raw.latex, tag=raw.tag)
            results.append((raw, eq, None))
        except LatexParseError as exc:
            results.append((raw, None, str(exc)))
    return results


def generate_module(text: str, module_doc: str = "") -> str:
    """Translate all equations in ``text`` and return runnable Python source.

    The returned string is a complete module: NumPy imports followed by one
    function per successfully parsed equation.  Equations that fail to parse are
    recorded as comments so nothing is silently dropped.
    """
    header = ['"""' + (module_doc or "Auto-generated by ExecuSci latex2python.") + '"""',
              "", _NAMESPACE_IMPORT.rstrip(), "", ""]
    body: List[str] = []
    used_names: Dict[str, int] = {}
    for raw, eq, error in translate_document(text):
        if error is not None or eq is None:
            body.append(f"# Could not translate (Eq. {raw.tag}): {raw.latex}")
            if error:
                body.append(f"#   reason: {error}")
            body.append("")
            continue
        name = eq._default_name()
        # Disambiguate duplicate names (several equations define ``h`` etc.).
        if name in used_names:
            used_names[name] += 1
            name = f"{name}_{used_names[name]}"
        else:
            used_names[name] = 1
        body.append(eq.function_source(name=name))
        body.append("")
        body.append("")
    return "\n".join(header + body).rstrip() + "\n"
