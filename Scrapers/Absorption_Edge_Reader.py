# A python script to rip absorption edge data from an online academic database
# Note that all data comes from Ethan Merritt at UW
# http://skuld.bmsc.washington.edu/scatter/AS_periodic.html

# -------- Imports --------
# Necessary to allow for .split() to take multiple delimiters
import re
# Necessary for webscraping HTML table off of above source
import requests
from bs4 import BeautifulSoup
#Necessary for writing JSON file with results
import json

# -------- Global Variables --------

# List of atomic symbols to enable iteration through each element's webpage

atomic_symbols = [
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U"
]

# -------- Functions --------

# Gets ASCII table from the webpage as pre-formatted ASCII text
def get_uw_ascii_table(atomic_symbol):
    general_url = "http://skuld.bmsc.washington.edu/scatter/data/{element}.html".format(element=atomic_symbol)
    try:
        response = requests.get(general_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the table - selector based on the <pre> tag for preformatted ASCII table
        table = soup.find("pre")
        table_text = table.get_text() # Outputs a multiline string without HTML tags from HTML-formatted ASCII table
        return table_text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Cleans the ASCII table of previous formatting and removes "blank" characters
def clean_ascii_table(ascii_table):
    ascii_data = [] # Establish an empty list to hold content
    ascii_rows = ascii_table.splitlines()  # Takes each line of the table and stores it in above list
    for str_data in ascii_rows: # For each line of the table:
        # Create a list of str data, split wherever there is a tab or space
        parsed_row_data = re.split("[\t ]", str_data)
        for text_item in parsed_row_data: # For each of those strings:
            if text_item: # if the string is not empty (i.e. "")
                ascii_data.append(text_item)
    return(ascii_data)

# Takes cleaned ASCII data and converts it to a dict of form {'Ir': [['K', '76.1110', '0.1629'], ['L-I', etc...
# Note the general form {"element": [[Name of edge, keV, A], [etc...
def create_edge_data_dict(cleaned_list):
    element_edge_data_dict = {cleaned_list[2]:[]} # Establish empty dict of {"element": [[edge 1][edge 2][etc.]]
    for i in range(9, len(cleaned_list), 3): # Iterate through edge data starting with first K edge
        # Append each Edge/KeV/A pair to a new list within the list that is the dict value
        element_edge_data_dict[cleaned_list[2]].append(cleaned_list[i: i+3])
    return  element_edge_data_dict

# Writes output of the above functions to a Python-parseable JSON file
# Function originates in Atomic_LAC_Reader.py
def simple_json_writer(data_dict, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(data_dict, f)  # Could add kwarg indent=4 for human-compatible printing
        print(f"Dictionary successfully written to {filename}")
    except Exception as e:
        print(f"Error writing dictionary to file: {e}")

# -------- Singular Examples to Run for Debugging --------

# cleaned_Na_table = clean_ascii_table(get_uw_ascii_table("Na"))
# cleaned_Ir_table = clean_ascii_table(get_uw_ascii_table("Ir"))
# print(cleaned_Na_table)
# print(cleaned_Ir_table)
# print(create_edge_data_dict(cleaned_Na_table))
# print(create_edge_data_dict(cleaned_Ir_table))

# -------- Functional Scraping/JSON Loop --------
# Caution - do not run this without justification (i.e. updating the current JSON file)
# It requests a lot of information from servers!

complete_uw_edge_repository = {} # Establish the empty dict to write to JSON file
for element in atomic_symbols: # Iterate from "Na" to "U"
    print("Beginning x-ray edge retrieval for: {element}".format(element=element))
    # Call each of the above functions
    ascii_retrieval = get_uw_ascii_table(element)
    clean_table = clean_ascii_table(ascii_retrieval)
    create_element_dict = create_edge_data_dict(clean_table)
    # Map singular output of create_element_dict to complete dictionary
    complete_uw_edge_repository[element] = create_element_dict[element]
    print("Completed x-ray edge retrival for: {element}".format(element=element))
# Write the file
simple_json_writer(complete_uw_edge_repository,
                   "../src/PXRD_Beam_Footprint_Calculator/MAC_Calculator_Directory/MAC_JSONs/X-ray_Absorption_Edges.json")
