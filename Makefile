# Directories and paths
export ROOT=$(CURDIR)
USSOURCEDIR = $(CURDIR)/../UKDA-6614-stata/stata/stata13_se/
DATADIR = $(CURDIR)/data
RAWDATA = $(DATADIR)/raw_US
CORRECTDATA = $(DATADIR)/corrected_US
COMPOSITEDATA = $(DATADIR)/composite_US
FINALDATA = $(DATADIR)/final_US
PERSISTDATA = $(CURDIR)/persistent_data
PERSISTJSON = $(PERSISTDATA)/JSON
SOURCEDIR = $(CURDIR)/minos
DATAGEN = $(SOURCEDIR)/data_generation
TRANSITION_SOURCE = $(SOURCEDIR)/transitions
DATAOUT = $(CURDIR)/output
CONFIG = $(CURDIR)/config
TRANSITION_DATA = $(DATADIR)/transitions

# This path points to the python site-packages directory in the conda environment
SITEPACKAGES = $(shell python3 -c 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')

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

# ARC4 install instructions
# https://arcdocs.leeds.ac.uk/getting_started/logon.html
# When logged in to arc4. need to create user directory
# mkdir /nobackup/<USERNAME>
# Move to this directory
# cd /nobackup/<USERNAME>
# Clone minos git in. (contains this makefile)
# git clone https://github.com/Leeds-MRG/Minos
# Should be able to run conda and install commands if needed.

## Conda install (if needed)
###
.PHONY: conda

conda:
	＠echo "Loading arc4 python module to use conda commands."
	module load python anaconda
	@echo "Initiating conda environment. "
	conda create -p conda_minos python=3.8
	@ "Minimal R 4.0.5 install in conda environment."
	conda install -c conda-forge r-base=4.0.5
	@echo "Activating conda environment"
	source activate conda_minos
	@echo "conda install complete!"

## Install
###
.PHONY: install

install: ### Install all Minos requirements via pip
	@echo "Installing requirements via pip"
	pip install -v -e .
	@echo "Replacing a line in vivarium.framework.randomness.py because it's broken."
	# New pandas version no longer needs to raise a key error.
	@sed -i 's/except (IndexError, TypeError)/except (IndexError, TypeError, KeyError)/' $(SITEPACKAGES)/vivarium/framework/randomness.py
	@echo "python install complete."
	@echo "installing R requirements"
	Rscript install.R # install any R packages. Annoying to do in conda.
	@echo "\nInstall complete!\n"


## Test
###
.PHONY: testRun

#testRun: ### Start a test run of the microsimulation using configuration defined in testConfig.yaml
testRun: data transitions
	$(PYTHON) scripts/run.py -c $(CONFIG)/testConfig.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)


## Data Generation
# Combined Rules
###

data: ### Run all four levels of data generation from raw Understanding Society data to imputed data in the correct
###	format with composite variables generated
data: raw_data corrected_data composite_data final_data

raw_data: ### Generate starting data in the correct format from raw Understanding Society data
raw_data: $(RAWDATA)/2019_US_cohort.csv

corrected_data: ### Run a number of imputation procedures on the raw data to produce corrected data
corrected_data: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv

composite_data: ### Generate composite variables
composite_data: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv

final_data: ### Produce the final version of the data, after running complete case correction
final_data: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(FINALDATA)/2019_US_cohort.csv

###

transitions: ### Run R scripts to generate transition models for each module
transitions: final_data $(TRANSITIONS)/hh_income/hh_income_2018_2019.rds $(TRANSITIONS)/housing/clm/housing_clm_2018_2019.rds $(TRANSITIONS)/mwb/ols/sf12_2018_2019.rds

# Input Populations

$(RAWDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_format_raw.py --source_dir $(USSOURCEDIR)

$(CORRECTDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/US_missing_deterministic.py $(DATAGEN)/US_missing_LOCF.py $(DATAGEN)/US_missing_description.py $(DATAGEN)/US_missing_data_correction.py $(DATAGEN)/US_complete_case.py $(PERSISTJSON)/*.json $(RAWDATA)/2018_US_cohort.csv
	$(PYTHON) $(DATAGEN)/US_missing_main.py

$(COMPOSITEDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/generate_composite_vars.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv
	$(PYTHON) $(DATAGEN)/generate_composite_vars.py

$(FINALDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/US_complete_case.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv
	$(PYTHON) $(DATAGEN)/US_complete_case.py

# Transitions

$(TRANSITIONS)/hh_income/hh_income_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/estimate_transition_models.r
	# Script needs 3 arguments (which are set as Makefile variables above, change there not here):
	# 1 - Minos root directory (i.e. $(ROOT))
	# 2 - Input data directory (i.e. data/composite or $(DATADIR))
	# 3 - Transition model directory (data/transitions or $(TRANSITIONS))
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transition_models.r --args $(DATADIR) $(TRANSITION_DATA) $(TRANSITION_SOURCE)

$(TRANSITIONS)/housing/clm/housing_clm_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/housing/Housing_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/housing/Housing_clm.R

$(TRANSITIONS)/mwb/ols/sf12_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/mwb/SF12_OLS.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/mwb/SF12_OLS.R

###
## Cleaning
.PHONY: clean clean_out clean_logs clean_data clean_all

clean: ### Remove output and log files
clean: clean_out clean_logs

clean_all: ### Remove output, log files, generated data files and transition models
clean_all: clean clean_data clean_transitions

clean_data: ### Remove data files generated in the pipeline
clean_data:
	rm -f data/*/*.csv

clean_out: ### Remove all output files
clean_out:
	rm -rf output/*

clean_logs: ### Remove log files (currently only test.log)
clean_logs:
	rm -rf test.log

clean_transitions: ### Remove model .rds files
clean_transitions:
	rm -rf data/transitions/*/*.rds
	rm -rf data/transitions/*/*.txt
	rm -rf data/transitions/*/*/*.rds
	rm -rf data/transitions/*/*/*.txt