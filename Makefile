# Directories and paths
export ROOT=$(CURDIR)
USSOURCEDIR = $(CURDIR)/../UKDA-6614-stata/stata/stata13_se/
SPATIALSOURCEDIR = $(CURDIR)/../US_spatial_lookup/
DATADIR = $(CURDIR)/data
RAWDATA = $(DATADIR)/raw_US
ADJRAWDATA = $(DATADIR)/adj_raw_US
CORRECTDATA = $(DATADIR)/corrected_US
COMPOSITEDATA = $(DATADIR)/composite_US
COMPLETEDATA = $(DATADIR)/complete_US
INFLATEDDATA = $(DATADIR)/inflated_US
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
GLASGOWSCALEDDATA = $(DATADIR)/scaled_glasgow_US
GLASGOWSCALEDDATA = $(DATADIR)/scaled_scotland_US
UKSCALEDDATA = $(DATADIR)/scaled_uk_US
TESTING = $(SOURCEDIR)/testing

# These paths point to the Python/R site-packages directory in the conda environment
SITEPACKAGES = $(shell python3 -c 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')
#SITEPACKAGES_VIVARIUM = $(shell python -c "import os, vivarium; print(os.path.dirname(vivarium.__file__))") # Alternative method
SITEPACKAGESR = $(shell Rscript -e '.libPaths()') | sed "s/^[^ ]* //"

# Executables
PYTHON = python
RSCRIPT = Rscript

# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

## Help
.PHONY: help

help: ### Show this help
	@echo "$(GREEN)Minos Makefile help$(RESET):"
	@echo
	@echo "The Makefile is the primary method of interacting with the Minos project, and provides the ability to do all "
	@echo "that is required to prepare and run the microsimulation."
	@echo "Key steps to running the simulation from scratch are:"
	@echo "    Installing the package and requirements"
	@echo "    Input Data Generation"
	@echo "    Producing transition models from input data"
	@echo "    Running the microsimulation, requiring both input data and transition models"
	@echo
	@echo "The Makefile is set up to run any process that is required and has not already been completed."
	@echo
	@fgrep -h "###" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/###//'

.PHONY: libpaths
libpaths: ### Grab paths to Python and R libraries
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

##########
## Install
##########

# Check for existence of vivarium/__init__.py in site_packages as this will tell us if install is required
install: ### Install Minos and requirements (all except vivarium removed to conda env file)
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

#####################################
### SETUP
#####################################

setup: ### Setup target to prepare everything required for simulation.
### Runs install, prepares input data, estimates transition models, and generates input populations
setup: install data transitions_default replenishing_data

setup_inflated: install data transitions_default inflated_data inflated_repl

setup_S7: install data transitions_SIPHER7 replenishing_data

scot_setup: install scot_data scot_transitions scot_replenishing

cv_setup: install cv_data cv_transitions cv_replenishing

cv_S7_setup: install data cv_S7_transitions cv_replenishing

setup_glasgow_scaled: install synthetic_glasgow_data transitions_default synthetic_glasgow_repl

setup_glasgow_scaled_S7: install synthetic_glasgow_data transitions_SIPHER7 synthetic_glasgow_repl

setup_scotland_scaled: install synthetic_glasgow_data transitions_default synthetic_scotland_repl

setup_scotland_scaled_S7: install synthetic_glasgow_data transitions_SIPHER7 synthetic_scotland_repl

setup_uk_scaled: install synthetic_uk_data transitions_default synthetic_uk_repl

setup_uk_scaled_S7: install synthetic_uk_data transitions_SIPHER7 synthetic_uk_repl

#####################################
### ADDITIONAL MAKEFILES
#####################################

include minos/data_generation/Makefile # data generation Makefile. files paths need fixing do later.
include minos/transitions/Makefile # transitions Makefile
include scripts/Makefile # running minos Makefile
include minos/outcomes/Makefile # plotting makefile
include minos/validation/Makefile # validation scripts
#include docsrc/Makefile # sphinx makefile


#####################################
### Cleaning
#####################################

.PHONY: clean_out clean_logs clean_data clean_all

clean_all: ### Remove output, log files, generated data files and transition models
clean_all: clean_data clean_out clean_transitions clean_logs

clean_data: ### Remove data files generated in the pipeline
clean_data:
	rm -f data/*/*.csv

clean_out: ### Remove all output files
clean_out:
	rm -rf output/*

#TODO add one for arc4 logs too.
clean_logs: ### Remove log files (including test.log, slurm, and arc logs)
clean_logs:
	rm -rf test.log
	rm -rf logs/*

clean_transitions: ### Remove model .rds files
clean_transitions:
	rm -rf data/transitions/*/*.rds
	rm -rf data/transitions/*/*.txt
	rm -rf data/transitions/*/*/*.rds
	rm -rf data/transitions/*/*/*.txt
	rm -rf data/transitions/*/*/*/*.rds
	rm -rf data/transitions/*/*/*/*.txt
	rm -rf data/transitions/*/*/*/*/*.rds
	rm -rf data/transitions/*/*/*/*/*.txt
	rm -rf data/transitions/scotland/*/*.rds

clean_scotland: ### Clean all files related to Scotland mode
clean_scotland:
	rm -rf data/transitions/scotland/*/*.rds
	rm -rf data/scotland_US/*.csv
	rm -rf data/replenishing/scotland/*.csv

clean_plots: ### Remove all <plot>.pdf files in plots/
	rm -rf plots/*.pdf
