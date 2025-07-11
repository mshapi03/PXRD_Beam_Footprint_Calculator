# Developed by Mitch S-A
# Updated on July 11, 2025
# Reason for archiving:
#   Because the atomic MAC's ripped from NIST are additive, we don't need to do our own density calcs!
#   The code below is a great example of complex logic, so I'm leaving it for archival reasons.
# Usage Notes: Single-human beta test shows no issue. No unit testing performed on simplifying functions. Yields the following:
#   A dictionary of elements and their stoichiometry (element_dict)
#   A user-specified density (true_density) for MAC calculations
#   For Z <= 92: A dictionary of values ["Z", "Element", "Z/A", "I (eV)", "Density (g/cm3)", "Molecular Weight (g/mol)"]
#       which can be called with master_atomic_info
# Reminders:
#   Implement an interference checker when the x-ray beam source is selected (e.g. raise flag if Cu X-rays are used with Fe species)
#   Continue developing MAC_Calculator in here and then switch to beam-sample considerations
# Status: Non-functional, unmanaged git integration

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
    with open("../Element_Densities_and_Weights.json", 'r') as jsonfile:  # Read in .json with necessary information
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

true_density = 0 # Establish the density to be used in penetration depth calculations

# Loop to use if the user's sample does not generate atomic substituent dictionary
if master_atomic_info is None:
    print("You will need to provide your sample's density or best estimate of it in g/cm^3.")
    density_user_confirmation = False  # Establish a bool to ensure the user can confirm their input
    while not density_user_confirmation: # Continues until the user confirms a numerical input density
        user_input_density = input("Please enter your sample's density (g/cm^3): ")
        try: # Check and make sure value is able to become a float and repeat until successful
            true_density = float(user_input_density) # Stores density as true_density
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        # Repeat user's density back to them and begin standard y/n loop
        density_reaffirmation = input(
            "You have entered {density} g/cm^3. Is this correct? y/n: ".format(density=user_input_density))
        if density_reaffirmation != "y" and density_reaffirmation != "n": # Ensure y/n response
            print("Invalid input. Please enter y or n.")
        else:
            if density_reaffirmation == "y":
                density_user_confirmation = True  # This escapes the while not density_user_confirmation loop
                print("Density stored.")  # Visual confirmation to user
            elif density_reaffirmation == "n":
                continue  # Throws back to the beginning of the while not density_user_confirmation loop

# Loop to use if the user's sample does generate atomic substituent dictionary
if master_atomic_info is not None:
    density_user_confirmation = False  # Establish a bool to ensure the user can confirm their input
    sample_calculated_density = density_calc(element_dict, master_atomic_info) # Calculate estimated density
    print("""You may choose to provide your sample's density or use a linear combination (LC) of densities from atomic
constituents For your sample, this LC is {:.2f} g/cm^3.""".format(sample_calculated_density))
    print("Note that best results are obtained with a literature-based or empirically determined sample density.")
    while not density_user_confirmation: # Continues until the user confirms a numerical input density
        density_user_choice = input("Enter your own (c)ustom density or use the (p)rovided density? c/p: ")
        if density_user_choice != "c" and density_user_choice != "p":
            print("Invalid input. Please enter c or p.")
            break # Reprompt for user input, preventing code from proceeding with true_density = 0
        elif density_user_choice == "c": # Allow user input code like in the above density loop
            user_input_density = input("Please enter your sample's density (g/cm^3): ")
            try:  # Check and make sure value is able to become a float and repeat until successful
                true_density = float(user_input_density)  # Stores density as true_density
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
        elif density_user_choice == "p": # Auto-assign calculated density
            true_density = sample_calculated_density
        # Repeat user's density back to them and begin standard y/n loop
        density_reaffirmation = input(
        "You have entered/selected {density} g/cm^3. Is this correct? y/n: ".format(density=true_density))
        if density_reaffirmation != "y" and density_reaffirmation != "n":  # Ensure y/n response
            print("Invalid input. Please enter y or n.")
        else:
            if density_reaffirmation == "y":
                density_user_confirmation = True  # This escapes the while not density_user_confirmation loop
                print("Density stored.")  # Visual confirmation to user
            elif density_reaffirmation == "n":
                continue  # Throws back to the beginning of the while not density_user_confirmation loop

# By this point, for the user's sample, you have:
# A dictionary of elements and their stoichiometry (element_dict)
# A user-specified density (true_density) for MAC calculations
# For Z <= 92: A dictionary of values ["Z", "Element", "Z/A", "I (eV)", "Density (g/cm3)", "Molecular Weight (g/mol)"]
#   which can be called with master_atomic_info

# Calculating the MAC

# Convert Cu, Co, and Mo shorthand to usable keV number:
Cu_Co_Mo = {"Cu": 8.04, "Co": 6.93, "Mo": 17.479}

# Prompt user for the incident X-ray energy used
incident_energy = 0 # Establish a variable to hold the energy for calculations
energy_input_checker = False # Establish a boolean to allow user to check their input
while incident_energy == 0 and not energy_input_checker:
    incident_energy_input = input(
    """Please enter your incident x-ray energy. You may enter "Cu", "Co", "Mo" if you are using an x-ray tube, or type
in a value in keV (1-15000):""") # Prompt user for incident energy
    # Data validation if statement
    try:
        float(incident_energy_input)
        if float(incident_energy_input) < 1 or float(incident_energy_input) > 15000:
            print("Invalid input. Please enter a number or one of [\"Cu\", \"Co\", \"Mo\"].")
            continue
    except ValueError:
        if incident_energy_input not in Cu_Co_Mo.keys():
            print("Invalid input. Please enter a number or one of [\"Cu\", \"Co\", \"Mo\"].")
            continue
    # Standard user confirmation loop
    radiation_reaffirmation = input("You have entered {radiation} (keV). Is this correct? y/n: ".format(radiation=incident_energy_input))
    if radiation_reaffirmation not in ["y", "n"]: # Data validation
        print("Invalid input. Please enter y or n.") # Returns to the beginning of the while loop
    else:
        if radiation_reaffirmation == "y": # Store numerical energy in incident_energy
            if incident_energy_input in Cu_Co_Mo.keys():
                incident_energy = Cu_Co_Mo[incident_energy_input]
            else:
                incident_energy = incident_energy_input
            energy_input_checker = True  # This escapes the while not energy_input_confirmation loop
            print("Incident energy stored.")  # Visual confirmation to user
        elif radiation_reaffirmation == "n":
            continue  # Throws back to the beginning of the while not energy_input_confirmation loop

print(incident_energy)


# Parse Atomic_LAC_Working.json for the relevant higher and lower energy for each element
# Assume linearity between those two points and calculate the best estimate of LAC for that element
# Use the molecular_weight calc function and density_function code to