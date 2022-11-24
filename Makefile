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
.PHONY: arc_conda

#conda:
#	@echo "Loading arc4 python module to use conda commands."
#	#module load python anaconda
#	@echo "Initiating conda environment. "
#	conda create -p conda_minos python=3.8
#	@echo "Activating conda environment"
#	source activate conda_minos
#	@echo "Minimal R 4.0.5 install in conda environment."
#	#conda install -c conda-forge r-base=4.0.5
#	conda install -c conda-forge r-essentials=4.0.5
#	@echo "conda install complete!"


####################### DOES NOT WORK #######################
arc_conda:
	@echo "WARNING: THIS TARGET DOES NOT WORK AND PROBABLY NEVER WILL"
	@echo "Maybe better to just force users to do it manually:"
	@echo "You must create a conda environment with python3.9 or higher, activate the env, then"
	@echo "install r-base=4.1.0"
	#@echo "Loading anaconda module..."
	#$(shell module load python anaconda)
	#@echo "Creating conda environment with python3.9..."
	#$(shell conda create -y -n conda_minos python=3.9) # create conda environment.
	#$(shell conda activate conda_minos) # activate conda environment.
	#@echo "Installing R..."
	#$(shell conda install -c conda-forge r-base=4.1.0) # install base R 4.1.0.
####################### DOES NOT WORK #######################
# I think the best solution to this problem is to just force users to create their own conda env and load it up
# realistically for the forseeable nobody outside of the research group is going to use it on arc anyway


## Install
###
.PHONY: install

# Check for existence of vivarium/__init__.py in site_packages as this will tell us if install is required
install: ### Install all Minos requirements via pip
install: $(SITEPACKAGES)/vivarium/__init__.py

$(SITEPACKAGES)/vivarium/__init__.py:
	@echo "Installing requirements via pip"
	pip install -v -e .
	@echo "Replacing a line in vivarium.framework.randomness.py because it's broken."
	# New pandas version no longer needs to raise a key error.
	@sed -i 's/except (IndexError, TypeError)/except (IndexError, TypeError, KeyError)/' $(SITEPACKAGES)/vivarium/framework/randomness.py
	@echo "python install complete."
	@echo "installing R requirements"
	Rscript install.R # install any R packages. Annoying to do in conda.
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
.phony: baseline intervention_hhIncome intervention_hhIncomeChildUplift intervention_hhIncomeChildUplift
.phony: intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift


## Local

all_scenarios: baseline intervention_hhIncome intervention_hhIncomeChildUplift intervention_hhIncomeChildUplift
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


## Arc4
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


## Beefy

beefy_baseline: ### Baseline run of MINOS on beefy. Runs 100 iterations with no interventions at all. Just status quo.
beefy_baseline: data transitions install beefy_conda
	$(PYTHON) # fill in when have access to beefy again..


### SETUP

setup: ### Setup target to prepare everything required for simulation.
### Runs install, prepares input data, estimates transition models, and generates input populations
setup: install data transitions replenishing_data


###
## Data Generation
###

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
replenishing_data: $(TRANSITION_DATA)/education/nnet/educ_nnet_2018_2019.rds $(DATADIR)/replenishing/replenishing_pop_2019-2070.csv

spatial_data: ### Attach Chris' spatially disaggregated dataset and extract all records for Sheffield, to generate a
### version of the final data to be used in spatial analyses (of Sheffield only)
spatial_data: $(SPATIALDATA)/2019_US_cohort.csv

###

transitions: ### Run R scripts to generate transition models for each module
transitions: | $(TRANSITION_DATA)
transitions: final_data $(TRANSITION_DATA)/hh_income/hh_income_2018_2019.rds $(TRANSITION_DATA)/housing/clm/housing_clm_2018_2019.rds
transitions: $(TRANSITION_DATA)/mwb/ols/sf12_ols_2018_2019.rds $(TRANSITION_DATA)/labour/nnet/labour_nnet_2018_2019.rds
transitions: $(TRANSITION_DATA)/neighbourhood/clm/neighbourhood_clm_2014_2017.rds $(TRANSITION_DATA)/tobacco/zip/tobacco_zip_2018_2019.rds
transitions: $(TRANSITION_DATA)/alcohol/zip/alcohol_zip_2018_2019.rds $(TRANSITION_DATA)/nutrition/ols/nutrition_ols_2018_2019.rds
transitions: $(TRANSITION_DATA)/loneliness/clm/loneliness_clm_2018_2019.rds

# Input Populations

$(RAWDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_format_raw.py --source_dir $(USSOURCEDIR)

$(CORRECTDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/US_missing_deterministic.py $(DATAGEN)/US_missing_LOCF.py $(DATAGEN)/US_missing_description.py $(DATAGEN)/US_missing_data_correction.py $(DATAGEN)/US_complete_case.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_missing_main.py

$(COMPOSITEDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_composite_vars.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_composite_vars.py

$(COMPLETEDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/US_complete_case.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_complete_case.py

$(FINALDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(COMPLETEDATA)/2019_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_stock_pop.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_stock_pop.py

$(DATADIR)/replenishing/replenishing_pop_2019-2070.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(COMPLETEDATA)/2019_US_cohort.csv $(FINALDATA)/2019_US_cohort.csv $(TRANSITION_DATA)/education/nnet/educ_nnet_2018_2019.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py

$(SPATIALDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(COMPLETEDATA)/2019_US_cohort.csv $(FINALDATA)/2019_US_cohort.csv $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(FINALDATA)/2019_US_cohort.csv) $(SPATIALSOURCEDIR)/ADULT_population_GB_2018.csv
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

$(TRANSITION_DATA)/education/nnet/educ_nnet_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/education/education_nnet.r
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


# Post-model aggregation and plots.
AGGREGATE_METHOD = nanmean
AGGREGATE_VARIABLE = SF_12
REF_LEVEL = Baseline
DIRECTORIES = baseline,povertyUplift,childUplift
DIRECTORY_TAGS = "Baseline,£20_PovertyLineUplift,£20_All_Child_Uplift"

aggregate_minos_output:
	# See file for tag meanings.
	# aggregate files for baseline, all child uplift, and poverty line uplift.
	python3 minos/validation/aggregate_minos_output.py -s $(DATAOUT) -d $(DIRECTORIES) -t $(DIRECTORY_TAGS) -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE)
	# stack aggregated files into one long array.
	python3 minos/validation/aggregate_long_stack.py -s $(DIRECTORIES) -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	python3 minos/validation/aggregate_lineplot.py -s $(DIRECTORIES) -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD)

###
## Cleaning
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

clean_plots: ### Remove all <plot>.pdf files in plots/
	rm -rf plots/*.pdf
