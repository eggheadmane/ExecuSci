To-Do (n = priority / 5):
- review usage of repr vs left aligned new lines vs pretty print new lines for MML representation in LLM input and training data (3)
- ~~review and standardise file types, class inputs and outputs, etc. (4)~~
- ~~develop dependency graph for finding the equations neededed to solve a top level equation (2)~~
- ~~extract constants from paper, must be done on campus wifi (2)~~
- ~~finish SOE class for recreating python file results (3)~~
- create utils class to abstract file I/O methods (1)
- ~~sort out returns vs modifying internal attributes (1)~~
- add new docstrings to used functions
- ~~fix reduce systems (2)~~
- ~~evaluate the usage of sentencepiece vs BPE for tokenizer with T5 (1)~~
- test combined var single tokens vs subtokens (1)
- ~~fix tokenizer performance from hub not retaining tags~~
- ~~test the ODE solver (4)~~

Process:
- input a DOI referring to a tribology paper
- extract constants from tables
- extract MathML representations of equations 
- pass MathML equations to a LLM for conversion to individual SymPy equations 
- implement the system of equations back into Python for solving, plotting and error analysis
