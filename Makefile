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

## Install
###

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


## Test Simulations
###
.PHONY: testRun testRun_Intervention

testRun: ### Start a test run of the microsimulation using configuration defined in testConfig.yaml
testRun: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml --output_subdir 'testRun'

testRun_Intervention: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml --output_subdir 'testRun' -i 'livingWageIntervention'

###
## Experiment Runs
###
.phony: all_scenarios baseline intervention_hhIncome intervention_hhIncomeChildUplift
.phony: intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift

#####################################
## Local runs of MINOS interventions.
#####################################

all_scenarios: baseline intervention_hhIncome intervention_hhIncomeChildUplift
all_scenarios: intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift

baseline: ### Baseline run of MINOS, using configuration defined in testConfig.yaml
baseline: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config'

intervention_hhIncome: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'hhIncomeIntervention'

intervention_hhIncomeChildUplift: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'hhIncomeChildUplift'

intervention_PovertyLineChildUplift: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'hhIncomePovertyLineChildUplift'

intervention_livingWage: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'livingWageIntervention'

intervention_energyDownLift: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'energyDownlift'


#####################################
## Scotland Local runs of MINOS interventions.
#####################################

scot_baseline: scot_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/scot_default.yaml -o 'scotland_mode'

scot_intervention_hhIncome: scot_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/scot_default.yaml -o 'scotland_mode' -i 'hhIncomeIntervention'

scot_intervention_hhIncomeChildUplift: scot_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/scot_default.yaml -o 'scotland_mode' -i 'hhIncomeChildUplift'

scot_intervention_PovertyLineChildUplift: scot_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/scot_default.yaml -o 'scotland_mode' -i 'hhIncomePovertyLineChildUplift'

scot_intervention_livingWage: scot_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/scot_default.yaml -o 'scotland_mode' -i 'livingWageIntervention'

scot_intervention_energyDownLift: scot_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/scot_default.yaml -o 'scotland_mode' -i 'energyDownlift'

scot_all_scenarios: scot_baseline scot_intervention_hhIncomeChildUplift scot_intervention_PovertyLineChildUplift scot_intervention_livingWage scot_intervention_energyDownLift

arc4_scot_baseline:
	bash scripts/arc_submit.sh -c config/scot_default.yaml -o 'scotland_mode'

arc4_scot_all_child_uplift:
	bash scripts/arc_submit.sh -c config/scot_default.yaml -o 'scotland_mode' -i 'hhIncomeChildUplift'
#####################################
## Running MINOS scenarios on Arc4
#####################################

.phony: arc4_baseline arc4_intervention_hhIncome arc4_intervention_hhIncomeChildUplift
.phony: arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift

arc4_baseline: setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config'

arc4_intervention_hhIncome: setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'hhIncomeIntervention'

arc4_intervention_hhIncomeChildUplift: setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'hhIncomeChildUplift'

arc4_intervention_PovertyLineChildUplift: setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'hhIncomePovertyLineChildUplift'

arc4_intervention_livingWage: setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'livingWageIntervention'

arc4_intervention_energyDownLift: setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'energyDownlift'

arc4_allscenarios: arc4_baseline arc4_intervention_hhIncome arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift

#####################################
# Running scenarios on beefy HPC in LIDA.
#####################################

# Needs doing when we can access the machine again..
beefy_baseline: ### Baseline run of MINOS on beefy. Runs 100 iterations with no interventions at all. Just status quo.
beefy_baseline: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o 'default_config'

beefy_intervention_hhIncome: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o 'default_config' -i 'hhIncomeIntervention'

beefy_intervention_hhIncomeChildUplift: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o 'default_config' -i 'hhIncomeChildUplift'

beefy_intervention_PovertyLineChildUplift: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o 'default_config' -i 'hhIncomePovertyLineChildUplift'

beefy_intervention_livingWage: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o 'default_config' -i 'livingWageIntervention'

beefy_intervention_energyDownLift: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o 'default_config' -i 'energyDownlift'

beefy_all: beefy_baseline beefy_intervention_hhIncomeChildUplift beefy_intervention_PovertyLineChildUplift beefy_intervention_livingWage beefy_intervention_energyDownLift

#####################################
### SETUP
#####################################

setup: ### Setup target to prepare everything required for simulation.
### Runs install, prepares input data, estimates transition models, and generates input populations
setup: install data transitions replenishing_data serialise_rpy2

scot_setup: install scot_data scot_transitions scot_replenishing serialise_rpy2

#####################################
### Data Generation
#####################################

data: ### Run all four levels of data generation from raw Understanding Society data to imputed data in the correct
###	format with composite variables generated
data: raw_data corrected_data composite_data complete_data final_data

raw_data: ### Generate starting data in the correct format from raw Understanding Society data
raw_data: $(RAWDATA)/2019_US_cohort.csv

corrected_data: ### Run a number of imputation procedures on the raw data to produce corrected data
corrected_data: $(CORRECTDATA)/2019_US_cohort.csv

composite_data: ### Generate composite variables
composite_data: $(COMPOSITEDATA)/2019_US_cohort.csv

complete_data: ### Generate a complete version of the data, after running complete case correction
complete_data: $(COMPLETEDATA)/2019_US_cohort.csv

final_data: ### Produce the final version of the data (including replenishing population for 2018-2070), after reweighting both the stock and replenishing input_populations
final_data: $(FINALDATA)/2019_US_cohort.csv

replenishing_data: ### Produce the replenishing population (MORE NEEDED HERE).
replenishing_data:  $(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds $(DATADIR)/replenishing/replenishing_pop_2019-2070.csv

scot_replenishing: $(DATADIR)/replenishing/scotland/replenishing_pop_2019-2070.csv $(SCOTDATA)/2019_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds

spatial_data: ### Attach Chris' spatially disaggregated dataset and extract all records for Sheffield, to generate a
### version of the final data to be used in spatial analyses (of Sheffield only)
spatial_data: $(SPATIALDATA)/2019_US_cohort.csv

scot_data: $(SCOTDATA)/2019_US_cohort.csv

serialise_rpy2: $(PYTHON)/data_generation/serialise_rpy2_pickle.py

#####################################
# Input Populations
#####################################

$(RAWDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_format_raw.py --source_dir $(USSOURCEDIR)

$(CORRECTDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/US_missing_deterministic.py $(DATAGEN)/US_missing_LOCF.py $(DATAGEN)/US_missing_description.py $(DATAGEN)/US_missing_data_correction.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_missing_main.py

$(COMPOSITEDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_composite_vars.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_composite_vars.py

$(COMPLETEDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/US_complete_case.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_complete_case.py

$(FINALDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(COMPLETEDATA)/2019_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_stock_pop.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_stock_pop.py

$(DATADIR)/replenishing/replenishing_pop_2019-2070.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(COMPLETEDATA)/2019_US_cohort.csv $(FINALDATA)/2019_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py

$(DATADIR)/replenishing/scotland/replenishing_pop_2019-2070.csv: $(SCOTDATA)/2019_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --scotland

$(SPATIALDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(COMPLETEDATA)/2019_US_cohort.csv $(FINALDATA)/2019_US_cohort.csv $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(FINALDATA)/2019_US_cohort.csv) $(SPATIALSOURCEDIR)/ADULT_population_GB_2018.csv
	$(PYTHON) $(DATAGEN)/US_generate_spatial_component.py --source_dir $(SPATIALSOURCEDIR)

$(SCOTDATA)/2019_US_cohort.csv: $(FINALDATA)/2019_US_cohort.csv
	$(PYTHON) $(DATAGEN)/US_scotland_subsetting.py

#####################################
### transitions
#####################################

#transitions: ### Run R scripts to generate transition models for each module
#transitions: | $(TRANSITION_DATA)
#transitions: final_data $(TRANSITION_DATA)/hh_income/hh_income_2018_2019.rds $(TRANSITION_DATA)/housing/clm/housing_clm_2018_2019.rds
#transitions: $(TRANSITION_DATA)/mwb/ols/sf12_ols_2018_2019.rds $(TRANSITION_DATA)/labour/nnet/labour_nnet_2018_2019.rds
#transitions: $(TRANSITION_DATA)/neighbourhood/clm/neighbourhood_clm_2014_2017.rds $(TRANSITION_DATA)/tobacco/zip/tobacco_zip_2018_2019.rds
#transitions: $(TRANSITION_DATA)/alcohol/zip/alcohol_zip_2018_2019.rds $(TRANSITION_DATA)/nutrition/ols/nutrition_ols_2018_2019.rds
#transitions: $(TRANSITION_DATA)/loneliness/clm/loneliness_clm_2018_2019.rds

transitions: | $(TRANSITION_DATA)
transitions: final_data $(TRANSITION_DATA)/hh_income/ols/hh_income_2018_2019.rds

scot_transitions: final_data $(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds

$(TRANSITION_DATA)/hh_income/ols/hh_income_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R

$(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds: $(SCOTDATA)/2019_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_SCOTLAND.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --scotland

$(TRANSITION_DATA)/loneliness/clm/loneliness_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/loneliness/loneliness_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/loneliness/loneliness_clm.R

$(TRANSITION_DATA)/neighbourhood_safety/clm/neighbourhood_safety_2014_2017.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R

$(TRANSITION_DATA):
	@echo "Creating transition data directory"
	mkdir -p $(TRANSITION_DATA)

#$(TRANSITION_DATA)/hh_income/hh_income_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/income/income_ols.r
#	# Script needs 3 arguments (which are set as Makefile variables, change there not here):
#	# 1 - Minos root directory (i.e. $(ROOT))
#	# 2 - Input data directory (i.e. data/composite or $(DATADIR))
#	# 3 - Transition model directory (data/transitions or $(TRANSITION_DATA))
#	$(RSCRIPT) $(SOURCEDIR)/transitions/income/income_ols.r --args $(DATADIR) $(TRANSITION_DATA) $(TRANSITION_SOURCE)

$(TRANSITION_DATA)/housing/clm/housing_clm_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/housing/Housing_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/housing/Housing_clm.R

$(TRANSITION_DATA)/mwb/ols/sf12_ols_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/mwb/SF12_OLS.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/mwb/SF12_OLS.R

$(TRANSITION_DATA)/labour/nnet/labour_nnet_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/labour/labour_nnet.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/labour/labour_nnet.R

$(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/education/education_nnet.r
	$(RSCRIPT) $(SOURCEDIR)/transitions/education/education_nnet.r

$(TRANSITION_DATA)/neighbourhood/clm/neighbourhood_clm_2014_2017.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R

$(TRANSITION_DATA)/tobacco/zip/tobacco_zip_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/tobacco/tobacco_zip.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/tobacco/tobacco_zip.R

$(TRANSITION_DATA)/alcohol/zip/alcohol_zip_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/alcohol/alcohol_zip.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/alcohol/alcohol_zip.R

$(TRANSITION_DATA)/nutrition/ols/nutrition_ols_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/nutrition/nutrition_ols.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/nutrition/nutrition_ols.R

$(TRANSITION_DATA)/loneliness/clm/loneliness_clm_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/loneliness/loneliness_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/loneliness/loneliness_clm.R


include minos/validation/Makefile # plotting makefile

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
	rm -rf data/transitions/scotland/*/*.rds

clean_scotland: ### Clean all files related to Scotland mode
clean_scotland:
	rm -rf data/transitions/scotland/*/*.rds
	rm -rf data/scotland_US/*.csv
	rm -rf data/replenishing/scotland/*.csv

clean_plots: ### Remove all <plot>.pdf files in plots/
	rm -rf plots/*.pdf
