#####################################
### Data Generation
#####################################

data: ### Run all four levels of data generation from raw Understanding Society data to imputed data in the correct
###	format with composite variables generated
data: raw_data adj_raw_data corrected_data composite_data complete_data final_data

raw_data: ### Generate starting data in the correct format from raw Understanding Society data
raw_data: $(RAWDATA)/2020_US_cohort.csv

adj_raw_data: ### Generate adjusted raw data, currently only simulates a council tax value
adj_raw_data: $(ADJRAWDATA)/2020_US_cohort.csv

corrected_data: ### Run a number of imputation procedures on the raw data to produce corrected data
corrected_data: $(CORRECTDATA)/2020_US_cohort.csv

composite_data: ### Generate composite variables
composite_data: $(COMPOSITEDATA)/2020_US_cohort.csv

complete_data: ### Generate a complete version of the data, after running complete case correction
complete_data: $(COMPLETEDATA)/2020_US_cohort.csv

final_data: ### Produce the final version of the data (including replenishing population for 2018-2070), after reweighting both the stock and replenishing input_populations
final_data: $(FINALDATA)/2020_US_cohort.csv

replenishing_data: ### Produce the replenishing population (MORE NEEDED HERE).
replenishing_data:  $(DATADIR)/replenishing/replenishing_pop_2019-2070.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds

scot_replenishing: $(DATADIR)/replenishing/scotland/replenishing_pop_2019-2070.csv $(SCOTDATA)/2019_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds

spatial_data: ### Attach Chris' spatially disaggregated dataset and extract all records for Sheffield, to generate a
### version of the final data to be used in spatial analyses (of Sheffield only)
spatial_data: $(SPATIALDATA)/2020_US_cohort.csv

scot_data: $(SCOTDATA)/2020_US_cohort.csv

cv_data: $(FINALDATA)/cross_validation/batch5/2020_US_cohort.csv

cv_replenishing: $(DATADIR)/replenishing/cross_validation/replenishing_pop_2019-2070.csv

#####################################
# Input Populations
#####################################

$(RAWDATA)/2020_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_format_raw.py --source_dir $(USSOURCEDIR)

$(ADJRAWDATA)/2020_US_cohort.csv: $(RAWDATA)/2020_US_cohort.csv $(DATAGEN)/fake_council_tax.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/fake_council_tax.py

$(CORRECTDATA)/2020_US_cohort.csv: $(RAWDATA)/2020_US_cohort.csv $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/US_missing_deterministic.py $(DATAGEN)/US_missing_LOCF.py $(DATAGEN)/US_missing_description.py $(DATAGEN)/US_missing_data_correction.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_missing_main.py

$(COMPOSITEDATA)/2020_US_cohort.csv: $(RAWDATA)/2020_US_cohort.csv $(CORRECTDATA)/2020_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_composite_vars.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_composite_vars.py

$(COMPLETEDATA)/2020_US_cohort.csv: $(RAWDATA)/2020_US_cohort.csv $(CORRECTDATA)/2020_US_cohort.csv $(COMPOSITEDATA)/2020_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/US_complete_case.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_complete_case.py

$(FINALDATA)/2020_US_cohort.csv: $(RAWDATA)/2020_US_cohort.csv $(CORRECTDATA)/2020_US_cohort.csv $(COMPOSITEDATA)/2020_US_cohort.csv $(COMPLETEDATA)/2020_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_stock_pop.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_stock_pop.py

$(DATADIR)/replenishing/replenishing_pop_2019-2070.csv: $(RAWDATA)/2020_US_cohort.csv $(CORRECTDATA)/2020_US_cohort.csv $(COMPOSITEDATA)/2020_US_cohort.csv $(COMPLETEDATA)/2020_US_cohort.csv $(FINALDATA)/2020_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py

$(DATADIR)/replenishing/scotland/replenishing_pop_2019-2070.csv: $(SCOTDATA)/2020_US_cohort.csv $(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --scotland

$(SPATIALDATA)/2020_US_cohort.csv: $(RAWDATA)/2020_US_cohort.csv $(CORRECTDATA)/2020_US_cohort.csv $(COMPOSITEDATA)/2020_US_cohort.csv $(COMPLETEDATA)/2020_US_cohort.csv $(FINALDATA)/2020_US_cohort.csv $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(FINALDATA)/2020_US_cohort.csv) $(SPATIALSOURCEDIR)/ADULT_population_GB_2018.csv
	$(PYTHON) $(DATAGEN)/US_generate_spatial_component.py --source_dir $(SPATIALSOURCEDIR)

$(SCOTDATA)/2020_US_cohort.csv: $(FINALDATA)/2020_US_cohort.csv
	$(PYTHON) $(DATAGEN)/US_scotland_subsetting.py

$(FINALDATA)/cross_validation/batch5/2020_US_cohort.csv: $(COMPLETEDATA)/2020_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_stock_pop.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_stock_pop.py --cross_validation

$(DATADIR)/replenishing/cross_validation/replenishing_pop_2019-2070.csv: $(FINALDATA)/cross_validation/batch5/2020_US_cohort.csv $(TRANSITION_DATA)/cross_validation/version5/education_state/nnet/education_state_2018_2019.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --cross_validation
