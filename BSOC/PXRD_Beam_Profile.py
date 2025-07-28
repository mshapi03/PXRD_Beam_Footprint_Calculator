# Developed by Mitch S-A
# Updated on July 19, 2025
# Usage Notes: Single-human beta test shows no terminal issue. No unit testing performed on individual functions.
# Status: In-development as a part two, git integrated

# ---------- Necessary imports ----------

# Library to allow code to interface with STIXE script
import sys
# import json
# import matplotlib.pyplot as plt
# from STIXE.PXRD_Sample_Considerations import DiffractionSample

# ---------- Short Reference Dictionaries and Lists ----------



# ---------- Class Definitions ----------



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

# Function to read in JSON files - implement later once we have structured the JSON files
def JSON_reader():
    pass

# Function to calculate incident divergence slit angle from millimeter width
def DS_phi_from_mm(millimeter):
    pass
# ---------- Begin User-Facing Code ----------

# Welcome message and state aim of code.
print(
    """Welcome to the beam profile calculator. The aim of this program is to provide simple Matplotlib visualizations
of the PXRD irradiated length in context of your sample provided details about the instrument, configuration, and 
optics chosen.""")

# Code checks for the instantiated DiffractionSample object from Pt. 1 and retrieves incident energy (global) and/
# self.mass_atten_coefficent

# Determine the geometry of the experiment - currently only compatible with Bragg-Brentano (BB), a.k.a reflexion.
geometry = user_pick_from(prompt= "Please select the geometry of the instrument: ", pick_list=["Bragg-Brentano/Reflexion"])

# Consult the "Favorites" JSON and retrieve the details of each saved instrument/configuration with a matching geometry
### Add code

# Implement pick list function with the "Favorites" list and include an option for "Other"
### Add code

# If user selected a preconfigured instrument (from "Favorites"), the relevant settings will be saved here
### Add code

# If the user selected "Other", the following prompts will get all gonio/configuration information required
### Add code
