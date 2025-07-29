# Developed by Mitch S-A
# Updated on July 29, 2025

# ---------- Necessary imports ----------

# Import simplifier logic functions from parent Beam_Profile_Calculator.py
from src.PXRD_Beam_Footprint_Calculator.Beam_Profile_Calculator import y_or_n_confirmation, get_user_float, user_pick_from
# Library to create stoichiometric dictionaries from chemical formula:
import chemparse
# Library to read and write JSON files:
import json
# Libraries to enable passing variables between Python scripts
import sys

# ---------- Short Reference Dictionaries and Lists ----------

# Convert Cu, Co, Mo, and Cr shorthand to usable keV number:
CCMC_Tubes = {"Cu": 8.04, "Co": 6.93, "Mo": 17.479, "Cr": 5.414}

# ---------- Class Definitions ----------

class SampleChemistry:
    def __init__(self, stoich_dict, valid_MAC = True):
        self.stoich = stoich_dict # Stores the stoichiometry of the passed sample, e.g. {"C":1, "O":2} for CO2
        self.valid_MAC = valid_MAC # Boolean to note if the stoich_dict contains Z > 92 (if a valid MAC can be calculated)

    def __repr__(self):
        return "A PXRD sample with atoms: " + str(self.stoich)

    def print_all_information(self):
        print(vars(self))

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
        # However, chemparse can't handle non-standard formulas (e.g. 3CaO·Al2O3·CaCO3·11H2O)
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
    validated_MAC = True # Create a boolean flag if an unrecognized element is discovered
    with open("JSONs/Element_Information_Dict.json", 'r') as jsonfile:  # Read in .json with necessary information
        element_data_dict = json.load(jsonfile)
        for element in stoich_dict.keys():  # Pull each unique element from input stoich_dict (e.g "Ca")
            # element_data_dict[element] yields the list of values for that element of the form /
            # ['Z', 'Element', 'Z/A', 'I (eV)', 'Density (g/cm3)', 'Molecular Weight (g/mol)']
            try: # For elements with Z <= 92
                atomic_info_dictionary[element] = element_data_dict[element]  # Note this is a list of strings still!
            except KeyError: # Bypass elements which are above Uranium that would throw an error
                print("Could not find element '{}'.".format(element)) # Notify user
                validated_MAC = False # Raise flag that unrecognized element was encountered
                continue # Continue to parse the remainder of the elements
    if not validated_MAC: # Tell user that MAC calculation is not available
        print("""Because of flagged elements above with Z > 92, MAC calculation for your sample is unavailable. However,
this calculator can still flag potential beam and sample interferences for 10 < Z <= 92.""")
    # Return an abridged atomic info dictionary containing information for known elements contained within the sample
    return atomic_info_dictionary, validated_MAC

# Generates dictionary of elemental MAC values for all elements in a given sample with given energy
def get_sample_MAC_library(atomic_info, incident_energy):
    sample_MAC_library = {} # Establish empty dictionary to be populated and returned by the function
    incident_energy_num = float(incident_energy) # Make sure function input is a float for math/comparisons later
    with open("JSONs/Atomic_MACs.json", "r") as jsonfile: # Read in .json with necessary information
        full_LAC_dict = json.load(jsonfile) # Contents of "Atomic_MACs.json" is now callable with Full_LAC_dict variable
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
    with open("JSONs/X-ray_Absorption_Edges.json", "r") as jsonfile: # Read in .json with necessary information
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

# Prompt user to either exit the program or pass values back to Beam_Profile_Calculator
def end_of_script_protocol(value1, value2):
    end_decision = user_pick_from("You have reached the end of the MAC Calculator. Please select an option from below.", ["Quit Program", "Return to Beam Profile Calculator"])
    if end_decision == "Quit Program":
        print("Thank you for using the MAC Calculator!")
        sys.exit(0)
    elif end_decision == "Return to Beam Profile Calculator":
        print("Returning to Beam Profile Calculator!")
        print("Writing JSON files...")
        try:
            with open("MAC_Calculator_Output.json", "w") as jsonfile:
                json.dump([value1, value2], jsonfile)
            print("JSON file written.")
        except Exception as e:
            print("An unexpected error occurred: {}".format(e))

# ---------- Begin Main Logic of the Code as Callable Function main() ----------

def main():
    # Establish MAC and thickness_check variables to be calculated and passed back to Beam_Profile_Calculator.py
    sample_MAC = 0
    check_thickness = True

    # Get chemical formula from user. Code below will repeat until a satisfactory element dictionary is generated.
    element_dict = {}
    while not element_dict: # While the dictionary is empty
        chemical_formula = input("Please enter your sample's known or approximate chemical formula: ")
        element_dict = chem_form_parser(chemical_formula)
        if element_dict != {}:
            user_confirmed = False
            while not user_confirmed:
                print("Please confirm the following elemental breakdown: ")
                for key,value in element_dict.items():
                    print(str(key), str(value))
                user_confirmation = y_or_n_confirmation("Is this correct?")
                if user_confirmation:
                    user_confirmed = True
                elif not user_confirmation:
                    element_dict = {}
                    user_confirmed = True
        else:
            continue

    # Establish atomic info library and MAC validity boolean in global scope
    # This will make sure the code runs properly when MAC_Calculator is run by Beam_Profile_Calculator.py
    sample_atomic_info = {}
    user_valid_MAC = True

    # Pull dictionary of relevant atomic information based on the user input
    print("Gathering information about the atoms in your sample...")
    try: # Gather info necessary for MAC and thickness calculations
        sample_atomic_info, user_valid_MAC = get_atomic_info(element_dict) # Gets Z, density, atomic weight, etc.
        print("Dictionary conversion successful.")
    except Exception as e: # Activates if the user managed to pass an imaginary element
        print("An error occurred: {e}".format(e=e))
        ### Add code here to exit to Beam_Profile_Calculator.py or stop program

    # Instantiate SampleChemistry object with element_dict
    user_sample = SampleChemistry(element_dict, user_valid_MAC) # This is periodically throwing errors?
    print("Sample created.")

    # If the user's sample cannot have a MAC calculated for it, inform the global check_thickness boolean
    if not user_sample.valid_MAC:
        check_thickness = False

    # Create a master list of energies at which sample absorption will occur
    sample_x_ray_edges = get_edge_info(user_sample.stoich) # Gets energies at which absorption occurs for each element

    # Prompt user for the incident X-ray energy used
    incident_energy = 0
    incident_energy_input = user_pick_from("""Please enter your incident x-ray energy. You may choose a common x-ray
tube anode type from below or enter a custom value.""", ["Cu", "Co", "Mo", "Cr", "Custom"])
    if incident_energy_input in CCMC_Tubes.keys(): # If user chooses a commonly used anode type
        incident_energy = CCMC_Tubes[incident_energy_input] # Set incident energy to energy value in reference dictionary
        # Print statement to indicate success to user
        print("Incident energy set to {energy} keV (default for {type} tube).".format(energy=str(incident_energy), type=incident_energy_input))
    elif incident_energy_input == "Custom":
        incident_energy = get_user_float("Please enter your incident x-ray energy in keV:", 1, 15000)

    # Check for sample-beam interactions based on known atoms in sample
    print("Checking for potential undesirable interactions between incident beam and sample...")
    beam_and_sample_interference(sample_x_ray_edges, incident_energy)
    # Prompt user to see all x-ray edges for their sample to do a manual check
    manual_interference_checker = y_or_n_confirmation("Would you like to examine the known absorption edges of the atoms in your sample?")
    if manual_interference_checker: # Print all edges with user-friendly formatting
        for element, interference_list in sample_x_ray_edges.items():
            print("{}:".format(element))
            for edge in interference_list:
                print("{edge} edge: {energy} keV, wavelength: {wavelength} angstroms.".format(edge=edge[0], energy=edge[1], wavelength=edge[2]))
    ### Add code here to exit to Beam_Profile_Calculator.py or stop program

    if check_thickness:
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
        sample_MAC = user_sample.mass_atten_coefficient

    end_of_script_protocol(check_thickness, sample_MAC)

# ---------- Calling the main() Function ----------

if __name__ == "__main__":
    main()

