# Directories and paths
export ROOT=$(CURDIR)
USSOURCEDIR = $(CURDIR)/../UKDA-6614-stata/stata/stata13_se/
SPATIALSOURCEDIR = $(CURDIR)/../US_spatial_lookup/
DATADIR = $(CURDIR)/data
RAWDATA = $(DATADIR)/raw_US
CORRECTDATA = $(DATADIR)/corrected_US
COMPOSITEDATA = $(DATADIR)/composite_US
FINALDATA = $(DATADIR)/final_US
SPATIALDATA = $(DATADIR)/spatial_US
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
	@echo "Activating conda environment"
	source activate conda_minos
	@ "Minimal R 4.0.5 install in conda environment."
	#conda install -c conda-forge r-base=4.0.5
	conda install -c conda-forge r-essentials=4.0.5
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

testRun: ### Start a test run of the microsimulation using configuration defined in testConfig.yaml
testRun: data transitions
	$(PYTHON) scripts/run.py -c $(CONFIG)/testConfig.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)

###
## Experiment Runs
###

baseline: ### Baseline run of MINOS, using configuration defined in beefyBaseline.yaml
baseline: data transitions
	$(PYTHON) scripts/run.py -c $(CONFIG)/beefyBaseline.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)

incomeIntervention: ### Run the income intervention using config defined in beefyIncomeIntervention.yaml. This is the
### flexible framework for running income interventions, and adjustments to the size and scale of the intervention can be
### made by editing the parameters in minos.modules.intervention.hhIncomeIntervention.pre_setup(). Eventually we might
### make these parameters available in the config file itself, but this will have to do for now.
incomeIntervention: data transitions
	$(PYTHON) scripts/run.py -c $(CONFIG)/beefyIncomeIntervention.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)

childUplift: ### Run the child uplift intervention using config defined in beefyChildUplift.yaml. This intervention
### gives all adults with children an extra £20 to their household income per week per child.
childUplift: data transitions
	$(PYTHON) scripts/run.py -c $(CONFIG)/beefyChildUplift.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)

povertyUplift: ### Run the poverty uplift intervention using config defined in beefyPovertyUplift.yaml. This intervention
### gives all adults in poverty with children an extra £20 to their household income per week per child. Anyone with a
### household income below 60% of the median household income is defined as being in poverty.
povertyUplift: data transitions
	$(PYTHON) scripts/run.py -c $(CONFIG)/beefyPovertyUplift.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)

###
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

spatial_data: ### Attach Chris' spatially disaggregated dataset and extract all records for Sheffield, to generate a
### version of the final data to be used in spatial analyses (of Sheffield only)
spatial_data: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(FINALDATA)/2019_US_cohort.csv $(SPATIALDATA)/2019_US_cohort.csv

###

transitions: ### Run R scripts to generate transition models for each module
transitions: | $(TRANSITION_DATA)
transitions: final_data $(TRANSITION_DATA)/hh_income/hh_income_2018_2019.rds $(TRANSITION_DATA)/housing/clm/housing_clm_2018_2019.rds $(TRANSITION_DATA)/mwb/ols/sf12_ols_2018_2019.rds $(TRANSITION_DATA)/labour/nnet/labour_nnet_2018_2019.rds

# Input Populations

$(RAWDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_format_raw.py --source_dir $(USSOURCEDIR)

$(CORRECTDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/US_missing_deterministic.py $(DATAGEN)/US_missing_LOCF.py $(DATAGEN)/US_missing_description.py $(DATAGEN)/US_missing_data_correction.py $(DATAGEN)/US_complete_case.py $(PERSISTJSON)/*.json $(RAWDATA)/2018_US_cohort.csv
	$(PYTHON) $(DATAGEN)/US_missing_main.py

$(COMPOSITEDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/generate_composite_vars.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv
	$(PYTHON) $(DATAGEN)/generate_composite_vars.py

$(FINALDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_complete_case.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv $(COMPOSITEDATA)/2018_US_cohort.csv
	$(PYTHON) $(DATAGEN)/US_complete_case.py

$(SPATIALDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_complete_case.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv $(COMPOSITEDATA)/2018_US_cohort.csv $(FINALDATA)/2019_US_cohort.csv) $(SPATIALSOURCEDIR)/ADULT_population_GB_2018.csv
	$(PYTHON) $(DATAGEN)/US_generate_spatial_component.py --source_dir $(SPATIALSOURCEDIR)

# Transitions

$(TRANSITION_DATA):
	@echo "Creating transition data directory"
	mkdir -p $(TRANSITION_DATA)

$(TRANSITION_DATA)/hh_income/hh_income_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/income/income_ols.r
	# Script needs 3 arguments (which are set as Makefile variables, change there not here):
	# 1 - Minos root directory (i.e. $(ROOT))
	# 2 - Input data directory (i.e. data/composite or $(DATADIR))
	# 3 - Transition model directory (data/transitions or $(TRANSITION_DATA))
	$(RSCRIPT) $(SOURCEDIR)/transitions/income/income_ols.r --args $(DATADIR) $(TRANSITION_DATA) $(TRANSITION_SOURCE)

$(TRANSITION_DATA)/housing/clm/housing_clm_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/housing/Housing_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/housing/Housing_clm.R

$(TRANSITION_DATA)/mwb/ols/sf12_ols_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/mwb/SF12_OLS.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/mwb/SF12_OLS.R

$(TRANSITION_DATA)/labour/nnet/labour_nnet_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/labour/labour_nnet.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/labour/labour_nnet.R

$(TRANSITION_DATA)/housing/clm/neighbourhood_clm_2014_2017.rds: $(FINALDATA)/2017_US_cohort.csv $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R

###
## Cleaning
.PHONY: clean_out clean_logs clean_data clean_all

clean_all: ### Remove output, log files, generated data files and transition models
clean_all: clean_data clean_transitions

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