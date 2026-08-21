"""LaTeX math -> Python / SymPy translator for ExecuSci.

Stage 02 uses this to split each display equation into an output, inputs, and a
one-line Python preview.  Stage 04 re-exports the same API from
``translate2python`` and turns the parsed equations into ``equations.py``.

It does **not** rely on SymPy's own ``parse_latex`` (whose ANTLR/Lark backends
choke on the real-world LaTeX found in papers -- multi-character subscripts
like ``k_{s t}``, placeholder superscripts like ``R_{s}{ }^{2}``, bare
``\\tan \\theta``, ``\\left( ... \\right)`` and accents like ``\\bar{\\lambda}``).

Typical use::

    from translator import translate
    eq = translate(r"h=1.45 k \\frac{\\tan \\theta}{\\sigma}"
                   r"\\left(\\frac{p}{H}\\right)^{0.985}")
    print(eq.python)          # h = 1.45*k*(p/H)**0.985*tan(theta)/sigma
    print(eq.evaluate(k=1, theta=0.1, sigma=2, p=3, H=4))
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

import sympy as sp

__all__ = [
    "Equation",
    "translate",
    "preprocess",
    "tokenize",
    "Parser",
    "name_to_latex",
    "latex_to_name",
    "MATH_NAMESPACE",
    "LatexParseError",
]


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
# Preprocessing
# --------------------------------------------------------------------------- #

_TAG_RE = re.compile(r"\\tag\{(?P<tag>[^}]*)\}")
_LABEL_RE = re.compile(r"\\label\{[^}]*\}")


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

# Token kinds: num = number, sym = symbol (variable),
# cmd = command (e.g. \frac, \sqrt),
# op = operator (e.g. +, -, *, /, ^, _, (, ), {, }, [, ], =).

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


# Operators with no algebraic Python form here.  Left to the tokenizer they would
# quietly become invented symbols -- ``\int_{0}^{t}`` reads as ``int_0**t`` and
# ``\sum_{i=1}^{m}`` as ``sum_i1**m`` -- so an equation that uses one is reported
# as untranslatable instead of producing plausible-looking nonsense.
_UNSUPPORTED_OPERATORS = {
    "int": "an integral (\\int)",
    "iint": "a double integral (\\iint)",
    "iiint": "a triple integral (\\iiint)",
    "oint": "a contour integral (\\oint)",
    "sum": "a summation (\\sum)",
    "prod": "a product (\\prod)",
    "lim": "a limit (\\lim)",
    "partial": "a partial derivative (\\partial)",
}


def _reject_unsupported(tokens: List[Token]) -> None:
    """Raise for constructs the parser cannot represent faithfully.

    Differentials are detected on the token stream rather than the raw LaTeX, so
    ``d t`` is caught while ``\\delta`` (a single command token) is not.
    """
    for index, tok in enumerate(tokens):
        if tok.kind == "cmd" and tok.value in _UNSUPPORTED_OPERATORS:
            raise LatexParseError(f"{_UNSUPPORTED_OPERATORS[tok.value]} is not supported")
        if tok.kind == "sym" and tok.value == "d":
            following = tokens[index + 1] if index + 1 < len(tokens) else None
            if following is not None and following.kind in ("sym", "cmd"):
                raise LatexParseError(
                    f"a differential (d {following.value}) is not supported"
                )


# --------------------------------------------------------------------------- #
# Parser (recursive descent)
# --------------------------------------------------------------------------- #

class Parser:
    r"""Recursive-descent parser turning a token stream into a SymPy expression.

    Grammar (informal)::

        equation := expr ('=' expr)*
        expr     := term (('+' | '-') term)*
        term     := factor ( ('/' | '*') factor | <implicit> factor )*
        factor   := ('+' | '-')* power
        power    := atom ('^' atom)?
        atom     := number | symbol | '(' expr ')' | '{' expr '}'
                  | \frac{expr}{expr} | \sqrt[expr]{expr} | func atom | accent atom
        symbol   := name ('_' name)? ('(' name ')')?
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.symbols: Dict[str, sp.Symbol] = {}
        #: ``name -> argument`` for symbols the paper writes as ``name(argument)``.
        self.dependencies: Dict[str, str] = {}
        #: Every member of a chained equality ``a = b = c``, in order.
        self.chain: List[object] = []

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
        """Parse the token stream into a SymPy ``Eq`` (or a bare expression).

        Papers often chain equalities to show their working, e.g.
        ``\\dot{h}(t) = \\dot{V}(t)/A = -h(t)(...)``.  Every member is parsed;
        the equation itself is the first member against the *last* (the one the
        paper evaluates), and the members in between are kept in
        :attr:`chain` as identities worth documenting.
        """
        members = [self._parse_expr()]
        while True:
            tok = self._peek()
            if tok is None or tok.kind != "op" or tok.value != "=":
                break
            self._next()
            members.append(self._parse_expr())
        if self._peek() is not None:
            raise LatexParseError(f"Unexpected trailing token {self._peek()}")

        self.chain = members
        if len(members) == 1:
            return members[0]
        # Keep the sides exactly as written (do not move terms around).
        return sp.Eq(members[0], members[-1], evaluate=False)

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
        """Attach an optional ``_subscript`` and function argument to a symbol."""
        name = base
        tok = self._peek()
        if tok and tok.kind == "op" and tok.value == "_":
            self._next()
            sub = self._read_name_group()
            name = f"{base}_{sub}"

        argument = self._peek_call_argument()
        if argument is not None:
            self.pos += 3  # '(', argument, ')'
            if argument.kind == "num":
                # ``V(0)`` is the value at that argument, i.e. its own quantity.
                name = f"{name}_{argument.value}"
            else:
                # ``\mu_{l}(t)`` is just ``mu_l``; the dependence on ``t`` is
                # recorded rather than turned into a factor of ``t``.
                self.dependencies.setdefault(name, argument.value)
        return self._sym(name)

    def _peek_call_argument(self) -> Optional[Token]:
        """The argument of ``symbol(argument)`` notation, if that is what follows.

        Only a *single* symbol or number counts, so the function-of notation in
        ``T(t)`` and ``V(0)`` is recognised while implicit multiplication such as
        ``A(1-\\exp (-B P))`` or ``F(\\sigma_{22}-\\sigma_{33})`` is left alone.
        """
        if self.pos + 3 > len(self.tokens):
            return None
        opening, argument, closing = self.tokens[self.pos : self.pos + 3]
        if opening.kind != "op" or opening.value != "(":
            return None
        if closing.kind != "op" or closing.value != ")":
            return None
        return argument if argument.kind in ("num", "sym") else None

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
    #: ``name -> argument`` for quantities the paper writes as ``name(argument)``.
    depends_on: Dict[str, str] = field(default_factory=dict)
    #: Intermediate members of a chained equality, e.g. ``\\dot{V}(t)/A``.
    identities: List[object] = field(default_factory=list)

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
        notes = self._notation_notes()
        if notes:
            lines.append("")
            lines.extend(notes)
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

    def _notation_notes(self) -> List[str]:
        """Docstring lines for the notation the translation had to normalise."""
        notes: List[str] = []
        by_argument: Dict[str, List[str]] = {}
        for symbol_name, argument in self.depends_on.items():
            by_argument.setdefault(argument, []).append(symbol_name)
        for argument in sorted(by_argument):
            written = ", ".join(f"{n}({argument})" for n in sorted(by_argument[argument]))
            notes.append(f"    The paper writes as functions of {argument}: {written}")
        left = (
            self.output.name
            if self.output is not None
            else (_to_python_source(self.lhs) if self.lhs is not None else "value")
        )
        for identity in self.identities:
            notes.append(f"    Also given as: {left} = {_to_python_source(identity)}")
        return notes

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
    _reject_unsupported(tokens)
    parser = Parser(tokens)
    try:
        expr = parser.parse()
    except LatexParseError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise LatexParseError(f"Failed to parse {latex!r}: {exc}") from exc
    return Equation(
        latex=latex.strip(),
        expr=expr,
        symbols=parser.symbols,
        tag=tag,
        depends_on=dict(parser.dependencies),
        identities=list(parser.chain[1:-1]),
    )


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
