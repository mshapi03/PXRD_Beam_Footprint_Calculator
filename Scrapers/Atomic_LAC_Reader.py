# A python script containing two approaches to rip MAC data from an online NIST database
# Note that all data comes from NIST Standard Reference Database 126
# https://www.nist.gov/pml/x-ray-mass-attenuation-coefficients

# Imports
# Necessary to allow for .split() to take multiple delimiters
import re
# Necessary for webscraping HTML table off of above source
import requests
from bs4 import BeautifulSoup
#Necessary for writing JSON file with results
import json

# Simple Approach: function to read in a table copy-pasted into a .txt

def elem_lac_reader(lac_file):
    # Establish an empty dictionary to append to
    energy_lac_dict = {}
    # Establish a counter variable to ensure the header lines are skipped
    counter = 0
    # Read the passed filename
    with open(lac_file, 'r') as active_file:
        try:
            lines = active_file.readlines()
            for line in lines:
                if counter >= 2:
                    parsed_row = re.split("[\t ]", line)  # Assuming tab or space separated values
                    # Length is 3, 4, or 5 - we always want first two numbers
                    i = len(parsed_row)
                    # Key becomes the incident energy, converted from MeV to keV
                    key = float(parsed_row[i-3])*1000
                    # Value becomes the element's mass attenuation coefficient at the key's incident energies
                    value = float(parsed_row[i-2])
                    # Add the key-value pair to the dictionary
                    energy_lac_dict[key] = value
                    # No return since this code is just to populate this .py file with callable lists
                    # No need to iterate counter
                else:
                    counter += 1
        except ValueError:
            print("Encountered ValueError. Perhaps initial file is empty or contains blank lines at conclusion.")
    # Print the resulting dictionary
    print(energy_lac_dict)

# Example call of the Simple Approach:
# Calling on the current contents of "Atomic_LAC_Working.txt" Z 1 -18
# elem_lac_reader("Atomic_LAC_Working.txt") # Beryllium example as of last update 7/09/2025

# Advanced Approach: HTML Parsing the website directly

# Modify the elem_lac_reader function to take in an ASCII table and specified element (Z)
# Output kwarg will determine whether the dictionary formed is printed or returned

def html_lac_reader(ascii_table, z_num, output="p"):
    # Establish an empty dictionary to append to
    html_lac_dict = {}
    # Establish a counter variable to ensure the header lines are skipped
    counter = 0
    try:
        ascii_rows = ascii_table.splitlines() # Yields a list where data begins on the 6th index
        for str_data in ascii_rows:
            if counter >= 5 and len(str_data) > 1: #
                parsed_row = re.split("[\t ]", str_data)  # Assuming tab or space separated values
                # Length is 8 (edge line) or 9 - we always want first two numbers
                i = len(parsed_row)
                # Key becomes the incident energy, converted from MeV to keV
                key = float(parsed_row[i-6])*1000
                # Value becomes the element's mass attenuation coefficient at the key's incident energies
                value = float(parsed_row[i-4])
                # Add the key-value pair to the dictionary
                html_lac_dict[key] = value
                # No return since this code is just to populate this .py file with callable lists
                # No need to iterate counter
            else:
                counter += 1
    except ValueError:
        print("Encountered non-fatal ValueError (blank lines at conclusion).")
    # Output the resulting dictionary depending on user input
    if output == "r":
        return html_lac_dict
    else:
        print("The dictionary for Z = {z_num} is as follows:".format(z_num=z_num))
        print(html_lac_dict)

def get_ascii_table(z_num):
    # Format z_num to integrate properly into URL
    if z_num < 10:
        str_z_num = str("0" + str(z_num))
    else:
        str_z_num = str(z_num)
    url = "https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z{0}.html".format(str_z_num)
    try:
        response = requests.get(url)
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

# Example call of the Advanced Approach - print:
# working_table = get_ascii_table(15)
# html_lac_reader(working_table, 15, "p")

# Write a helper function that will write each dictionary to a master .txt file:

def simple_json_writer(data_dict, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(data_dict, f)  # Could add kwarg indent=4 for human-compatible printing
        print(f"Dictionary successfully written to {filename}")
    except Exception as e:
        print(f"Error writing dictionary to file: {e}")

# For loop that will rip Z's 1 - 92 and output to JSON file
# Do NOT run this unless you absolutely need to update values - it's a lot of server requests!
# Just reference the .json file in the project

master_z_mac_dict = {}
for z in range(1, 93):
    working_table = get_ascii_table(z)
    energy_mac_dict = html_lac_reader(working_table, z, "r")
    master_z_mac_dict[z] = energy_mac_dict
simple_json_writer(master_z_mac_dict,
                   "../src/PXRD_Beam_Footprint_Calculator/MAC_Calculator_Directory/JSONs/Atomic_MACs.json")