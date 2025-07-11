# Developed by Mitch S-A
# Updated on July 11, 2025
# Cloned from PXRD_Sample_Consideration and removed unnecessary sample density work
# Usage Notes: Single-human beta test shows no issue. No unit testing performed on simplifying functions.
# Reminders:
#   Implement an interference checker when the x-ray beam source is selected (e.g. raise flag if Cu X-rays are used with Fe species)
#   Continue developing MAC_Calculator in here and then switch to beam-sample considerations
# Status: Non-functional, unmanaged git integration

# ---------- Necessary imports ----------

import chemparse
import json

# ---------- Short Reference Dictionaries and Lists ----------

# Convert Cu, Co, and Mo shorthand to usable keV number:
Cu_Co_Mo = {"Cu": 8.04, "Co": 6.93, "Mo": 17.479}

# ---------- Class Definitions ----------

class DiffractionSample:
    def __init__(self, stoich_dict, z_calculable=True):
        self.stoich = stoich_dict # Stores the stoichiometry of the passed sample e.g. {"C":1, "O":2} for CO2
        self.z_calculable = z_calculable # Stores a boolean to tell beam calculation code if thickness (z direction) can be considered

    def __repr__(self):
        repr_string = "A PXRD sample with atoms: " + str(self.stoich) + f" and {'calculable' if self.z_calculable else 'uncalculable'} MAC."
        return repr_string

    def change_z_calculable(self, boolean):
        self.z_calculable = boolean

    def molecular_weight(self, atomic_info): # Returns molecular weight float given an atomic info dictionary
        # Note: atomic_info dictionary must be generated outside class definition because /
        #   chemparse will not fail above Z = 92 but atomic_info will fail
        molecular_weight_sum = 0  # Establish the desired variable with zero value
        for element in self.stoich.keys():  # Recall the keys of both passed dictionaries match
            # atomic_info[element] yields the list of str values for that element of the form /
            # ['Z', 'Element', 'Z/A', 'I (eV)', 'Density (g/cm3)', 'Molecular Weight (g/mol)']
            molecular_weight_sum += float(atomic_info[element][5]) * float(
                self.stoich[element])  # molecular weight * stoichiometric abundance
        self.molecular_weight = molecular_weight_sum # Becomes a callable parameter as it is a quality of the sample
        return molecular_weight_sum

    def get_relative_abundance(self, atomic_info, molecular_weight): # Returns a dict of {"element" : relative abundance}
        relative_abundance = {}
        for element in self.stoich.keys():
            gram_percent_abundance = (float(self.stoich[element]) * float(atomic_info[element][5])) / molecular_weight
            relative_abundance[element] = gram_percent_abundance
        return relative_abundance

    def calculate_sample_MAC(self, relative_abundance_dict, MAC_dict):
        pass
        # rel_abu_Dict is of the form {"element": abundance}
        # MAC_dict is of the form {"element": MAC}
        # Simple algebra
        # self.mass_atten_coef = mass_atten_coef # Becomes a callable parameter as it is a quality of the sample

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

# def get_sample_MAC_library(stoich_dict, incident_energy):
# should read .json file and return a dictionary with {"element": "MAC", etc.} for all elements in sample
# Keys will match stoich_dict
# Values: iterate through the keys in the .json file and find proper range of energies
    # Find the two entries (keys in the values of the nested dict which surround the passed incident energy (i.e. 10.0 and 15.0 if 12.5 keV is passed)
    # Calculate the "bias" of the passed energy (abs(15.0 - 12.5)/abs(15.0 - 10.0) = 50.0%
    # Pull the MACs from the surroudning incident energy - e.g. values attached to 10.0 and 15.0, 0.1 and 0.2
    # Assume linearity between MACs and apply the bias - e.g. MAC = 0.1 + (100% + 50%)*(0.2-0.1)
    # Save that as the MAC value for the element

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

# Pull dictionary of relevant atomic information based on the user input if all Z <= 92
print("Gathering information about the atoms in your sample...")
try:
    master_atomic_info = get_atomic_info(element_dict)
except Exception as e: # Terminates program if sample contains elements with Z > 92
    master_atomic_info = None # Set master_atomic_info as a variable to properly instantiate Diffraction_Sample instance
    print("An error occurred: {e}".format(e=e))
    print("This is the result of unrecognized elements (Z > 92). MAC calculation for your sample is unavailable.")
    print("However, the program can still check the beam's axial and equatorial profile will fit on your sample.")

# Instantiate the DiffractionSample class with user input information

if master_atomic_info: # If atomic info library is generated, z remains calculable
    user_sample = DiffractionSample(element_dict)
else: # Otherwise overwrite the default z to False so the beam calculator script can avoid thickness calcs
    user_sample = DiffractionSample(element_dict, False)

### Testing the class instantiation

# print(user_sample)
# print(user_sample.stoich)
# print(user_sample.z_calculable)
# test_molecular_weight = user_sample.molecular_weight(master_atomic_info)
# print(test_molecular_weight)
# print(user_sample.get_relative_abundance(master_atomic_info, test_molecular_weight))

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


# Use global function to parse Atomic_LAC_Working.json for the relevant higher and lower energy for each element
# Line 91: get_sample_MAC_library(stoich_dict, incident_energy)

# Use class function to determine the sample's MAC
# Line 53: def calculate_sample_MAC(self, relative_abundance_dict, MAC_dict):