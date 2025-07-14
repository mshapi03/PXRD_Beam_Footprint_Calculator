from Scrapers.Atomic_LAC_Reader import simple_json_writer
import csv

element_data_dict = {}

with open("Elemental_Densities.csv", 'r', newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    for row in csv_reader:  # Looking in a list a la [Z,Element,Z/A,I (eV),Density (g/cm3),Molecular Weight (g/mol)]
        element_data_dict[row[1]] = [row[0], row[2], row[3], row[4], row[5], row[6]] # generates dictionary of form "Element":[Z, Z/A, I (eV),Density (g/cm3),Molecular Weight (g/mol)]

print(element_data_dict)

simple_json_writer(element_data_dict, "../Element_Densities_and_Weights.json")