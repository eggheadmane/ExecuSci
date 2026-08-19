"""Reduce a paper's equations to the subgraph needed for one target variable.

Stage 02's ``symbols.json`` already records each equation's ``output`` and
``inputs``.  This module turns that into a directed acyclic graph, keeps only
the last definition of each symbol (literature surveys often redefine the
same quantity), walks the dependencies of a chosen target, and evaluates the
generated ``eq_*`` functions in topological order.
"""

from __future__ import annotations

import inspect
import json
import os
import re
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    import networkx as nx
except ImportError:  # pragma: no cover - optional for evaluation-only use
    plt = None
    nx = None


class CycleError(ValueError):
    """The equation graph contains a directed cycle."""


@dataclass(frozen=True)
class GraphEquation:
    """One successfully translated equation in the dependency graph."""

    tag: str
    output: str
    inputs: Tuple[str, ...]
    python: Optional[str] = None

    @property
    def function_name(self) -> str:
        slug = re.sub(r"\W+", "_", self.tag).strip("_")
        return f"eq_{slug}" if slug else "equation"


@dataclass
class ReducedSystem:
    """A target equation plus the ancestors needed to evaluate it."""

    target: GraphEquation
    y_symbol: str
    equations: List[GraphEquation]
    leaves: Tuple[str, ...]

    @property
    def tags(self) -> List[str]:
        return [eq.tag for eq in self.equations]


def tag_sort_key(tag: Optional[str]) -> Tuple[int, float, str]:
    """Sort paper tags so ``9`` precedes ``10`` and unnumbered tags go last."""
    if tag is None or tag == "":
        return (2, 0.0, "")
    try:
        return (0, float(tag), tag)
    except ValueError:
        match = re.match(r"(\d+(?:\.\d+)?)", tag)
        if match:
            return (1, float(match.group(1)), tag)
        return (2, 0.0, tag)


def load_symbols(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


class EquationGraph:
    """Directed dependency graph of a paper's translated equations.

    Edges run from an equation's output symbol to each input (the same
    orientation as the FYP ``EquationGraph``).  When several equations define
    the same symbol, only the highest-numbered tag is kept.
    """

    def __init__(self, payload: Mapping[str, Any]):
        self.source = payload.get("source", "")
        self.symbols: Dict[str, dict] = dict(payload.get("symbols") or {})
        self.equations: List[GraphEquation] = []
        self.by_tag: Dict[str, GraphEquation] = {}
        self.definition: Dict[str, GraphEquation] = {}
        self._edges: Dict[str, List[str]] = defaultdict(list)

        records = sorted(
            payload.get("equations") or [],
            key=lambda rec: tag_sort_key(rec.get("tag")),
        )
        for rec in records:
            if rec.get("error") or not rec.get("output") or rec.get("tag") is None:
                continue
            eq = GraphEquation(
                tag=str(rec["tag"]),
                output=str(rec["output"]),
                inputs=tuple(str(name) for name in rec.get("inputs") or []),
                python=rec.get("python"),
            )
            self.equations.append(eq)
            self.by_tag[eq.tag] = eq
            self.definition[eq.output] = eq

        for eq in self.definition.values():
            self._edges[eq.output] = [
                name for name in eq.inputs if name in self.definition
            ]

        self._assert_acyclic(list(self.definition.values()))

    @classmethod
    def from_json(cls, payload: Mapping[str, Any]) -> "EquationGraph":
        return cls(payload)

    @classmethod
    def from_path(cls, path: str) -> "EquationGraph":
        return cls(load_symbols(path))

    def defining(self, symbol: str) -> Optional[GraphEquation]:
        """The last tagged equation that defines ``symbol``, if any."""
        return self.definition.get(symbol)

    def last_defining(self, symbol: str) -> GraphEquation:
        eq = self.defining(symbol)
        if eq is None:
            known = ", ".join(sorted(self.definition)) or "<none>"
            raise LookupError(
                f"No translated equation defines {symbol!r}. Defined symbols: {known}"
            )
        return eq

    def target_equation(
        self,
        y_symbol: Optional[str] = None,
        eq_tag: Optional[str] = None,
    ) -> GraphEquation:
        """Pick the equation to reduce from.

        ``eq_tag`` wins when given.  Otherwise the last tagged equation whose
        output is ``y_symbol`` is used.
        """
        if eq_tag is not None:
            key = str(eq_tag)
            if key not in self.by_tag:
                raise LookupError(
                    f"No translated equation with tag {key!r}. "
                    f"Known: {', '.join(self.by_tag) or '<none>'}"
                )
            return self.by_tag[key]
        if not y_symbol:
            raise ValueError("Provide y_symbol or eq_tag to choose a target equation")
        return self.last_defining(y_symbol)

    def reduce(
        self,
        y_symbol: Optional[str] = None,
        eq_tag: Optional[str] = None,
    ) -> ReducedSystem:
        """BFS from the target output through derived symbols; topo-sort the result."""
        target = self.target_equation(y_symbol=y_symbol, eq_tag=eq_tag)
        y = y_symbol or target.output

        def lookup(symbol: str) -> Optional[GraphEquation]:
            if symbol == target.output:
                return target
            return self.definition.get(symbol)

        collected: Dict[str, GraphEquation] = {}
        queue: deque[str] = deque([target.output])
        while queue:
            symbol = queue.popleft()
            if symbol in collected:
                continue
            eq = lookup(symbol)
            if eq is None:
                continue
            collected[symbol] = eq
            for name in eq.inputs:
                if lookup(name) is not None and name not in collected:
                    queue.append(name)

        equations = self._topo(list(collected.values()))
        defined = set(collected)
        leaves = tuple(
            sorted(
                {
                    name
                    for eq in equations
                    for name in eq.inputs
                    if name not in defined
                }
            )
        )
        return ReducedSystem(target=target, y_symbol=y, equations=equations, leaves=leaves)

    def evaluate(
        self,
        equations_module: Any,
        constants: Mapping[str, float],
        x_symbol: str,
        x_value: float,
        y_symbol: Optional[str] = None,
        eq_tag: Optional[str] = None,
        extras: Optional[Mapping[str, float]] = None,
    ) -> float:
        """Evaluate the reduced system at one independent-variable value."""
        system = self.reduce(y_symbol=y_symbol, eq_tag=eq_tag)
        values: Dict[str, float] = {str(k): float(v) for k, v in constants.items()}
        if extras:
            values.update({str(k): float(v) for k, v in extras.items()})
        values[x_symbol] = float(x_value)

        for eq in system.equations:
            fn = _resolve_function(equations_module, eq)
            missing = [name for name in eq.inputs if name not in values]
            if missing:
                raise KeyError(
                    f"Eq. ({eq.tag}) defining {eq.output!r} is missing values for: "
                    + ", ".join(missing)
                )
            args = _call_args(fn, values)
            values[eq.output] = float(np.asarray(fn(*args), dtype=float).item())

        if system.y_symbol not in values:
            raise KeyError(f"Target {system.y_symbol!r} was not produced by the reduced system")
        return float(values[system.y_symbol])

    def evaluate_curve(
        self,
        equations_module: Any,
        constants: Mapping[str, float],
        x_symbol: str,
        x_values: Sequence[float],
        y_symbol: Optional[str] = None,
        eq_tag: Optional[str] = None,
        extras: Optional[Mapping[str, float]] = None,
    ) -> np.ndarray:
        """Vector of predicted ``y`` values for each entry in ``x_values``."""
        system = self.reduce(y_symbol=y_symbol, eq_tag=eq_tag)
        out = np.empty(len(x_values), dtype=float)
        for i, x in enumerate(x_values):
            try:
                out[i] = self.evaluate(
                    equations_module,
                    constants,
                    x_symbol,
                    float(x),
                    y_symbol=system.y_symbol,
                    eq_tag=system.target.tag,
                    extras=extras,
                )
            except (KeyError, TypeError, ValueError, ZeroDivisionError, FloatingPointError):
                out[i] = np.nan
        return out

    def plot(
        self,
        system: Optional[ReducedSystem] = None,
        path: Optional[str] = None,
        show: bool = False,
    ) -> Optional[str]:
        """Draw the reduced (or full) dependency graph. Returns the save path."""
        if nx is None or plt is None:
            raise ImportError("networkx and matplotlib are required to plot the graph")

        eqs = system.equations if system is not None else list(self.definition.values())
        outputs = {eq.output for eq in eqs}
        G = nx.DiGraph()
        for eq in eqs:
            G.add_node(eq.output)
        for eq in eqs:
            for name in eq.inputs:
                if name in outputs:
                    G.add_edge(eq.output, name)
                else:
                    G.add_node(name)
                    G.add_edge(eq.output, name)

        title = "Equation dependency graph"
        if system is not None:
            title = f"{system.y_symbol} (Eq. {system.target.tag}) dependency graph"

        pos = nx.spring_layout(G, seed=0, k=1.2)
        fig, ax = plt.subplots(figsize=(10, 8))
        nx.draw_networkx(
            G,
            pos,
            ax=ax,
            with_labels=True,
            node_size=2200,
            node_color="#cfe8ff",
            font_size=9,
            arrows=True,
        )
        ax.set_title(title)
        ax.axis("off")
        fig.tight_layout()
        saved = None
        if path:
            os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
            fig.savefig(path)
            saved = path
        if show:
            plt.show()
        else:
            plt.close(fig)
        return saved

    def _assert_acyclic(self, equations: Sequence[GraphEquation]) -> None:
        outputs = {eq.output for eq in equations}
        adj = {
            eq.output: [name for name in eq.inputs if name in outputs]
            for eq in equations
        }
        WHITE, GRAY, BLACK = 0, 1, 2
        colour = {node: WHITE for node in adj}
        stack: List[str] = []

        def dfs(node: str) -> None:
            colour[node] = GRAY
            stack.append(node)
            for nxt in adj[node]:
                if colour[nxt] == GRAY:
                    start = stack.index(nxt)
                    cycle = stack[start:] + [nxt]
                    raise CycleError("Cycle in equation graph: " + " -> ".join(cycle))
                if colour[nxt] == WHITE:
                    dfs(nxt)
            stack.pop()
            colour[node] = BLACK

        for node in adj:
            if colour[node] == WHITE:
                dfs(node)

    def _topo(self, equations: Sequence[GraphEquation]) -> List[GraphEquation]:
        """Return ``equations`` in evaluation order (dependencies first)."""
        self._assert_acyclic(equations)
        by_output = {eq.output: eq for eq in equations}
        indegree = {eq.output: 0 for eq in equations}
        children: Dict[str, List[str]] = {eq.output: [] for eq in equations}
        for eq in equations:
            for name in eq.inputs:
                if name in by_output:
                    indegree[eq.output] += 1
                    children[name].append(eq.output)

        queue = deque(sorted((o for o, d in indegree.items() if d == 0)))
        ordered: List[GraphEquation] = []
        while queue:
            output = queue.popleft()
            ordered.append(by_output[output])
            for child in children[output]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)

        if len(ordered) != len(equations):
            raise CycleError("Could not topologically sort the reduced equations")
        return ordered


def _resolve_function(module: Any, eq: GraphEquation) -> Callable:
    fn = getattr(module, eq.function_name, None)
    if fn is None:
        raise AttributeError(
            f"{getattr(module, '__name__', 'equations')} has no {eq.function_name} "
            f"(needed for Eq. ({eq.tag}) defining {eq.output})"
        )
    return fn


def _call_args(fn: Callable, values: Mapping[str, float]) -> List[float]:
    """Bind ``values`` to ``fn``'s named parameters, ignoring *args/**kwargs."""
    try:
        signature = inspect.signature(fn)
    except (TypeError, ValueError):
        return [values[name] for name in values]
    args: List[float] = []
    for name, param in signature.parameters.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        if name not in values:
            if param.default is not inspect.Parameter.empty:
                continue
            raise KeyError(f"Missing value for argument {name!r} of {fn.__name__}")
        args.append(float(values[name]))
    return args
