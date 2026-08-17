# ExecuSci

• Scientific knowledge is still locked inside PDFs, making it difficult to reuse, validate, and integrate published models into real engineering workflows. 
	
• This project will develop ExecuSci, an AI-based tool that transforms frontier knowledge embedded in metal forming-related papers into executable, reusable research plug-ins. 
	
• Empowered by AI, ExecuSci will interpret equations, models, workflows, assumptions, and engineering logic directly from the paper. 
	
• The vision is simple: users provide a paper DOI, and ExecuSci generates structured, interactive, and computationally usable scientific plug-ins, avoiding the need to manually rebuild published models from scratch.

## Pipeline

Each folder is one stage and consumes the previous stage's output. Folder numbers
follow the order the stages run in; code never hard-codes those numbers, it looks
folders up by name through `execusci_paths.py`, so stages can be reordered.

| Stage | Folder | Input | Output |
|-------|--------|-------|--------|
| 01 | `01 PDF2Latex` | the PDF | `target_paper.md` (Mathpix markdown) |
| 02 | `02 Extract Equations` | `target_paper.md` | `output/equations.md`, `output/symbols.json` |
| 03 | `03 Scrape Constants` | `target_paper.md` | `constants.py`, `constants.md` |
| 04 | `04 Latex2Python` | `equations.md` + `symbols.json` | `equations.py` |
| 05 | `05 Plotting` | `equations.py` + `constants.py` | figures under `output/` |

### Install and run

```bash
pip install -r requirements.txt
python run_pipeline.py            # stages 02 -> 04
python run_pipeline.py --plot     # also runs stage 05
python run_pipeline.py --paper "01 PDF2Latex/another_paper.md"
```

Every stage is also runnable on its own:

```bash
python "02 Extract Equations/extract_equations.py"
python "03 Scrape Constants/scrape_constants.py"
python "04 Latex2Python/main.py"
python "05 Plotting/plot_compare.py" --no-show
```

## Stage 02 — Extract equations

`extract_equations.py` pulls every display equation out of the paper and writes a
self-contained `equations.md`: the LaTeX (with the paper's `\tag{n}` preserved,
so the numbering survives downstream), the Python form, the paper line it came
from, and the sentence that introduces it.

It also builds a **symbol dictionary** covering every variable and constant the
equations use, described in the authors' own words. Descriptions are mined from
the "where $x$ is ..." clauses that follow each equation, including shared ones
("where $h_g$ and $h_c$ are ..."), and each symbol is classified as:

| Kind | Meaning |
|------|---------|
| `derived` | an equation defines it (e.g. `K_st` from Eq. 8) |
| `parameter` | the paper calls it a model parameter/constant (e.g. `lamda`) |
| `input` | supplied by the caller or scraped in stage 03 (e.g. `P`) |

The same content is written to `symbols.json` for the later stages: stage 03
reports which symbols still lack a value, and stage 04 documents its generated
functions with the descriptions.

## Stage 03 — Scrape constants

`scrape_constants.py` finds every numeric constant the paper states and gives it
the same symbol name the equations use, plus a `sympy.Symbol`:

- **symbol-keyed tables** (Table 3, "Material constants and model parameters"):
  `k_s`, `R_s`, `sigma_U`, `alpha`, `lamda`, `beta`, `gamma`, and per-tool `k_t`
  and `R_t` for H13, cast iron and P20;
- **property tables** (Table 2, "Material properties"), keyed by property per row
  and material per column: Young's modulus → `E`, density → `rho`, thermal
  conductivity → `k`, specific heat → `c_p`, Poisson's ratio → `nu`;
- **prose** such as "$h_a$ ... approximately 0.8".

Values the paper gives as functions of temperature (`-39.082 T + 82532`) are kept
as expressions in `TEMPERATURE_DEPENDENT` rather than being mistaken for numbers.
`constants.md` records where every value came from and which equation symbols
still have no value.

```python
from constants import get_constants, material_properties, subs_map, symbol

c = get_constants(tool="P20", delta=1.5e-5)   # flat dict for the generated functions
material_properties("H13")["rho"]             # 7800.0
symbol("k_s")                                 # sympy Symbol('k_s')
expr.subs(subs_map(tool="H13"))               # substitute into a SymPy expression
```

## Stage 04 — LaTeX → Python equation translator

`latex2python.py` turns the equations into **executable Python**. It is
purpose-built for real-world paper LaTeX and copes with the quirks that break
`sympy.parse_latex`, including:

- multi-character subscripts such as `K_{s t l}` → `K_stl`;
- Mathpix placeholder superscripts such as `R_{s}{ }^{2}` → `R_s**2`;
- cosmetic wrappers inside names such as `K_{\text {stl }}` → `K_stl`;
- bare functions such as `\tan \theta`, `\exp (-B P)`;
- `\left( ... \right)` delimiters and accents such as `\bar{\lambda}` → `lamda_bar`;
- Greek letters, mapping the Python keyword `\lambda` → `lamda`.

`main.py` writes `equations.py`, one documented function per equation, named
after the paper's equation number:

```python
def eq_13(delta, gamma):
    """N_L = 1 - exp(-delta*gamma)

    LaTeX: N_{L}=1-\\exp (-\\gamma \\delta)

    Args:
        delta: the applied lubricant layer thickness
        gamma: a model parameter
    """
    return 1 - exp(-delta*gamma)
```

### Library

```python
from latex2python import translate

eq = translate(r"K_{s t}=\frac{2}{k_{s}^{-1}+k_{t}^{-1}}")
print(eq.python)                     # K_st = 2/(1/k_t + 1/k_s)
print([s.name for s in eq.inputs])   # ['k_s', 'k_t']
print(eq.evaluate(k_s=0.14, k_t=0.0244))   # 0.04155...  (harmonic mean)
print(eq.function_source())          # a stand-alone def K_st(k_s, k_t): ...
```

`Equation` exposes several views of the same equation:

| Attribute / method    | Description                                             |
| --------------------- | ------------------------------------------------------- |
| `.expr`               | the SymPy `Eq` (or expression)                          |
| `.python`             | one-line Python source, e.g. `h = A*(1 - exp(-B*P))`    |
| `.inputs` / `.output` | free symbols on the RHS / the defined LHS symbol        |
| `.callable()`         | a NumPy-backed function (works on scalars and arrays)   |
| `.evaluate(**values)` | evaluate the RHS for given inputs                       |
| `.function_source()`  | source code of a documented stand-alone function        |

Module-level helpers: `extract_equations`, `translate_document`,
`generate_module`, and the naming pair `latex_to_name` / `name_to_latex`.

## Stage 05 — Plotting

`plot_compare.py` evaluates the generated Eq. (6) chain over contact pressure and
overlays it on the paper's digitized P20 curve, saving a comparison and an error
plot. With the scraped constants it currently tracks the paper to within
0.1 % mean absolute error.

## Tests

```bash
python -m pytest
```

`test_pipeline.py` runs stages 02–04 into a temporary directory and checks that
the generated code reproduces the IHTC values the paper reports for P20 tools
(6.7 kW/m²K at 3 MPa dry; 14.5 kW/m²K at 13 MPa lubricated).
