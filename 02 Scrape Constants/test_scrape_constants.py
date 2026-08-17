"""Tests for scraping paper constants from Mathpix markdown tables / prose."""

import math

import pytest

from scrape_constants import (
    extract_constants,
    generate_constants_module,
    latex_to_name,
    parse_number,
)


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


def test_mathpix_pdf_table3_if_present():
    """Integration: scrape real Mathpix OCR of the paper when the file exists."""
    try:
        with open("mathpix_pdf.md", "r", encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        pytest.skip("mathpix_pdf.md not present")

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
