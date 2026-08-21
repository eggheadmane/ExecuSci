"""Stage 05 DAG: last definition of the y-symbol, reduction, cycles."""

from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from execusci_paths import add_stages, paper_path  # noqa: E402

add_stages("Extract Equations", "Translate2Python", "Plotting")

from equation_graph import CycleError, EquationGraph  # noqa: E402
from extract_equations import extract  # noqa: E402

PAPER = paper_path()


@pytest.fixture(scope="module")
def graph() -> EquationGraph:
    with open(PAPER, "r", encoding="utf-8") as fh:
        extraction = extract(fh.read(), source=PAPER)
    return EquationGraph.from_json(extraction.to_json())


def test_last_definition_of_h_is_equation_6(graph: EquationGraph):
    assert graph.last_defining("h").tag == "6"


def test_literature_definitions_of_h_are_dropped(graph: EquationGraph):
    system = graph.reduce(y_symbol="h")
    assert system.target.tag == "6"
    assert "1" not in system.tags
    assert "2" not in system.tags
    assert "4" not in system.tags
    assert "5" not in system.tags


def test_reduced_ihtc_chain_is_equations_6_to_13(graph: EquationGraph):
    system = graph.reduce(y_symbol="h")
    assert set(system.tags) == {"6", "7", "8", "9", "10", "11", "12", "13"}
    assert system.tags.index("8") < system.tags.index("7")
    assert system.tags.index("7") < system.tags.index("6")
    assert system.tags.index("13") < system.tags.index("11")
    assert system.tags.index("11") < system.tags.index("6")
    assert "P" in system.leaves
    assert "delta" in system.leaves


def test_eq_tag_override_uses_that_definition(graph: EquationGraph):
    system = graph.reduce(eq_tag="4")
    assert system.target.tag == "4"
    assert system.tags == ["4"]
    assert set(system.leaves) == {"A", "B", "P"}


def test_cycle_is_reported():
    payload = {
        "equations": [
            {"tag": "1", "output": "a", "inputs": ["b"], "error": None, "python": "a = b"},
            {"tag": "2", "output": "b", "inputs": ["a"], "error": None, "python": "b = a"},
        ],
        "symbols": {},
    }
    with pytest.raises(CycleError, match="Cycle in equation graph"):
        EquationGraph.from_json(payload)


def test_failed_equations_are_ignored():
    payload = {
        "equations": [
            {
                "tag": "1",
                "output": None,
                "inputs": [],
                "error": "an integral is not supported",
                "python": None,
            },
            {
                "tag": "2",
                "output": "y",
                "inputs": ["x"],
                "error": None,
                "python": "y = x",
            },
        ],
        "symbols": {},
    }
    graph = EquationGraph.from_json(payload)
    system = graph.reduce(y_symbol="y")
    assert system.tags == ["2"]
