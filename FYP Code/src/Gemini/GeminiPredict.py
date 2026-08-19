import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os
import csv
import sacrebleu
from tqdm import tqdm
import time


class GeminiPredict():
    def __init__(self, api_key, model_name):
        """
        Initialise the GeminiPredict object with a model name and load the given API key.
        """
        self.predictions = []
        self.model_name = model_name

        if api_key:
            self.api_key = api_key
            genai.configure(api_key=api_key)
            print("API key loaded successfully!")
        else:
            raise ValueError("API key not found. Please provide a valid API key.")

    def predict(self, mml, temperature=0.1, retries=3):
        """
        Predicts the SymPy Python code equivalent of a given MathML expression using the Gemini model set in __init__().

        Args:
            mml (str): The MathML expression to be translated.
            temperature (float, optional): The temperature parameter for generation. Defaults to 0.1.
            retries (int, optional): Number of retries in case of failure. Defaults to 3.
        
        Returns:
            str: The SymPy Python code equivalent of the given MathML expression.
        """
        prompt = f"""
        You are an expert at translating MathML to Python code using the SymPy library. Translate the following MathML expression into a valid Python SymPy expression. 
        Ensure that all variables are treated as symbolic variables and each is defined separately on a new line. 
        Assume that SymPy has been imported as `from sympy import *` so DO NOT include any import statements in your output.
        Example: 
        MathML: '<mml:mi>p</mml:mi>\n<mml:mo>=</mml:mo>\n<mml:mrow>\n<mml:msub>\n<mml:mi>p</mml:mi>\n<mml:mi>a</mml:mi>\n</mml:msub>\n<mml:mo>-</mml:mo>\n<mml:msub>\n<mml:mi>y</mml:mi>\n<mml:mrow>\n<mml:mi>r</mml:mi>\n<mml:mi>e</mml:mi>\n<mml:mi>2</mml:mi>\n</mml:mrow>\n</mml:msub>\n</mml:mrow>'
        SymPy Python code: 'p = Symbols('p')\np_a = Symbols('p_a')\ny_re2 = Symbols('y_re2')\ne = Eq(p, p_a - y_re2)'
        
        Now, translate the following MathML expression into Python code using SymPy.
        MathML: {mml}
        SymPy Python code:
        """
        model = genai.GenerativeModel(model_name=self.model_name)
        generation_config = GenerationConfig(temperature=temperature)

        
        for attempt in range(retries):
            try:
                response = model.generate_content(prompt, generation_config=generation_config) # Pass prompt to model and generate response
                return response.text
            except Exception as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt # Expontential backoff
                    time.sleep(wait_time)
                else:
                    raise e

    def predict_from_txt(self, filepath, retries=3):  
        """
        Predicts the SymPy Python code equivalent of a list of MathML expressions stored line by line in a .txt file.

        Args:
            filepath (str): The path to the .txt file containing MathML expressions.
            retries (int, optional): Number of retries in case of failure. Defaults to 3.

        Returns:
            predictions: A list of SymPy Python code equivalent of the given MathML expressions.
        """
        with open(filepath, "r") as file:
            total_rows = sum(1 for row in file) # For progress bar

        with open(filepath, "r") as file:
            lines = file.readlines()
            with tqdm(total=total_rows, desc="Generating Predictions", unit="row") as pbar:
                for mml in lines: # Predict rows 1 by 1
                    text = self.predict(mml, retries=retries)
                    self.predictions.append(text)
                    pbar.update(1)

        return self.predictions

    def predict_from_csv(self, filepath, retries=3):
        """
        Predicts the SymPy Python code equivalent of a list of MathML expressions stored in a .csv file.

        Args:
            filepath (str): The path to the .csv file containing MathML expressions.
            retries (int, optional): Number of retries in case of failure. Defaults to 3.

        Returns:
            predictions: A list of SymPy Python code equivalent of the given MathML expressions.
        """
        with open(filepath, "r") as file:
            reader = csv.reader(file)
            total_rows = sum(1 for row in reader) - 1 # For progress bar
        
        with open(filepath, "r") as file:
            reader = csv.reader(file)
            next(reader)
            with tqdm(total=total_rows, desc="Generating Predictions", unit="row") as pbar:
                for row in reader:
                    mml = row[0]
                    text = self.predict(mml, retries=retries)
                    self.predictions.append(text)
                    pbar.update(1)
        
        return self.predictions
    
    def predict_from_list(self, mml_list, retries=3):
        """
        Predicts the SymPy Python code equivalent of a list of MathML expressions.

        Args:
            mml_list (list): A list of MathML expressions.
            retries (int, optional): Number of retries in case of failure. Defaults to 3.

        Returns:
            predictions: A list of SymPy Python code equivalent of the given MathML expressions.
        """
        total_rows = len(mml_list)
        with tqdm(total=total_rows, desc="Generating Predictions", unit="row") as pbar:
            for mml in mml_list:
                text = self.predict(mml, retries=retries)
                self.predictions.append(text)
                pbar.update(1)
        
        return self.predictions
    
    def generate_predictions(self, mml_list=None, filepath=None):
        """
        Main function to generate predictions from a list of MathML expressions or a file containing MathML expressions.

        Args:
            mml_list (list, optional): A list of MathML expressions.
            filepath (str, optional): The path to a file containing MathML expressions.

        Returns:
            predictions: A list of SymPy Python code equivalent of the given MathML expressions.
        """
        if mml_list and filepath:
            raise ValueError("Please provide either a list of MathML expressions or a file containing MathML expressions, not both.")

        if mml_list:
            predictions = self.predict_from_list(mml_list)
            return predictions

        if filepath:
            self.filepath = filepath
            self.filename = os.path.splitext(filepath)[0]
            if filepath.endswith(".txt"):
                predictions = self.predict_from_txt(filepath)
            elif filepath.endswith(".csv"):
                predictions = self.predict_from_csv(filepath)
            else:
                raise ValueError("File must be either a .txt or .csv file")
        else:
            raise ValueError("Please provide either a list of MathML expressions or a file containing MathML expressions")
        
        return predictions
                    
    def save_predictions(self, new_filename=None):
        if not self.predictions:
            print("Generating predictions first")
            self.predict_from_file()
        if new_filename is None:
            new_filename = self.filename

        with open(f"{new_filename}_predictions.txt", "w") as file:
            for pred in self.predictions:
                file.write(pred + "\n")

    def evaluate_bleu(self, filename=None, model_name=None):
        if filename is None:
            filename = self.filename
        if model_name is None:
            model_name = self.model_name
        if not self.predictions:
            # self.predict_from_file(filename, model_name)
            with open(f"{filename}.csv", "r") as file:
                reader = csv.reader(file)
                total_rows = sum(1 for row in reader) - 1 # For progress bar
            
            predictions = []  
            with open(f"{filename}.csv", "r") as file:
                reader = csv.reader(file)
                next(reader)
                with tqdm(total=total_rows, desc="Generating Predictions", unit="row") as pbar:
                    for row in reader:
                        mml = repr(row[0])
                        text = self.predict(mml, model_name=model_name)
                        predictions.append(repr(text))
                        pbar.update(1)
                    
            with open(f"{filename}_predictions.txt", "w") as file:
                for pred in predictions:
                    file.write(pred + "\n")

        with open(f"{filename}.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)
            refs = [repr(row[1]) for row in reader]
        with open(f"{filename}_predictions.txt", "r") as file:
            preds = [row for row in file]

        bleu = sacrebleu.corpus_bleu(preds, [refs])
        print(f"SacreBLEU Score: {bleu.score}")

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    gemini = GeminiPredict(api_key)
    gemini.evaluate_bleu("gemini_test_1", "models/gemini-1.5-flash")

if __name__ == "__main__":
    main()