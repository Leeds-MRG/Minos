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
	pip install -v -e .
	@echo "Replacing a line in vivarium.framework.randomness.py because it's broken..."
	# New pandas version no longer needs to raise a key error.
	@sed -i 's/except (IndexError, TypeError)/except (IndexError, TypeError, KeyError)/' $(SITEPACKAGES)/vivarium/framework/randomness.py
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
.phony: all_scenarios baseline intervention_hhIncome intervention_hhIncomeChildUplift intervention_hhIncomeChildUplift
.phony: intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift

#####################################
## Local runs of MINOS interventions.
#####################################

all_scenarios: baseline intervention_hhIncome intervention_hhIncomeChildUplift intervention_hhIncomeChildUplift
all_scenarios: intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift

baseline: ### Baseline run of MINOS, using configuration defined in testConfig.yaml
baseline: new_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config'

intervention_hhIncome: new_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'hhIncomeIntervention'

intervention_hhIncomeChildUplift: new_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'hhIncomeChildUplift'

intervention_PovertyLineChildUplift: new_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'hhIncomePovertyLineChildUplift'

intervention_livingWage: new_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'livingWageIntervention'

intervention_energyDownLift: new_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o 'default_config' -i 'energyDownlift'


#####################################
## Running MINOS scenarios on Arc4
#####################################

.phony: arc4_baseline arc4_intervention_hhIncome arc4_intervention_hhIncomeChildUplift
.phony: arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift

arc4_baseline: new_setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config'

arc4_intervention_hhIncome: new_setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'hhIncomeIntervention'

arc4_intervention_hhIncomeChildUplift: new_setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'hhIncomeChildUplift'

arc4_intervention_PovertyLineChildUplift: new_setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'hhIncomePovertyLineChildUplift'

arc4_intervention_livingWage: new_setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'livingWageIntervention'

arc4_intervention_energyDownLift: new_setup
	bash scripts/arc_submit.sh -c config/default.yaml -o 'default_config' -i 'energyDownlift'


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
setup: install data transitions replenishing_data

new_setup: install data new_transitions replenishing_data

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
replenishing_data: $(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds $(DATADIR)/replenishing/replenishing_pop_2019-2070.csv

spatial_data: ### Attach Chris' spatially disaggregated dataset and extract all records for Sheffield, to generate a
### version of the final data to be used in spatial analyses (of Sheffield only)
spatial_data: $(SPATIALDATA)/2019_US_cohort.csv

scot_data: final_data
scot_data: $(SCOTLANDDATA)/2019_US_cohort.csv

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

$(SPATIALDATA)/2019_US_cohort.csv: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv $(COMPLETEDATA)/2019_US_cohort.csv $(FINALDATA)/2019_US_cohort.csv $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(FINALDATA)/2019_US_cohort.csv) $(SPATIALSOURCEDIR)/ADULT_population_GB_2018.csv
	$(PYTHON) $(DATAGEN)/US_generate_spatial_component.py --source_dir $(SPATIALSOURCEDIR)

$(SCOTLANDDATA)/2019_US_cohort.csv: $(FINALDATA)/2019_US_cohort.csv
	$(PYTHON) $(DATAGEN)/US_scotland_subsetting.py --source_dir $(SPATIALSOURCEDIR)

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
transitions: $(TRANSITION_SOURCE)/model_definitions.txt final_data $(TRANSITION_SOURCE)/whole_population_mode.txt
new_transitions: $(TRANSITION_DATA)/loneliness/clm/loneliness_2018_2019.rds

scot_transitions: $(TRANSITION_SOURCE)/model_definitions_SCOTLAND.txt scot_data $(TRANSITION_SOURCE)/scotland_mode.txt

$(TRANSITION_SOURCE)/whole_population_mode.txt: $(FINALDATA)/2019_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R

$(TRANSITION_SOURCE)/scotland_mode.txt: $(SCOTDATA)/2019_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R
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


#####################################
# Post-hoc aggregation of multiple MINOS runs on bash terminal.
#####################################

AGGREGATE_METHOD = nanmean
AGGREGATE_VARIABLE = SF_12
REF_LEVEL = Baseline
DIRECTORIES = baseline,hhIncomeChildUplift,livingWageIntervention,energyDownlift
DIRECTORY_TAGS = "Baseline,£25 All Child Uplift,Living Wage,Energy Downlift"
SUBSET_FUNCTIONS = "who_alive,who_alive,who_alive,who_alive"

aggregate_minos_output:
	# See file for tag meanings.
	# aggregate files for baseline, all child uplift, and poverty line uplift.
	$(PYTHON) minos/validation/aggregate_minos_output.py -s $(DATAOUT)/default_config -d $(DIRECTORIES) -t $(DIRECTORY_TAGS) -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f $(SUBSET_FUNCTIONS)
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -s $(DIRECTORIES) -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -s $(DIRECTORIES) -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD)

aggregate_minos_output_treated:
	# See file for tag meanings.
	# aggregate files for baseline, all child uplift, and poverty line uplift.
	$(PYTHON) minos/validation/aggregate_minos_output.py -s $(DATAOUT)/default_config -d $(DIRECTORIES) -t $(DIRECTORY_TAGS) -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f who_alive,who_boosted,who_boosted,who_boosted
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -s $(DIRECTORIES) -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -s $(DIRECTORIES) -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "treated"

aggregate_minos_output_living_wage:
	# custom baseline for living wage only.
	$(PYTHON) minos/validation/aggregate_minos_output.py -s $(DATAOUT)/default_config -d baseline,livingWageIntervention -t "Baseline,Living Wage Intervention" -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f who_below_living_wage,who_boosted
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -s baseline,livingWageIntervention -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -s baseline,livingWageIntervention -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "living_wage_treated"

aggregate_minos_output_poverty_child_uplift:
	# custom baseline for living wage only.
	$(PYTHON) minos/validation/aggregate_minos_output.py -s $(DATAOUT)/default_config -d baseline,hhIncomePovertyLineChildUplift -t "Baseline,Poverty Line Uplift" -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f who_below_poverty_line_and_kids,who_boosted
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -s baseline,hhIncomePovertyLineChildUplift -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -s baseline,hhIncomePovertyLineChildUplift -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "poverty_line_child_uplift"

aggregate_minos_output_all_child_uplift:
	# custom baseline for living wage only.
	$(PYTHON) minos/validation/aggregate_minos_output.py -s $(DATAOUT)/default_config -d baseline,hhIncomeChildUplift -t "Baseline,All Children Uplift" -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f who_kids,who_boosted
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -s baseline,hhIncomeChildUplift -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -s baseline,hhIncomeChildUplift -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "all_child_uplift"

aggregate_minos_output_energy:
	# custom baseline for living wage only.
	$(PYTHON) minos/validation/aggregate_minos_output.py -s $(DATAOUT)/default_config -d baseline,energyDownlift -t "Baseline,Energy Downlift" -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f who_alive,who_boosted
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -s baseline,energyDownlift -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -s baseline,energyDownlift -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "energy_downlift"

all_lineplots: aggregate_minos_output aggregate_minos_output_treated aggregate_minos_output_living_wage aggregate_minos_output_all_child_uplift aggregate_minos_output_poverty_child_uplift aggregate_minos_output_energy
all_treated_lineplots: aggregate_minos_output_living_wage aggregate_minos_output_poverty_child_uplift aggregate_minos_output_all_child_uplift aggregate_minos_output_energy

#####################################
# Mapping multiple MINOS outputs into super outputs (LSOA/data zones) over Glasgow, Sheffield, Manchester, and Scotland regions.
#####################################

DEFAULT_OUTPUT_SUBDIRECTORY = default_config

INTERVENTION1 = baseline
INTERVENTION2 = povertyUplift
OUT_BASELINE = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/baseline
OUT_HHINCOMECHILDUP = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/hhIncomeChildUplift
OUT_ENERGYDOWNLIFT = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/energyDownlift
OUT_LIVINGWAGEINT = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/livingWageIntervention
OUT_POVERTYUP = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/hhIncomePovertyLineChildUplift
SPATIAL_DIRECTORY1 = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/$(INTERVENTION1)# first geojson for comparison in diff plot.
SPATIAL_DIRECTORY2 = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/$(INTERVENTION2)# second geojson for comparison in aggregate_two_and_diff
AGG_METHOD = nanmean# what method to aggregate with.
AGG_VARIABLE = SF_12# what variable to aggregate.
AGG_YEAR = 2025# what year to map in data.
AGG_LOCATION = glasgow # or manchester/scotland/sheffield
SAVE_FILE1 = $(SPATIAL_DIRECTORY1)/$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR).geojson # data source from aggregation. Need to automate these file paths somehow.
SAVE_PLOT1 = $(SPATIAL_DIRECTORY1)/$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR) # where to save plot for aggregate_lsoas_and_map
SAVE_FILE2 = $(SPATIAL_DIRECTORY2)/$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR).geojson # data source for aggregation of second minos run. Used when comparing two interventions in aggreate_two_and_map_diff
SAVE_PLOT2 = $(SPATIAL_DIRECTORY1)/$(INTERVENTION1)_vs_$(INTERVENTION2)_$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR) # pdf file name for aggregate_two_and_diff. saves in first specified file.

aggregate_and_map:
	# aggregate minos outputs into LSOAs.
	$(PYTHON) minos/validation/format_spatial_output.py -s $(SPATIAL_DIRECTORY1) -y $(AGG_YEAR) -d $(SPATIAL_DIRECTORY1) -m $(AGG_METHOD) -v $(AGG_VARIABLE) -f geojson
	# Map data now aggregated.
	$(RSCRIPT) minos/validation/sf12_single_map.R -f $(SAVE_FILE1) -d $(SAVE_PLOT1) -m $(AGG_LOCATION) -v $(AGG_VARIABLE)

aggregate_two_and_map_diff:
	# aggregate minos outputs into LSOAs.
	$(PYTHON) minos/validation/format_spatial_output.py -s $(SPATIAL_DIRECTORY1) -y $(AGG_YEAR) -d $(SPATIAL_DIRECTORY1) -m $(AGG_METHOD) -v $(AGG_VARIABLE) -f geojson
	$(PYTHON) minos/validation/format_spatial_output.py -s $(SPATIAL_DIRECTORY2) -y $(AGG_YEAR) -d $(SPATIAL_DIRECTORY2) -m $(AGG_METHOD) -v $(AGG_VARIABLE) -f geojson
	# map LSOAs.
	$(RSCRIPT) minos/validation/sf12_difference_map.R -f $(SAVE_FILE2) -g $(SAVE_FILE1) -d $(SAVE_PLOT2) -m $(AGG_LOCATION) -v $(AGG_VARIABLE)

aggregate_baseline_map:
	# aggregate minos outputs into LSOAs.
	$(PYTHON) minos/validation/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m $(AGG_METHOD) -v $(AGG_VARIABLE) -f geojson
	# Map data now aggregated.
	$(RSCRIPT) minos/validation/sf12_single_map.R -f $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson -d $(PLOTDIR)/baseline_map -m $(AGG_LOCATION) -v $(AGG_VARIABLE)

aggregate_baseline_energy_map:
	$(PYTHON) minos/validation/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m nanmean -v SF_12 -f geojson -u who_bottom_income_quintile
	$(PYTHON) minos/validation/format_spatial_output.py -s $(OUT_ENERGYDOWNLIFT) -y $(AGG_YEAR) -d $(OUT_ENERGYDOWNLIFT) -m nanmean -v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/validation/sf12_difference_map.R -f $(OUT_ENERGYDOWNLIFT)/nanmean_SF_12_$(AGG_YEAR).geojson -g $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson -d $(PLOTDIR)/baseline_vs_energy_difference_map -m $(AGG_LOCATION) -v SF_12

aggregate_baseline_living_wage_map:
	$(PYTHON) minos/validation/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m nanmean -v SF_12 -f	geojson -u who_below_living_wage
	$(PYTHON) minos/validation/format_spatial_output.py -s $(OUT_LIVINGWAGEINT) -y $(AGG_YEAR) -d $(OUT_LIVINGWAGEINT) -m	nanmean	-v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/validation/sf12_difference_map.R -f $(OUT_LIVINGWAGEINT)/nanmean_SF_12_$(AGG_YEAR).geojson -g $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson -d $(PLOTDIR)/baseline_vs_living_wage_difference_map -m $(AGG_LOCATION) -v SF_12

aggregate_baseline_all_uplift_map:
	$(PYTHON) minos/validation/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m nanmean -v SF_12 -f	geojson -u who_kids
	$(PYTHON) minos/validation/format_spatial_output.py -s $(OUT_HHINCOMECHILDUP) -y $(AGG_YEAR) -d $(OUT_HHINCOMECHILDUP) -m nanmean -v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/validation/sf12_difference_map.R -f $(OUT_HHINCOMECHILDUP)/nanmean_SF_12_$(AGG_YEAR).geojson -g $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson  -d $(PLOTDIR)/baseline_vs_all_25_uplift_difference_map -m $(AGG_LOCATION) -v SF_12

aggregate_baseline_poverty_uplift_map:
	$(PYTHON) minos/validation/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m nanmean -v SF_12 -f	geojson -u who_below_poverty_line_and_kids
	$(PYTHON) minos/validation/format_spatial_output.py -s $(OUT_POVERTYUP) -y $(AGG_YEAR) -d $(OUT_POVERTYUP) -m	nanmean	-v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/validation/sf12_difference_map.R -f $(OUT_POVERTYUP)/nanmean_SF_12_$(AGG_YEAR).geojson -g $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson -d $(PLOTDIR)/baseline_vs_poverty_25_uplift_difference_map -m $(AGG_LOCATION) -v SF_12

map_all: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map aggregate_baseline_poverty_uplift_map
map_concept_note: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map


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

clean_plots: ### Remove all <plot>.pdf files in plots/
	rm -rf plots/*.pdf
