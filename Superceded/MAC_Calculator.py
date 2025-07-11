### Superceded by code in PXRD_Sample_Considerations (July 11, 2025)


# Assistant script to calculate MAC of sample provided an approximate chemical formula and density
# To be used to validate sample thickness choice for given sample holder

# Before throwing to this calculator in the main script, implement if/else logic for experimentally determined MAC

print(
    """Please note: the following calculator makes the assumption that your diffraction specimen's
     MAC is well-represented by a linear combination of its elemental composition. Well-determined 
     experimental values will provide more accurate results.""")

sample_chem_formula = input("Enter your exact/approximate chemical formula: ")




#This will be passed to this script using the main .py application, but for now is a re-input
incident_energy = input("Enter your incident energy (keV): ")

print(sample_chem_formula)

# Overview:
# String parser to deconvolute the chem_formula input into usable lookup values
# Throw to ALAC txt file to pull relevant atomic coefficients
# Return a simple linear combination of the pulled values!

