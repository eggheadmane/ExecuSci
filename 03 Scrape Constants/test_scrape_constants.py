"""Tests for scraping paper constants from Mathpix markdown tables / prose."""

from __future__ import annotations

import math
import os
import sys

import pytest
import sympy as sp

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from execusci_paths import add_stages, paper_path  # noqa: E402

add_stages("Scrape Constants", "Latex2Python")

from scrape_constants import (  # noqa: E402
    extract_constants,
    generate_constants_module,
    generate_report,
    latex_to_name,
    parse_number,
    run,
)

PAPER = paper_path()


TABLE3_SNIPPET = """
Table 3
Material constants and model parameters of IHTC model.
| $k_{s}(\\mathrm{~kW} / \\mathrm{mK})$ | $k_{t}$ (H13) | $k_{\\mathrm{t}}$ (Cast iron) | $k_{t}$ (P20) | $k_{l}$ (Lubricant) |
| :--- | :--- | :--- | :--- | :--- |
| 0.14 | 0.0244 | 0.044 | 0.0315 | 0.024 |
| $R_{s}(\\mathrm{~m})$ | $R_{t}$ (H13) | $R_{t}$ (Cast iron) | $R_{t}$ (P20) | $h_{a}\\left(\\mathrm{~kW} / \\mathrm{m}^{2} \\mathrm{~K}\\right)$ |
| $3.4 \\mathrm{e}-7$ | $9.8 \\mathrm{e}-7$ | $8.1 \\mathrm{e}-7$ | $9.6 \\mathrm{e}-7$ | 0.8 |
| $\\sigma_{U}$ | $\\alpha(-)$ | $\\lambda(-)$ | $\\beta(-)$ | $\\gamma\\left(\\mathrm{m}^{-1}\\right)$ |
| 21 | $2.01 \\mathrm{e}-4$ | 6.05 | $1.1 \\mathrm{e}-4$ | 2e5 |
"""

TABLE2_SNIPPET = """
Table 2
Material properties of the specimen and tools.
| Property | AA7075 |
| :--- | :--- |
| Young's modulus (MPa) | $-39.082 \\mathrm{~T}+82532$ |
| Thermal conductivity (kW/mK) | $\\begin{gathered} -5.145 \\mathrm{e}-08 \\mathrm{~T}^{2}+1.368 \\mathrm{e}-04 \\mathrm{~T} \\\\ +0.085224 \\end{gathered}$ |


| Property | H13 | Cast iron | P20 |
| :--- | :--- | :--- | :--- |
| Young's modulus (GPa) | 210 | 101.4 | 205 |
| Density ( $\\mathrm{kg} / \\mathrm{m}^{3}$ ) | 7.8e03 | 7.15 e 03 | 7.85 e 03 |
| Thermal conductivity (kW/mK) | 0.0244 | 0.044 | 0.0315 |
| Specific heat capacity (J/kgK) | 460 | 465 | 473 |
| Poisson's ratio (-) | 0.3 | 0.29 | 0.285 |
"""


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("0.14", 0.14),
        ("21", 21.0),
        (r"$3.4 \mathrm{e}-7$", 3.4e-7),
        (r"$2.01 \mathrm{e}-4$", 2.01e-4),
        ("2e5", 2e5),
        ("7.85 e 03", 7.85e3),
        ("Bal.", None),
    ],
)
def test_parse_number(raw, expected):
    got = parse_number(raw)
    if expected is None:
        assert got is None
    else:
        assert got == pytest.approx(expected)


@pytest.mark.parametrize(
    "latex,name",
    [
        (r"k_{s}", "k_s"),
        (r"\lambda", "lamda"),
        (r"\sigma_{U}", "sigma_U"),
        (r"h_{a}", "h_a"),
        (r"\alpha", "alpha"),
        (r"R_{t}", "R_t"),
    ],
)
def test_latex_to_name(latex, name):
    assert latex_to_name(latex) == name


def test_extract_table3_shared_and_tools():
    consts = extract_constants(TABLE3_SNIPPET, include_prose=False)
    by_key = {(c.name, c.variant): c.value for c in consts}

    assert by_key[("k_s", None)] == pytest.approx(0.14)
    assert by_key[("k_l", None)] == pytest.approx(0.024)
    assert by_key[("R_s", None)] == pytest.approx(3.4e-7)
    assert by_key[("h_a", None)] == pytest.approx(0.8)
    assert by_key[("sigma_U", None)] == pytest.approx(21.0)
    assert by_key[("alpha", None)] == pytest.approx(2.01e-4)
    assert by_key[("lamda", None)] == pytest.approx(6.05)
    assert by_key[("beta", None)] == pytest.approx(1.1e-4)
    assert by_key[("gamma", None)] == pytest.approx(2e5)

    assert by_key[("k_t", "H13")] == pytest.approx(0.0244)
    assert by_key[("k_t", "P20")] == pytest.approx(0.0315)
    assert by_key[("k_t", "CastIron")] == pytest.approx(0.044)
    assert by_key[("R_t", "H13")] == pytest.approx(9.8e-7)
    assert by_key[("R_t", "P20")] == pytest.approx(9.6e-7)
    assert by_key[("R_t", "CastIron")] == pytest.approx(8.1e-7)


def test_prose_ha_constant():
    text = (
        "Therefore, it was reasonable to assume a constant value for the "
        r"null-pressure IHTC $h_{a}$ of approximately $0.8 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$, "
        "which was determined by running IHTC tests."
    )
    consts = extract_constants(text, include_prose=True)
    assert any(c.name == "h_a" and math.isclose(c.value, 0.8) for c in consts)


def test_generate_constants_module_executes_and_matches_equations_names():
    source = generate_constants_module(TABLE3_SNIPPET)
    ns: dict = {}
    exec(compile(source, "<constants>", "exec"), ns)

    get_constants = ns["get_constants"]
    consts = get_constants(tool="P20", delta=1.5e-5)

    # Names must match latex2python / equations.py argument spellings.
    assert consts["lamda"] == pytest.approx(6.05)
    assert consts["sigma_U"] == pytest.approx(21.0)
    assert consts["k_s"] == pytest.approx(0.14)
    assert consts["k_t"] == pytest.approx(0.0315)
    assert consts["R_t"] == pytest.approx(9.6e-7)
    assert consts["delta"] == pytest.approx(1.5e-5)

    h13 = get_constants(tool="H13")
    assert h13["k_t"] == pytest.approx(0.0244)

    assert set(ns["available_tools"]()) == {"CastIron", "H13", "P20"}


def test_property_table_values_per_material():
    consts = extract_constants(TABLE2_SNIPPET, include_prose=False)
    by_key = {(c.name, c.variant): c for c in consts if c.category == "material"}

    assert by_key[("E", "H13")].value == pytest.approx(210.0)
    assert by_key[("E", "H13")].unit == "GPa"
    assert by_key[("rho", "CastIron")].value == pytest.approx(7.15e3)
    assert by_key[("k", "P20")].value == pytest.approx(0.0315)
    assert by_key[("c_p", "H13")].value == pytest.approx(460.0)
    assert by_key[("nu", "P20")].value == pytest.approx(0.285)
    assert by_key[("E", "H13")].label == "Young's modulus"


def test_temperature_dependent_properties_are_not_numbers():
    """``-39.082 T + 82532`` is a function of T, not the constant -39.082."""
    consts = extract_constants(TABLE2_SNIPPET, include_prose=False)
    aa7075 = {c.name: c for c in consts if c.variant == "AA7075"}

    assert aa7075["E"].value is None
    assert aa7075["E"].expression == "-39.082 T+82532"
    # Mathpix line-break packaging is removed from the quoted expression.
    assert "gathered" not in aa7075["k"].expression
    assert aa7075["k"].expression.startswith("-5.145 e-08 T^{2}")


def test_thermal_expansion_does_not_collide_with_the_model_parameter_alpha():
    """Table 2's thermal expansion is ``alpha_t``; Table 3's parameter keeps ``alpha``."""
    with open(PAPER, "r", encoding="utf-8") as fh:
        consts = extract_constants(fh.read(), include_prose=False)
    by_key = {(c.name, c.variant): c for c in consts}

    assert by_key[("alpha_t", "AA7075")].label == "Thermal expansion"
    assert by_key[("alpha", None)].value == pytest.approx(2.01e-4)


def test_composition_table_is_not_scraped_as_constants():
    text = """
Table 1
The chemical composition of AA7075.
| Element | Si | Fe | Cu | Al |
| :--- | :--- | :--- | :--- | :--- |
| $\\mathrm{Wt} \\%$ | 0.09 | 0.13 | 1.4 | Bal. |
"""
    assert extract_constants(text, include_prose=False) == []


def test_generated_module_exposes_sympy_symbols():
    source = generate_constants_module(TABLE3_SNIPPET + TABLE2_SNIPPET)
    ns: dict = {}
    exec(compile(source, "<constants>", "exec"), ns)

    symbols = ns["SYMBOLS"]
    assert symbols["k_s"] == sp.Symbol("k_s")
    assert ns["symbol"]("lamda") == sp.Symbol("lamda")
    with pytest.raises(KeyError):
        ns["symbol"]("not_a_constant")

    # Substituting the scraped values into a symbolic equation evaluates it.
    k_s, k_t = sp.Symbol("k_s"), sp.Symbol("k_t")
    K_st = 2 / (1 / k_s + 1 / k_t)
    value = float(K_st.subs(ns["subs_map"](tool="H13")))
    assert value == pytest.approx(2 / (1 / 0.14 + 1 / 0.0244))


def test_generated_module_exposes_material_properties():
    source = generate_constants_module(TABLE3_SNIPPET + TABLE2_SNIPPET)
    ns: dict = {}
    exec(compile(source, "<constants>", "exec"), ns)

    assert set(ns["available_materials"]()) == {"CastIron", "H13", "P20"}
    assert ns["material_properties"]("P20")["rho"] == pytest.approx(7.85e3)
    with pytest.raises(ValueError):
        ns["material_properties"]("Inconel")
    # AA7075 only has temperature-dependent properties, so it has no constants.
    assert "AA7075.E" in ns["TEMPERATURE_DEPENDENT"]


def test_report_lists_sources_and_missing_values():
    report = generate_report(TABLE3_SNIPPET + TABLE2_SNIPPET, source="paper.md")
    assert "# Constants scraped from `paper.md`" in report
    assert "Table 3" in report and "Table 2" in report
    assert "Temperature-dependent properties" in report


def test_run_writes_module_and_report(tmp_path):
    constants_path = tmp_path / "constants.py"
    report_path = tmp_path / "constants.md"
    constants = run(
        paper=PAPER,
        constants_path=str(constants_path),
        report_path=str(report_path),
        verbose=False,
    )
    assert constants
    assert report_path.read_text(encoding="utf-8").startswith("# Constants scraped")

    ns: dict = {}
    exec(compile(constants_path.read_text(encoding="utf-8"), "<constants>", "exec"), ns)
    assert ns["get_constants"]("P20")["k_t"] == pytest.approx(0.0315)


def test_target_paper_table3():
    """Integration: scrape the real paper markdown."""
    with open(PAPER, "r", encoding="utf-8") as fh:
        text = fh.read()

    consts = extract_constants(text, include_prose=True)
    shared = {c.name: c.value for c in consts if c.variant is None}
    tools = {}
    for c in consts:
        if c.variant:
            tools.setdefault(c.variant, {})[c.name] = c.value

    assert shared.get("k_s") == pytest.approx(0.14)
    assert shared.get("lamda") == pytest.approx(6.05)
    assert shared.get("alpha") == pytest.approx(2.01e-4)
    assert "P20" in tools and tools["P20"]["k_t"] == pytest.approx(0.0315)
    assert "H13" in tools and tools["H13"]["R_t"] == pytest.approx(9.8e-7)


def test_compose_with_translated_equations():
    """Scraped constants plug into latex2python-evaluated IHTC pieces."""
    from latex2python import translate

    source = generate_constants_module(TABLE3_SNIPPET)
    ns: dict = {}
    exec(compile(source, "<constants>", "exec"), ns)
    c = ns["get_constants"](tool="H13")

    k_st = translate(r"K_{s t}=\frac{2}{k_{s}^{-1}+k_{t}^{-1}}").evaluate(
        k_s=c["k_s"], k_t=c["k_t"]
    )
    R = translate(r"R=\sqrt{R_{s}{ }^{2}+R_{t}{ }^{2}}").evaluate(
        R_s=c["R_s"], R_t=c["R_t"]
    )
    n_p = translate(
        r"N_{P}=1-\exp \left(-\lambda \frac{P}{\sigma_{U}}\right)"
    ).evaluate(P=7, lamda=c["lamda"], sigma_U=c["sigma_U"])
    h_c = translate(r"h_{c}=\alpha \frac{K_{s t} N_{P}}{R}").evaluate(
        K_st=k_st, N_P=n_p, R=R, alpha=c["alpha"]
    )
    assert 5.0 < h_c < 9.0
