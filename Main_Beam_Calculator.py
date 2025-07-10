# Developed by Mitch S-A
# Updated on July 10, 2025
# Usage Notes: Don't
# Dev Notes: Implement an interference checker when the x-ray beam source is selected (e.g. raise flag if Cu X-rays are used with Fe species)
# Status: Non-functional, unmanaged git integration

# To-Do:
# Finalize density calculation section (line 123)

# ---------- Necessary imports ----------

import chemparse
import json

# ---------- Class Definitions ----------

# ---------- Simplifying functions ----------

# Exception-handling version of chemparse's formula parsing function:
def chem_form_parser(formula):
    try:
        # chemparse.parse_formula returns a dictionary with element counts
        element_counts = chemparse.parse_formula(formula)
        # However, chemparse can't handle stupid formulas (e.g. 3CaO·Al2O3·CaCO3·11H2O)
        if len(element_counts) == 0:
            print("Could not recognize formula '{}'".format(formula))
            print("""Please ensure your formula is free of the following: \n>> * \n>> ·\n>> sub/superscript formating"
>> unorthodox chemical notation (e.g. use \"Ca4Al2C3O20H22\" for 3CaO·Al₂O₃·CaCO₃·11H₂O\n""")
            return {}
        return element_counts
    except Exception as e:
        print(f"Error parsing formula: {e}")
        return {}

# Generates dictionary of relevant atomic information based on a stoich dictionary from chem_form_parser
def get_atomic_info(stoich_dict):
    atomic_info_dictionary = {}  # Establish desired dictionary as empty
    with open("Element_Densities_and_Weights.json", 'r') as jsonfile:  # Read in .json with necessary information
        element_data_dict = json.load(jsonfile)
        for element in stoich_dict.keys():  # Pull each unique element from input stoich_dict (e.g "Ca")
            # element_data_dict[element] yields the list of values for that element of the form /
            # ['Z', 'Element', 'Z/A', 'I (eV)', 'Density (g/cm3)', 'Molecular Weight (g/mol)']
            atomic_info_dictionary[element] = element_data_dict[element]  # Note this is a list of strings still!
    # return an abridged atomic info dictionary containing only information for relevant elements
    # avoids reading in the same large .json file multiple times
    return atomic_info_dictionary

# Takes a stoich dictionary from chem_form_parser and atomic info from .json file returns a total mass
def molecular_weight_total(stoich_dict, atomic_info):
    molecular_weight_sum = 0 # Establish the desired variable with zero value
    for element in stoich_dict.keys(): # Recall the keys of both passed dictionaries match
        # atomic_info[element] yields the list of str values for that element of the form /
        # ['Z', 'Element', 'Z/A', 'I (eV)', 'Density (g/cm3)', 'Molecular Weight (g/mol)']
        molecular_weight_sum += float(atomic_info[element][5]) * float(stoich_dict[element]) # molecular weight * stoich abundance
    return molecular_weight_sum

# Function to calculate the weighted average density from stoichiometry
def density_calc(stoich_dict, atomic_info): # Takes a dictionary from chem_form_parser
    # Establish returnable density variable
    calculated_density = 0
    # Determine the sample's total molecular weight
    sample_molecular_weight = molecular_weight_total(stoich_dict, atomic_info)
    # Write a master for loop to calculate the gram-based percent abundance of the element and multiple by density
    for element in stoich_dict.keys(): # recall stoich_dict.keys() is equivalent to atomic_info.keys()
        gram_percent_abundance = (float(stoich_dict[element]) * float(atomic_info[element][5])) / sample_molecular_weight
        calculated_density += gram_percent_abundance * float(atomic_info[element][4])
    return calculated_density

# ---------- Function debugging section ----------

# sample_CaCO3_dict = {'Ca': 1.0, 'C': 1.0, 'O': 3.0}
# sample_metal_dict = {'Fe': 5.0, 'Cu': 3.0, 'O': 20.0, 'C':6}
#
# master_CaCO3_dict = get_atomic_info(sample_CaCO3_dict)
# master_metal_dict = get_atomic_info(sample_metal_dict)
# print(density_calc(sample_CaCO3_dict, master_CaCO3_dict))
# print(density_calc(sample_metal_dict, master_metal_dict))

# ---------- Begin user facing code ----------
# Welcome message

print("""Welcome to the powder XRD beam footprint calculator! This program is designed to help you determine the best
optics settings for your sample, sample holder, and diffractometer when collecting powder X-ray diffraction data.""")

# Get chemical formula from user. Code below will repeat until a satisfactory element dictionary is generated.

element_dict = {}
while not element_dict:
    chemical_formula = input("Please enter your sample's known or approximate chemical formula: ")
    element_dict = chem_form_parser(chemical_formula)
    if element_dict != {}:
        user_confirmed = False
        while not user_confirmed:
            print("Please confirm the following elemental breakdown: ")
            for key,value in element_dict.items():
                print(str(key), str(value))
            user_confirmation = input("Is this correct? y/n: ")
            if user_confirmation == "y":
                user_confirmed = True
            elif user_confirmation == "n":
                element_dict = {}
                user_confirmed = True
            else:
                print("Invalid input. Please enter y or n.")
    else:
        continue

print("Dictionary conversion successful.")

# Pull dictionary of relevant atomic information based on the user input

print("Gathering information about the atoms in your sample...")
try:
    master_atomic_info = get_atomic_info(element_dict)
except Exception as e:
    print("An error occurred: {e}. Density calculation for your sample unavailable.".format(e=e))
    master_atomic_info = None

# Loop to determine density of sample

true_density = 0 # Establish the density to be used in penetration depth calculations
density_user_confirmation = False # Establish a bool to ensure the user can confirm their input
while true_density == 0 and not density_user_confirmation:
    if master_atomic_info is None: # Code to use if the user's sample does not generate atomic substituent dictionary
        print("You will need to provide your sample's density or best estimate of it in g/cm^3.")
        user_input_density = input("Please enter your sample's density (g/cm^3): ")
        # Code to ask for user estimated density and confirm with user
    elif master_atomic_info is not None:  # Code to use if the user's sample does generate atomic substituent dictionary
        print("You may choose to provide your sample's density or use a linear combination of densities from atomic constituents.")
        print("Note that best results are obtained with a literature-based or empirically determined sample density.")
        calculated_density = density_calc(element_dict, master_atomic_info)
        print("Your sample's density is {:.2f} g/cm^3.".format(calculated_density))
        density_user_choice = input("Enter your own (c)ustom density or use the (p)rovided density? c/p ")


# Tell user what the assumed density will be and proceed.