# Directories and paths
export ROOT=$(CURDIR)
DATADIR = $(CURDIR)/data
RAWDATA = $(DATADIR)/raw_US
CORRECTDATA = $(DATADIR)/corrected_US
SOURCEDIR = $(CURDIR)/source
DATAGEN = $(SOURCEDIR)/data_generation

# Executables
PYTHON = python
RSCRIPT = Rscript



## Data Generation

data: $(RAWDATA)/2018_US_cohort.csv $(CORRECTDATA)/2018_US_cohort.csv

$(RAWDATA)/2018_US_cohort.csv: $(DATAGEN)/US_format_raw.py
	$(PYTHON) $(DATAGEN)/US_format_raw.py

$(CORRECTDATA)/2018_US_cohort.csv: $(DATAGEN)/US_missing_main.py
	$(PYTHON) $(DATAGEN)/US_missing_main.py
