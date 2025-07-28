# Developed by Mitch S-A
# Updated on July 28, 2025
# Usage Notes: Single-human beta test shows no terminal issue. No unit testing performed on individual functions.
# Status: Functional as a part one, git integrated

# ---------- Necessary imports ----------

# Library to create stoichiometric dictionary from chemical formula:
import chemparse
# Library to read and write json files:
import json
# Libraries to enable throwing to BSOC (Pt. 2 of code) when complete
import subprocess
import sys
import os
import pickle

# ---------- Short Reference Dictionaries and Lists ----------

# Convert Cu, Co, and Mo shorthand to usable keV number:
Cu_Co_Mo = {"Cu": 8.04, "Co": 6.93, "Mo": 17.479}
# Construct the file path for BSOC (Part 2) script to throw to once MAC is calculated
STIXE_file_path = os.path.abspath(sys.argv[0]) # Sample Output: /Users/mitchshapiro-albert/Pycharm_Projects_2025/STIXE/PXRD_Sample_Considerations.py
STIXE_path_split = STIXE_file_path.split("STIXE", 1) # Sample Output: [/Users/mitchshapiro-albert/Pycharm_Projects_2025/, /PXRD_Sample_Considerations.py]
BSOC_file_path = STIXE_path_split[0] + str("BSOC/PXRD_Beam_Profile.py") # Sample Output: /Users/mitchshapiro-albert/Pycharm_Projects_2025/BSOC/PXRD_Beam_Profile.py

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
        self.molecular_weight_value = molecular_weight_sum # Becomes a callable parameter as it is a quality of the sample
        return molecular_weight_sum

    def get_relative_abundance(self, atomic_info, molecular_weight): # Returns a dict of {"element" : relative abundance}
        relative_abundance_dictionary = {}
        for element in self.stoich.keys():
            gram_percent_abundance = (float(self.stoich[element]) * float(atomic_info[element][5])) / molecular_weight
            relative_abundance_dictionary[element] = gram_percent_abundance
        self.relative_abundance = relative_abundance_dictionary

    def calculate_sample_MAC(self, relative_abundance_dict, MAC_dict):
        # "For compounds and mixtures, values for μ/ρ can be obtained by simple additivity
        # i.e., combining values for the elements according to their proportions by weight."
        # https://physics.nist.gov/PhysRefData/XrayMassCoef/intro.html
        mass_atten_coef = 0
        # rel_abu_dict is of the form {"element": abundance}
        # MAC_dict is of the form {"element": MAC}
        for element in relative_abundance_dict.keys(): # Keys in both dictionaries match
            mass_atten_coef += relative_abundance_dict[element] * MAC_dict[element]
        self.mass_atten_coefficient = mass_atten_coef # Becomes a callable parameter as it is a quality of the sample

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
>> unorthodox chemical notation (e.g. use \"Ca4Al2C3O20H22\" for 3CaO·Al₂O₃·CaCO₃·11H₂O)\n""")
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

# Generates dictionary of elemental MAC values for all elements in a given sample with given energy
def get_sample_MAC_library(atomic_info, incident_energy):
    sample_MAC_library = {} # Establish empty dictionary to be populated and returned by the function
    incident_energy_num = float(incident_energy) # Make sure function input is a float for math/comparisons later
    with open("Atomic_LAC_Working.json", "r") as jsonfile: # Read in .json with necessary information
        full_LAC_dict = json.load(jsonfile) # Contents of "Atomic_LAC_Working.json" is now callable with Full_LAC_dict variable
        proton_numbers = [] # Establish an empty list to hold Z values of sample elements, used to iterate through .json
        returnable_key_list =[] # Establish an empty list to hold chemical symbol "keys" for final dict
        for element in atomic_info.keys(): # Iterate through "Symbol" (e.g. "Ca") in atomic_info
            returnable_key_list.append(element) # Populate final "keys" list
            proton_numbers.append(atomic_info[element][0]) # Populate list with Z of each element
        calculated_elemental_MACs = [] # Establish an empty list to hold each Z's calculated MAC
        for proton in proton_numbers:
            energy_dependent_MAC_dict = full_LAC_dict.get(str(proton))  # Navigate to the sub-dictionary of all MACs for the element
            keV_MAC_bounds = [] # Empty list to store floats for MAC calculation
            # After for loop, contains [lower keV bound, upper MAC value, upper keV bound, lower MAC value]
            # Keep in mind that lower energy has higher MAC!
            for keV in energy_dependent_MAC_dict.keys(): # Iterate through every keV in the elements keV/MAC list
                keV_num = float(keV) # Type conversion to allow proper </> comparisons
                if keV_num <= incident_energy_num: # Update the keV and MAC values if a closer value is found
                    keV_MAC_bounds.clear()
                    keV_MAC_bounds.append(keV_num)
                    keV_MAC_bounds.append(energy_dependent_MAC_dict[keV])
                elif keV_num > incident_energy_num: # Assign the current keV and MAC values as the first value above the input
                    keV_MAC_bounds.append(keV_num)
                    keV_MAC_bounds.append(energy_dependent_MAC_dict[keV])
                    break # break the loop as soon as this value is found
            # Assume linearity between the two energies and calculate a fudge factor
            # Calculated as a percentage closeness to lower keV (e.g. 0.98 for Cu/8.04 keV compared to 8 and 10 keV)
            linearity_bias = (keV_MAC_bounds[2] - incident_energy_num) / (keV_MAC_bounds[2] - keV_MAC_bounds[0])
            # Applied linearity fudge factor to pull MACs to yield single representative elemental MAC
            biased_MAC = keV_MAC_bounds[1] - ((1 - linearity_bias) * (keV_MAC_bounds[1] - keV_MAC_bounds[3]))
            calculated_elemental_MACs.append(biased_MAC)
        for i in range(0, len(returnable_key_list)):
            sample_MAC_library[returnable_key_list[i]] = calculated_elemental_MACs[i]
    return sample_MAC_library

# Generate a dictionary of all x-ray edges for the atoms in the user's sample
def get_edge_info(stoich_dict):
    sample_x_ray_energy_dictionary ={} # Established desired dictionary as empty
    with open("x-ray_absorption_edges_UW.json", "r") as jsonfile: # Read in .json with necessary information
        master_x_ray_energy_dict = json.load(jsonfile) # Make JSON file accessible as dictionary
        for element in stoich_dict.keys(): # Iterate through the elements in the user's sample
            try: # Append edge information for elements 11 <= Z <= 92
                sample_x_ray_energy_dictionary[element] = master_x_ray_energy_dict[element]
            except KeyError: # Ignore elements 1 <= Z < 11 (no pertinent edges) or Z > 92
                continue
    # return an abridged x-ray edge info dictionary containing data only for relevant elements
    # Avoids reading in the same large .json file multiple times
    return sample_x_ray_energy_dictionary

# Flag if the incident energy is close to any known sample edges
def beam_and_sample_interference(atoms_and_x_ray_energies, incident_energy):
    incident_energy_num = float(incident_energy)
    print("Referencing the atoms in your sample against the incident energy...")
    warning_counter = 0 # Logs the number of times an interference is found
    for element in atoms_and_x_ray_energies: # Iterate through elements in the sample
        for edge in atoms_and_x_ray_energies[element]: # Iterate through edges for the element
            # Raise warning if the edge is within 1 keV of the incident energy
            if abs(incident_energy_num - float(edge[1])) <= 1:
                print("Potential interference: {edge} edge of {element} atom lies at {energy}.".format(edge=edge[0], element=element, energy=edge[1]))
                warning_counter += 1 # Adds one to the interference counter
    print("{} warning(s) raised.".format(warning_counter))

# ---------- Begin User-Facing Code ----------

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
try: # Gather info necessary for MAC and thickness calculations
    sample_atomic_info = get_atomic_info(element_dict) # Gets Z, density, atomic weight, etc.
except Exception as e: # Sets a flag to skip MAC/thickness calculations in remaining program if sample contains elements with Z > 92
    sample_atomic_info = None # Set master_atomic_info as a variable to properly instantiate Diffraction_Sample instance
    print("An error occurred: {e}".format(e=e))
    print("This is the result of unrecognized elements (Z > 92). MAC calculation for your sample is unavailable.")
    print("However, the program can still check the beam's axial and equatorial profile will fit on your sample.")
else: # Allows for program to still flag potential absorption/fluorescence issues
    sample_x_ray_edges = get_edge_info(element_dict)  # Gets energies at which absorption occurs for each element

# Instantiate the DiffractionSample class with user input information
if sample_atomic_info: # If atomic info library is generated, z remains calculable
    user_sample = DiffractionSample(element_dict)
else: # Otherwise overwrite the default z to False so the beam calculator script can avoid thickness calcs
    user_sample = DiffractionSample(element_dict, False)

# Prompt user for the incident X-ray energy used
incident_energy = 0 # Establish a variable to hold the energy for calculations
energy_input_checker = False # Establish a boolean to allow user to check their input
while incident_energy == 0 and not energy_input_checker:
    incident_energy_input = input(
    """Please enter your incident x-ray energy. You may enter "Cu", "Co", "Mo" if you are using an x-ray tube, or type
in a value in keV (1-15000): """) # Prompt user for incident energy
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

# Begin code block to calculate interferences and MAC if the DiffractionSample instance has z_calculable = True
if user_sample.z_calculable: # Check for sample-beam interactions if atomic libraries were calculated correctly
    # Auto-check selected incident energy against known fluorescence interferences using beam and sample interference function
    print("Checking for potential undesirable interactions between incident beam and sample...")
    beam_and_sample_interference(sample_x_ray_edges, incident_energy)
    # Prompt user to see all x-ray edges for their sample to do a manual check
    interference_y_n_checked = False # Establish bool to ensure proper y/n looping
    while not interference_y_n_checked:
        manual_interference_checker = input("Would you like to examine the known absorption edges of the atoms in your sample? y/n: ")
        if manual_interference_checker not in ["y", "n"]:
            print("Invalid input. Please enter y or n.") # Throw back to above prompt
        elif manual_interference_checker == "y": # Print all edges with user-friendly formatting
            for element, interference_list in sample_x_ray_edges.items():
                print("{}:".format(element))
                for edge in interference_list:
                    print("{edge} edge: {energy} keV, wavelength: {wavelength} angstroms.".format(edge=edge[0], energy=edge[1], wavelength=edge[2]))
            interference_y_n_checked = True
        elif manual_interference_checker == "n": # Move on without printing
            interference_y_n_checked = True
    # End interference checking code
    # Calculate sample MAC if atomic libraries are generated correctly
    print("Attempting to calculate the MAC of your sample...")
    # Calculate the sample molecular weight with a class method and atomic info
    user_sample.molecular_weight(sample_atomic_info)
    # Calculate the relative abundances of atoms in your sample in gram basis using class method
    user_sample.get_relative_abundance(sample_atomic_info, user_sample.molecular_weight_value)
    # Call get_sample_MAC_library on the sample to generate {"element" : MAC to use for given energy}
    sample_MAC_dict = get_sample_MAC_library(sample_atomic_info, incident_energy)
    # Call class method calculate_sample_MAC
    user_sample.calculate_sample_MAC(user_sample.relative_abundance, sample_MAC_dict) # Callable as user_sample.mass_atten_coefficient
    # Confirm success with user as print statement
    print("Success. Your sample's MAC is approximately {:.2f} cm^2/g.".format(user_sample.mass_atten_coefficient))
    # End MAC calculation for sample

# Because the DiffractionSample object is not a str or byte, we must use Pickle module to serialize and de-serialize the user's sample
# Serialize the instance to a byte string
serialized_sample = pickle.dumps(user_sample)
# Convert the byte string to a hex string for safe passage as a command-line argument
hex_serialized_sample = serialized_sample.hex()

# Pass the user's DiffractionSample object to the BSOC (PT. 2) code for beam profile calculation
command_list = [sys.executable, BSOC_file_path, hex_serialized_sample] # Specify the command list to throw to the BSOC script and pass the user's sample
try:
    print("Moving to beam shape considerations (part 2)...")
    subprocess.run(command_list, check=True)  # Try to run BSOC script
    print("Beam profile calculated successfully.")  # Message upon successful completion
except subprocess.CalledProcessError as e:  # Error handling
    print("An error occurred in calculating the beam profile: {e}".format(e=e))

print("Both scripts completed successfully. Happy experimenting!")

# At this point, this script can pass a:
#   (class variable) self.stoich - a dictionary of stoichiometry in the form {"Element" : "Atoms/Molecule"}
#   (global variable) The incident energy the user identified (incident_energy)
# Additionally, if the z_calculable is true (all elements Z > 92) you can pass:
#   (cv) self.molecular_weight_value - the molecular weight of the sample
#   (cv) self.relative_abundance - a dictionary of {"element" : relative abundance}
#   (cv) self.mass_atten_coefficient - the MAC of the sample for the incident energy the user identified
#   (gv) A dictionary of the elemental MACs for the user identified energy (pre-weighted sum)
#   (gv) A dictionary of the elemental absorption edges for the atoms in the sample