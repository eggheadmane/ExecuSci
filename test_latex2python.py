"""Tests for the ExecuSci LaTeX -> Python equation translator."""

import math

import pytest
import sympy as sp

from latex2python import (
    LatexParseError,
    extract_equations,
    generate_module,
    preprocess,
    translate,
    translate_document,
)

# The 13 equations from the source paper (markdown equation.md), keyed by tag.
PAPER_EQUATIONS = {
    "1": r"h=h_{g}+h_{c}",
    "2": r"h=1.45 k \frac{\tan \theta}{\sigma}\left(\frac{p}{H}\right)^{0.985}",
    "3": r"h=8000 \bar{\lambda}\left(\frac{p}{C \sigma_{U}} K\right)^{0.86}",
    "4": r"h=A(1-\exp (-B P))",
    "5": r"h=\frac{1-A}{h_{f}} \frac{2 k_{f} k_{t} k_{w}}{2 k_{t} k_{w}-k_{w} k_{f}-k_{f} k_{t}}",
    "6": r"h=h_{a}+h_{c}+h_{l}",
    "7": r"h_{c}=\alpha \frac{K_{s t} N_{P}}{R}",
    "8": r"K_{s t}=\frac{2}{k_{s}^{-1}+k_{t}^{-1}}",
    "9": r"R=\sqrt{R_{s}{ }^{2}+R_{t}{ }^{2}}",
    "10": r"N_{P}=1-\exp \left(-\lambda \frac{P}{\sigma_{U}}\right)",
    "11": r"h_{l}=\beta \frac{K_{s t l} N_{L}}{R}",
    "12": r"K_{s t l}=\frac{3}{k_{s}^{-1}+k_{t}^{-1}+k_{l}^{-1}}",
    "13": r"N_{L}=1-\exp (-\gamma \delta)",
}


@pytest.mark.parametrize("tag,latex", PAPER_EQUATIONS.items())
def test_every_paper_equation_parses(tag, latex):
    eq = translate(latex, tag=tag)
    assert isinstance(eq.expr, sp.Equality)
    # Right-hand side compiles to valid Python and has at least one input.
    compile(eq.python, "<eq>", "exec")
    assert eq.inputs


def test_addition_structure_preserved():
    eq = translate(PAPER_EQUATIONS["1"])
    assert eq.output.name == "h"
    assert {s.name for s in eq.inputs} == {"h_g", "h_c"}


def test_multichar_subscript_becomes_identifier():
    eq = translate(PAPER_EQUATIONS["12"])  # K_{s t l}
    assert eq.output.name == "K_stl"
    assert {s.name for s in eq.inputs} == {"k_s", "k_t", "k_l"}


def test_greek_lambda_is_not_a_python_keyword():
    eq = translate(PAPER_EQUATIONS["10"])
    # lambda -> lamda so the generated source is valid Python.
    assert "lamda" in [s.name for s in eq.inputs]
    compile(eq.function_source(), "<fn>", "exec")


def test_accent_bar_lambda():
    eq = translate(PAPER_EQUATIONS["3"])
    assert "lamda_bar" in [s.name for s in eq.inputs]


def test_placeholder_superscript_is_power():
    # R = sqrt(R_s**2 + R_t**2); the Mathpix "{ }^{2}" must become a real power.
    eq = translate(PAPER_EQUATIONS["9"])
    val = eq.evaluate(R_s=3.0, R_t=4.0)
    assert val == pytest.approx(5.0)


def test_harmonic_mean_numeric():
    eq = translate(PAPER_EQUATIONS["8"])
    # 2 / (1/a + 1/b) is the harmonic mean.
    a, b = 0.14, 0.0244
    expected = 2 / (1 / a + 1 / b)
    assert eq.evaluate(k_s=a, k_t=b) == pytest.approx(expected)


def test_exponential_law_numeric():
    eq = translate(PAPER_EQUATIONS["4"])
    A, B, P = 8.0, 0.2, 5.0
    assert eq.evaluate(A=A, B=B, P=P) == pytest.approx(A * (1 - math.exp(-B * P)))


def test_frac_and_power_precedence():
    eq = translate(PAPER_EQUATIONS["2"])
    k, theta, sigma, p, H = 2.0, 0.1, 3.0, 6.0, 4.0
    expected = 1.45 * k * (math.tan(theta) / sigma) * (p / H) ** 0.985
    assert eq.evaluate(k=k, theta=theta, sigma=sigma, p=p, H=H) == pytest.approx(expected)


def test_evaluate_missing_argument_raises():
    eq = translate(PAPER_EQUATIONS["4"])
    with pytest.raises(TypeError):
        eq.evaluate(A=1.0, B=2.0)  # missing P


def test_callable_is_vectorised():
    import numpy as np

    eq = translate(PAPER_EQUATIONS["4"])
    fn = eq.callable()
    out = fn(np.array([1.0, 2.0]), 0.2, np.array([5.0, 10.0]))
    assert out.shape == (2,)


def test_bad_input_raises_parse_error():
    with pytest.raises(LatexParseError):
        translate(r"\frac{1}{")  # unterminated


def test_extraction_from_markdown():
    with open("markdown equation.md", "r", encoding="utf-8") as fh:
        raws = extract_equations(fh.read())
    tags = [r.tag for r in raws]
    assert tags == [str(i) for i in range(1, 14)]


def test_translate_document_all_ok():
    with open("markdown equation.md", "r", encoding="utf-8") as fh:
        results = translate_document(fh.read())
    assert len(results) == 13
    assert all(eq is not None and err is None for _, eq, err in results)


def test_generate_module_is_valid_python():
    with open("markdown equation.md", "r", encoding="utf-8") as fh:
        source = generate_module(fh.read())
    ns = {}
    exec(compile(source, "<generated>", "exec"), ns)
    # Every equation produced a callable function.
    funcs = [v for k, v in ns.items() if k.startswith("eq_") and callable(v)]
    assert len(funcs) == 13


def test_preprocess_strips_left_right_and_tag():
    out = preprocess(r"\left(\frac{p}{H}\right)^{0.86} \tag{2}")
    assert "\\left" not in out and "\\right" not in out and "tag" not in out


def test_full_ihtc_model_composes():
    """Compose Eqs 7-10 into the solid-contact IHTC and sanity-check magnitude."""
    k_st = translate(PAPER_EQUATIONS["8"]).evaluate(k_s=0.14, k_t=0.0244)
    R = translate(PAPER_EQUATIONS["9"]).evaluate(R_s=3.4e-7, R_t=9.8e-7)
    n_p = translate(PAPER_EQUATIONS["10"]).evaluate(P=7, lamda=6.05, sigma_U=21)
    h_c = translate(PAPER_EQUATIONS["7"]).evaluate(K_st=k_st, N_P=n_p, R=R, alpha=2.01e-4)
    # Paper reports total IHTC ~8.2 kW/m2K at 7 MPa (H13, dry); h_c is the bulk of it.
    assert 5.0 < h_c < 9.0
