# Directories and paths
export ROOT=$(CURDIR)
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
	@sed -i 's/except (IndexError, TypeError)/except (IndexError, TypeError, KeyError)/' /opt/conda/envs/minos/lib/python3.8/site-packages/vivarium/framework/randomness.py


## Test

testRun:
	$(PYTHON) scripts/run_in_console.py -c $(CONFIG)/controlConfig.yaml --location E08000032 --input_data_dir $(DATADIR) --persistent_data_dir $(PERSISTDATA) --output_dir $(DATAOUT)


## Data Generation
# Combined Rules

data: raw_data corrected_data composite_data

raw_data: $(RAWDATA)/2018_US_cohort.csv

corrected_data: $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv

composite_data: $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv $(COMPOSITEDATA)/2018_US_cohort.csv

# Targets

$(RAWDATA)/2018_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_format_raw.py

$(CORRECTDATA)/2018_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/US_missing_deterministic.py $(DATAGEN)/US_missing_LOCF.py $(DATAGEN)/US_missing_description.py $(DATAGEN)/US_missing_data_correction.py $(DATAGEN)/US_complete_case.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_missing_main.py

$(COMPOSITEDATA)/2018_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/generate_composite_vars.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_composite_vars.py

## Cleaning
.PHONY: clean clean_out

clean: clean_out

clean_out:
	rm -rf output/*