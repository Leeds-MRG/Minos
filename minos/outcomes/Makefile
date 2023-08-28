

#TODO: Now that the makefile is split and in the same directory as its scripts, can we do relative paths?

test_plot: MODE=default_config
test_plot: ALIVE=who_alive
test_plot: BOOSTED=who_boosted
test_plot: aggregate_minos_output_energy

#####################################
# Post-hoc aggregation of multiple MINOS runs on bash terminal.
#####################################

#TODO: Parameterise this so we can run `make scot_all_lineplots` and it sets the $(MODE) var and runs all lineplots with it
scot_all_lineplots: MODE=scotland_mode
scot_all_lineplots: ALIVE=who_alive
scot_all_lineplots: BOOSTED=who_boosted
scot_all_lineplots: LIVING_WAGE=who_below_living_wage
scot_all_lineplots: POVERTY=who_below_poverty_line_and_kids
scot_all_lineplots: CHILD=who_kids
scot_all_lineplots: all_lineplots

default_all_lineplots: MODE=default_config
default_all_lineplots: ALIVE=who_alive
default_all_lineplots: BOOSTED=who_boosted
default_all_lineplots: LIVING_WAGE=who_below_living_wage
default_all_lineplots: POVERTY=who_below_poverty_line_and_kids
default_all_lineplots: CHILD=who_kids
default_all_lineplots: all_lineplots

all_lineplots: aggregate_minos_output_treated aggregate_minos_output_living_wage aggregate_minos_output_all_child_uplift aggregate_minos_output_poverty_child_uplift aggregate_minos_output_energy
vulnerable_groups_lineplots: aggregate_combined_vulnerable aggregate_minos_output_all_child_uplift aggregate_minos_output_disabled_child_uplift aggregate_minos_output_minority_child_uplift aggregate_minos_output_three_child_uplift aggregate_minos_output_young_adult_child_uplift aggregate_minos_output_uneducated_child_uplift


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

BOOSTED="who_boosted"
aggregate_all_child_uplifts: MODE=default_config
aggregate_all_child_uplifts: TREATED_DIRECTORIES = baseline,25All,50All,75All,100All
aggregate_all_child_uplifts: TREATED_DIRECTORY_TAGS="Baseline,£25 All Child Uplift,£50 All Child Uplift,£75 All Child Uplift,£100 All Child Uplift"
aggregate_all_child_uplifts: TREATED_DIRECTORY_SUBSETS = "who_kids",$(BOOSTED),$(BOOSTED),$(BOOSTED),$(BOOSTED)
aggregate_all_child_uplifts:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "varying_all_child_uplifts"

aggregate_poverty_line_child_uplifts: MODE=default_config
aggregate_poverty_line_child_uplifts: TREATED_DIRECTORIES = baseline,25RelativePoverty,50RelativePoverty,75RelativePoverty,100RelativePoverty
aggregate_poverty_line_child_uplifts: TREATED_DIRECTORY_TAGS="Baseline,£25 Poverty Line Child Uplift,£50,£75,£100"
aggregate_poverty_line_child_uplifts: TREATED_DIRECTORY_SUBSETS = "who_below_poverty_line_and_kids",$(BOOSTED),$(BOOSTED),$(BOOSTED),$(BOOSTED)
aggregate_poverty_line_child_uplifts:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "varying_poverty_line_child_uplifts"

aggregate_universal_credit_child_uplifts: MODE=default_config
aggregate_universal_credit_child_uplifts: TREATED_DIRECTORIES = baseline,25UniversalCredit,50UniversalCredit,75UniversalCredit,100UniversalCredit
aggregate_universal_credit_child_uplifts: TREATED_DIRECTORY_TAGS="Baseline,£25 Universal Credit,£50 Universal Credit,£75 Universal Credit,£100 Universal Credit"
aggregate_universal_credit_child_uplifts: TREATED_DIRECTORY_SUBSETS = "who_universal_credit_and_kids",$(BOOSTED),$(BOOSTED),$(BOOSTED),$(BOOSTED)
aggregate_universal_credit_child_uplifts:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "varying_universal_credit_child_uplifts"


aggregate_25_universal_credit: MODE=default_config
aggregate_25_universal_credit: TREATED_DIRECTORIES = baseline,25UniversalCredit
aggregate_25_universal_credit: TREATED_DIRECTORY_TAGS="Baseline,£25 Universal Credit"
aggregate_25_universal_credit: TREATED_DIRECTORY_SUBSETS = "who_universal_credit_and_kids",$(BOOSTED)
aggregate_25_universal_credit:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "25_universal_credit_child_uplifts"

aggregate_25_relative_poverty: MODE=default_config
aggregate_25_relative_poverty: TREATED_DIRECTORIES = baseline,25RelativePoverty
aggregate_25_relative_poverty: TREATED_DIRECTORY_TAGS="Baseline,£25 Relative Poverty"
aggregate_25_relative_poverty: TREATED_DIRECTORY_SUBSETS = "who_below_poverty_line_and_kids",$(BOOSTED)
aggregate_25_relative_poverty:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "25_relative_poverty_child_uplifts"

aggregate_25_all_children: MODE=default_config
aggregate_25_all_children: TREATED_DIRECTORIES = baseline,25All
aggregate_25_all_children: TREATED_DIRECTORY_TAGS="Baseline,£25 All Children"
aggregate_25_all_children: TREATED_DIRECTORY_SUBSETS = "who_kids",$(BOOSTED)
aggregate_25_all_children:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "25_all_children_child_uplifts"

aggregate_combined_25_child_uplifts: MODE=default_config
aggregate_combined_25_child_uplifts: TREATED_DIRECTORIES = baseline,25UniversalCredit,25RelativePoverty,25All
aggregate_combined_25_child_uplifts: TREATED_DIRECTORY_TAGS="Baseline,£25 Universal Credit,£25 Relative Poverty,£25 All"
aggregate_combined_25_child_uplifts: TREATED_DIRECTORY_SUBSETS = "who_kids",$(BOOSTED),$(BOOSTED),$(BOOSTED)
aggregate_combined_25_child_uplifts:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "combined_25_child_uplifts"

aggregate_all_child_uplifts: aggregate_25_all_children aggregate_25_relative_poverty aggregate_25_universal_credit aggregate_combined_25_child_uplifts

#################################
# Custom subset for scotgov piece
#################################

aggregate_25_UC_vulnerable: MODE=default_config
aggregate_25_UC_vulnerable: TREATED_DIRECTORIES = baseline,25UniversalCredit,25Vulnerable
aggregate_25_UC_vulnerable: TREATED_DIRECTORY_TAGS="Baseline,£25 Universal Credit,£25 Vulnerable Groups"
aggregate_25_UC_vulnerable: TREATED_DIRECTORY_SUBSETS = "who_universal_credit_and_kids",$(BOOSTED),$(BOOSTED)
aggregate_25_UC_vulnerable:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "25_UC_vulnerable_uplift"

aggregate_50_UC_vulnerable: MODE=default_config
aggregate_50_UC_vulnerable: TREATED_DIRECTORIES = baseline,50UniversalCredit,50Vulnerable
aggregate_50_UC_vulnerable: TREATED_DIRECTORY_TAGS="Baseline,£50 Universal Credit,£50 Vulnerable Groups"
aggregate_50_UC_vulnerable: TREATED_DIRECTORY_SUBSETS = "who_universal_credit_and_kids",$(BOOSTED),$(BOOSTED)
aggregate_50_UC_vulnerable:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "50_UC_vulnerable_uplift"

aggregate_75_UC_vulnerable: MODE=default_config
aggregate_75_UC_vulnerable: TREATED_DIRECTORIES = baseline,75UniversalCredit,75Vulnerable
aggregate_75_UC_vulnerable: TREATED_DIRECTORY_TAGS="Baseline,£75 Universal Credit,£75 Vulnerable Groups"
aggregate_75_UC_vulnerable: TREATED_DIRECTORY_SUBSETS = "who_universal_credit_and_kids",$(BOOSTED),$(BOOSTED)
aggregate_75_UC_vulnerable:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "75_UC_vulnerable_uplift"

aggregate_100_UC_vulnerable: MODE=default_config
aggregate_100_UC_vulnerable: TREATED_DIRECTORIES = baseline,100UniversalCredit,100Vulnerable
aggregate_100_UC_vulnerable: TREATED_DIRECTORY_TAGS="Baseline,£100 Universal Credit,£100 Vulnerable Groups"
aggregate_100_UC_vulnerable: TREATED_DIRECTORY_SUBSETS = "who_universal_credit_and_kids",$(BOOSTED),$(BOOSTED)
aggregate_100_UC_vulnerable:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "100_UC_vulnerable_uplift"

all_uc_vuln: aggregate_25_UC_vulnerable aggregate_50_UC_vulnerable aggregate_75_UC_vulnerable aggregate_100_UC_vulnerable

aggregate_minos_output_living_wage:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,livingWageIntervention "Baseline,Living Wage Intervention" who_below_living_wage,who_boosted "living_wage_treated"

aggregate_minos_output_poverty_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomePovertyLineChildUplift "Baseline,Poverty Line Uplift" who_below_poverty_line_and_kids,who_boosted "poverty_line_child_uplift"

#aggregate_minos_output_all_child_uplift:
#	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,All Children Uplift" who_kids,who_boosted "all_child_uplift"

aggregate_minos_output_all_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift,hhIncomePovertyLineChildUplift "Baseline,All Children Uplift,Poverty Line Child Uplift" who_kids,who_boosted,who_boosted "all_vs_poverty_child_uplift"

aggregate_minos_output_scottish: MODE=default_config
aggregate_minos_output_scottish: DIRECTORIES=baseline,hhIncomeChildUplift,livingWageIntervention,energyDownlift
aggregate_minos_output_scottish: DIRECTORY_TAGS="Baseline,£25 All Child Uplift,Living Wage,Energy Downlift"
aggregate_minos_output_scottish: SUBSET_FUNCTIONS=who_scottish,who_scottish,who_scottish,who_scottish
aggregate_minos_output_scottish:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(DIRECTORIES) $(DIRECTORY_TAGS) $(SUBSET_FUNCTIONS) "who_scottish?"

aggregate_minos_output_living_wage_scot:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,livingWageIntervention "Baseline,Living Wage Intervention" who_scottish,who_scottish "living_wage_treated"

aggregate_minos_output_all_child_uplift_scot:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,All Children Uplift" who_scottish,who_scottish "all_child_uplift"

aggregate_minos_output_poverty_child_uplift_scot:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomePovertyLineChildUplift "Baseline,Poverty Line Uplift" who_scottish,who_scottish "poverty_line_child_uplift"

aggregate_minos_output_energy_scot:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,energyDownlift "Baseline,Energy Downlift" who_scottish,who_scottish "energy_downlift"

lineplots_national_scottish_subsample: aggregate_minos_output_living_wage_scot aggregate_minos_output_all_child_uplift_scot aggregate_minos_output_poverty_child_uplift_scot aggregate_minos_output_energy_scot aggregate_minos_output_scottish

aggregate_combined_vulnerable:MODE=default_config
aggregate_combined_vulnerable:VULNERABLE_DIRECTORIES=baseline,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift
aggregate_combined_vulnerable:VULNERABLE_DIRECTORY_TAGS="Baseline,All Children Uplift,Disabled Children Uplift,Minority Children Uplift,Three Children Uplift,Young Single Parent Children Uplift,Low Education Children Uplift"
aggregate_combined_vulnerable:VULNERABLE_DIRECTORY_SUBSETS=who_alive,who_kids,who_disabled,who_ethnic_minority,who_three_kids,who_young_adults,who_no_formal_education
aggregate_combined_vulnerable:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(VULNERABLE_DIRECTORIES) $(VULNERABLE_DIRECTORY_TAGS) $(VULNERABLE_DIRECTORY_SUBSETS) "all_vulnerable"

aggregate_all_vulnerable_subgroups:
	bash minos/outcomes/make_lineplot.sh default_config baseline,25All "Baseline,Vulnerable" who_vulnerable_subgroups,who_vulnerable_subgroups "vulnerable_subgroups"

aggregate_minos_output_energy:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,energyDownlift,energyDownliftNoSupport "Baseline,Energy crisis with the EPCG,Energy crisis with no support" who_uses_energy,who_boosted,who_boosted "epcg"

aggregate_minos_output_energy_old: # old command not using intervention with no support as well
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,energyDownlift "Baseline,Energy Downlift" who_uses_energy,who_boosted "energy_downlift"


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

map_all: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map aggregate_baseline_poverty_uplift_map
map_concept_note: aggregate_baseline_map aggregate_baseline_energy_map aggregate_baseline_living_wage_map aggregate_baseline_all_uplift_map