#TODO: Now that the makefile is split and in the same directory as its scripts, can we do relative paths?
#TODO: make bash functions for vulnerable subgroups in aggregated_lineplots.sh
#TODO make bash script for maps.
#TODO add bash script with 4 interventions (no poverty line).

##############################################################
# Post-hoc aggregation of multiple MINOS runs into lineplots #
##############################################################


all_initial_lineplots: all_child_lineplot poverty_line_lineplot living_wage_lineplot ebss_lineplot all_five_lineplot

aggregate_minos_output:
aggregate_minos_output:	DIRECTORIES = baseline,hhIncomeChildUplift,livingWageIntervention,energyDownlift
aggregate_minos_output:	DIRECTORY_TAGS = "Baseline,£25 All Child Uplift,Living Wage,Energy Downlift"
aggregate_minos_output:	SUBSET_FUNCTIONS = "who_alive,who_alive,who_alive,who_alive"
aggregate_minos_output:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(DIRECTORIES) $(DIRECTORY_TAGS) $(DIRECTORY_SUBSETS) "all"


aggregate_minos_output_treated: MODE=default_config
aggregate_minos_output_treated:	TREATED_DIRECTORIES = baseline,hhIncomeChildUplift,hhIncomePovertyLineChildUplift,livingWageIntervention,energyDownlift
aggregate_minos_output_treated:	TREATED_DIRECTORY_TAGS="Baseline,£25 All Child Uplift,£25 Poverty Line Child Uplift, Living Wage,Energy Crisis"
aggregate_minos_output_treated:	TREATED_DIRECTORY_SUBSETS = $(ALIVE),$(BOOSTED),$(BOOSTED),$(BOOSTED),$(BOOSTED)
aggregate_minos_output_treated:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "treated"


###########################
# Living Wage Lineplots ###
###########################

# Living Wage Intervention
living_wage_lineplot: MODE="default_config"
living_wage_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "living_wage"

##########################################
# Child Income Intervention Lineplots #
#######################################

# old interventions that are fixed £25 increase.
# All Children Uplift
all_child_lineplot: MODE="default_config"
all_child_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "all_child"

# Poverty Line Child Uplift
poverty_line_lineplot: MODE="default_config"
poverty_line_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py  $(MODE) "poverty_line_child"


# individual lineplots for new child interventions in increments up to £100

BOOSTED="who_boosted"
aggregate_all_child_uplifts: MODE="default_config"
aggregate_all_child_uplifts:
	bash minos/outcomes/make_lineplots_macros.sh $(MODE) "incremental_all_child"

aggregate_poverty_line_child_uplifts: MODE="default_config"
aggregate_poverty_line_child_uplifts:
	bash minos/outcomes/make_lineplots_macros.sh $(MODE) "incremental_relative_poverty"

aggregate_universal_credit_child_uplifts: MODE="default_config"
aggregate_universal_credit_child_uplifts:
	bash minos/outcomes/make_lineplots_macros.sh $(MODE) "incremental_universal_credit"

aggregate_priority_groups_child_uplifts: MODE="default_config"
aggregate_priority_groups_child_uplifts:
	bash minos/outcomes/make_lineplots_macros.sh $(MODE) "incremental_priority_groups"

aggregate_25_universal_credit: MODE="default_config"
aggregate_25_universal_credit:
	bash minos/outcomes/make_lineplots_macros.sh $(MODE) "25_universal_credit"

aggregate_25_relative_poverty: MODE="default_config"
aggregate_25_relative_poverty:
	bash minos/outcomes/make_lineplots_macros.sh "25_relative_poverty"

aggregate_25_all_children: MODE="default_config"
aggregate_25_all_children:
	bash minos/outcomes/make_lineplots_macros.sh $(MODE) "25_all"

#################################
# Custom subset for scotgov piece
#################################

aggregate_25_UC_vulnerable: MODE="scaled_glasgow"
aggregate_25_UC_vulnerable:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "25_UC_priority"

aggregate_50_UC_vulnerable: MODE="scaled_glasgow"
aggregate_50_UC_vulnerable:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "50_UC_priority"

aggregate_75_UC_vulnerable: MODE="scaled_glasgow"
aggregate_75_UC_vulnerable:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "75_UC_priority"

aggregate_100_UC_vulnerable: MODE="scaled_glasgow"
aggregate_100_UC_vulnerable:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "100_UC_priority"

all_uc_vuln: aggregate_25_UC_vulnerable aggregate_50_UC_vulnerable aggregate_75_UC_vulnerable aggregate_100_UC_vulnerable

########################################################
# SIMD decile lineplots for glasgow using spatial data #
########################################################


baseline_all_deciles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_baseline_all_deciles"

poverty_all_deciles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_poverty_all_deciles"

poverty_first_decile_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_poverty_first"

poverty_fifth_decile_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_poverty_fifth"

poverty_tenth_decile_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_poverty_tenth"

###############################
# energy crisis lineplots #####
###############################

# EBSS energy downlift.
ebss_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "ebss"

# do all the above together
all_five_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "all_five"

epcg_simd_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "epcg_simd_lineplot"

########################################################################
# need to add macros for these in make_lineplot_macros.sh. do later..  #
########################################################################

aggregate_combined_25_child_uplifts: MODE=default_config
aggregate_combined_25_child_uplifts: TREATED_DIRECTORIES = baseline,25UniversalCredit,25RelativePoverty,25All
aggregate_combined_25_child_uplifts: TREATED_DIRECTORY_TAGS="Baseline,£25 Universal Credit,£25 Relative Poverty,£25 All"
aggregate_combined_25_child_uplifts: TREATED_DIRECTORY_SUBSETS = "who_kids",$(BOOSTED),$(BOOSTED),$(BOOSTED)
aggregate_combined_25_child_uplifts:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "combined_25_child_uplifts"

aggregate_all_25_child_uplifts: aggregate_25_all_children aggregate_25_relative_poverty aggregate_25_universal_credit aggregate_combined_25_child_uplifts

aggregate_minos_output_living_wage:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,livingWageIntervention "Baseline,Living Wage Intervention" who_below_living_wage,who_boosted "living_wage_treated"

aggregate_minos_output_energy:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,energyDownlift,energyDownliftNoSupport "Baseline,Energy crisis with the EPCG,Energy crisis with no support" who_uses_energy,who_boosted,who_boosted "epcg"

all_decile_lineplots: baseline_all_deciles poverty_all_deciles poverty_fifth_decile_lineplot poverty_first_decile_lineplot poverty_tenth_decile_lineplot

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
AGG_VARIABLE = SF_12# what variable to aggregate.
AGG_YEAR = 2025# what year to map in data.
AGG_LOCATION = scotland # or manchester/scotland/sheffield
SAVE_FILE1 = $(SPATIAL_DIRECTORY1)/$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR).geojson # data source from aggregation. Need to automate these file paths somehow.
SAVE_PLOT1 = $(SPATIAL_DIRECTORY1)/$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR) # where to save plot for aggregate_lsoas_and_map
SAVE_FILE2 = $(SPATIAL_DIRECTORY2)/$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR).geojson # data source for aggregation of second minos run. Used when comparing two interventions in aggreate_two_and_map_diff
SAVE_PLOT2 = $(SPATIAL_DIRECTORY1)/$(INTERVENTION1)_vs_$(INTERVENTION2)_$(AGG_METHOD)_$(AGG_VARIABLE)_$(AGG_YEAR) # pdf file name for aggregate_two_and_diff. saves in first specified file.

aggregate_and_map:
	# aggregate minos outputs into LSOAs.
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(SPATIAL_DIRECTORY1) -y $(AGG_YEAR) -d $(SPATIAL_DIRECTORY1) -m $(AGG_METHOD) -v $(AGG_VARIABLE) -f geojson
	# Map data now aggregated.
	$(RSCRIPT) minos/outcomes/sf12_single_map.R -f $(SAVE_FILE1) -d $(SAVE_PLOT1) -m $(AGG_LOCATION) -v $(AGG_VARIABLE)

aggregate_two_and_map_diff:
	# aggregate minos outputs into LSOAs.
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(SPATIAL_DIRECTORY1) -y $(AGG_YEAR) -d $(SPATIAL_DIRECTORY1) -m $(AGG_METHOD) -v $(AGG_VARIABLE) -f geojson
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(SPATIAL_DIRECTORY2) -y $(AGG_YEAR) -d $(SPATIAL_DIRECTORY2) -m $(AGG_METHOD) -v $(AGG_VARIABLE) -f geojson
	# map LSOAs.
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -f $(SAVE_FILE2) -g $(SAVE_FILE1) -d $(SAVE_PLOT2) -m $(AGG_LOCATION) -v $(AGG_VARIABLE)

aggregate_baseline_map:
	# aggregate minos outputs into LSOAs.
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m $(AGG_METHOD) -v $(AGG_VARIABLE) -f geojson
	# Map data now aggregated.
	$(RSCRIPT) minos/outcomes/sf12_single_map.R -f $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson -d $(PLOTDIR)/baseline_map -m $(AGG_LOCATION) -v $(AGG_VARIABLE)

aggregate_baseline_energy_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m nanmean -v SF_12 -f geojson -u who_bottom_income_quintile
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(OUT_ENERGYDOWNLIFT) -y $(AGG_YEAR) -d $(OUT_ENERGYDOWNLIFT) -m nanmean -v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -f $(OUT_ENERGYDOWNLIFT)/nanmean_SF_12_$(AGG_YEAR).geojson -g $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson -d $(PLOTDIR)/baseline_vs_energy_difference_map -m $(AGG_LOCATION) -v SF_12

aggregate_baseline_living_wage_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m nanmean -v SF_12 -f	geojson -u who_below_living_wage
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(OUT_LIVINGWAGEINT) -y $(AGG_YEAR) -d $(OUT_LIVINGWAGEINT) -m	nanmean	-v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -f $(OUT_LIVINGWAGEINT)/nanmean_SF_12_$(AGG_YEAR).geojson -g $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson -d $(PLOTDIR)/baseline_vs_living_wage_difference_map -m $(AGG_LOCATION) -v SF_12

aggregate_baseline_all_uplift_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m nanmean -v SF_12 -f	geojson -u who_kids
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(OUT_HHINCOMECHILDUP) -y $(AGG_YEAR) -d $(OUT_HHINCOMECHILDUP) -m nanmean -v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -f $(OUT_HHINCOMECHILDUP)/nanmean_SF_12_$(AGG_YEAR).geojson -g $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson  -d $(PLOTDIR)/baseline_vs_all_25_uplift_difference_map -m $(AGG_LOCATION) -v SF_12

aggregate_baseline_poverty_uplift_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(OUT_BASELINE) -y $(AGG_YEAR) -d $(OUT_BASELINE) -m nanmean -v SF_12 -f	geojson -u who_below_poverty_line_and_kids
	$(PYTHON) minos/outcomes/format_spatial_output.py -s $(OUT_POVERTYUP) -y $(AGG_YEAR) -d $(OUT_POVERTYUP) -m	nanmean	-v SF_12 -f geojson -u who_boosted
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -f $(OUT_POVERTYUP)/nanmean_SF_12_$(AGG_YEAR).geojson -g $(OUT_BASELINE)/nanmean_SF_12_$(AGG_YEAR).geojson -d $(PLOTDIR)/baseline_vs_poverty_25_uplift_difference_map -m $(AGG_LOCATION) -v SF_12

epcg_ebss_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "EBSS" -y 2025 -m "glasgow_scaled" -s who_boosted -p true -r "glasgow"
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "EPCG" -y 2025 -m "glasgow_scaled" -s who_boosted -p true -r "glasgow"
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m "glasgow_scaled" -j "EPCG" -i "EBSS" -r "glasgow" -d "plots/epcg_ebss_diff_map.pdf" -y 2025

uc_baseline_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "baseline" -y 2025 -m "scaled_glasgow" -s who_universal_credit_and_kids -p true -r "glasgow"
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "25UniversalCredit" -y 2025 -m "scaled_glasgow" -s who_boosted -p true -r "glasgow"
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m "scaled_glasgow" -j "Baseline" -i "25Universal" -r "glasgow" -d "plots/universal_credit_baseline_difff_map.pdf" -y 2025

priority_baseline_map:
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "baseline" -y 2025 -m "scaled_glasgow" -s who_universal_credit_and_kids -p true -r "glasgow"
	$(PYTHON) minos/outcomes/format_spatial_output.py -i "25Priority" -y 2025 -m "scaled_glasgow" -s who_boosted -p true -r "glasgow"
	$(RSCRIPT) minos/outcomes/sf12_difference_map.R -m "scaled_glasgow" -j "Baseline" -i "25Priority" -r "glasgow" -d "plots/priority_baseline_difff_map.pdf" -y 2025

# experimental bash scripts.
main_maps:
	bash minos/outcomes/aggregated_maps.sh


map_all: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map aggregate_baseline_poverty_uplift_map
map_concept_note: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map
