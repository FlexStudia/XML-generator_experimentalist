# XML-generator experimentalist
SSHADE XML generator project


**Description**:
- it is a program
- it is coded in Python 3.7.6
- it is created for SSHADE.eu to help fill the "experimentalist" XML file
- it is powered by the PyQt library to create a "web-form" interface which contains all the main fields of the SSHADE experimentalist XML file
- it generates an "experimentalist" SSHADE XML file filled with the data entered in the "web-form" interface


**Usage**

in any python 3 environment
1. to be able to run this python file, you must have python 3 installed ([python.org](www.python.org/downloads))
2. after it is necessary to install all the required packages (listed in requirements.txt provided with the py code file and this readme) for example via a virtual environment:
		
		python3 -m venv .venv
		source .venv/bin/activate
		pip install --upgrade pip setuptools wheel
		pip install --upgrade -r requirements.txt
    
3. it is possible to read and run the code in the native python environment or install an IDE, for example "PyCharm"


**Compilation**

it is possible to create a single executable file with PyInstaller with the following command line:

for Linux:

		pyinstaller --noconsole --onefile XMLgenerator_Experimentalist.py
      
for Mac:

		pyinstaller --noconsole --onefile --icon "icon.icns" XMLgenerator_Experimentalist.py 
      
for Windows:

		pyinstaller --noconsole --onefile --icon "icon.ico" XMLgenerator_Experimentalist.py
      
where "icon.ico"/"icon.icns" is an option to include an icon for the executable (provided)


**Authors and acknowledgment**
- program code is by Maria Gorbacheva (flex.studia.dev@gmail.com) with the kind help of Philippe Bollard (philippe.bollard@univ-grenoble-alpes.fr)
- scientific base is by Bernard Schmitt (bernard.schmitt@univ-grenoble-alpes.fr)
	
  
**Contributing**

for any questions, proposals and bug reports, please write to XML.generator.experimentalist@gmail.com


**License**

CC-BY 4.0 (Authors attribution alone required)

for more info: [creativecommons.org](https://creativecommons.org/licenses/by/4.0/deed.fr)
	
  
**Changelog**

28.08.20: version 0.95 is officially released at [wiki.sshade.eu](wiki.sshade.eu/sshade/tools) as cross-platform executables

22.10.29: projct added to [GitHub](https://github.com/FlexStudia/XML-generator_experimentalist)
