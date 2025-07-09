# Developed by Mitch S-A
# Updated on July 8, 2025
# Usage Notes:
# Dev Notes: Implement an interference checker when the x-ray beam source is selected (e.g. raise flag if Cu X-rays are used with Fe species)
# Status: Non-functional, unmanaged git integration

# ---------- Necessary imports ----------

import csv
import chemparse

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

# ---------- Begin user facing code ----------
# Welcome message

print("""Welcome to the powder XRD beam footprint calculator! This program is designed to help you determine the best
optics settings for your sample, sample holder, and diffractometer when collecting powder X-ray diffraction data.""")

# Get chemical formula from user. Code below will repeat until a satisfactory element dictionary is generated.

element_dict_empty = True
while element_dict_empty == True:
    chemical_formula = input("Please enter your sample's known or approximate chemical formula: ")
    element_dict = chem_form_parser(chemical_formula)
    if element_dict != {}:
        user_confirmed = False
        while user_confirmed == False:
            print("Please confirm the following elemental breakdown: ")
            for key,value in element_dict.items():
                print(str(key), str(value))
            user_confirmation = input("Is this correct? y/n: ")
            if user_confirmation == "y":
                user_confirmed = True
                element_dict_empty = False
            elif user_confirmation == "n":
                break
            else:
                print("Invalid input. Please enter y or n.")
    else:
        continue

print("Dictionary conversion successful.")
#Debugging print:
print(element_dict)

# Now, prompt for density, and store a user given value.
# If no user has no value, calculate a weighted average from Elemental_Densities.
# Tell user what the assumed density will be and proceed.




# sample_density = 0.0
# density_acquired = False
# while density_acquired == False:
#     density_prompt = input("Is your density known? y/n: ")
#     if density_prompt == "y":
#         sample_density = input("Enter your sample density (g/cm^3): ")
#         density_acquired = True
#     elif density_prompt == "n":
#         # Change below to throw to density calculator
#         sample_density = 0
#         density_acquired = True
#     else:
#         print("Invalid input. Please enter y or n.")