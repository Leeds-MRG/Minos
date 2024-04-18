# Directories and paths
export ROOT=$(CURDIR)
USSOURCEDIR = $(CURDIR)/../UKDA-6614-stata/stata/stata13_se/
SPATIALSOURCEDIR = $(CURDIR)/../US_spatial_lookup/
DATADIR = $(CURDIR)/data
RAWDATA = $(DATADIR)/raw_US
ADJRAWDATA = $(DATADIR)/adj_raw_US
CORRECTDATA = $(DATADIR)/corrected_US
COMPOSITEDATA = $(DATADIR)/composite_US
COMPLETEDATA = $(DATADIR)/complete_US
INFLATEDDATA = $(DATADIR)/inflated_US
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
GLASGOWSCALEDDATA = $(DATADIR)/scaled_glasgow_US
TESTING = $(SOURCEDIR)/testing
SCOTLANDSCALEDDATA = $(DATADIR)/scaled_scotland_US
GLASGOWSCALEDDATA = $(DATADIR)/scaled_glasgow_US
UKSCALEDDATA = $(DATADIR)/scaled_uk_US
TESTING = $(SOURCEDIR)/testing

# Executables
PYTHON = python
RSCRIPT = Rscript

# This script will run through the entire setup target for Minos, for the purpose of submitting this as a job for
# arc.


## STEPS:

# Raw data
echo "Collating raw data..."
$(PYTHON) $(DATAGEN)/US_format_raw.py --source_dir $(USSOURCEDIR)

# Impute Missing
echo "Imputing missing data..."
$(PYTHON) $(DATAGEN)/US_missing_main.py

# Create Composite Variables
echo "Generating composite variables..."
$(PYTHON) $(DATAGEN)/generate_composite_vars.py

# Run Complete Case
echo "Running Complete Case..."
$(PYTHON) $(DATAGEN)/US_complete_case.py

# Create Stock Population (Final_US)
echo "Creating stock population..."
$(PYTHON) $(DATAGEN)/generate_stock_pop.py



# Generate Transition Models
echo "Running transition models..."
mkdir -p $(TRANSITION_DATA)
$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --default
$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_longitudinal_transitions.R --default



# Create Replenishing Population
echo "Generating replenishing population..."
$(PYTHON) $(DATAGEN)/generate_repl_pop.py


echo "All steps complete!"