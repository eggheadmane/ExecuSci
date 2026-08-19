import requests
import bs4
import os
import csv

class Scraper:
    def __init__(self, doi: str, api_key: str):
        """
        Initialise the Scraper with a DOI and API key.

        Args:
            doi (str): The DOI of the article to scrape.
            api_key (str): The API key for accessing the Elsevier API.
        """
        self.doi = doi
        self.api_key = api_key
        self.dataset = []

    def make_request(self):
        """
        Make a request to the Elsevier API to retrieve the article content.

        Raises:
            Exception: If the request fails with a status code other than 200.
        """
        response = requests.get(f"https://api.elsevier.com/content/article/doi/{self.doi}?APIKey={self.api_key}") # Make request to Elsevier API
        if response.status_code == 200:
            print("Request successful \n")
            self.response = response
            self.full_text = response.text 
        else:
            raise Exception(f"Request failed with status code: {response.status_code} \n")

    def make_soup(self):
        """
        Parse the response text and create a BeautifulSoup object for easy parsing.
        """
        self.soup = bs4.BeautifulSoup(self.full_text, "lxml") 

    def find_equations(self):
        """
        Find all equations in the article and store them in a dictionary.

        Returns:
            mathml_dict: A dictionary containing the equation number and their MathML representations.
        """
        self.equation = self.soup.find_all("ce:formula")

        self.mathml_dict = {}
        for eq in self.equation:
            label = eq.find("ce:label") # Find equation number in the format (n)
            index = int(label.text[1:-1]) # Remove parentheses and convert to int
            mathml = eq.find("mml:math") 
            mathml = mathml.contents[1] # Remove \n from beginning and end along with outer tags
            self.mathml_dict[index] = str(mathml) 
        
        return self.mathml_dict
    
    def find_constants(self):
        """
        Find all constants in the article and store them in a dictionary with their units and values.

        Returns:
            const_dict: A dictionary containing the constants and their values.
        """
        self.tables = self.soup.find_all("ce:table")
        
        consts = []
        vals = []
        for i, table in enumerate(self.tables):
            if i != 2: # WIP - only looking at table 3 for now
                continue
            groups = table.find_all("tgroup") # Combined groups of header and body
            for group in groups:
                head = group.find("thead")
                h_entries = head.find_all("entry") # Contains unformatted constant names
                for entry in h_entries:
                    entry = entry.text.replace("\n", "").strip() # Remove newlines and whitespace

                    if entry.startswith("("): # Move units at start of constant to end
                        lhs, rhs = entry.split(")")
                        entry = f"{rhs} {lhs})"

                    if len(entry.split()[0]) > 1: # Underscore combined constant names
                        lhs, rhs = entry.split(" ", 1)
                        lhs = f"{lhs[0]}_{lhs[1:]}"
                        entry = f"{lhs} {rhs}"

                    consts.append(entry)

                body = group.find("tbody")
                b_entries = body.find_all("entry") # Contains constant values
                for entry in b_entries:
                    vals.append(float(entry.text))
                
        self.const_dict = dict(zip(consts, vals))
        return self.const_dict
    
    def create_mathml_txt(self, filepath: str):
        """
        Create a text file containing all the MathML equations.

        Args:
            filepath (str): The name of the file to save the equations to.

        Raises:
            Exception: If the file name does not end with .txt.
        """
        mmld = self.mathml_dict

        if not filepath.endswith(".txt"):
            raise Exception("File must be a .txt file")
        
        with open(f"{filepath}", "w", encoding="utf-8") as file:
            for i in range(1, len(mmld) + 1):
                mathml = str(mmld[i]) # Get string representation of MathML
                self.dataset.append(mathml)
                file.write(repr(mathml) + "\n") # Write repr to file to preserve formatting
            print(f"Equations saved to {filepath}")
    
    def create_mathml_csv(self, filepath: str):
        """
        Create a CSV file containing all the MathML equations.

        Args:
            filepath (str): The name of the file to save the equations to.

        Raises:
            Exception: If the file name does not end with .csv.
        """
        mmld = self.mathml_dict

        if not filepath.endswith(".csv"):
            raise Exception("File must be a .csv file")
        
        with open(f"{filepath}", "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            for i in range(1, len(mmld) + 1):
                mathml = str(mmld[i])
                writer.writerow([mathml])
    
    def scrape(self, filepath: str=None):
        """
        Main function to scrape equations and constants from a DOI.

        Args:
            filepath (str, optional): The path to the file to save the equations to.

        Returns:
            mathml_dict: A dictionary containing the equation number and their MathML representations.
            const_dict: A dictionary containing the constants and their values.   
        """
        self.make_request()
        self.make_soup()
        mathml_dict = self.find_equations()
        if not mathml_dict:
            raise Exception("No equations found. Ensure your WiFi account is verified with Elsevier.")
        const_dict = self.find_constants()

        if filepath:
            if filepath.endswith(".txt"):
                self.create_mathml_txt(filepath)
            elif filepath.endswith(".csv"):
                self.create_mathml_csv(filepath)
        
        return mathml_dict, const_dict

def test():
    doi = "10.1016/j.jmatprotec.2017.04.005"
    api_key = os.getenv("ELSEVIER_API_KEY")
    scraper = Scraper(doi, api_key)
    mathml_dict, const_dict = scraper.scrape()

def main():
    doi = "10.1016/j.jmatprotec.2017.04.005"
    api_key = os.getenv("ELSEVIER_API_KEY")
    scraper = Scraper(doi, api_key)
    scraper.make_request()
    scraper.make_soup()
    scraper.find_equations()
    scraper.find_constants()

if __name__ == "__main__":
    main()