# Developed by Mitch S-A
# Updated on July 29, 2025

# ---------- Necessary imports ----------

# Library to allow code to interface with other Python scripts
import sys
import subprocess
import os
# Library to allow code to read and write JSON files
import json
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
            self.depth = depth

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
            print("Calculator initialized.")
        except OSError as e:
            print("Error initializing calculator: {}".format(e))
    else:
        print("No previous output found - calculator initialized.")

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



# ---------- Gonio and Beam Calculation Functions ----------

# Function to calculate incident divergence slit angle from millimeter width
def DS_phi_from_mm(millimeter):
    pass
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

    # Initialize the calculator by making sure there is no previous MAC Calculator Output
    delete_MAC_output(MAC_Calc_Output)

    # Build pre-configured dictionaries from JSON files
    # General form: manufacturers_models = {"Rigaku": ["SmartLab", "SmartLab SE", "MiniFlex", "MiniFlex XpC"],
    manufacturers_models = load_preconfiguration(os.path.join(Beam_Calc_J_directory, "manufacturers_and_models.json"))
    # General form: ["Name", "Circle", diameter, depth, min_2theta] or ["Name" "Rectangle", axial dimension, equitorial dimension, depth, min_2theta] with values in mm
        # {"Rigaku": [["Glass 0.2mm", "Rectangle", 15, 15, 0.2, 0], ["Glass 0.5mm", "Rectangle", 15, 15, 0.5, 0], etc.
        # Note that axial is the length of sample well along the beam direction, equitorial is the width of the sample orthogonal to beam direction
    manufacturers_sampleholders = load_preconfiguration(os.path.join(Beam_Calc_J_directory, "manufacturers_and_sample_holders.json"))
    # General form: {"X'Pert^3": 240, "X'Pert Pro": 240} with values in mm
    instruments_gonio_radii = load_preconfiguration(os.path.join(Beam_Calc_J_directory, "instruments_and_radii.json"))

    # Welcome message and state aim of code
    print("""Welcome to the powder XRD beam footprint calculator! This program is designed to help visualize an X-ray
beam's profile on a powder diffraction sample. I hope it will help you determine the best optics settings for your 
sample, sample holder, and diffractometer when collecting powder X-ray diffraction data.\n""")

    # Establish global boolean for checking sample thickness via MAC
    check_thickness = False
    sample_MAC = 0

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
    if user_manufacturer == "Other":
        user_manufacturer = get_user_string("Please enter the manufacturer of your XRD unit:")
    # user_manufacturer is no longer other, but is accurate. May or not exist in dictionaries

    # Prompt the user for the instrument they are using:
    user_instrument = None # Establish variable on global scale
    # If the user_manufacturer is already present in manufacturers_and_models preconfiguration, start by picking from that list
    try:
        user_instrument = user_pick_from("Please select the instrument you are using from the following:", othering(manufacturers_models[user_manufacturer]))
    except KeyError: # If the user_manufacturer does not exist, it will throw a KeyError
        user_instrument = get_user_string("Please write the name of the instrument you are using:", 20)
    finally: # If the manufacturer is known but the instrument is not (i.e. user_instrument == "Other"), have user put in their instrument
        if user_instrument == "Other":
            user_instrument = get_user_string("Please write the name of the instrument you are using:", 20)

    #  Debug/test
    print(user_manufacturer)
    print(user_instrument)

    # Prompt the user for information about their sample dimensions and flesh out the DiffractionSample class.
    user_holder = None # Establish variable on global scale
    user_holder_information = [] # Establish empty list on global scale
    if user_manufacturer != "Other": # As long as the manufacturer is known
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
    if user_manufacturer == "Other" or user_holder == "Other": # Throw here if user_manufacturer is "Other" or user_holder is "Other" after above test
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
        # Get depth of sample well if thickness check is desired, else set to 0
        if check_thickness:
            user_well_depth = get_user_float("Please input the depth of your sample holder in mm:")
            user_holder_information.append(user_well_depth)
        elif not check_thickness:
            user_holder_information.append(0)
        # Prompt user for minimum 2theta range
        user_holder_angle_limit = get_user_float("If known, please input the minimum 2theta angle at which your sample can be used. Else, write \"0\":")
        user_holder_information.append(user_holder_angle_limit)

    print("Sample information stored.")

    # If the user's sample is of a known manufacturer, ask if they'd like to store the sample for future use
    if user_holder_information[0] == "Custom" and user_manufacturer != "Other":
        update_sampleholder_JSON = y_or_n_confirmation("Would you like to save your custom sample holder for future use under the {} brand?".format(user_manufacturer))
        if update_sampleholder_JSON:
            user_holder_name = get_user_string("Please name your custom sample holder:", 12)
            user_holder_information[0] = user_holder_name # Update the user holder name to be "User input"
            ### Implement function once reference dictionaries are MAC_JSONs.
            ### Note that the function needs to handle cases where the manufacturer key already exists (Malvern) and cases where it does not (Thermo)!
            print("The following will be added as a sample to the JSON file:")
            #print("The manufacturers_sampleholders dictionary has been updated.")

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

    print(user_diffraction_sample)
    user_diffraction_sample.print_all_information()

    # Get Goniometer radius
    # print("You are using a/an {instrument} diffractometer from the vendor \"{manufacturer}\".").format(instrument=user_instrument, manufacturer=user_manufacturer)
    # user_gonio_radius = 0
    # if user_instrument in instruments_gonio_radii.keys():
    #     user_gonio_radius = instruments_gonio_radii[user_instrument]
    #     print("The goniometer radius is {radius} mm.".format(radius=user_gonio_radius))
    # elif user_instrument not in instruments_gonio_radii.keys():
    #     user_gonio_radius = get_user_float("Please input the radius of your goniometer in mm:")


