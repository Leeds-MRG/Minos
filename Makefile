# Directories and paths
export ROOT=$(CURDIR)
DATADIR = $(CURDIR)/data
RAWDATA = $(DATADIR)/raw_US
CORRECTDATA = $(DATADIR)/corrected_US
PERSISTDATA = $(CURDIR)/persistent_data
PERSISTJSON = $(PERSISTDATA)/JSON
SOURCEDIR = $(CURDIR)/minos
DATAGEN = $(SOURCEDIR)/data_generation

# Executables
PYTHON = python
RSCRIPT = Rscript

## Help

help:
	@echo "Tasks in \033[1;32mMinos\033[0m:"
	@cat Makefile

## Data Generation

raw_data: $(RAWDATA)/2018_US_cohort.csv

corrected_data: $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv

$(RAWDATA)/2018_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/depression.json $(PERSISTJSON)/sexes.json $(PERSISTJSON)/education*.json $(PERSISTJSON)/ethnicity*.json $(PERSISTJSON)/labour_status*.json
	$(PYTHON) $(DATAGEN)/US_format_raw.py

$(CORRECTDATA)/2018_US_cohort.csv: $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py
	$(PYTHON) $(DATAGEN)/US_missing_main.py
