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
.PHONY: conda

conda:
	@echo "Loading arc4 python module to use conda commands."
	#module load python anaconda
	@echo "Initiating conda environment. "
	conda create -p conda_minos python=3.8
	@echo "Activating conda environment"
	source activate conda_minos
	@"Minimal R 4.0.5 install in conda environment."
	#conda install -c conda-forge r-base=4.0.5
	conda install -c conda-forge r-essentials=4.0.5
	@echo "conda install complete!"

.PHONY: arc_conda

arc_conda:
	$(shell module load python anaconda)
	conda create -n conda_minos python=3.9 # create conda environment.
	#conda activate conda_minos # activate conda environment.
	conda install -c conda-forge r-base=4.1.0 # install base R 4.1.0.
	conda install -c conda-forge r-sf
	conda install -c conda-forge r-dplyr
	conda install -c conda-forge r-tidyverse
	
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
testRun: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/testConfig.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)

testRun_Intervention: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/beefyLivingWageIntervention.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)

###
## Experiment Runs
###

baseline: ### Baseline run of MINOS, using configuration defined in beefyBaseline.yaml
baseline: data transitions
	$(PYTHON) scripts/run.py -c $(CONFIG)/beefyBaseline.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)

#beefy_baseline: # Baseline run of MINOS on beefy. Runs 100 iterations with no interventions at all. Just status quo.
#beefy_baseline: data transitions install beefy_conda
#	$(PYTHON) # fill in when have access to beefy again..

arc4_baseline:
	$(shell module load python anaconda)
	$(shell conda activate conda_minos)
	$(shell qsub scripts/arc.sh config/beefyBaseline.yaml)

arc4_living_wage:
	$(shell module load python anaconda)
	$(shell conda activate conda_minos)
	$(shell qsub scripts/arc.sh config/beefyLivingWageIntervention.yaml)

arc4_energy:
	$(shell qsub scripts/arc.sh config/beefyEnergyDownlift.yaml)

arc4_all_child_uplift:
	$(shell qsub scripts/arc.sh config/beefyChildUplift.yaml)

arc4_poverty_line_uplift:
	$(shell qsub scripts/arc.sh config/beefyPovertyUplift.yaml)

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

setup: ### Setup target just for ease of development, NEED MORE INFORMATION SOON.
setup: data transitions replenishing_data

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
DIRECTORIES = baseline,povertyUplift,childUplift,livingWageIntervention,energyDownlift
DIRECTORY_TAGS = "Baseline,£20_PovertyLineUplift,£20_All_Child_Uplift,Living_Wage,Energy_Downlift"
SUBSET_FUNCTIONS = "who_alive,who_alive,who_alive,who_alive,who_alive"

aggregate_minos_output:
	# See file for tag meanings.
	# aggregate files for baseline, all child uplift, and poverty line uplift.
	$(PYTHON) minos/validation/aggregate_minos_output.py -s $(DATAOUT) -d $(DIRECTORIES) -t $(DIRECTORY_TAGS) -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f $(SUBSET_FUNCTIONS)
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -s $(DIRECTORIES) -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -s $(DIRECTORIES) -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD)

AGGREGATE_METHOD = nanmean
AGGREGATE_VARIABLE = SF_12
REF_LEVEL = Baseline
DIRECTORIES = baseline,povertyUplift,childUplift,livingWageIntervention
DIRECTORY_TAGS = "Baseline,£20_PovertyLineUplift,£20_All_Child_Uplift,Living_Wage"
SUBSET_FUNCTIONS = "who_alive,who_boosted,who_boosted,who_boosted"

aggregate_minos_output_treated:
	# See file for tag meanings.
	# aggregate files for baseline, all child uplift, and poverty line uplift.
	$(PYTHON) minos/validation/aggregate_minos_output.py -s $(DATAOUT) -d $(DIRECTORIES) -t $(DIRECTORY_TAGS) -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f $(SUBSET_FUNCTIONS)
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -s $(DIRECTORIES) -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -s $(DIRECTORIES) -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "treated"


INTERVENTION1 = baseline
INTERVENTION2 = povertyUplift
SPATIAL_DIRECTORY1 = output/$(INTERVENTION1)# first geojson for comparison in diff plot.
SPATIAL_DIRECTORY2 = output/$(INTERVENTION2)# second geojson for comparison in aggregate_two_and_diff
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


aggregate_baseline_energy_map:
	$(PYTHON) minos/validation/format_spatial_output.py -s output/baseline -y $(AGG_YEAR) -d output/baseline -m nanmean -v SF_12 -f geojson -u who_alive
	$(PYTHON) minos/validation/format_spatial_output.py -s output/energyDownlift -y $(AGG_YEAR) -d output/energyDownlift -m nanmean -v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/validation/sf12_difference_map.R -f output/baseline/nanmean_SF_12_$(AGG_YEAR).geojson -g output/energyDownlift/nanmean_SF_12_$(AGG_YEAR).geojson -d plots/baseline_vs_energy_difference_map.pdf -m $(AGG_LOCATION) -v SF_12

aggregate_baseline_living_wage_map:
	$(PYTHON) minos/validation/format_spatial_output.py -s output/baseline -y $(AGG_YEAR) -d output/baseline -m nanmean -v SF_12 -f	geojson -u who_alive
	$(PYTHON) minos/validation/format_spatial_output.py -s output/livingWageIntervention -y $(AGG_YEAR) -d output/livingWageIntervention -m	nanmean	-v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/validation/sf12_difference_map.R -f output/baseline/nanmean_SF_12_$(AGG_YEAR).geojson -g output/livingWageIntervention/nanmean_SF_12_$(AGG_YEAR).geojson -d plots/baseline_vs_living_wage_difference_map.pdf -m $(AGG_LOCATION) -v SF_12

aggregate_baseline_all_uplift_map:
	$(PYTHON) minos/validation/format_spatial_output.py -s output/baseline -y $(AGG_YEAR) -d output/baseline -m nanmean -v SF_12 -f	geojson -u who_alive
	$(PYTHON) minos/validation/format_spatial_output.py -s output/childUplift -y $(AGG_YEAR) -d output/childUplift -m nanmean -v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/validation/sf12_difference_map.R -f output/baseline/nanmean_SF_12_$(AGG_YEAR).geojson -g output/childUplift/nanmean_SF_12_$(AGG_YEAR).geojson -d plots/baseline_vs_all_25_uplift_difference_map.pdf -m $(AGG_LOCATION) -v SF_12

aggregate_baseline_poverty_uplift_map:
	$(PYTHON) minos/validation/format_spatial_output.py -s output/baseline -y $(AGG_YEAR) -d output/baseline -m nanmean -v SF_12 -f	geojson -u who_alive
	$(PYTHON) minos/validation/format_spatial_output.py -s output/povertyUplift -y $(AGG_YEAR) -d output/povertyUplift -m	nanmean	-v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/validation/sf12_difference_map.R -f output/baseline/nanmean_SF_12_$(AGG_YEAR).geojson -g output/povertyUplift/nanmean_SF_12_$(AGG_YEAR).geojson -d plots/baseline_vs_poverty_25_uplift_difference_map.pdf -m $(AGG_LOCATION) -v SF_12

map_all: aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map aggregate_baseline_poverty_uplift_map


###
## Cleaning
.PHONY: clean_out clean_logs clean_data clean_all

clean_all: ### Remove output, log files, generated data files and transition models
clean_all: clean_data clean_transitions clean_logs

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

clean_logs: # remove all slurm minos logs.
clean_logs: rm -rf logs/*
clean_logs: #TODO add one for arc4 logs too. 
