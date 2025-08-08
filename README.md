> [!NOTE]
> The following code was written to practice writing Python code and using common version control tools (Git/Github). As a result, the organization of this project and the code written is suboptimal.

# Scripts for Determining the Mass Attenuation Coefficient of a Powder Sample and the Appropriate Optical Settings for a Powder X-Ray Diffractometer
## __For operation in reflexion mode using divergence slits and beam masks__
**by Mitchell Shapiro-Albert**\
**Updated August 8<sup>th</sup>, 2025**
---

## Abstract
The project contains the scripts and libraries necessary to calculate a powder sample's compatibility with an X-ray diffractometer. "Compatibility" can be thought of in two ways. The first is _z_ compatibility, or sufficient sample thickness for the incident x-ray energy. This is often only an issue with thin films of 10's of microns, but involves the calculation of a sample's attenuation coefficients (ACs). A sample's mass attenuation coefficient (_MAC, cm<sup>2</sup>/g_) is a simple mass-based weighted average of its component elements, while the linear attenuation coefficient (_LAC,cm<sup>-1</sup>_) of a sample is what can be used in Beer's Law to determine the attenuation through a layer of thickness _z_. _LAC_ is calculated by dividing the _MAC_ by the sample's density (g/cm<sup>3</sup>). 

The second "compatibility" is _x-y_, which is whether the profile of the incident beam from the XRD, as shaped by the optics you've chosen, will fit inside the bounds of your sample holder. This is a pretty simple question if you are running your experiment in _automatic divergence slit_ mode, where you set your irradiated length and vary the aperture size of your slit, with a rectangular sample. However, most powder XRDs fit a square peg (beam) in a round hole (sample holder), which can make it difficult to know if your beam fits, let alone if you're maximizing the available sample surface. Moreover, most XRDs are run in _fixed divergence slit_ mode, where your irradiated length is changing depending on your 2<theta> range. If you only irradiate your sample holder at low angle without realizing it, it opens the door to confusing systematic error!

## Disclaimer
The two fundamental scripts in this repository aim to address these two problems in as much breadth as possible to lower the barrier to entry to collecting high-quality diffractograms. It should be noted however that the modularity of modern diffraction experimentation makes it hard to catch every combination. To ensure what was written was as accurate as possible, this script cannot consider non-Bragg-Brentano geometries, transmission experiments, incident monochromators, or focusing mirrors. As noted above, this began as an exercise in learning Python, core Python libraries, and Git, so the packaging of the code may be wonky. There is certainly room for optimization, better error handling, and improvements I don't know enough about Python to know that I need. Many of the "solutions" I tried to implement were more in hopes of allowing me to practice certain Python features than a genuine reflection on what would be the most elegant solution. The creation of classes for the user's sample and optics are two examples of this, as is the approach of breaking this project down into two scripts. However, the latter of these examples does preserve a user's ability to use the _MAC_ calculator independently of the parent Beam Profile Calculator.

## Usage and Permissions
Feel free to use this code for any non-commercial purpose you would like! This was inspired by a much cleaner script from Jordan Cox at MIT.nano, and is my best attempt at an homage to shared usage experimentation facilities. If you use any part of this script to develop a calculator for a tool you own or supervise, know that somewhere I am very happy!

## Directory Structure
This project uses a relatively straightforward directory structure. The _src_ directory contains the source root code and everything crucial to the program's function. The _Scrapers_ folder contains HTML-scraping programs which were used to build the .json files that are contained in the _JSONs_ folder. You do not need to re-run these scrapers on your local system - they are housed here for reference. _PXRD_Beam_Footprint_Calculator_ is the directory which contains the main, parent script _Beam_Profile_Calculator.py_. It also contains two subdirectories:
1. _MAC_Calculator_Directory_, which itself contains the child script _MAC_Calculator.py_. 
2. _Beam_Calc_JSONs_, which houses preconfigurations for various manufacturers, instrument models, sample holders, and optic choices.

Beyond this, most other files can be ignored. For those as new to Python as I am at the time of writing, here are these files' purpose:
+ \__init__._py_ - blank files to which indicate the directory which contains them is a package, therefore allowing me to use package-level commands when moving between scripts.
+ _MAC_Calculator_Output.json_ - a file which is created at the end of _MAC_Calculator.py_ if the calculated MAC needs to passed back to the _Beam_Profile_Calculator.py_, but is deleted (i.e. initialized) at the start of every call of _Beam_Profile_Calculator.py_.
+ _.gitignore_ - a file which tells Git/Github what parts of the project to ignore for change-tracking purposes (the JSON above is a great example of something that changes constantly and inconsequentially).
+ _Profile_Calculator_Planning.txt_ - an outdated .txt file which helped me plan development of the _Beam_Profile_Calculator.py_ program.
+ _README.md_ - this! A Markdown type file that explains the purpose of the code and how to use it.

## MAC and Beam-Sample Interference Calculations (Child Script: _MAC_Calculator.py_)

_MAC_Calculator.py_ is able to calculate both a MAC and a LAC for your sample and determine the potential interferences with a user provided chemical formula (parsed with the great chemparse library) and a provided incident energy. This script can be run independently if your only aim is to estimate the attenuation coefficients of a sample which does not contain atoms above atomic number (Z) > 92. The inclusion of atoms beyond Uranium will not cause a failure, but the script cannot calculate the MAC of your sample in this case. The second nifty feature of _MAC_Calculator.py_ is its ability to flag potential beam-sample interferences, like Fe's fluorescence under Cu K-<alpha> radiation. You can select your anode type or input your incident energy (for synchrontrons/free beams) and the program will both automatically check for interferences and, if selected, print out all absorption edges for the elements in your sample with Z < 93. It makes use of the three JSON files in the _JSONS_ directory:

+ **Atomic_MACs.json** - a nested dictionary containing a table of incident energy (keV) vs. elemental mass attenuation coefficient (cm<sup>2</sup>/g) for all elements. Of the form _{{"Z": "keV": MAC, "keV": MAC, etc..._
  + This data comes from [NIST Standard Reference Database 126](https://physics.nist.gov/PhysRefData/XrayMassCoef/tab3.html).
  + The HTML scraper used to convert the tables in the JSON dictionary can be found under _Scrapers > Atomic_LAC_reader.py._ Users should not need to re-scrape.
+ **Element_Information_Dict.json** - a dictionary containing basic information for each element of the form _{"Symbol": ["Z", "Element", "Z/A", "I (eV)", "Density (g/cm3)", "Molecular Weight (g/mol)"], etc..._
  + This data also comes from [NIST Standard Reference Database 126](https://physics.nist.gov/PhysRefData/XrayMassCoef/tab1.html).
  + Google AI mode was used to integrate molecular weight data and format the combination into the JSON file.
+ **X-ray_Absorption_Edges.json** - a dictionary containing a list of all X-ray edge energies for elements Z = 11 to Z = 92 of the form _{"Symbol": [["Edge type", "keV", "Angstrom"]["Edge type", etc..._
  + This data comes from S. Brennan and P.L. Cowan c/o [Ethan A. Merritt at UW](http://skuld.bmsc.washington.edu/scatter/AS_periodic.html)
  + The HTML scraper used to convert the tables in the JSON dictionary can be found under _Scrapers > Absorption_Edge_Reader.py._ Users should not need to re-scrape.
 
After the successful calculation of a MAC, the user is prompted to input their sample's density to generate the requisite LAC to check for appropriate sample thickness. There is an option to have the code generate a mass-based weighted average density, but for the sake of your 8th grade science teacher, don't use this - it was helpful for me for debugging, and the non-additive quality of volume means the LAC will be inaccurate. Once this is generated, you may opt to save the ACs as a .json output (which the _Beam_Profile_Calculator.py_ script will read if you are running _MAC_Calculator.py_ as a child script) or forego saving and quit the program (which means your thickness will not be checked if you are running _MAC_Calculator.py_ as a child script).

The code should be sufficiently commented to be read through with only novice understanding of Python. The program creates a SampleChemistry class that is then instantiated by user inputs. Qualities of the sample itself, like the final sample _MAC_, are saved into class variables. The use of a custom class here is a leftover from a previous structuring of this code, but enough of  _MAC_Calculator.py_ hinged on class functions that the class was kept. Once the program understands the atoms in the user's sample, it will generate smaller dictionaries containing with only the key:value pairs of included atoms. These subdictionaries are not saved to class variables, as they were never intended to be passed back to the parent script (below). If the program cannot understand the user's chemical formula, or if it contains elements above Z = 92, it will flag a boolean that will tell the parent script to avoid doing a penetration depth calculation to avoid errors. It will then proceed to offer an interference check on the atoms it does recognize (For Pu<sub>2</sub>Te<sub>2</sub>O<sub>9</sub>, it would check the absorption edges of "Te").

> [!IMPORTANT]
> This code cannot calculate MAC for samples which contain elements above atomic number (Z) 92, but this will not cause fatal errors.

## Beam Profile Calculations and Visualizations (Parent Script: _Beam_Profile_Calculator.py_)

Progress on this feature is forthcoming!

