import pandas as pd
import sympy as sp
import os
from sympy import *
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import random
from IPython.display import Markdown
from lxml import etree
import json
from IPython.display import display
from tqdm import tqdm
import re
import csv

class Equation:
    # Class attributes (only instantiated the first time)
    latin = symbols('a b c d f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z')
    greek = symbols('α β γ δ ε ζ η θ ι κ λ μ ν ξ ο ρ σ τ υ φ χ ψ ω Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω')
    vars = latin + greek 
    operators = ('+', '-', '*', '/', '**')
    functions = (sin, cos, tan, exp, log, sqrt)
    nums = tuple(range(1, 10))

    def __init__(self, n=52):
        self.get_combined_vars(n) # 52 to roughly match the number of latin and greek letters for equal probability of choice
        self.vars += self.combined_vars # Add the combined variables to the list of variables

    def get_combined_vars(self, num):
        combined_vars = []
        for _ in range(num): # Create num combined variables by joining two random variables with a "_"
            part1 = random.choice(self.vars)
            part2 = random.choice(self.vars + self.nums)
            part3 = random.choice(self.vars + self.nums)
            part4 = random.choice(self.vars + self.nums)
           
            cv1 = f"{part1}_{part2}"
            cv2 = f"{part1}_{part2}_{part3}"
            cv3 = f"{part1}_{part2}_{part3}_{part4}"

            combined_vars.append(random.choice([cv1, cv2, cv3]))
        self.combined_vars = symbols(" ".join(combined_vars)) # Convert the list of combined variables to a tuple of SymPy symbols

    def generate_expression(self):            
        complexity1 = random.randint(1, 2) # Length of expression
        expression = random.choice(self.functions)(random.choice(self.vars))  # Start with a function of a variable e.g. sin(a)
        
        for _ in range(complexity1):
            operator = random.choice(self.operators)
            complexity2 = random.randint(1, 3) # Complexity of the term
            if complexity2 == 1:
                term = random.choice((random.choice(self.vars), random.choice(self.nums))) # e.g. a, 1
            elif complexity2 == 2:
                term = random.choice(self.functions)(random.choice(self.vars)) # e.g. sin(a), log(b)
            elif complexity2 == 3:
                func = random.choice(self.functions)
                inner1 = random.choice(self.vars)
                inner2 = random.choice((random.choice(self.nums), random.choice(self.vars)))
                inner_operator = random.choice(self.operators)
                term = f"{func.__name__}({inner1} {inner_operator} {inner2})" # e.g. sin(a + b), log(c * d)   
            
            expression = f"{expression} {operator} {term}" # Concatenate the expression with the operator and term
        return sympify(expression)
    
    def generate_equation(self):
        lhs = random.choice(self.vars) # Choose a random variable for the left-hand side
        rhs = self.generate_expression()
        self.equation = Eq(lhs, rhs) # Create an attribute containing a SymPy equation in the form of lhs = rhs
    
    def generate_sum(self):
        lhs = random.choice(self.vars) # Choose a random variable for the left-hand side
        
        expression = self.generate_expression()
        rhs = Sum(expression, (random.choice(self.vars), random.choice(self.nums), random.choice(self.nums + self.vars))) # Create a summation on the right-hand side
        
        self.equation = Eq(lhs, rhs) # Create an attribute containing a SymPy sum equation in the form of lhs = rhs

    def generate_derivative(self):
        lhs = random.choice(self.vars) # Choose a random variable for the left-hand side
        expression = self.generate_expression()
        expression_vars = list(expression.free_symbols)
        
        rhs = Derivative(expression, random.choice(expression_vars)) # Create a derivative on the right-hand side

        self.equation = Eq(lhs, rhs) # Create an attribute containing a SymPy derivative equation in the form of lhs = rhs

    def generate_integral(self):
        lhs = random.choice(self.vars)
        expression = self.generate_expression()
        expression_vars = list(expression.free_symbols)
        
        indefinite_rhs = Integral(expression, random.choice(expression_vars)) # Create an integral on the right-hand side
        definite_rhs = Integral(expression, (random.choice(expression_vars), random.choice(self.nums), random.choice(self.nums))) # Create a definite integral on the right-hand side

        self.equation = Eq(lhs, random.choice((indefinite_rhs, definite_rhs))) # Create an attribute containing a SymPy integral equation in the form of lhs = rhs
    
    def to_python(self):
        self.py = sp.printing.python(self.equation) # Convert the SymPy expression to Python code

    def format_python(self):
        py = self.py
        for line in py.splitlines():
            symbol = line.split(" = ")[0]
            if symbol == "e": # Ignore the equation line
                continue
            parts = symbol.split('_')  # Split by underscore
            if len(parts) > 2:  # Ensure there are multiple parts to process
                new_symbol =  parts[0] + '_' + ''.join(parts[1:])
                py = py.replace(symbol, new_symbol)  
        
        self.py = py # Update attribute
    
    def to_mathml(self):
        self.mml = sp.printing.mathml(self.equation, printer='presentation') # Convert the SymPy expression to MathML in the correct style
    
    def format_mathml(self):
        mml = self.mml
        mml = mml.replace("<mo>&InvisibleTimes;</mo>", "") # Remove invisible times operator to match scraped MathML
        mml = mml.replace("<mi>&ExponentialE;</mi>", "<mtext>exp</mtext>") # Replace exponential e with exp to match scraped MathML
        mml = mml.replace("<mo>&dd;</mo>", "<mi>d</mi>") # Replace differential d with d to match scraped MathML
        parser = etree.XMLParser(remove_blank_text=True) # Create an XML parser that removes blank text
        root = etree.fromstring(mml, parser) # Parse the MathML string into an XML element tree

        namespace = "http://www.w3.org/1998/Math/MathML" # Define the MathML namespace
        
        def add_namespace(elem): # Recursively add the namespace to all elements
            elem.tag = f"{{{namespace}}}{elem.tag}" # Add the namespace to the current tag
            for child in elem: # Do the same for all children
                add_namespace(child)                
    
        add_namespace(root) # Apply namespace

        mml =  etree.tostring(root, pretty_print=True, xml_declaration=False, encoding="UTF-8").decode("utf-8") # Convert the XML element tree back to a string
        mml = '\n'.join([line.lstrip() for line in mml.splitlines()]) # Remove leading whitespace from each line
        mml = mml.replace("ns0", "mml") # Replace the namespace prefix with "mml" to match scraped MathML
        mml = mml.replace('<mml:mrow xmlns:mml="http://www.w3.org/1998/Math/MathML">', "") # Remove first tag
        mml = re.sub(r"<mml:mo> </mml:mo>\s*\n", "", mml) # Remove empty <mo> tags and get rid of the empty line left behind
        
        index = mml.rfind("</mml:mrow>") # Logic to remove final mrow tag
        if index != -1:
            mml = mml[:index] + mml[index + 11:] # 11 is len(tag)       
        
        self.mml = mml[1:-1] # Update attribute removing first and last \n

    def print_latex(self):
        display(Markdown(f"$$ {latex(self.equation)} $$")) # Display the equation in LaTeX format

    def generate(self):
        random.choices((self.generate_equation, self.generate_sum, self.generate_integral, self.generate_derivative), weights=[40, 20, 20, 20])[0]() # Choose a random equation type and generate it
        self.to_python()
        self.format_python()
        self.to_mathml()
        self.format_mathml()
        return self.py, self.mml

class BaseDataset:
    def __init__(self, num):
        self.num = num
        self.dataset = []
    
    def get_columns(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    def _get_equation(self):

        try:
            columns = self.get_columns()
            eq = Equation()
            py, mml = eq.generate()
            return {columns[0]: mml, columns[1]: py}
        except:
            return None
        
    def create_dataset(self):
        mathml_py_dicts = []
        with tqdm(desc="Generating dataset") as pbar:
            while len(mathml_py_dicts) < self.num:
                result = self._get_equation()
                if result:
                    mathml_py_dicts.append(result)
                    pbar.total = self.num
                    pbar.update(1)
        
        self.dataset.extend(mathml_py_dicts)

    def create_dataset_mthread(self):
        n_cores = os.cpu_count() # Get the number of CPU cores on current machine
        n_workers = min(self.num, n_cores - 1) # Leave one core for the main process
        with ThreadPoolExecutor(max_workers=n_workers) as executor: # Create a pool of workers for multiprocessing
            futures = [executor.submit(self._get_equation) for _ in range(self.num)] # Submit the tasks to the workers

            mathml_py_dicts = []
            with tqdm(desc="Generating dataset") as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        mathml_py_dicts.append(result)
                        pbar.total=self.num
                        pbar.update(1)
                
        self.dataset.extend(mathml_py_dicts)
        
    def get_dataset(self):
        return self.dataset
    
    def clear_dataset(self):
        self.dataset.clear()
    
    def load_json(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)  # Update attribute from read file

    def load_csv(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, quotechar='"', delimiter=",")
            self.dataset = [row for row in reader]  # Update attribute from read file
    
    def _create_json(self):
        columns = self.get_columns()
        try: # Check to see if there is already data at the filepath
            with open(self.filepath, "r") as f:
                existing_data = json.load(f) # Load it if it exists
        except FileNotFoundError:
            existing_data = [] # Create an empty list otherwise

        self.create_dataset() # Make the dataset with num equations   
                
        existing_data.extend(self.dataset)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

    def _create_csv(self):
        columns = self.get_columns()
        try: # Check to see if there is already data at the filepath
            existing_data = pd.read_csv(self.filepath) # Load it if it exists
        except FileNotFoundError:
            existing_data = pd.DataFrame(columns=columns) # Create an empty df otherwise

        self.create_dataset() # Make the dataset with num equations
        
        new_data = pd.DataFrame(self.dataset)
        existing_data = pd.concat([existing_data, new_data])
        existing_data.to_csv(self.filepath, index=False)

    def create(self, filepath=None):
        if filepath:
            self.filepath = filepath

        if self.filepath.split(".")[-1] == "json":
            self._create_json()
        elif self.filepath.split(".")[-1] == "csv":
            self._create_csv()
        else:
            print("Invalid file format. Please use .json or .csv")

class TestDataset(BaseDataset):
    def __init__(self, num, filepath):
        super().__init__(num, filepath)
    def get_columns(self):
        return ["test1", "test2"]
    
def main():
    dataset = TestDataset(10, "test.csv")
    dataset.create()
    print(len(dataset.dataset))

def test():
    eq = Equation()
    py, mml = eq.generate()
    print(py)


if __name__ == "__main__":
    main()