# Developed by Mitch S-A
# Updated on July 29, 2025

# ---------- Necessary imports ----------

# Library to allow code to interface with other Python scripts
import sys
import subprocess
import os
# Library to allow code to read and write JSON files
import json
# Library to allow for trigonometric calculations
from math import degrees, radians, atan, sin
# Library to allow code to create and output visualizations
import matplotlib as mpl

# ---------- Short Reference Dictionaries and Lists ----------

# Simple list of holder shapes to more easily expand code applicability in the future
holder_shapes = ["Circle", "Rectangle"]

# ---------- Class Definitions ----------
class DiffractionSample:
    def __init__(self, name, shape, z_check, diameter= 0, axi = 0, equi = 0, MAC = 0, depth = 0, min_2theta = 0):
        self.name = name
        self.shape = shape
        self.min_2theta = min_2theta
        if self.shape == "Circle":
            self.diameter = diameter
        else:
            self.axi = axi
            self.equi = equi
        self.z_check = z_check
        if self.z_check == True:
            self.MAC = MAC
        self.depth = depth # Depth must be initialized even if MAC is not to allow users to write custom sample holders for future use

    def __repr__(self):
        string_1 = "A {shape} sample with ".format(shape=self.shape)
        string_2 = ""
        if self.shape == "Circle":
            string_2 = "a diameter of {diameter} mm".format(diameter=self.diameter)
        else:
            string_2 = "dimensions {axi} mm by {equi} mm".format(axi=self.axi, equi=self.equi)
        string_3 = ""
        if self.z_check == True:
            string_3 = " by {depth} mm deep and a MAC of {MAC} cm^2/g usable above {min_2theta} degrees 2theta.".format(depth= self.depth, MAC=self.MAC, min_2theta=self.min_2theta)
        else:
            string_3 = " usable above {min_2theta} degrees 2theta.".format(min_2theta=self.min_2theta)
        return string_1 + string_2 + string_3

    def print_all_information(self):
        print(vars(self))

    ### Here we will write functions that calculate area for circle and rectangle as well as perform a thickness check with MAC and depth if possible
    ### To be done after/during MatPlotLib calculations

class Optics:
    pass

# ---------- Simplifying Functions ----------

# Function to get a y or n input from a user input
def y_or_n_confirmation(prompt): # Pass a y/n question as a string to prompt the user
    proceed_with_value = None # Define the returnable boolean that will indicate whether the user said "y" (True) or "n" (False)
    loop_continue = True # Establish a boolean to ensure while loop iterates until "y" or "n" has been found
    while loop_continue: # Loop according to the above boolean
        user_input = input("{} (y/n): ".format(prompt))  # Attempt to get user_input
        if user_input not in ["y", "n"]: # Handle the case where the input is not "y" or "n"
            print("Invalid input. Please enter 'y' or 'n'.") # Prompt new user input
        elif user_input == "y": # User input is "y"
            proceed_with_value = True # The value is confirmed
            loop_continue = False # The loop is ended
        elif user_input == "n": # User input is "n"
            proceed_with_value = False # The value is not confirmed
            loop_continue = False # The loop is ended
    return proceed_with_value # Tells the program whether to proceed with confirmed value (True) or not (False)

# Function to get a float value from the user and confirm proper entry
def get_user_float(prompt, lower_bound = None, upper_bound = None): # Get a float-type input from the user and confirm it is properly entered
    # Optional arguments exist to ensure the number is within a specific range
    returned_value = None # Define a variable to hold the user-confirmed float type value
    loop_continue = True # Establish a boolean to ensure while loop iterates until float value has been confirmed
    while loop_continue: # Loop according to the above boolean
        user_input = input("{} ".format(prompt)) # Prompt the user to input their number
        try: # If the input cannot be made a float, ValueError and throw back to beginning of loop
            user_input_num = float(user_input)
            if lower_bound is not None: # Make sure value is greater than lower bound, if passed
                if user_input_num < lower_bound:
                    print("Invalid input; value too small.")
                    continue
            if upper_bound is not None: # Make sure value is lower than upper bound, if passed
                if user_input_num > upper_bound:
                    print("Invalid input; value too large.")
                    continue
        except ValueError: # Minimal exception handling
            print("Invalid input. Please enter a number.")
            continue
        user_y_or_n = y_or_n_confirmation("You have entered: {}. Is this correct?".format(user_input)) # Call earlier y_or_n to ensure user input is typed correctly
        if user_y_or_n: # If the result of the user confirmation loop is True, return the float value and end the loop
            returned_value = user_input_num
            loop_continue = False
        elif not user_y_or_n: # If the result of the user confirmation loop is False, start from the top of the while loop
            continue
    return returned_value

# Function to get a string value from the user and confirm proper entry
def get_user_string(prompt, max_length = None):
    returned_value = None  # Define a variable to hold the user-confirmed string type value
    loop_continue = True  # Establish a boolean to ensure while loop iterates until string value has been confirmed
    while loop_continue:  # Loop according to the above boolean
        user_input = input("{} ".format(prompt))  # Prompt the user to input their number
        try:  # If the input cannot be made a str, ValueError and throw back to beginning of loop
            user_input_str = str(user_input)
            if max_length is not None:  # Make sure string length is smaller than bound, if passed
                if len(user_input_str) > max_length:
                    print("Invalid input; entry too long.")
                    continue
        except ValueError:  # Minimal exception handling
            print("Invalid input. Please enter text.")
            continue
        user_y_or_n = y_or_n_confirmation("You have entered: {}. Is this correct?".format(
            user_input))  # Call earlier y_or_n to ensure user input is typed correctly
        if user_y_or_n:  # If the result of the user confirmation loop is True, return the float value and end the loop
            returned_value = user_input_str
            loop_continue = False
        elif not user_y_or_n:  # If the result of the user confirmation loop is False, start from the top of the while loop
            continue
    return returned_value

# Function to have user pick from a list of value and confirm proper entry
def user_pick_from(prompt, pick_list): # Present pick list of choices with custom prompt
    confirmed_user_choice = None # Create a variable that will hold the finalized user choice
    loop_continue = True # Establish a boolean to ensure while loop iterates until choice has been confirmed
    while loop_continue: # Loop according to the above boolean
        print("{}".format(prompt)) # Present prompt
        for i in range(0, len(pick_list)): # For loop to present enumerated options
            print("[{bullet}] {option}".format(bullet=i+1, option=pick_list[i]))
        user_selection = input("Please select the number of your choice: ") # Actual prompt for user choice
        try: # Exception handling to make sure value is an integer
            user_selection_num = int(user_selection)
            if int(user_selection) not in range(1, len(pick_list) + 1): # Check to make sure input is within the range of the passed list
                print("Invalid input. Please select a number from the above list.")
                continue
        except ValueError:
            print("Invalid input. Please select a number from the above list.")
            continue
        # Have user confirm their selection
        user_y_or_n = y_or_n_confirmation("You have selected {num}, {choice}. Is this correct? ".format(num=user_selection, choice=pick_list[user_selection_num-1]))
        if user_y_or_n: # If the result of the user confirmation loop is True, return the user choice and end the loop
            confirmed_user_choice = pick_list[user_selection_num-1]
            loop_continue = False
        elif not user_y_or_n: # If the result of the user confirmation loop is False, start from the top of the while loop
            continue
    return confirmed_user_choice

# Function to delete an existing MAC_Calculator_Output.json (i.e. initialize the program)
def delete_MAC_output(filepath):
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print("Previous MAC output found and removed - calculator initialized.")
        except OSError as e:
            print("Error initializing calculator: {}".format(e))
    else:
        print("No previous MAC output found - calculator initialized.")

# Function to read in MAC_Calculator_Output.json files
def MAC_Output_Reader(filepath):
    try:
        with open(filepath, "r") as jsonfile: # Basic JSON reading
            MAC_Calc_Output = json.load(jsonfile) # Load the two-item list as a variable
            return bool(MAC_Calc_Output[0]), float(MAC_Calc_Output[1]) # return both items in bool, float order
    except Exception as e:
        print("Error reading MAC calculator output file: {}".format(e))

# Function to take a list and return said list with the "Other" keyword
def othering(my_list):
    list_to_return = list(my_list) # Perhaps redundant, avoids .keys() issue with dictionaries
    list_to_return.append("Other") # Add "Other" as option
    return list_to_return # Return list\

# Function to read in Beam_Calc_JSONs as usable dictionaries of preconfigurations in the script
def load_preconfiguration(filepath):
    try:
        with open(filepath, "r") as jsonfile:
            preconfig_dict = json.load(jsonfile)
            return preconfig_dict
    except Exception as e:
        print("Error loading preconfiguration file: {}".format(e))

# Function to update a JSON with user-desired information
def update_JSON(filepath, key_to_update, new_value):
    data = load_preconfiguration(filepath) # Call JSON reading function to populate a Python dictionary with current JSON
    data_values = list(data.values()) # Load all dict values into a list
    value_type = type(data_values[0]) # Check the type of the first item in the list of dict values (either list or not a list)
    # Test the type of the dictionary's values (list, int) to dictate the procedure for updating the dictionary
    if value_type != list: # If the value is not a list, like float/int for instru_gonio, just do a simple update
        data[key_to_update] = new_value # Perform the update, initializing a new key if the instr does not exist
    elif value_type == list: # If the value is a list, for manu_instr or manu_sample, need to append to existing list
        get_key = data.get(key_to_update, "New Manufacturer") # Get the manufacturer key if it exists, else add new key
        if get_key == "New Manufacturer": # Add new entry since manufacturer does not exist, passing new_value as the sole item in a new list
            data[key_to_update] = [] # Establish an empty list and append, else we get each character of the string appended
            data[key_to_update].append(new_value)
        else: # If the key passed to update_JSON already exists, append the new value to the list
            data[key_to_update] = data[key_to_update].append(new_value)
    try: # Overwrite the previous JSON file with new update
        with open(filepath, "w") as jsonfile:
            json.dump(data, jsonfile, indent=4)
        print("{file} updated.".format(file=filepath))
    except Exception as e:
        print("Error updating JSON file (file): {error}".format(file=filepath, error=e))

# ---------- Gonio and Beam Calculation Functions ----------

# Function to calculate incident divergence slit angle from millimeter width
# Note, this function comes from a Bruker D8 manual where the following {width in mm (w): angle in degrees (phi)} pairs are given:
    # {0.05: 0.025, 0.1: 0.05, 0.2: 0.1, 0.6: 0.3, 1: 0.5, 2: 1, 6: 3}
    # From this and trig, the constant d = 114.59 mm was worked from tan(phi/2) = (w/2)/d
    # As Bruker is the only vendor to the author's knowledge that uses mm, it is assumed these relations hold true for other models and vendors which do the same
def DS_phi_from_mm(millimeter):
    phi = degrees(2*atan((millimeter/229.18)))
    return phi
# ---------- Begin User-Facing Code ----------

if __name__ == "__main__": # All code must go inside in this block to ensure proper resolving between packages

    # Establish pertinent file paths to ensure successful navigation between scripts and JSON loading
    # Get the absolute path to the directory of the current script (PXRD_Beam_Footprint_Calculator, for global reference)
    Beam_Profile_directory = os.path.dirname(os.path.abspath(__file__)) #PXRD_Beam_Footprint_Calculator
    # Build the absolute path to the child script's directory from the directory above (for MAC_JSONs)
    MAC_Calc_directory = os.path.join(Beam_Profile_directory, "MAC_Calculator_Directory") # MAC_Calculator_Directory
    # Build the absolute path to the child script's JSON output in the directory above (for MAC_JSONs)
    MAC_Calc_Output = os.path.join(MAC_Calc_directory, "MAC_Calculator_Output.json") # MAC_Calculator_Directory
    # Build absolute path to the directory containing preconfiguration JSONs (for Beam_Calculation)
    Beam_Calc_J_directory = os.path.join(Beam_Profile_directory, "Beam_Calc_JSONs") # Beam_Calc_JSONs
    # Build absolute path to each preconfiguration JSON (for Beam_Calculation)
    manu_model_path = os.path.join(Beam_Calc_J_directory, "manufacturers_and_models.json")
    manu_samphold_path = os.path.join(Beam_Calc_J_directory, "manufacturers_and_sample_holders.json")
    instru_gonio_path = os.path.join(Beam_Calc_J_directory, "instruments_and_radii.json")

    # Initialize the calculator by making sure there is no previous MAC Calculator Output
    delete_MAC_output(MAC_Calc_Output)

    # Build pre-configured dictionaries from JSON files
    # General form: manufacturers_models = {"Rigaku": ["SmartLab", "SmartLab SE", "MiniFlex", "MiniFlex XpC"],
    manufacturers_models = load_preconfiguration(manu_model_path)
    # General form: ["Name", "Circle", diameter, depth, min_2theta] or ["Name" "Rectangle", axial dimension, equitorial dimension, depth, min_2theta] with values in mm
        # {"Rigaku": [["Glass 0.2mm", "Rectangle", 15, 15, 0.2, 0], ["Glass 0.5mm", "Rectangle", 15, 15, 0.5, 0], etc.
        # Note that axial is the length of sample well along the beam direction, equitorial is the width of the sample orthogonal to beam direction
    manufacturers_sampleholders = load_preconfiguration(manu_samphold_path)
    # General form: {"X'Pert^3": 240, "X'Pert Pro": 240} with values in mm
    instruments_gonio_radii = load_preconfiguration(instru_gonio_path)

    # Welcome message and state aim of code
    print("""Welcome to the powder XRD beam footprint calculator! This program is designed to help visualize an X-ray
beam's profile on a powder diffraction sample in Bragg-Brentano/reflexion geometry when using divergence slits. Results 
are not guaranteed for the use of focusing mirrors or incident monochromators. I hope it will help you determine the 
best optics settings for your sample, sample holder, and diffractometer when collecting powder X-ray diffraction data.\n""")

    # Establish global boolean for checking sample thickness via MAC
    check_thickness = False
    # Establish global value for sample MAC
    sample_MAC = 0

    # Establish global booleans for saving user inputs as part of the preconfigurations
    save_new_manu_instr = False
    save_new_manu_sample = False
    save_new_radius = False

    # Prompt the user to engage with the MAC_Calculator
    print("""This program has the capability to determine your sample's mass attenuation coefficient (MAC) if you (1) know 
the incident radiation energy (or tube anode material) you will be using and (2) are gathering data on a sample which
does not contain any elements above atomic number (Z) 92. This enables the program to ensure your sample thickness is 
well-matched to the penetration depth of your beam.""")
    throw_to_MAC = y_or_n_confirmation("Would you like to calculate your samples MAC?")
    if not throw_to_MAC: # Do not throw to MAC_Calculator
        estimate_MAC = y_or_n_confirmation("Would you like to provide an estimate of your sample's MAC?")
        if estimate_MAC: # Provide an estimate of MAC
            user_input_MAC = get_user_float("Please enter the MAC of your sample (cm^2/g):")
            sample_MAC = float(user_input_MAC)
            check_thickness = True
        elif not estimate_MAC: # Forgo sample thickness calculations
            print("This program will not consider your sample's thickness.")
            check_thickness = False # Change global boolean to skip thickness calculations/visualizations
    elif throw_to_MAC: # Throw to MAC Calculator
        # Write the bash command to execute when moving to the other script
        # -m tells to run it with the name __main__
        # "MAC_Calculator" is the name of the script to run
        bash_command = [sys.executable, "-m", "MAC_Calculator"]  # Specify the command list to throw to the MAC calculator script
        try:
            print("Moving to MAC Calculator...")
            # Change the cwd to the directory in which the script lies so MAC_Calculator can find the JSON files
            subprocess.run(bash_command, cwd=MAC_Calc_directory, check=True)  # Run MAC Calculator script
            print("MAC_Calculator run successfully.")  # Message upon successful completion
        except subprocess.CalledProcessError as e:  # Minimal error handling
            print("An error occurred in calculating the sample MAC: {e}".format(e=e))

    # The script now checks for the existence of MAC_Calculator_Output.json file
    # If it does not exist, the user has either provided the values or decided against them, or check_thickness and sample_MAC are accurate
    # If the file does exist, the code below updates the check_thickness and sample_MAC values to that from MAC_Calculator
    if os.path.exists(MAC_Calc_Output):
        check_thickness, sample_MAC = MAC_Output_Reader(MAC_Calc_Output)
    # At this point, the thickness check boolean and MAC value are updated and usable.

    # Prompt user for brand of instrument they are using:
    user_manufacturer = user_pick_from("Please select the manufacturer of your XRD unit from the following:", othering(manufacturers_models.keys()))
    if user_manufacturer == "Other": # If the manufacturer is not included in the preconfigs, ask if they'll want to save this to preconfigurations
        save_this_manu = y_or_n_confirmation("Would you like to save your manufacturer/instrument to the preconfigurations? You will be able to select it directly next time.")
        if save_this_manu: # If yes, change the global boolean that controls this save
            save_new_manu_instr = True
            user_manufacturer = get_user_string("Please enter the manufacturer of your XRD unit:")

    # user_manufacturer can now be from preconfig dictionaries, custom to be saved, or "Other" if we do not want to save

    # Prompt the user for the instrument they are using:
    user_instrument = None # Establish variable on global scale
    try: # If the user_manufacturer is already present in manufacturers_and_models preconfiguration, start by picking from that list
        user_instrument = user_pick_from("Please select the instrument you are using from the following:", othering(manufacturers_models[user_manufacturer]))
        if user_instrument == "Other": # If the manufacturer is known but the instrument is not
            save_this_instr = y_or_n_confirmation("Would you like to save your instrument to the preconfigurations? You will be able to select it directly next time.")
            if save_this_instr:
                save_new_manu_instr = True
                user_instrument =get_user_string("Please enter the instrument you are using:")
    except KeyError: # If the user_manufacturer is "Other" or custom, it will throw a KeyError
        # If the user_manufacturer is custom, save_new_manu_instr is True and the instrument becomes named
        if save_new_manu_instr: # If the user would like to save this new manufacturer/instrument pair:
            user_instrument = get_user_string("Please write the name of the instrument you are using:", 20)
        # If the user_manufacturer was not specified above, it is "Other" and save_new_manu_instr is False
        else:
            user_instrument = "Other"

    # Prompt the user for information about their sample dimensions and flesh out the DiffractionSample class.
    user_holder = None # Establish variable on global scale
    user_holder_information = [] # Establish empty list on global scale
    if user_manufacturer in manufacturers_sampleholders.keys(): # If the manufacturer exists in the manufacturers_and_sample_holders.json
        try: # Add error handling if a manufacturer model exists without any sample holders
            known_compatible_sample_holders = manufacturers_sampleholders[user_manufacturer] # Access list of lists (sample holders) for specified manufacturer
            sample_holder_names = [holder[0] for holder in known_compatible_sample_holders] # List comprehension to generate all holder names
            user_holder = user_pick_from("Please select your sample holder from the following:", othering(sample_holder_names))
            if user_holder != "Other": # User selects a known sample holder from the list, map that info to user_holder_information
                for holder in known_compatible_sample_holders: # For holder info list in all lists for a given manufacturer
                    if holder[0] == user_holder: # If the names match, map the user's sample holder info with the library info and stop looking
                        user_holder_information = holder
                        break
        except Exception as e:
            user_holder = "Other" # Force the user to input sample information as we have no known samples for that manufacturer
    if user_manufacturer not in manufacturers_sampleholders.keys() or user_holder == "Other": # Throw here if user_manufacturer does not exist in the manufacturers_and_sample_holders.json or user_holder is "Other" after above test
        user_holder = "Custom" # Mark the name of this hold as a custom input from the user
        user_holder_information.append(user_holder) # Append this to user_holder_information list to keep standard formatting
        # Populate user_holder_information with custom user inputs
        user_holder_shape = user_pick_from("Please select your sample holder shape:", holder_shapes)
        user_holder_information.append(user_holder_shape)  # Append this shape to user_holder_information list to keep standard formatting
        # Get area dimensions of sample holder according to shape
        if user_holder_shape == "Circle":
            user_diameter = get_user_float("Please input the diameter of your sample holder in mm:")
            user_holder_information.append(user_diameter)
        else: # Assume all other sample holders will need axial and equitorial coordinates
            user_axial = get_user_float("Please input the axial (direction of beam propagation) length of your sample holder in mm:")
            user_holder_information.append(user_axial)
            user_equitorial = get_user_float("Please input the equitorial (orthogonal to beam propagation) width of your sample holder in mm:")
            user_holder_information.append(user_equitorial)
        # Get depth of sample well even if thickness check is not desired so it will be accurate if saved
        user_well_depth = get_user_float("Please input the depth of your sample holder in mm:")
        user_holder_information.append(user_well_depth)
        # Prompt user for minimum 2theta range
        user_holder_angle_limit = get_user_float("If known, please input the minimum 2theta angle at which your sample can be used. Else, write \"0\":")
        user_holder_information.append(user_holder_angle_limit)

    print("Sample information stored.")

    # If the user's sample is custom entered and they have not previously decided against storing the manufacturer, ask if they'd like to store the sample for future use
    # Do not reference save_new_manu_instr boolean, since it will be False if the manufacturer and instrument already exist!
    if user_holder_information[0] == "Custom" and user_manufacturer != "Other":
        update_sampleholder_JSON = y_or_n_confirmation("Would you like to save your custom sample holder for future use under the {} brand?".format(user_manufacturer))
        if update_sampleholder_JSON:
            save_new_manu_sample = True
            user_holder_name = get_user_string("Please name your custom sample holder:", 12)
            user_holder_information[0] = user_holder_name # Update the user holder name to be the user input from above

    # Instantiate the DiffractionSample object with known information
    if len(user_holder_information) == 5: # If the holder is circular
        user_diffraction_sample = DiffractionSample(name=user_holder_information[0], shape=user_holder_information[1],
                                                    z_check=check_thickness, diameter=user_holder_information[2],
                                                    MAC=sample_MAC, depth=user_holder_information[3],
                                                    min_2theta=user_holder_information[4])
    elif len(user_holder_information) == 6: # If the holder is rectangular
        user_diffraction_sample = DiffractionSample(name=user_holder_information[0], shape=user_holder_information[1],
                                                    z_check=check_thickness, axi=user_holder_information[2],
                                                    equi=user_holder_information[3], MAC=sample_MAC,
                                                    depth=user_holder_information[4],
                                                    min_2theta=user_holder_information[5])
    else: # should be inaccessible as user_holder_information should always have 5 or 6 entries
        print("There was some issue in creating your sample - please restart the program.")
        raise TypeError("user_holder_information should have length 5 or 6 for proper instantiation of the DiffractionSample class.")

    # Get goniometer radius
    user_gonio_radius = 0 # Establish variable as global
    confirm_radius = False # Establish radius confirmation globally to enable elif statement to update radius if user doesn't like the preconfig
    if user_instrument in instruments_gonio_radii.keys(): # If the user's instrument has an associated radius already
        confirm_radius = y_or_n_confirmation("Your \"{manufacturer}\" {instrument} diffractometer has a radius of {radius}. Is this correct?".format(
            manufacturer=user_manufacturer, instrument=user_instrument, radius=instruments_gonio_radii[user_instrument]))
        if confirm_radius: # The user sees the expect goniometer radius
            user_gonio_radius = instruments_gonio_radii[user_instrument]
            print("Radius confirmed.")
    # If the user's instrument does not exist in instrument_and_radii.json or the value was not user confirmed
    if user_instrument not in instruments_gonio_radii.keys() or not confirm_radius:
        user_gonio_radius = get_user_float("Please enter the radius of your goniometer in mm:") # User inputs a goniometer radius
        if user_instrument != "Other": # If the user opted to store their instrument under a custom name
            store_gonio_radius = y_or_n_confirmation("Would you like to store or update your instruments goniometer radius for future use?")
            if store_gonio_radius: # If they want to store, the global update boolean is updated to True
                save_new_radius = True

    # Now that all required JSONs have been referenced, update them if user requested
    if save_new_manu_sample or save_new_manu_instr or save_new_radius:
        print("Updating JSON files as requested...")

    # Implement JSON updating code
    if save_new_manu_instr:
        update_JSON(manu_model_path, user_manufacturer, user_instrument)
        print("{instrument} was added to {manufacturer}'s library.".format(instrument=user_instrument,
                                                                           manufacturer=user_manufacturer))
    if save_new_manu_sample:
        # List of sample traits we add varies slightly depending on the shape of sample
        if user_diffraction_sample.shape == "Circle":
            update_JSON(manu_samphold_path, user_manufacturer, [user_diffraction_sample.name, user_diffraction_sample.shape, user_diffraction_sample.diameter, user_diffraction_sample.depth, user_diffraction_sample.min_2theta])
        elif user_diffraction_sample.shape == "Rectangle":
            update_JSON(manu_samphold_path, user_manufacturer, [user_diffraction_sample.name, user_diffraction_sample.shape, user_diffraction_sample.axi, user_diffraction_sample.equi, user_diffraction_sample.depth, user_diffraction_sample.min_2theta])
        print("{sample} was added to {manufacturer}'s sample library.".format(sample=user_diffraction_sample.name,
                                                                              manufacturer=user_manufacturer))
    if save_new_radius:
        update_JSON(instru_gonio_path, user_instrument, user_gonio_radius)
        print("{instrument} was given a radius of {radius} mm".format(instrument=user_instrument,
                                                                      radius=user_gonio_radius))

    # Begin portion of code which prompts user for optic components
    print("Now I will need some information about the optics you are planning to use for your experiment.")

    ### Add option to read in a selection from preconfig_optics.json and skip the entries below
    ### print("If you have used this calculator before, you may retrieve settings from before.")
        # Will need to check preconfig_optics.json to be empty, otherwise call the list in a formatted way

    # Ask user if they are running in fixed or variable divergence slit mode
    fixed_or_variable = user_pick_from("Are you operating your instrument in fixed divergence slit (FDS) or variable/automatic divergence slit (ADS) mode?", ["Fixed", "Variable", "Explain"])
    if fixed_or_variable == "Explain": # Offer more information to user on this choice.
        print("""FDS means your divergence slit opening remains constant during your experiment, while the beam length 
changes. This is a constant irradiated volume experiment compatible with Rietveld analysis. ADS refers to a divergence 
slit opening changing over the course of the experiment to keep a constant irradiated length (and therefore area). ADS 
is commonly used for thin-film samples, and not all instruments have ADS capabilities. This choice determines how certain
key math is performed, as well as whether you are presented with a graph of beam length vs. two-theta or divergence slit
opening vs. two-theta.""")
        # Prompt user to update to value to one of two options
        fixed_or_variable = user_pick_from("Are you operating your instrument in fixed divergence slit (FDS) or variable/automatic divergence slit (ADS) mode?", ["Fixed", "Variable"])

    # Get beam length if operating mode is variable
    beam_length = 0 # Establish variable on global scope
    if fixed_or_variable == "Variable":
        beam_length = get_user_float("Please enter your beam length in mm:", 0.0001) # Add lower bound to make sure the value is non-zero

    # Get divergence slit angle if operating mode is fixed
    divergence_slit_angle = 0 # Establish variable on global scope
    if fixed_or_variable == "Fixed":
        slit_form = user_pick_from("""Is your divergence slit provided in degrees or mm? Note that values provided
in degrees will result in more accurate calculations.""", ["Degrees", "Millimeters"])
        # This is because conversion from width to angle requires knowledge of the distance between the x-ray tube and the divergence slit
        if slit_form == "Degrees":
            # Somewhat arbitrary cutoffs for slit size, 1/64 and 8 degrees seeing as I've always seen 1/32 and 4 as the smallest and largest
            divergence_slit_angle = get_user_float("Please enter your divergence slit angle in degrees:", 0.015625, 8)
        elif slit_form == "Millimeters":
            # Impose same cutoffs for slit size in form of mm width
            divergence_slit_width = get_user_float("Please enter your divergence slit angle in millimeters:", 0.03125, 16.026)
            divergence_slit_angle = DS_phi_from_mm(divergence_slit_width) # Call function to convert width to angle
            print("Your divergence slit has been converted from {mm} to {degrees:.2f} degrees to enable proper calculation.".format(mm=divergence_slit_width, degrees=divergence_slit_angle))

    # Get the beam mask size
    ### Add code

    # Instantiate the Optics object
    ### Add code

    # Offer to write the Optics object to a preconfiguration
    ### Add code


    # Get the minimum and maximum two theta range
    ### Reminder to add a checker to see if the minimum 2theta is below their DiffractionSample two-theta!