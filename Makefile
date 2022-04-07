# Directories and paths
export ROOT=$(CURDIR)
USSOURCEDIR = $(CURDIR)/../UKDA-6614-stata/stata/stata13_se/
DATADIR = $(CURDIR)/data
RAWDATA = $(DATADIR)/raw_US
CORRECTDATA = $(DATADIR)/corrected_US
COMPOSITEDATA = $(DATADIR)/composite_US
PERSISTDATA = $(CURDIR)/persistent_data
PERSISTJSON = $(PERSISTDATA)/JSON
SOURCEDIR = $(CURDIR)/minos
DATAGEN = $(SOURCEDIR)/data_generation
DATAOUT = $(CURDIR)/output
CONFIG = $(CURDIR)/config
TRANSITIONS = $(DATADIR)/transitions

# This path points to the python site-packages directory in the conda environment
SITEPACKAGES = $(shell python3 -c 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')

# Executables
PYTHON = python
RSCRIPT = Rscript

## Help
.PHONY: help

help:
	@echo "Tasks in \033[1;32mMinos\033[0m:"
	@cat Makefile

## Install
.PHONY: install

install:
	@echo "Installing requirements via pip"
	pip install -v -e .
	@echo "Replacing a line in vivarium.framework.randomness.py because it's broken."
	@sed -i 's/except (IndexError, TypeError)/except (IndexError, TypeError, KeyError)/' $(SITEPACKAGES)/vivarium/framework/randomness.py
	@echo "\nInstall complete!\n"


## Test
.PHONY: testRun

testRun: data transitions
	$(PYTHON) scripts/run.py -c $(CONFIG)/testConfig.yaml --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)


## Data Generation
# Combined Rules

data: raw_data corrected_data composite_data

raw_data: $(RAWDATA)/2019_US_cohort.csv

corrected_data: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv

composite_data: $(RAWDATA)/2019_US_cohort.csv $(CORRECTDATA)/2019_US_cohort.csv $(COMPOSITEDATA)/2019_US_cohort.csv

transitions: composite_data $(TRANSITIONS)/income.rds

# Input Populations

$(RAWDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_format_raw.py --source_dir $(USSOURCEDIR)

$(CORRECTDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/US_missing_deterministic.py $(DATAGEN)/US_missing_LOCF.py $(DATAGEN)/US_missing_description.py $(DATAGEN)/US_missing_data_correction.py $(DATAGEN)/US_complete_case.py $(PERSISTJSON)/*.json $(RAWDATA)/2018_US_cohort.csv
	$(PYTHON) $(DATAGEN)/US_missing_main.py

$(COMPOSITEDATA)/2019_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/generate_composite_vars.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv
	$(PYTHON) $(DATAGEN)/generate_composite_vars.py

# Transitions

$(TRANSITIONS)/income.rds: $(TRANSITIONS)/model_definitions.txt $(COMPOSITEDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/estimate_transition_models.r
	# Script needs 3 arguments (which are set as Makefile variables above, change there not here):
	# 1 - Minos root directory (i.e. $(ROOT))
	# 2 - Input data directory (i.e. data/composite or $(DATADIR))
	# 3 - Transition model directory (data/transitions or $(TRANSITIONS))
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transition_models.r --args $(DATADIR) $(TRANSITIONS)

## Cleaning
.PHONY: clean clean_out clean_logs clean_data clean_all

clean: clean_out clean_logs

clean_all: clean clean_data clean_transitions

clean_data:
	rm -f data/*/*.csv

clean_out:
	rm -rf output/*

clean_logs:
	rm -rf test.log

clean_transitions:
	rm -rf data/transitions/*.rds