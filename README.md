> [!NOTE]
> The following code was written to practice writing Python code and using common version control tools (Git/Github). As a result, the organization of this project and the code written is suboptimal.

> [!NOTE]
> User "mitchellhshap" is the owner, mshapi03's, old and unused Github account. To date, all contributions are solely from Mitchell Shapiro-Albert.

# Scripts for Determining the Appropriate Optical Settings for a Powder X-Ray Diffractometer 
**by Mitchell Shapiro-Albert**
---

The project contains the scripts and libraries necessary to calculate sample thickness and optical compatibility with an X-ray diffractometer. These scripts aim to tackle two notable problems encountered
during the planning or set-up of a benchtop XRD instrument (like a Malvern Panalytical X'Pert Pro) to collect a powder diffractogram of a solid sample:

1. Matching the sample thickness to the X-ray energy used to ensure a valid assumption of "infinite thickness" and 
2. The question of incident beam optics shaping the X-ray into a rectangular beam to fall on a (usually) circular holder

This project aims to address both of these problems in as much breadth as possible to lower the barrier to entry to collecting high-quality diffractograms. 

If you download this repository to your local system for use, it is possible you'll need to edit the lines of code pertaining to os/sys/subprocess in the STIXE script under _Short Reference Dictionaries and Lists_. It should
be written in a way to avoid this, but if you encounter an error, that would be the first place to check. The approach of breaking this project down into two scripts was in hopes of letting the second portion be used independently 
of the first while allowing the developer (me) practice having one script throw to another.

## Sample Thickness and Incident X-Ray Energy (STIXE)

The first question is addressed by the _PXRD_Sample_Considerations.py_ script, located in the _STIXE_ folder. The program takes a user input molecular formula and incident beam energy, and returns the mass attenuation coefficient
of the sample. To do this, it references the included JSON dictionaries:

+ **Atomic_LAC_Working.json** - a nested dictionary containing a table of incident energy (keV) vs. elemental mass attenuation coefficient (g/cm<sup>3</sup>) for all elements. Of the form _{{"Z": "keV": MAC, "keV": MAC, etc..._
  + This data comes from [NIST Standard Reference Database 126](https://physics.nist.gov/PhysRefData/XrayMassCoef/tab3.html).
  + The HTML scraper used to convert the tables in the JSON dictionary can be found under _Scrapers > Atomic_LAC_reader.py._ Users should not need to re-scrape.
+ **Element_Densities_and_Weights.json** - a dictionary containing basic information for each element of the form _{"Symbol": ["Z", "Element", "Z/A", "I (eV)", "Density (g/cm3)", "Molecular Weight (g/mol)"], etc..._
  + This data also comes from [NIST Standard Reference Database 126](https://physics.nist.gov/PhysRefData/XrayMassCoef/tab1.html).
  + Google AI mode was used to integrate molecular weight data and format the combination into the JSON file.
+ **x-ray_absorption_edges_UW.json** - a dictionary containing a list of all X-ray edge energies for elements Z = 11 to Z = 92 of the form _{"Symbol": [["Edge type", "keV", "Angstrom"]["Edge type", etc..._
  + This data comes from S. Brennan and P.L. Cowan c/o [Ethan A. Merritt at UW](http://skuld.bmsc.washington.edu/scatter/AS_periodic.html)
  + The HTML scraper used to convert the tables in the JSON dictionary can be found under _Scrapers > Absorption_Edge_Reader.py._ Users should not need to re-scrape.
 
The code should be sufficiently commented to be read through with only novice understanding of Python. The programs creates a DiffractionSample class that is then instantiated by user inputs. Qualities of the sample itself, 
like the final sample mass attenuation coefficient, as saved into class variables. Once the program understands the atoms in the user's sample, it will generate smaller dictionaries containing with only the key:value pairs of 
included atoms. These subdictionaries are not saved to class variables, as they are not needed to move on to the second script (below). If the program cannot understand the user's chemical formula, it will flag a class variable
boolean that will skip the remainder of the programs where errors could be encountered.

As this is ultimately an educational exercise and only the beginnings of implementable tool, there is only basic y/n looping to ensure proper user inputs. There is a fair amount of repetition and poor handling or data types,
so feel free to clone this repository and clean this up for your own use!

> [!CAUTION]
> This code cannot calculate MAC for samples which contain elements above atomic number (Z) 92.

## Beam Shaping and Optical Calculations

Progress on this feature is forthcoming!
