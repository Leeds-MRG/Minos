#####################################
### Data Generation
#####################################

data: ### Run all four levels of data generation from raw Understanding Society data to imputed data in the correct
###	format with composite variables generated
data: raw_data adj_raw_data corrected_data composite_data complete_data final_data

synthetic_glasgow_data: data glasgow_scaled_data

synthetic_scotland_data: data scotland_scaled_data synthetic_scotland_repl

synthetic_uk_data: data uk_scaled_data synthetic_uk_repl

synthetic_manchester_data: data manchester_scaled_data synthetic_manchester_repl


raw_data: ### Generate starting data in the correct format from raw Understanding Society data
raw_data: $(RAWDATA)/2021_US_cohort.csv

corrected_data: ### Run a number of imputation procedures on the raw data to produce corrected data
corrected_data: $(CORRECTDATA)/2021_US_cohort.csv

composite_data: ### Generate composite variables
composite_data: $(COMPOSITEDATA)/2021_US_cohort.csv

complete_data: ### Generate a complete version of the data, after running complete case correction
complete_data: $(COMPLETEDATA)/2021_US_cohort.csv

final_data: ### Produce the final version of the data (including replenishing population for 2018-2070), after reweighting both the stock and replenishing input_populations
final_data: $(FINALDATA)/2021_US_cohort.csv

inflated_data: ### Inflate the data to account for survey weights, with records duplicated (weight * 100) times
inflated_data: $(INFLATEDDATA)/2021_US_cohort.csv

inflated_repl: ### Replenishing population generated from inflated data.
inflated_repl: $(DATADIR)/replenishing/inflated/replenishing_pop_2015-2070.csv

replenishing_data: ### Produce the replenishing population (MORE NEEDED HERE).
replenishing_data:  $(DATADIR)/replenishing/replenishing_pop_2015-2070.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2020_2021.rds

scot_replenishing: $(DATADIR)/replenishing/scotland/replenishing_pop_2015-2070.csv $(SCOTDATA)/2019_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2020_2021.rds

spatial_data: ### Attach Chris' spatially disaggregated dataset and extract all records for Sheffield, to generate a
### version of the final data to be used in spatial analyses (of Sheffield only)
spatial_data: $(SPATIALDATA)/2021_US_cohort.csv

scot_data: $(SCOTDATA)/2021_US_cohort.csv

cv_data: $(FINALDATA)/cross_validation/batch5/2021_US_cohort.csv

cv_replenishing: $(DATADIR)/replenishing/cross_validation/replenishing_pop_2015-2070.csv

# creating spatial populations from WS3 data

glasgow_scaled_data: $(GLASGOWSCALEDDATA)/2020_US_cohort.csv

synthetic_glasgow_repl: $(DATADIR)/replenishing/glasgow_scaled/replenishing_pop_2015-2070.csv

scotland_scaled_data : $(SCOTLANDSCALEDDATA)/2020_US_cohort.csv

manchester_scaled_data : $(MANCHESTERSCALEDDATA)/2020_US_cohort.csv

synthetic_scotland_repl: $(DATADIR)/replenishing/scotland_scaled/replenishing_pop_2015-2070.csv

uk_scaled_data: $(UKSCALEDDATA)/2020_US_cohort.csv

synthetic_uk_repl: $(DATADIR)/replenishing/uk_scaled/replenishing_pop_2015-2070.csv

synthetic_manchester_repl: $(DATADIR)/replenishing/manchester_scaled/replenishing_pop_2015-2070.csv

#sheffield_scaled_data goes here.

#####################################
# Input Populations
#####################################

$(RAWDATA)/2021_US_cohort.csv: $(DATAGEN)/US_format_raw.py $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_format_raw.py --source_dir $(USSOURCEDIR)

$(CORRECTDATA)/2021_US_cohort.csv: $(RAWDATA)/2021_US_cohort.csv $(DATAGEN)/US_missing_main.py $(DATAGEN)/US_utils.py $(DATAGEN)/US_missing_deterministic.py $(DATAGEN)/US_missing_LOCF.py $(DATAGEN)/US_missing_description.py $(DATAGEN)/US_missing_data_correction.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_missing_main.py

$(COMPOSITEDATA)/2021_US_cohort.csv: $(RAWDATA)/2021_US_cohort.csv $(CORRECTDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_composite_vars.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_composite_vars.py

$(COMPLETEDATA)/2021_US_cohort.csv: $(RAWDATA)/2021_US_cohort.csv $(CORRECTDATA)/2021_US_cohort.csv $(COMPOSITEDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/US_complete_case.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/US_complete_case.py

$(FINALDATA)/2021_US_cohort.csv: $(RAWDATA)/2021_US_cohort.csv $(CORRECTDATA)/2021_US_cohort.csv $(COMPOSITEDATA)/2021_US_cohort.csv $(COMPLETEDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_stock_pop.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_stock_pop.py

$(INFLATEDDATA)/2021_US_cohort.csv: $(FINALDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/weight_inflate_pop.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/weight_inflate_pop.py

$(DATADIR)/replenishing/replenishing_pop_2015-2070.csv: $(FINALDATA)/2021_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2020_2021.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py

$(DATADIR)/replenishing/inflated/replenishing_pop_2015-2070.csv: $(INFLATEDDATA)/2021_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2020_2021.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --inflated

$(DATADIR)/replenishing/scotland/replenishing_pop_2015-2070.csv: $(SCOTDATA)/2021_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2020_2021.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --scotland

$(SPATIALDATA)/2021_US_cohort.csv: $(RAWDATA)/2021_US_cohort.csv $(CORRECTDATA)/2021_US_cohort.csv $(COMPOSITEDATA)/2021_US_cohort.csv $(COMPLETEDATA)/2021_US_cohort.csv $(FINALDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py $(PERSISTJSON)/*.json $(FINALDATA)/2021_US_cohort.csv) $(SPATIALSOURCEDIR)/ADULT_population_GB_2018.csv
	$(PYTHON) $(DATAGEN)/US_generate_spatial_component.py --source_dir $(SPATIALSOURCEDIR)

$(SCOTDATA)/2021_US_cohort.csv: $(FINALDATA)/2021_US_cohort.csv
	$(PYTHON) $(DATAGEN)/US_scotland_subsetting.py

$(FINALDATA)/cross_validation/batch5/2021_US_cohort.csv: $(COMPLETEDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/generate_stock_pop.py $(PERSISTJSON)/*.json
	$(PYTHON) $(DATAGEN)/generate_stock_pop.py --cross_validation

$(DATADIR)/replenishing/cross_validation/replenishing_pop_2015-2070.csv: $(FINALDATA)/cross_validation/batch5/2021_US_cohort.csv $(TRANSITION_DATA)/cross_validation/version5/education_state/nnet/education_state_2020_2021.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --cross_validation

### Synthetic Populations

# synthetic input for glasgow with spatial component.
$(GLASGOWSCALEDDATA)/2020_US_cohort.csv: $(FINALDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/US_household_upscaling.py
	$(PYTHON) $(DATAGEN)/US_household_upscaling.py -r 'glasgow' -p 100

$(DATADIR)/replenishing/glasgow_scaled/replenishing_pop_2015-2070.csv: $(GLASGOWSCALEDDATA)/2020_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2020_2021.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --region 'glasgow'

# synthetic input for glasgow with spatial component.
$(SCOTLANDSCALEDDATA)/2020_US_cohort.csv: $(FINALDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/US_household_upscaling.py
	$(PYTHON) $(DATAGEN)/US_household_upscaling.py -r 'scotland' -p 10

$(DATADIR)/replenishing/scotland_scaled/replenishing_pop_2015-2070.csv: $(SCOTLANDSCALEDDATA)/2020_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2020_2021.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --region 'scotland'

# synthetic input for UK with spatial component.
$(UKSCALEDDATA)/2020_US_cohort.csv: $(FINALDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py $(DATAGEN)/US_household_upscaling.py
	$(PYTHON) $(DATAGEN)/US_household_upscaling.py -r 'uk' -p 1

$(DATADIR)/replenishing/uk_scaled/replenishing_pop_2015-2070.csv: $(UKSCALEDDATA)/2020_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2020_2021.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --region 'uk'

# synthetic input for manchester with spatial component.
$(MANCHESTERSCALEDDATA)/2020_US_cohort.csv: $(FINALDATA)/2021_US_cohort.csv $(DATAGEN)/US_utils.py
	$(PYTHON) $(DATAGEN)/US_household_upscaling.py -r 'manchester' -p 20

$(DATADIR)/replenishing/manchester_scaled/replenishing_pop_2015-2070.csv: $(MANCHESTERSCALEDDATA)/2020_US_cohort.csv $(TRANSITION_DATA)/education_state/nnet/education_state_2020_2021.rds $(DATAGEN)/US_utils.py $(DATAGEN)/generate_repl_pop.py $(PERSISTJSON)/*.json $(MODULES)/r_utils.py
	$(PYTHON) $(DATAGEN)/generate_repl_pop.py --region 'manchester'
