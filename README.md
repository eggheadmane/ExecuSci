# ExecuSci

• Scientific knowledge is still locked inside PDFs, making it difficult to reuse, validate, and integrate published models into real engineering workflows. 
	
• This project will develop ExecuSci, an AI-based tool that transforms frontier knowledge embedded in metal forming-related papers into executable, reusable research plug-ins. 
	
• Empowered by AI, ExecuSci will interpret equations, models, workflows, assumptions, and engineering logic directly from the paper. 
	
• The vision is simple: users provide a paper DOI, and ExecuSci generates structured, interactive, and computationally usable scientific plug-ins, avoiding the need to manually rebuild published models from scratch.

## LaTeX → Python equation translator

`latex2python.py` is the first building block towards that vision: it turns the
mathematical equations embedded in papers (as produced by OCR tools such as
Mathpix, i.e. `\begin{equation*} ... \end{equation*}` blocks) into **executable
Python**.

It is purpose-built for real-world paper LaTeX and copes with the quirks that
break `sympy.parse_latex`, including:

- multi-character subscripts such as `K_{s t l}` → `K_stl`;
- Mathpix placeholder superscripts such as `R_{s}{ }^{2}` → `R_s**2`;
- bare functions such as `\tan \theta`, `\exp (-B P)`;
- `\left( ... \right)` delimiters and accents such as `\bar{\lambda}` → `lamda_bar`;
- Greek letters, mapping the Python keyword `\lambda` → `lamda`.

### Install

```bash
pip install -r requirements.txt
```

### Command line

```bash
python main.py
```

Reads the configured document (`DEFAULT_DOC` in `main.py`) and automatically
writes both the equations module and, when tables/prose yield values, a
`constants.py` with names aligned to equation arguments (`lamda`, `sigma_U`, …).

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

### Constants scraper

`scrape_constants.py` runs automatically with equation translation. It pulls
numeric model parameters from markdown tables (e.g. Table 3) and simple prose
patterns, then writes `constants.py` with `get_constants(tool, delta)`:

```python
from constants import get_constants
import equations

c = get_constants(tool="P20")
K_st = equations.eq_8(c["k_s"], c["k_t"])
```

### Tests

```bash
python -m pytest test_latex2python.py test_scrape_constants.py
```
