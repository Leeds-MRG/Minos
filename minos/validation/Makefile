
#####################################
# Post-hoc aggregation of multiple MINOS runs on bash terminal.
#####################################

AGGREGATE_METHOD = nanmean
AGGREGATE_VARIABLE = SF_12
REF_LEVEL = Baseline
DIRECTORIES = baseline,hhIncomeChildUplift,livingWageIntervention,energyDownlift
DIRECTORY_TAGS = "Baseline,£25 All Child Uplift,Living Wage,Energy Downlift"
SUBSET_FUNCTIONS = "who_alive,who_alive,who_alive,who_alive"

#TODO: Parameterise this so we can run `make scot_all_lineplots` and it sets the $(MODE) var and runs all lineplots with it
scot_all_lineplots: MODE=scotland_mode
scot_all_lineplots: ALIVE=who_scottish
scot_all_lineplots: BOOSTED=who_scottish_boosted
scot_all_lineplots: LIVING_WAGE=who_scottish_below_living_wage
scot_all_lineplots: POVERTY=who_scottish_below_poverty_line_and_kids
scot_all_lineplots: CHILD=who_scottish_and_kids
scot_all_lineplots: all_lineplots

default_all_lineplots: MODE=default_config
default_all_lineplots: ALIVE=who_alive
default_all_lineplots: BOOSTED=who_boosted
default_all_lineplots: LIVING_WAGE=who_below_living_wage
default_all_lineplots: POVERTY=who_below_poverty_line_and_kids
default_all_lineplots: CHILD=who_kids
default_all_lineplots: all_lineplots

all_lineplots: aggregate_minos_output aggregate_minos_output_treated aggregate_minos_output_living_wage aggregate_minos_output_all_child_uplift aggregate_minos_output_poverty_child_uplift aggregate_minos_output_energy

# Set the output directory based on
OUTPUT_DIR = $(/DATAOUT)$(MODE)

aggregate_minos_output:
	# See file for tag meanings.
	# aggregate files for baseline, all child uplift, and poverty line uplift.
	$(PYTHON) minos/validation/aggregate_minos_output.py -o $(OUTPUT_DIR) -d $(DIRECTORIES) -t $(DIRECTORY_TAGS) -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f $(SUBSET_FUNCTIONS)
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -o $(OUTPUT_DIR) -s $(DIRECTORIES) -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -o $(OUTPUT_DIR) -s $(DIRECTORIES) -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD)

aggregate_minos_output_treated:
	# See file for tag meanings.
	# aggregate files for baseline, all child uplift, and poverty line uplift.
	$(PYTHON) minos/validation/aggregate_minos_output.py -o $(OUTPUT_DIR) -d $(DIRECTORIES) -t $(DIRECTORY_TAGS) -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f $(ALIVE),$(BOOSTED),$(BOOSTED),$(BOOSTED)
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -o $(OUTPUT_DIR) -s $(DIRECTORIES) -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -o $(OUTPUT_DIR) -s $(DIRECTORIES) -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "treated"

aggregate_minos_output_living_wage:
	# custom baseline for living wage only.
	$(PYTHON) minos/validation/aggregate_minos_output.py -o $(OUTPUT_DIR) -d baseline,livingWageIntervention -t "Baseline,Living Wage Intervention" -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f $(LIVING_WAGE),$(BOOSTED)
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -o $(OUTPUT_DIR) -s baseline,livingWageIntervention -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -o $(OUTPUT_DIR) -s baseline,livingWageIntervention -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "living_wage_treated"

aggregate_minos_output_poverty_child_uplift:
	# custom baseline for living wage only.
	$(PYTHON) minos/validation/aggregate_minos_output.py -o $(OUTPUT_DIR) -d baseline,hhIncomePovertyLineChildUplift -t "Baseline,Poverty Line Uplift" -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f $(POVERTY),$(BOOSTED)
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -o $(OUTPUT_DIR) -s baseline,hhIncomePovertyLineChildUplift -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -o $(OUTPUT_DIR) -s baseline,hhIncomePovertyLineChildUplift -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "poverty_line_child_uplift"

aggregate_minos_output_all_child_uplift:
	# custom baseline for living wage only.
	$(PYTHON) minos/validation/aggregate_minos_output.py -o $(OUTPUT_DIR) -d baseline,hhIncomeChildUplift -t "Baseline,All Children Uplift" -m $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f $(CHILD),$(BOOSTED)
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -o $(OUTPUT_DIR) -s baseline,hhIncomeChildUplift -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -m $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -o $(OUTPUT_DIR) -s baseline,hhIncomeChildUplift -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -m $(AGGREGATE_METHOD) -p "all_child_uplift"

aggregate_minos_output_energy: MODE="scotland_mode"
aggregate_minos_output_energy:
	# custom baseline for living wage only.
	$(PYTHON) minos/validation/aggregate_minos_output.py -m $(MODE) -d baseline,energyDownlift -t "Baseline,Energy Downlift" -a $(AGGREGATE_METHOD) -v $(AGGREGATE_VARIABLE) -f $(ALIVE),$(BOOSTED)
	# stack aggregated files into one long array.
	$(PYTHON) minos/validation/aggregate_long_stack.py -m $(MODE) -s baseline,energyDownlift -r $(REF_LEVEL) -v $(AGGREGATE_VARIABLE) -a $(AGGREGATE_METHOD)
	# make line plot.
	$(PYTHON) minos/validation/aggregate_lineplot.py -m $(MODE) -s baseline,energyDownlift -v $(AGGREGATE_VARIABLE) -d $(PLOTDIR) -a $(AGGREGATE_METHOD) -p "energy_downlift"

all_lineplots: aggregate_minos_output aggregate_minos_output_treated aggregate_minos_output_living_wage aggregate_minos_output_all_child_uplift aggregate_minos_output_poverty_child_uplift aggregate_minos_output_energy
all_treated_lineplots: aggregate_minos_output_living_wage aggregate_minos_output_poverty_child_uplift aggregate_minos_output_all_child_uplift aggregate_minos_output_energy

####################################################################################################################################################
# Mapping multiple MINOS outputs into super outputs (LSOA/data zones) over Glasgow, Sheffield, Manchester, and Scotland regions.
####################################################################################################################################################

#TODO: Parameterise this as above for the lineplots. This var can be set by a target
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
AGG_LOCATION = scotland # or manchester/scotland/sheffield
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

