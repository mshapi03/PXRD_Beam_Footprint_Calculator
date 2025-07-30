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
# The lists below will hold presets from Malvern and Rigaku since the developer uses those, but can be updated to hold any values!

# XRD Manufacturers and Models Dictionary
manufacturers_models = {"Rigaku": ["SmartLab", "SmartLab SE", "MiniFlex", "MiniFlex XpC"],
                        "Malvern Panalytical": ["Aeris", "CubiX 3", "Empyrean", "X'Pert^3", "X'Pert Pro"]}
                        # "Bruker": ["D8 DISCOVER", "D8 ADVANCE", "D6 PHASER", "D2 PHASER", "D8 ENDEAVOR"],
                        # "Thermo Fisher": ["ARL X'TRA", "ARL EQUINOX 100"],
                        # "Proto": ["AXRD Benchtop", "AXRD Theta-Theta", "AXRD LPD", "AXRD LPD-HR", "AXRD LPD-HT"]

# XRD Brands as keys with a list of lists as values, holding known compatible sample holders in the general form:
# ["Name", "Circle", diameter, depth, min_2theta] or ["Name" "Rectangle", axial dimension, equitorial dimension, depth, min_2theta] with values in mm
# Note that axial is the length of sample well along the beam direction, equitorial is the width of the sample orthogonal to beam direction
manufacturers_sampleholders = {"Rigaku": [["Glass 0.2mm", "Rectangle", 15, 15, 0.2, 0],
                                          ["Glass 0.5mm", "Rectangle", 15, 15, 0.5, 0],
                                          ["ZDS 5x0.2 mm", "Circle", 5, 0.2, 0],
                                          ["ASC 2mm", "Circle", 30, 2, 0],
                                          ["ASC 0.5mm", "Circle", 30, 0.5, 0],
                                          ["ASC 0.2mm", "Circle", 30, 0.2, 0]],
                               # Rigaku sample holder info was found from resources online - check with your sample holders before using!
                               "Malvern Panalytical": [["Reg 16mm", "Circle", 16, 2.4, 0],
                                                       ["Reg 27mm", "Circle", 27, 2.4, 0],
                                                       ["Si Substrate", "Circle", 15, 0.2, 0]]}
                               # I ignored the 26, 32, and 40 mm spring-loaded sample holders since thickness varies


# ---------- Class Definitions ----------
class DiffractionSample:
    def __init__(self, x, y, z):
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

# Function to take a dictionary and return a list of keys plus the "Other" keyword
def othering(my_dict):
    list_to_return = list(my_dict.keys())
    list_to_return.append("Other")
    return list_to_return


# ---------- Gonio and Beam Calculation Functions ----------

# Function to calculate incident divergence slit angle from millimeter width
def DS_phi_from_mm(millimeter):
    pass
# ---------- Begin User-Facing Code ----------

if __name__ == "__main__": # All code must go inside in this block to ensure proper resolving between packages

    # Establish pertinent file paths to ensure successful navigation between scripts
    Beam_Profile_directory = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of current script
    # Build the absolute path to the child script's directory from the current script directory above
    MAC_Calc_directory = os.path.join(Beam_Profile_directory, "MAC_Calculator_Directory")
    MAC_Calc_Output = os.path.join(MAC_Calc_directory, "MAC_Calculator_Output.json")

    # Initialize the calculator by making sure there is no previous MAC Calculator Output
    delete_MAC_output(MAC_Calc_Output)

    # Welcome message and state aim of code
    print("""Welcome to the powder XRD beam footprint calculator! This program is designed to help visualize an X-ray
beam's profile on a powder diffraction sample. I hope it will help you determine the best optics settings for your 
sample, sample holder, and diffractometer when collecting powder X-ray diffraction data.\n""")

    # Establish global boolean for checking sample thickness via MAC
    check_thickness = True
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
            print("Sample MAC calculated successfully.")  # Message upon successful completion
        except subprocess.CalledProcessError as e:  # Minimal error handling
            print("An error occurred in calculating the sample MAC: {e}".format(e=e))

    # The script now checks for the existence of MAC_Calculator_Output.json file
    # If it does not exist, the user has either provided the values or decided against them, or check_thickness and sample_MAC are accurate
    # If the file does exist, the code below updates the check_thickness and sample_MAC values to that from MAC_Calculator
    if os.path.exists(MAC_Calc_Output):
        check_thickness, sample_MAC = MAC_Output_Reader(MAC_Calc_Output)

    # At this point, the thickness check boolean and MAC value are updated and usable.
    # Prompt user for brand and instrument they are using:

    user_manufacturer = user_pick_from("Please select the manufacturer of your XRD unit from the following:", othering(manufacturers_models))

    # Now we will prompt the user for information about their sample dimensions and flesh out the DiffractionSample class.