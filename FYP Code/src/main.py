import os
import pandas as pd

from Gemini.GeminiPredict import GeminiPredict
from Generation.Equation_BaseDataset import Equation, BaseDataset
from Postprocessing.SOE_EquationGraph import SystemOfEquations, EquationGraph
from Scraping.Scraper import Scraper

# Input parameters
doi = "10.1016/j.jmatprotec.2017.04.005"
elsevier_api_key = os.getenv("ELSEVIER_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY") 
model_name = "tunedModels/mmltopython4-f3fuppiemnq9"

# Input and format data
column_names = ["P", "h"]
data_filepath = "C:\\Users\\Eito\\OneDrive - Imperial College London\\ME2 UROP\\03 FYP GitHub Code\\src\\Data\\p20.csv"
p20_df = pd.read_csv(data_filepath, header=None, names=column_names)
P_list = pd.to_numeric(p20_df["P"]).tolist()
h_list_ref = pd.to_numeric(p20_df["h"]).tolist()

def main():
    # 1. Scraping journal data 
    scraper = Scraper(doi, elsevier_api_key)
    mathml_dict, const_dict = scraper.scrape()

    # 2. Equation translation        
    predictor = GeminiPredict(gemini_api_key, model_name)
    mathml_equations = list(mathml_dict.values())
    full_equations = predictor.generate_predictions(mml_list=mathml_equations)

    # 3. Solving system of equations
    solver = SystemOfEquations(equations=full_equations)
    solutions = solver.solve_system(const_dict=const_dict,
                                    independent_vals=P_list,
                                    independent_symbol="P",
                                    target_symbol="h",
                                    equation_number=6)

    # 4. Outputs
    solver.plot_graph(P_list, solutions, h_list_ref)
    solver.plot_error_graph(P_list, solutions, h_list_ref)
    solver.plot_dependency_graph()

if __name__ == "__main__":
    main()