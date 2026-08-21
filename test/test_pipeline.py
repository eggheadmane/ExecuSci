"""End-to-end test: paper in, executable model out, numbers matching the paper.

Runs stages 02-04 into a temporary directory and checks that the generated
``equations.py`` and ``constants.py``, composed as the paper composes them,
reproduce the two IHTC values the paper reports for P20 tools (Section 4):
6.7 kW/m²K at 3 MPa dry, and 14.5 kW/m²K at 13 MPa with a 0.015 mm lubricant
layer.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from execusci_paths import add_stages, paper_path, stage_dir  # noqa: E402

add_stages("Extract Equations", "Scrape Constants", "Translate2Python", "Plotting")

import extract_equations  # noqa: E402
import scrape_constants  # noqa: E402
import translate2python  # noqa: E402
from equation_graph import EquationGraph  # noqa: E402

PAPER = paper_path()


def _load(name: str, path: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pipeline(tmp_path_factory):
    """Run the whole pipeline into a temp directory and load what it wrote."""
    out = tmp_path_factory.mktemp("execusci")
    extraction = extract_equations.run(
        paper=PAPER,
        out_dir=str(out),
        report_path=str(out / "equations.md"),
        verbose=False,
    )
    scrape_constants.run(
        paper=PAPER,
        constants_path=str(out / "constants.py"),
        report_path=str(out / "constants.md"),
        verbose=False,
    )
    status = translate2python.run_document(
        str(out / extract_equations.EQUATIONS_RAW_FILENAME),
        module_path=str(out / "equations.py"),
        symbols_path=str(out / extract_equations.SYMBOLS_FILENAME),
        verbose=False,
    )
    assert status == 0
    return types.SimpleNamespace(
        extraction=extraction,
        equations=_load("generated_equations", str(out / "equations.py")),
        constants=_load("generated_constants", str(out / "constants.py")),
        out=out,
    )


def ihtc(pipeline, pressure: float, tool: str, delta: float) -> float:
    """The paper's last definition of ``h``, evaluated through the DAG."""
    graph = EquationGraph.from_path(str(pipeline.out / "symbols.json"))
    consts = pipeline.constants.get_constants(tool=tool, delta=delta)
    return graph.evaluate(
        pipeline.equations,
        consts,
        x_symbol="P",
        x_value=pressure,
        y_symbol="h",
    )


def test_every_stage_produced_its_artefacts(pipeline):
    for name in ("equations.md", "equations_raw.md", "symbols.json", "constants.py", "constants.md", "equations.py"):
        assert (pipeline.out / name).exists(), f"missing {name}"
    assert pipeline.extraction.failed == []


def test_p20_dry_matches_the_paper(pipeline):
    """Paper: 6.7 kW/m²K at 3 MPa, dry, P20 tools."""
    assert ihtc(pipeline, pressure=3.0, tool="P20", delta=0.0) == pytest.approx(6.7, abs=0.1)


def test_p20_lubricated_matches_the_paper(pipeline):
    """Paper: 14.5 kW/m²K at 13 MPa with a 0.015 mm lubricant layer, P20 tools."""
    assert ihtc(pipeline, pressure=13.0, tool="P20", delta=1.5e-5) == pytest.approx(
        14.5, abs=0.1
    )


def test_lubricated_p20_curve_tracks_digitized_oracle(pipeline):
    """DAG evaluation over the WebPlotDigitizer P20 curve stays in the same ballpark."""
    import numpy as np

    csv = os.path.join(stage_dir("Plotting", root=_SRC), "data", "p20.csv")
    data = np.loadtxt(csv, delimiter=",")
    pressure, h_paper = data[:, 0], data[:, 1]
    graph = EquationGraph.from_path(str(pipeline.out / "symbols.json"))
    consts = pipeline.constants.get_constants(tool="P20", delta=1.5e-5)
    predicted = graph.evaluate_curve(
        pipeline.equations, consts, "P", pressure, y_symbol="h"
    )
    error = np.abs((predicted - h_paper) / np.maximum(np.abs(h_paper), 1e-12)) * 100.0
    assert float(np.mean(error)) < 5.0


def test_h13_plateau_matches_the_paper(pipeline):
    """Paper: the IHTC plateaus at about 8.6 kW/m²K for H13 under dry conditions."""
    plateau = ihtc(pipeline, pressure=20.0, tool="H13", delta=0.0)
    assert plateau == pytest.approx(8.6, abs=0.5)


def test_zero_pressure_falls_back_to_the_null_pressure_ihtc(pipeline):
    """With no pressure and no lubricant, only h_a remains."""
    assert ihtc(pipeline, pressure=0.0, tool="P20", delta=0.0) == pytest.approx(
        pipeline.constants.get_constants()["h_a"]
    )


def test_constants_substitute_into_the_symbolic_equations(pipeline):
    """The SymPy symbols named in stage 03 line up with the equation symbols."""
    import sympy as sp

    from translate2python import translate

    equation = translate(r"K_{s t}=\frac{2}{k_{s}^{-1}+k_{t}^{-1}}")
    value = float(equation.rhs.subs(pipeline.constants.subs_map(tool="H13")))
    assert value == pytest.approx(pipeline.equations.eq_8(0.14, 0.0244))
    assert all(isinstance(s, sp.Symbol) for s in pipeline.constants.SYMBOLS.values())


def test_generated_functions_carry_the_papers_wording(pipeline):
    doc = pipeline.equations.eq_13.__doc__
    assert "the applied lubricant layer thickness" in doc
    assert "N_L = 1 - exp(-delta*gamma)" in doc
