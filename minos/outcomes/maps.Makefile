####################################################################################################################################################
# Mapping multiple MINOS outputs into super outputs (LSOA/data zones) over Glasgow, Sheffield, Manchester, and Scotland regions.
####################################################################################################################################################

#TODO: Parameterise this as above for the lineplots. This var can be set by a target
#TODO: needs a bash fuction similar to make_lineplot.sh
#TODO: More involved as some variable names are more complex such as paths but not too difficult.

DEFAULT_OUTPUT_SUBDIRECTORY = default_config
INTERVENTION1 = baseline
INTERVENTION2 = povertyUplift
OUT_BASELINE = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/baseline
OUT_HHINCOMECHILDUP = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/hhIncomeChildUplift
OUT_ENERGYDOWNLIFT = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/energyDownlift
OUT_ENERGYDOWNLIFTNOSUPPORT = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/energyDownliftNoSupport
OUT_LIVINGWAGEINT = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/livingWageIntervention
OUT_POVERTYUP = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/hhIncomePovertyLineChildUplift

SPATIAL_DIRECTORY1 = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/$(INTERVENTION1)# first geojson for comparison in diff plot.
SPATIAL_DIRECTORY2 = output/$(DEFAULT_OUTPUT_SUBDIRECTORY)/$(INTERVENTION2)# second geojson for comparison in aggregate_two_and_diff
AGG_METHOD = nanmean# what method to aggregate with.
#AGG_VARIABLE = SF_12# what variable to aggregate.
AGG_YEAR = 2025# what year to map in data.
AGG_LOCATION=glasgow # or manchester/scotland/sheffield
SAVE_FILE1 = $(SPATIAL_DIRECTORY1)/$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR).geojson # data source from aggregation. Need to automate these file paths somehow.
SAVE_PLOT1 = $(SPATIAL_DIRECTORY1)/$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR) # where to save plot for aggregate_lsoas_and_map
SAVE_FILE2 = $(SPATIAL_DIRECTORY2)/$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR).geojson # data source for aggregation of second minos run. Used when comparing two interventions in aggreate_two_and_map_diff
SAVE_PLOT2 = $(SPATIAL_DIRECTORY1)/$(INTERVENTION1)_vs_$(INTERVENTION2)_$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR) # pdf file name for aggregate_two_and_diff. saves in first specified file.

aggregate_and_map:
	# aggregate minos outputs into LSOAs.
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(SPATIAL_DIRECTORY1) -y $(AGG_YEAR) -d $(SPATIAL_DIRECTORY1) -m $(AGG_METHOD) -v $(AGG_VAR) -f geojson
	# Map data now aggregated.
	$(RSCRIPT) minos/outcomes/sf12_single_map.R -f $(SAVE_FILE1) -d $(SAVE_PLOT1) -m $(AGG_LOCATION) -v $(AGG_VARIABLE)

aggregate_two_and_map_diff:
	# aggregate minos outputs into LSOAs.
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(SPATIAL_DIRECTORY1) -y $(AGG_YEAR) -d $(SPATIAL_DIRECTORY1) -m $(AGG_METHOD) -v $(AGG_VAR) -f geojson
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(SPATIAL_DIRECTORY2) -y $(AGG_YEAR) -d $(SPATIAL_DIRECTORY2) -m $(AGG_METHOD) -v $(AGG_VAR) -f geojson
	# map LSOAs.
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -f $(SAVE_FILE2) -g $(SAVE_FILE1) -d $(SAVE_PLOT2) -m $(AGG_LOCATION) -v $(AGG_VARIABLE)

aggregate_baseline_map:
	# aggregate minos outputs into LSOAs.
	$(PYTHON) minos/outcomes/format_spatial_output.py -m $(OUTPUT_SUBDIR) -i baseline -y $(AGG_YEAR) -r $(REGION) -s who_alive -p $(SYNTH) -v $(AGG_VAR)
	# Map data now aggregated.
	$(RSCRIPT) minos/outcomes/sf12_single_map.R -m $(OUTPUT_SUBDIR) -b baseline -r $(REGION) -y $(AGG_YEAR) -s $(SYNTH) -v $(AGG_VAR)

baseline_map_test: AGG_VAR=SF_12
baseline_map_test: OUTPUT_SUBDIR=default_config
baseline_map_test: REGION=glasgow
baseline_map_test: SYNTH=false
baseline_map_test: aggregate_baseline_map

aggregate_baseline_energy_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -m $(OUTPUT_SUBDIR) -i baseline -y $(AGG_YEAR) -r $(REGION) -s who_uses_energy -p $(SYNTH) -v $(AGG_VAR)
	$(PYTHON) minos/outcomes/format_spatial_output.py -m $(OUTPUT_SUBDIR) -i energyDownlift -y $(AGG_YEAR) -r $(REGION) -s who_boosted -p $(SYNTH) -v $(AGG_VAR)
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m $(OUTPUT_SUBDIR) -b baseline -i energyDownlift -r $(REGION) -y $(AGG_YEAR) -s $(SYNTH) -v $(AGG_VAR)

aggregate_baseline_living_wage_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -m $(OUTPUT_SUBDIR) -i baseline -y $(AGG_YEAR) -r $(REGION) -s who_below_living_wage -p $(SYNTH) -v $(AGG_VAR)
	$(PYTHON) minos/outcomes/format_spatial_output.py -m $(OUTPUT_SUBDIR) -i livingWageIntervention -y $(AGG_YEAR) -r $(REGION) -s who_boosted -p $(SYNTH) -v $(AGG_VAR)
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m $(OUTPUT_SUBDIR) -b baseline -i livingWageIntervention -r $(REGION) -y $(AGG_YEAR) -s $(SYNTH) -v $(AGG_VAR)

aggregate_baseline_all_uplift_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -m $(OUTPUT_SUBDIR) -i baseline -y $(AGG_YEAR) -r $(REGION) -s who_kids -p $(SYNTH) -v $(AGG_VAR)
	$(PYTHON) minos/outcomes/format_spatial_output.py -m $(OUTPUT_SUBDIR) -i hhIncomeChildUplift -y $(AGG_YEAR) -r $(REGION) -s who_boosted -p $(SYNTH) -v $(AGG_VAR)
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m $(OUTPUT_SUBDIR) -b baseline -i hhIncomeChildUplift -r $(REGION) -y $(AGG_YEAR) -s $(SYNTH) -v $(AGG_VAR)

aggregate_baseline_poverty_uplift_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -m $(OUTPUT_SUBDIR) -i baseline -y $(AGG_YEAR) -r $(REGION) -s who_below_poverty_line_and_kids -p $(SYNTH) -v $(AGG_VAR)
	$(PYTHON) minos/outcomes/format_spatial_output.py -m $(OUTPUT_SUBDIR) -i hhIncomePovertyLineChildUplift -y $(AGG_YEAR) -r $(REGION) -s who_boosted -p $(SYNTH) -v $(AGG_VAR)
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m $(OUTPUT_SUBDIR) -b baseline -i hhIncomePovertyLineChildUplift -r $(REGION) -y $(AGG_YEAR) -s $(SYNTH) -v $(AGG_VAR)

epcg_ebss_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "EBSS" -y 2025 -m "glasgow_scaled" -s who_boosted -p true -r "glasgow"
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "EPCG" -y 2025 -m "glasgow_scaled" -s who_boosted -p true -r "glasgow"
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m "glasgow_scaled" -b "EPCG" -i "EBSS" -r "glasgow" -y $(AGG_YEAR) -y 2025 -s $(SYNTH) -v $(AGG_VAR)

aggregate_all_energy_interventions:
	python3 minos/outcomes/make_lineplots_macros.py "all_energy_lineplots"

# Combined target for running all interventions at once
all_intervention_maps: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map aggregate_baseline_poverty_uplift_map

#### NOTES ####

## TARGET YEAR
# Target year for mapping is set to 2025 as default. This can be changed above on line 191 (AGG_YEAR), or can
# be specified for an individual run by adding a line to the make targets below. For example to change the target year to
# 2030, just add the following line to the make target
# map_all_MCS: AGG_YEAR=2030

## REGION
# The target region for mapping is set to Glasgow as default (on line 192).
# Other regions can also be specified by setting the AGG_LOCATION parameter in the make target
# Regions currently supported are Scotland, Glasgow, Sheffield, and Manchester.
# To switch to one of these regions other than Glasgow, add a line to the make target as so:
# map_all_MCS: AGG_LOCATION=sheffield
# NOTE:
# If the synth parameter is set to True (explained below), meaning a synthetic spatial population has been used
# as input population, the AGG_LOCATION parameter should match that region or some weird things might happen.

## SYNTH
# The synth parameter should be set to true or false (default is false), and indicates whether we are mapping the output
# of a simulation using regular US data or synthetic data of some kind. If using results from a synthetic data run, it
# is important that this parameter is set correctly to true as it will then use location data from the file itself,
# instead of adding it afterwards.

# The current targets are all combined targets, producing maps for all interventions in one go. If you want to produce
# just one map, say for example the living wage intervention, you will need to write a make target for just that
# intervention, setting the parameters as seen in the combined targets below. For example:
#
# map_livingWage_MCS: OUT_SUBDIRECTORY=default_config
# map_livingWage_MCS: AGG_VARIABLE=SF_12
# map_livingWage_MCS: AGG_YEAR=2026
# map_livingWage_MCS: AGG_LOCATION=manchester
# map_livingWage_MCS: aggregate_baseline_living_wage_map
#
# This would generate a map of change in SF_12 in 2026 for manchester, for only the living wage intervention.

### SF_12 Maps

## SF_12_MCS

# Currently only SF_12_MCS is implemented, but SF_12_PCS is coming soon!
map_all_MCS: AGG_VAR=SF_12
map_all_MCS: OUTPUT_SUBDIR=default_config
map_all_MCS: REGION=glasgow
map_all_MCS: SYNTH=false
map_all_MCS: all_intervention_maps

map_concept_note_MCS: AGG_VAR=SF_12
map_concept_note_MCS: OUTPUT_SUBDIR=default_config
map_concept_note_MCS: REGION=glasgow
map_concept_note_MCS: SYNTH=false
map_concept_note_MCS: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map

### Equivalent Income

# This target will generate maps for
map_all_EI: AGG_VAR=equivalent_income
map_all_EI: OUTPUT_SUBDIR=SIPHER7
map_all_EI: REGION=glasgow
map_all_EI: SYNTH=false
map_all_EI: all_intervention_maps

map_all_EI_synthetic: AGG_VAR=equivalent_income
map_all_EI_synthetic: OUTPUT_SUBDIR=SIPHER7_glasgow
map_all_EI_synthetic: REGION=glasgow
map_all_EI_synthetic: SYNTH=true
map_all_EI_synthetic: all_intervention_maps

#######################################################################################################
# NEW MAPS (Mostly Scottish Child Payment)
#######################################################################################################

uc_baseline_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "baseline" -y 2025 -m "glasgow_scaled" -s who_universal_credit_and_kids -p true -r "glasgow"
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "25UniversalCredit" -y 2025 -m "glasgow_scaled" -s who_boosted -p true -r "glasgow"
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m "glasgow_scaled" -j "baseline" -i "25UniversalCredit" -r "glasgow" -d "plots/universal_credit_baseline_diff_map.pdf" -y 2025

priority_baseline_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "baseline" -y 2025 -m "glasgow_scaled" -s who_universal_credit_and_kids -p true -r "glasgow"
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "25Priority" -y 2025 -m "glasgow_scaled" -s who_boosted -p true -r "glasgow"
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m "glasgow_scaled" -j "baseline" -i "25Priority" -r "glasgow" -d "plots/priority_baseline_diff_map.pdf" -y 2025

25_UC_2025_glasgow_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "baseline" -y 2025 -m "scaled_scotland" -s who_universal_credit_and_kids -p true -r "glasgow" -v "SF_12"
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "25UniversalCredit" -y 2025 -m "scaled_scotland" -s who_universal_credit_and_kids -p true -r "glasgow" -v "SF_12"
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m "scaled_scotland" -b "baseline" -i "25UniversalCredit" -r "glasgow" -y 2025 -v "SF_12" -s true

25_UC_2025_edinburgh_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "baseline" -y 2025 -m "scaled_scotland" -s who_universal_credit_and_kids -p true -r "edinburgh" -v "SF_12"
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "25UniversalCredit" -y 2025 -m "scaled_scotland" -s who_universal_credit_and_kids -p true -r "edinburgh"  -v "SF_12"
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m "scaled_scotland" -b "baseline" -i "25UniversalCredit" -r "edinburgh" -y 2025 -v "SF_12" -s true

all_25_UC_scotland_maps: 25_UC_2025_glasgow_map 25_UC_2025_edinburgh_map

# experimental bash scripts.
main_maps:
	bash minos/outcomes/aggregated_maps.sh


map_all: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map aggregate_baseline_poverty_uplift_map
map_concept_note: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map