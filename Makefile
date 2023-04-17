# Directories and paths
export ROOT=$(CURDIR)
USSOURCEDIR = $(CURDIR)/../UKDA-6614-stata/stata/stata13_se/
SPATIALSOURCEDIR = $(CURDIR)/../US_spatial_lookup/
DATADIR = $(CURDIR)/data
RAWDATA = $(DATADIR)/raw_US
CORRECTDATA = $(DATADIR)/corrected_US
COMPOSITEDATA = $(DATADIR)/composite_US
COMPLETEDATA = $(DATADIR)/complete_US
FINALDATA = $(DATADIR)/final_US
SPATIALDATA = $(DATADIR)/spatial_US
SCOTDATA = $(DATADIR)/scotland_US
PERSISTDATA = $(CURDIR)/persistent_data
PERSISTJSON = $(PERSISTDATA)/JSON
SOURCEDIR = $(CURDIR)/minos
DATAGEN = $(SOURCEDIR)/data_generation
TRANSITION_SOURCE = $(SOURCEDIR)/transitions
MODULES = $(SOURCEDIR)/modules
DATAOUT = $(CURDIR)/output
CONFIG = $(CURDIR)/config
TRANSITION_DATA = $(DATADIR)/transitions
PLOTDIR = $(CURDIR)/plots

# These paths point to the Python/R site-packages directory in the conda environment
SITEPACKAGES = $(shell python3 -c 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')
#SITEPACKAGES_VIVARIUM = $(shell python -c "import os, vivarium; print(os.path.dirname(vivarium.__file__))") # Alternative method
SITEPACKAGESR = $(shell Rscript -e '.libPaths()') | sed "s/^[^ ]* //"

# Executables
PYTHON = python
RSCRIPT = Rscript

.PHONY: libpaths
## Print out the library paths for Python and R libraries in conda
libpaths:
	@echo "Default conda site-packages paths for Python and R modules:"
	@echo $(SITEPACKAGES)
	@echo $(SITEPACKAGESR)


# ARC4 install instructions
# https://arcdocs.leeds.ac.uk/getting_started/logon.html
# When logged in to arc4. need to create user directory
# mkdir /nobackup/<USERNAME>
# Move to this directory
# cd /nobackup/<USERNAME>
# Clone minos git in. (contains this makefile)
# git clone https://github.com/Leeds-MRG/Minos


#-------------- INSTALL --------------#

# Check for existence of vivarium/__init__.py in site_packages as this will tell us if install is required
## Install Minos and requirements (all except vivarium removed to conda env file)
install: $(SITEPACKAGES)/vivarium/__init__.py

$(SITEPACKAGES)/vivarium/__init__.py:
	@echo "Installing remaining requirements via pip..."
	#pip install vivarium~=0.10.12 # Alternative method to specifying this in setup.py, which is called by "pip install" below
	pip install -v -e .
	#conda develop . # Alternative method, but Minos will not be shown in "conda list"
	@echo "Replacing a line in vivarium.framework.randomness.py because it's broken..."
	# New pandas version no longer needs to raise a key error.
	@sed -i.backup 's/except (IndexError, TypeError)/except (IndexError, TypeError, KeyError)/' $(SITEPACKAGES)/vivarium/framework/randomness.py
	@echo "\nInstall complete!\n"


#-------------- SETUP --------------#

## Prepare everything required for simulation.
## Runs install, prepares input data, estimates transition models, and generates input populations
setup: install data transitions replenishing_data

## Prepare everything for Scottish simulation
scot_setup: install scot_data scot_transitions scot_replenishing

## Prepare everything for Cross-validation
cv_setup: install cv_data cv_transitions cv_replenishing


#-------------- ADDITIONAL MAKEFILES --------------#

include minos/data_generation/Makefile # data generation Makefile. files paths need fixing do later.
include minos/transitions/Makefile # transitions Makefile
include scripts/Makefile # running minos Makefile
include minos/outcomes/Makefile # plotting makefile
include minos/validation/Makefile # validation scripts
#include docsrc/Makefile # sphinx makefile
include clean.makefile # cleaning
include help.makefile # show help
