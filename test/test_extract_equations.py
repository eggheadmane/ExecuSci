"""Tests for stage 02: extracting equations and their symbol dictionary."""

from __future__ import annotations

import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from execusci_paths import add_stages, paper_path  # noqa: E402

add_stages("Extract Equations")

from extract_equations import (  # noqa: E402
    extract,
    extract_latex_equations,
    find_appositions,
    find_definitions,
    render_markdown,
    render_raw_markdown,
    run,
    where_clause,
)

PAPER = paper_path()

SNIPPET = """
Some introduction to the model.

$$
\\begin{equation*}
h_{c}=\\alpha \\frac{K_{s t} N_{P}}{R} \\tag{7}
\\end{equation*}
$$

where $\\alpha$ is a model parameter, $K_{s t}$ is the harmonic mean thermal
conductivity of the contact solids, $R$ is the root mean square of surface
roughness of the contact solids and $N_{P}$ is a pressure dependent parameter.
The solid-contact IHTC $h_{c}$ is thus correlated positively with $K_{s t}$.
"""


@pytest.fixture(scope="module")
def paper_text() -> str:
    with open(PAPER, "r", encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def extraction(paper_text):
    return extract(paper_text, source=PAPER)


# --------------------------------------------------------------------------- #
# Display-equation finder
# --------------------------------------------------------------------------- #

def test_extraction_from_markdown(paper_text):
    raws = extract_latex_equations(paper_text)
    tags = [r.tag for r in raws]
    assert tags == [str(i) for i in range(1, 14)]


def test_equations_are_ordered_numerically_by_tag():
    """Eq. (10) must follow Eq. (9), not sort as the string "10" < "9"."""
    tags = [str(i) for i in range(1, 14)]
    document = "\n\n".join(
        f"$$\n\\begin{{equation*}}\nx = {tag} \\tag{{{tag}}}\n\\end{{equation*}}\n$$"
        for tag in reversed(tags)
    )
    assert [r.tag for r in extract_latex_equations(document)] == tags


def test_untagged_equations_keep_document_order():
    document = (
        "$$\n\\begin{equation*}\nb = 2 a\n\\end{equation*}\n$$\n\n"
        "$$\n\\begin{equation*}\nc = 3 a\n\\end{equation*}\n$$\n"
    )
    assert [r.latex.split("=")[0].strip() for r in extract_latex_equations(document)] == ["b", "c"]


# --------------------------------------------------------------------------- #
# Definition mining
# --------------------------------------------------------------------------- #

def test_where_clause_stops_at_the_end_of_the_sentence():
    clause = where_clause(SNIPPET)
    assert clause.startswith("$\\alpha$ is a model parameter")
    assert "correlated positively" not in clause


def test_definitions_are_taken_from_the_where_clause():
    definitions = dict(
        (tuple(names), text) for names, text in find_definitions(SNIPPET)
    )
    assert definitions[("alpha",)] == "a model parameter"
    assert definitions[("N_P",)] == "a pressure dependent parameter"
    assert "harmonic mean thermal conductivity" in definitions[("K_st",)]


def test_statements_about_a_symbol_are_not_treated_as_definitions():
    """"$h_c$ is thus correlated positively with ..." describes, not defines."""
    names = {name for group, _ in find_definitions(SNIPPET) for name in group}
    assert "h_c" not in names
    loose = {name for group, _ in find_definitions(SNIPPET, strict=False) for name in group}
    assert "h_c" in loose


def test_shared_definition_covers_every_symbol_in_the_group():
    text = (
        "where $h_{g}$ and $h_{c}$ are the heat transfer coefficients across "
        "the air gap and for the solid contact respectively."
    )
    names, description = find_definitions(text)[0]
    assert names == ["h_g", "h_c"]
    assert description.startswith("the heat transfer coefficients")


def test_comma_packed_math_span_is_split():
    """Mathpix emits "$k_{s}, k_{t}$ and $k_{l}$" as two spans, not three."""
    text = (
        "where $k_{s}, k_{t}$ and $k_{l}$ are the average thermal conductivities "
        "of the specimen, tools and grease-based graphite lubricant respectively."
    )
    names, _ = find_definitions(text)[0]
    assert names == ["k_s", "k_t", "k_l"]


def test_sentence_cut_keeps_abbreviations_but_ends_at_a_real_stop():
    text = (
        "where $\\sigma_{U}$ is the ultimate strength of AA7075 at 490 °C. "
        "In order to increase the IHTC values, a pressure could be applied."
    )
    _, description = find_definitions(text)[0]
    assert description == "the ultimate strength of AA7075 at 490 °C"


def test_apposition_fallback():
    text = "determined from the average surface roughness of the specimen $R_{s}$"
    names, description = find_appositions(text)[0]
    assert names == ["R_s"]
    assert description == "the average surface roughness of the specimen"


# --------------------------------------------------------------------------- #
# Whole-paper extraction
# --------------------------------------------------------------------------- #

def test_all_thirteen_equations_are_extracted(extraction):
    assert [e.tag for e in extraction.equations] == [str(i) for i in range(1, 14)]
    assert extraction.failed == []


def test_outputs_and_inputs_are_recorded(extraction):
    by_tag = {e.tag: e for e in extraction.equations}
    assert by_tag["8"].output == "K_st"
    assert set(by_tag["8"].inputs) == {"k_s", "k_t"}
    assert by_tag["10"].python == "N_P = 1 - exp(-P*lamda/sigma_U)"


def test_symbol_dictionary_covers_every_symbol(extraction):
    used = {name for e in extraction.equations for name in e.symbols}
    assert used == set(extraction.symbols)
    assert len(extraction.symbols) > 30


@pytest.mark.parametrize(
    "name,fragment",
    [
        ("lamda", "model parameter"),
        ("P", "contact pressure"),
        ("delta", "lubricant layer thickness"),
        ("K_st", "harmonic mean thermal conductivity"),
        ("sigma_U", "ultimate strength"),
        ("R_s", "surface roughness"),
    ],
)
def test_descriptions_use_the_papers_wording(extraction, name, fragment):
    assert fragment in extraction.symbols[name].description


def test_symbol_kinds(extraction):
    assert extraction.symbols["K_st"].kind == "derived"  # defined by Eq. 8
    assert extraction.symbols["lamda"].kind == "parameter"  # "a model parameter"
    assert extraction.symbols["P"].kind == "input"  # supplied by the caller


def test_symbol_latex_matches_the_paper(extraction):
    assert extraction.symbols["sigma_U"].latex == "\\sigma_{U}"
    assert extraction.symbols["lamda_bar"].latex == "\\bar{\\lambda}"


# --------------------------------------------------------------------------- #
# Rendered documents
# --------------------------------------------------------------------------- #

def test_markdown_is_re_extractable(extraction):
    """Stage 04 reads equations_raw.md, so its blocks must survive a round trip."""
    markdown = render_raw_markdown(extraction)
    round_trip = extract_latex_equations(markdown)
    assert [e.tag for e in round_trip] == [str(i) for i in range(1, 14)]
    assert round_trip[6].latex == "h_{c}=\\alpha \\frac{K_{s t} N_{P}}{R}"


def test_markdown_documents_every_symbol(extraction):
    markdown = render_markdown(extraction)
    assert "## Symbol dictionary" in markdown
    for name in extraction.symbols:
        assert f"`{name}`" in markdown


def test_run_writes_both_artefacts(tmp_path):
    extraction = run(
        paper=PAPER,
        out_dir=str(tmp_path),
        report_path=str(tmp_path / "equations.md"),
        verbose=False,
    )
    equations_raw = tmp_path / "equations_raw.md"
    equations_md = tmp_path / "equations.md"
    symbols_json = tmp_path / "symbols.json"
    assert equations_raw.exists() and equations_md.exists() and symbols_json.exists()
    assert "## Symbol dictionary" in equations_md.read_text(encoding="utf-8")
    assert "\\begin{equation*}" in equations_raw.read_text(encoding="utf-8")
    assert "## Symbol dictionary" not in equations_raw.read_text(encoding="utf-8")

    payload = json.loads(symbols_json.read_text(encoding="utf-8"))
    assert payload["equation_count"] == len(extraction.equations)
    assert payload["symbols"]["k_s"]["used_in"] == ["8", "12"]
    assert payload["source"] == os.path.basename(PAPER)
