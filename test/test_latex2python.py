"""Tests for the ExecuSci LaTeX -> Python equation translator."""

from __future__ import annotations

import math
import os
import sys

import pytest
import sympy as sp

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BUILD = os.path.join(_ROOT, "build")
if _BUILD not in sys.path:
    sys.path.insert(0, _BUILD)

from execusci_paths import add_stages, paper_path  # noqa: E402

add_stages("Latex2Python")

from latex2python import (  # noqa: E402
    LatexParseError,
    extract_equations,
    generate_module,
    latex_to_name,
    name_to_latex,
    preprocess,
    translate,
    translate_document,
)

_PAPER = paper_path()

# The 13 equations of the target paper, keyed by their \tag number.
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


def test_implicit_multiply_with_brackets():
    """\\frac{1}{2}\\left[...\\right] must parse as (1/2)*[...], not stall on '['."""
    eq = translate(
        r"\sigma_y = \sqrt{\frac{1}{2}\left[(\sigma_1 - \sigma_2)^2"
        r" + (\sigma_2 - \sigma_3)^2 + (\sigma_3 - \sigma_1)^2\right]}"
    )
    assert eq.output.name == "sigma_y"
    assert {s.name for s in eq.inputs} == {"sigma_1", "sigma_2", "sigma_3"}
    compile(eq.python, "<eq>", "exec")


def test_criterion_form_flips_to_assignment():
    """``[...]^n = y`` (yield criterion style) becomes ``y = [...]^n``."""
    eq = translate(
        r"\left[ F(\sigma_{22} - \sigma_{33})^2 + G(\sigma_{33} - \sigma_{11})^2"
        r" + H(\sigma_{11} - \sigma_{22})^2 + 2L\sigma_{23}^2 + 2M\sigma_{31}^2"
        r" + 2N\sigma_{12}^2 \right]^{\frac{1}{2}} = \sigma_y"
    )
    assert eq.output.name == "sigma_y"
    assert eq.python.startswith("sigma_y = ")
    expected = {
        "F", "G", "H", "L", "M", "N",
        "sigma_11", "sigma_12", "sigma_22", "sigma_23", "sigma_31", "sigma_33",
    }
    assert {s.name for s in eq.inputs} == expected
    compile(eq.python, "<eq>", "exec")


def test_bad_input_raises_parse_error():
    with pytest.raises(LatexParseError):
        translate(r"\frac{1}{")  # unterminated


def _paper_text() -> str:
    with open(_PAPER, "r", encoding="utf-8") as fh:
        return fh.read()


def test_extraction_from_markdown():
    raws = extract_equations(_paper_text())
    tags = [r.tag for r in raws]
    assert tags == [str(i) for i in range(1, 14)]


def test_equations_are_ordered_numerically_by_tag():
    """Eq. (10) must follow Eq. (9), not sort as the string "10" < "9"."""
    document = "\n\n".join(
        f"$$\n\\begin{{equation*}}\n{latex} \\tag{{{tag}}}\n\\end{{equation*}}\n$$"
        for tag, latex in reversed(list(PAPER_EQUATIONS.items()))
    )
    assert [r.tag for r in extract_equations(document)] == [
        str(i) for i in range(1, 14)
    ]


def test_untagged_equations_keep_document_order():
    document = (
        "$$\n\\begin{equation*}\nb = 2 a\n\\end{equation*}\n$$\n\n"
        "$$\n\\begin{equation*}\nc = 3 a\n\\end{equation*}\n$$\n"
    )
    assert [r.latex.split("=")[0].strip() for r in extract_equations(document)] == ["b", "c"]


def test_translate_document_all_ok():
    results = translate_document(_paper_text())
    assert len(results) == 13
    assert all(eq is not None and err is None for _, eq, err in results)


def test_generate_module_is_valid_python():
    source = generate_module(_paper_text())
    ns = {}
    exec(compile(source, "<generated>", "exec"), ns)
    # Every equation produced a callable function.
    funcs = [v for k, v in ns.items() if k.startswith("eq_") and callable(v)]
    assert len(funcs) == 13


def test_generated_functions_document_their_arguments():
    source = generate_module(
        _paper_text(),
        descriptions={"lamda": "a model parameter", "P": "the contact pressure"},
    )
    ns: dict = {}
    exec(compile(source, "<generated>", "exec"), ns)
    doc = ns["eq_10"].__doc__
    assert "lamda: a model parameter" in doc
    assert "P: the contact pressure" in doc
    # Symbols without a description are still listed, just without wording.
    assert "sigma_U" in doc


@pytest.mark.parametrize(
    "latex,name",
    [
        (r"k_{s}", "k_s"),
        (r"\lambda", "lamda"),
        (r"\sigma_{U}", "sigma_U"),
        (r"K_{s t l}", "K_stl"),
        (r"K_{\text {stl }}", "K_stl"),  # Mathpix spells the prose version this way
        (r"k_{\mathrm{t}}", "k_t"),
        (r"\bar{\lambda}", "lamda_bar"),
        ("0.85", None),  # a number is not a symbol
    ],
)
def test_latex_to_name(latex, name):
    assert latex_to_name(latex) == name


@pytest.mark.parametrize(
    "name,latex",
    [
        ("k_s", "k_{s}"),
        ("lamda", r"\lambda"),
        ("sigma_U", r"\sigma_{U}"),
        ("K_stl", "K_{stl}"),
        ("lamda_bar", r"\bar{\lambda}"),
        ("h", "h"),
    ],
)
def test_name_to_latex(name, latex):
    assert name_to_latex(name) == latex


def test_name_round_trip_for_every_paper_symbol():
    for latex in PAPER_EQUATIONS.values():
        for symbol in translate(latex).symbols.values():
            assert latex_to_name(name_to_latex(symbol.name)) == symbol.name


def test_preprocess_strips_left_right_and_tag():
    out = preprocess(r"\left(\frac{p}{H}\right)^{0.86} \tag{2}")
    assert "\\left" not in out and "\\right" not in out and "tag" not in out


# --------------------------------------------------------------------------- #
# Notation of the friction paper (``Sample Paper 2.md``): quantities written as
# functions of time, chained equalities, integrals and summations.
# --------------------------------------------------------------------------- #

_FRICTION_PAPER = paper_path("Sample Paper 2.md")

FRICTION_EQUATIONS = {
    "1": r"\mu(t)=(1-\beta) \mu_{l}(t)+\beta \mu_{d}(t)",
    "2": r"\mu_{l}(t)=\mu_{l 0} \exp \left(-\frac{Q_{l}}{R T(t)}\right)",
    "3": r"\mu_{d}(t)=\mu_{d 0} \exp \left(-\frac{Q_{d}}{R T(t)}\right)",
    "4": r"\beta(t)=\exp \left[-\left(\lambda_{1} h(t)\right)^{\lambda_{2}}\right]",
    "8": r"\dot{h}(t)=\frac{\dot{V}(t)}{A}"
         r"=-h(t)\left(c P^{k_{p}} v^{k_{v}} / \eta^{k_{\eta}}\right)",
    "9": r"\eta=\eta_{0} \exp \left(\frac{Q_{\eta}}{R T}\right)",
}


def _friction_paper_text() -> str:
    with open(_FRICTION_PAPER, "r", encoding="utf-8") as fh:
        return fh.read()


def test_function_of_time_is_not_a_factor_of_time():
    r"""``\mu_{l}(t)`` is the quantity ``mu_l``, not ``mu_l`` times ``t``."""
    eq = translate(FRICTION_EQUATIONS["2"], tag="2")
    assert eq.python == "mu_l = mu_l0*exp(-Q_l/(R*T))"
    assert [s.name for s in eq.inputs] == ["Q_l", "R", "T", "mu_l0"]
    # The dependence is documented instead of becoming arithmetic.
    assert eq.depends_on == {"mu_l": "t", "T": "t"}
    assert "functions of t: T(t), mu_l(t)" in eq.function_source()


def test_time_dependent_equation_keeps_its_output_symbol():
    """With ``\\mu(t)`` read as a product, Eq. (1) had no left-hand side at all."""
    eq = translate(FRICTION_EQUATIONS["1"], tag="1")
    assert eq.output.name == "mu"
    assert [s.name for s in eq.inputs] == ["beta", "mu_d", "mu_l"]
    assert eq.evaluate(beta=0.5, mu_l=0.2, mu_d=1.5) == pytest.approx(0.85)


def test_numeric_argument_becomes_part_of_the_name():
    """``V(0)`` is the initial volume: a quantity of its own, not ``V*0``."""
    eq = translate(r"V(0)=V_{i}+\Delta")
    assert eq.output.name == "V_0"


def test_implicit_multiplication_by_a_bracket_is_not_a_function_call():
    """``A(1-\\exp (-B P))`` is a product; only a lone argument means a function."""
    eq = translate(PAPER_EQUATIONS["4"])
    assert eq.depends_on == {}
    assert eq.evaluate(A=2.0, B=0.5, P=4.0) == pytest.approx(2.0 * (1 - math.exp(-2.0)))


def test_chained_equality_uses_the_evaluable_side():
    """``h_dot = V_dot/A = -h(...)``: the last member is the one to compute."""
    eq = translate(FRICTION_EQUATIONS["8"], tag="8")
    assert eq.output.name == "h_dot"
    assert [s.name for s in eq.inputs] == [
        "P", "c", "eta", "h", "k_eta", "k_p", "k_v", "v"
    ]
    # The member in between is kept as an identity rather than dropped.
    assert [str(identity) for identity in eq.identities] == ["V_dot/A"]
    assert "Also given as: h_dot = V_dot/A" in eq.function_source()


def test_longer_chain_records_every_intermediate_member():
    eq = translate(r"a=b=c=d")
    assert eq.output.name == "a"
    assert [str(identity) for identity in eq.identities] == ["b", "c"]


@pytest.mark.parametrize(
    "latex,reason",
    [
        (r"V=\int_{0}^{t} h w v d t", "integral"),
        (r"f=\sum_{i=1}^{m} w_{i} \mu_{i}", "summation"),
        (r"K=\prod_{i=1}^{n} k_{i}", "product"),
        (r"d V=a h w v d t", "differential"),
    ],
)
def test_unsupported_operators_fail_loudly(latex, reason):
    r"""These used to become invented symbols such as ``int_0**t``."""
    with pytest.raises(LatexParseError, match=reason):
        translate(latex)


def test_friction_paper_translates_its_evaluable_equations():
    """The six algebraic equations translate; the other four say why they cannot."""
    results = translate_document(_friction_paper_text())
    translated = {raw.tag: eq for raw, eq, error in results if eq is not None}
    failed = {raw.tag: error for raw, eq, error in results if eq is None}

    assert sorted(translated, key=int) == ["1", "2", "3", "4", "8", "9"]
    assert sorted(failed, key=int) == ["5", "6", "7", "10"]
    assert translated["4"].python == "beta = exp(-(h*lamda_1)**lamda_2)"
    assert translated["9"].python == "eta = eta_0*exp(Q_eta/(R*T))"


def test_friction_paper_module_is_valid_python():
    source = generate_module(_friction_paper_text())
    ns: dict = {}
    exec(compile(source, "<generated>", "exec"), ns)
    assert sorted(k for k in ns if k.startswith("eq_")) == [
        "eq_1", "eq_2", "eq_3", "eq_4", "eq_8", "eq_9"
    ]
    # Untranslatable equations are commented out, with the reason kept.
    assert "Could not translate (Eq. 5)" in source
    assert "summation" in source


def test_friction_model_reproduces_the_papers_cof_values():
    """At 300 °C the paper measures COF ~0.24 lubricated and ~1.5 dry (Fig. 2).

    The activation energies are tabulated in kJ/mol while ``R`` is in J/(K mol),
    so they are scaled here: stage 03 records units but converts nothing.
    """
    T, R = 573.15, 8.314
    mu_l = translate(FRICTION_EQUATIONS["2"]).evaluate(mu_l0=1.23, Q_l=7.8e3, R=R, T=T)
    mu_d = translate(FRICTION_EQUATIONS["3"]).evaluate(mu_d0=9.65, Q_d=8.8e3, R=R, T=T)
    assert mu_l == pytest.approx(0.24, abs=0.01)
    assert mu_d == pytest.approx(1.5, abs=0.05)

    overall = translate(FRICTION_EQUATIONS["1"])
    assert overall.evaluate(beta=0.0, mu_l=mu_l, mu_d=mu_d) == pytest.approx(mu_l)
    assert overall.evaluate(beta=1.0, mu_l=mu_l, mu_d=mu_d) == pytest.approx(mu_d)


def test_unlubricated_area_ratio_grows_as_the_film_thins():
    """``beta`` runs from 0 (thick film, lubricated) to 1 (no film, dry)."""
    eq = translate(FRICTION_EQUATIONS["4"])
    thick = eq.evaluate(lamda_1=20.0, lamda_2=1.10, h=1.0)
    thin = eq.evaluate(lamda_1=20.0, lamda_2=1.10, h=0.001)
    assert thick < 0.01 < thin < 1.0


def test_film_thinning_rate_accelerates_with_pressure():
    """Eq. (8) is the ODE the paper integrates; it must at least be evaluable."""
    eq = translate(FRICTION_EQUATIONS["8"])
    values = dict(c=0.012, k_p=2.05, k_v=1.0, k_eta=5.30, eta=1.0, v=50.0, h=1.0)
    slow = eq.evaluate(P=270.0, **values)
    fast = eq.evaluate(P=410.0, **values)
    assert fast < slow < 0  # the film always thins, and faster under load


def test_full_ihtc_model_composes():
    """Compose Eqs 7-10 into the solid-contact IHTC and sanity-check magnitude."""
    k_st = translate(PAPER_EQUATIONS["8"]).evaluate(k_s=0.14, k_t=0.0244)
    R = translate(PAPER_EQUATIONS["9"]).evaluate(R_s=3.4e-7, R_t=9.8e-7)
    n_p = translate(PAPER_EQUATIONS["10"]).evaluate(P=7, lamda=6.05, sigma_U=21)
    h_c = translate(PAPER_EQUATIONS["7"]).evaluate(K_st=k_st, N_P=n_p, R=R, alpha=2.01e-4)
    # Paper reports total IHTC ~8.2 kW/m2K at 7 MPa (H13, dry); h_c is the bulk of it.
    assert 5.0 < h_c < 9.0
