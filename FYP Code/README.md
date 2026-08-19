This repository contains the source code for the project entitled:

# Automated Implementation of Boundary Condition Research Using Large Langauge Models (LLMs)

```text
smart-scraper/
├── .env                      # Environment variables
├── .gitattributes            # Git attributes file
├── .gitignore                # Git ignore file
├── environment.yml           # Conda environment specification
├── README.md                 # Repository documentation
├── requirements.txt          # Python dependencies
│
├── .vscode/                  # VS Code configuration
│   └── settings.json
│
├── archived_legacy_code/     # Legacy code
│   ├── ConstantsCoursework1.m
│   ├── converter.py
│   ├── friction_schuler.py
│   ├── functional_module.ipynb
│   ├── ihtc_template.py
│   ├── notes.txt
│   ├── paper_url.txt
│   ├── README.md
│   ├── requirements.txt
│   ├── scraper.py            # Original MathScraper implementation
│   ├── template.py
│   ├── test.py
│   ├── figures/
│   ├── scraped_python/       # Generated Python code from scraping
│   └── scraped_txt/          # Scraped text content
│
├── models/                   # Trained models
│   └── checkpoint-100/       # Model checkpoint
│
└── src/                      # Source code
    ├── __init__.py
    ├── fig.ipynb             # Report visualisation notebook
    ├── main.py               # Main application entry point
    ├── test.ipynb            # Testing notebook
    ├── TODO.md               # Project to-do list
    ├── __pycache__/
    │
    ├── Data/                 # Top level files (accessible by main.py)
    │   ├── gemini_test_4_predictions.txt            # 4th and 5th iteration data
    │   ├── gemini_test_4.csv
    │   ├── gemini_test_5.csv
    │   ├── HTC_equations.txt                        # Saved IHTC paper MathML
    │   ├── HTC_gemini5_predictions.txt
    │   └── p20.csv                                  # Reference data for IHTC
    │
    ├── Docs/                 # Papers
    │   ├── DOIs
    │   ├── Friction Modelling.pdf
    │   ├── HTC Paper.pdf
    │   └── Material Property Modelling.pdf
    │
    ├── Figures/              # Generated figures
    │   ├── bothIHTC.svg
    │   ├── boxplot_metrics.svg
    │   ├── dependency_graph.pdf
    │   ├── equation_type_distribution.svg
    │   ├── Friction_pie.svg
    │   └── ...
    │
    ├── Gemini/               # Google Gemini model integration
    │   ├── GeminiPredict.py
    │   ├── training_script.ipynb
    │   └── Data/             # Gemini testing data 
    │       └── ...
    │
    ├── Generation/           # Synthetic dataset generation
    │   ├── Equation_BaseDataset.py
    │   ├── Equation_BaseDataset_dev.ipynb
    │   ├── examples.ipynb
    │   └── Data/             # Synthetically generated data
    │       └── ...
    │
    ├── Postprocessing/       # Post-processing tools
    │   ├── postprocessing_dev.ipynb
    │   ├── SOE_EquationGraph.py
    │   └── Data/             # Translated SymPy equations
    │       └── ...
    │
    ├── Scraping/             # New scraper implementation
    │   ├── Scraper_dev.ipynb
    │   ├── Scraper.py
    │   └── Data/             # Scraped MathML equations
    │       └── ...
    │
    └── T5/                   # T5 model integration
    │   ├── tokenizer_training.ipynb
    │   ├── training_script.ipynb
    │   ├── translation_test.ipynb
    │   ├── wandb_test1.py
    │   ├── wandb_test2.py
    │   ├── colab_training_script.ipynb
    │   ├── Data/             # Scraped MathML equations
    │   |   └── ...
    │   ├── Model_Files/      # Trained model weights
    │   |   └── ...
    │   ├── Tokenizer_Files/  # Data for tokenizer training
    │   |   └── ...
    │   └── wandb/            # Logging files
    │       └── ...
```
