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
# Translate a single equation
python main.py --latex "h=A(1-\exp (-B P))"

# Translate every equation in a document and print them
python main.py "markdown equation.md"

# Translate a document and write a runnable module of functions
python main.py "markdown equation.md" --module equations.py
```

`equations.py` in this repo is an example of that generated output for the
included paper (13/13 equations translated).

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

### Tests

```bash
python -m pytest test_latex2python.py
```
