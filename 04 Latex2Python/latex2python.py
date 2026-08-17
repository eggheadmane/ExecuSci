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
    "RawEquation",
    "translate",
    "translate_document",
    "extract_equations",
    "preprocess",
    "tokenize",
    "Parser",
    "generate_module",
    "name_to_latex",
    "latex_to_name",
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

# Commands that decorate the following symbol.  Several LaTeX spellings share a
# suffix on purpose (``\bar`` and ``\overline`` both read as "bar"), so the
# generated name does not depend on which spelling the OCR produced:
# ``\bar{\lambda}`` and ``\overline{\lambda}`` are both ``lamda_bar``.
# An empty suffix marks a purely cosmetic wrapper (``\mathrm{t}`` -> ``t``).
_ACCENTS = {
    "bar": "bar", "overline": "bar", "hat": "hat", "widehat": "hat",
    "tilde": "tilde", "widetilde": "tilde", "vec": "vec", "dot": "dot",
    "ddot": "ddot", "overrightarrow": "vec", "mathbf": "", "boldsymbol": "",
    "mathrm": "", "text": "", "operatorname": "",
}

# Reverse tables used by :func:`name_to_latex` to render a name as math again.
_GREEK_LATEX = {
    "lamda": r"\lambda", "Lamda": r"\Lambda",
    **{v: "\\" + k for k, v in reversed(list(_GREEK.items())) if v != "lamda"},
}
_ACCENT_LATEX = {"bar", "hat", "tilde", "vec", "dot", "ddot"}

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
    """A LaTeX equation extracted from a document, before translation.

    ``source_line`` is the 1-based line of the document the equation was found
    on; the extraction report written by the "Extract Equations" stage cites it
    so a reader can trace every equation back to the paper.
    """

    latex: str
    tag: Optional[str] = None
    source_line: Optional[int] = None


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1       # Counts how many \n before the index, +1 for 1-based line number


def extract_equations(text: str) -> List[RawEquation]:
    """Return every LaTeX display equation found in ``text``.

    Handles ``\\begin{equation*}`` style environments (optionally wrapped in
    ``$$ ... $$``) as well as bare ``$$ ... $$`` blocks.  The ``\\tag{...}``
    number, if present, is captured separately and stripped from the math.
    """
    found: List[RawEquation] = []
    consumed: List[Tuple[int, int]] = []

    for m in _EQ_ENV_RE.finditer(text):
        body = m.group("body")      # .group is how you access the matched text from the regex
        tag_m = _TAG_RE.search(body)
        tag = tag_m.group("tag").strip() if tag_m else None
        found.append(
            RawEquation(latex=_clean_body(body), tag=tag, source_line=_line_of(text, m.start()))
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
                RawEquation(latex=cleaned, tag=tag, source_line=_line_of(text, m.start()))
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


def _tag_number(tag: Optional[str]) -> Optional[float]:
    """Numeric value of a ``\\tag{...}``, or ``None`` if it is not a number."""
    if tag is None:
        return None
    try:
        return float(tag)
    except ValueError:
        return None

# Removes \tag / \label from a body and strips whitespace.
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

@dataclass      # The reason why the Token class looks like this is because it is used to represent the tokens that are generated by the tokenizer. Each token has a kind (which can be 'num', 'sym', 'cmd', or 'op') and a value (which is the actual string representation of the token).
class Token:
    kind: str  # 'num', 'sym', 'cmd', 'op'
    value: str

"""
num = number
sym = symbol (variable)
cmd = command (e.g. \frac, \sqrt)
op = operator (e.g. +, -, *, /, ^, _, (, ), {, }, [, ], =)
"""

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

        # Check if the current character is a digit or a decimal point, indicating the start of a number.
        m = _NUMBER_RE.match(s, i)
        if m:
            tokens.append(Token("num", m.group()))
            i = m.end()
            continue

        # Check if the current character is a backslash, indicating the start of a LaTeX command.
        if c == "\\":
            m = _COMMAND_RE.match(s, i)
            if not m:
                raise LatexParseError(f"Dangling backslash at position {i}: {s[i:i+10]!r}")
            tokens.append(Token("cmd", m.group()[1:]))  # store name without backslash
            i = m.end()
            continue

        # Check if the current character is an operator (e.g., +, -, *, /, ^, _, (, ), {, }, [, ], =).
        if c in _OPS:
            tokens.append(Token("op", c))
            i += 1
            continue

        # Check if the current character is an alphabetic character, indicating the start of a symbol (variable).
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

    # Returns the current token WITHOUT advancing the position.
    def _peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    # Returns current token and advances the position.
    def _next(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    # Returns the current token if it matches the expected kind and value, otherwise raises an error.
    def _expect(self, kind: str, value: str) -> Token:
        tok = self._peek()
        if tok is None or tok.kind != kind or tok.value != value:
            raise LatexParseError(f"Expected {value!r} but found {tok}")
        return self._next()

    # Turns to SymPy symbol, caching so repeated names are the same object.
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

    # Expression is the last part of the parser that handles the addition and subtraction of terms. 
    # It starts by parsing a term, and then enters a loop where it checks for the presence of '+' or '-' operators. 
    # If it finds one, it consumes the operator and parses the next term, combining it with the previous term using the appropriate operation (addition or subtraction). 
    # This continues until there are no more '+' or '-' operators, at which point it returns the resulting expression.

    def _parse_expr(self):
        node = self._parse_term()
        while True:
            tok = self._peek()

            # If there is token and it is an operator and the operator is either '+' or '-':
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
        if tok.kind == "op" and tok.value in "({[":
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
            # Cosmetic wrappers inside an identifier carry no name of their own:
            # ``K_{\text {stl }}`` must read as ``K_stl``, not ``K_textstl``.
            if tok.value in _ACCENTS and not _ACCENTS[tok.value]:
                return self._read_name_group()
            if tok.value in _ACCENTS:
                return f"{self._read_name_group()}_{_ACCENTS[tok.value]}"
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

def _docsafe(text: Optional[str]) -> Optional[str]:
    """Flatten a scraped description so it can sit inside a docstring."""
    if not text:
        return None
    flat = re.sub(r"\s+", " ", text).strip()
    flat = flat.replace("\\", "\\\\").replace('"""', "'''")
    return flat or None


def name_to_latex(name: str) -> str:
    r"""Render a generated symbol name back as LaTeX math (without ``$``).

    The inverse of the naming rules used by the parser, so reports can show the
    paper's notation next to the Python identifier::

        name_to_latex("sigma_U")   -> '\sigma_{U}'
        name_to_latex("lamda_bar") -> '\bar{\lambda}'
        name_to_latex("K_stl")     -> 'K_{stl}'
    """
    base, *parts = name.split("_")
    accents = []
    while parts and parts[-1] in _ACCENT_LATEX:
        accents.append(parts.pop())
    core = _GREEK_LATEX.get(base, base)
    if parts:
        core = f"{core}_{{{''.join(parts)}}}"
    for accent in accents:
        core = f"\\{accent}{{{core}}}"
    return core


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

    # If output is on RHS like ``f(...) = y``, flip LHS and RHS.  
    def __post_init__(self):
        if isinstance(self.expr, sp.Equality):
            lhs, rhs = self.expr.lhs, self.expr.rhs
            
            if isinstance(rhs, sp.Symbol) and not isinstance(lhs, sp.Symbol):
                lhs, rhs = rhs, lhs
                self.expr = sp.Eq(lhs, rhs, evaluate=False)
            self.lhs, self.rhs = lhs, rhs
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

    def function_source(
        self,
        name: Optional[str] = None,
        descriptions: Optional[Dict[str, str]] = None,
    ) -> str:
        """Return the source of a stand-alone Python function for this equation.

        ``descriptions`` maps symbol names to the wording the paper uses for
        them (as collected by the "Extract Equations" stage); matching symbols
        are documented as ``Args`` entries.
        """
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
        ]
        described = [(s.name, _docsafe((descriptions or {}).get(s.name))) for s in self.inputs]
        if any(text for _, text in described):
            lines.append("")
            lines.append("    Args:")
            for sym, text in described:
                lines.append(f"        {sym}: {text}" if text else f"        {sym}")
        out_doc = (
            _docsafe(descriptions.get(self.output.name))
            if descriptions and self.output is not None
            else None
        )
        if out_doc:
            lines.append("")
            lines.append("    Returns:")
            lines.append(f"        {self.output.name}: {out_doc}")
        lines.append('    """')
        lines.append(f"    return {rhs_src}")
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


def latex_to_name(latex: str) -> Optional[str]:
    """Map a LaTeX symbol fragment to the ASCII name used for Python code.

    ``k_{s}`` -> ``k_s``, ``\\lambda`` -> ``lamda``, ``K_{\\text {stl }}`` ->
    ``K_stl``.  Returns ``None`` when the fragment is not a single symbol (a
    number, a whole equation, a unit, ...).
    """
    frag = latex.strip()
    if not frag:
        return None
    try:
        eq = translate(frag)
    except LatexParseError:
        return None
    expr = eq.expr
    if getattr(expr, "is_Symbol", False):
        return str(expr.name)
    free = list(getattr(expr, "free_symbols", []) or [])
    if len(free) == 1:
        return free[0].name
    if eq.output is not None and not eq.inputs:
        return eq.output.name
    return None


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


def generate_module(
    text: str,
    module_doc: str = "",
    descriptions: Optional[Dict[str, str]] = None,
) -> str:
    """Translate all equations in ``text`` and return runnable Python source.

    The returned string is a complete module: NumPy imports followed by one
    function per successfully parsed equation.  Equations that fail to parse are
    recorded as comments so nothing is silently dropped.  ``descriptions`` maps
    symbol names to the paper's wording and is used to document the arguments.
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
        body.append(eq.function_source(name=name, descriptions=descriptions))
        body.append("")
        body.append("")
    return "\n".join(header + body).rstrip() + "\n"
