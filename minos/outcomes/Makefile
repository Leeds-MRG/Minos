

#TODO: Now that the makefile is split and in the same directory as its scripts, can we do relative paths?

test_plot: MODE=default_config
test_plot: ALIVE=who_alive
test_plot: BOOSTED=who_boosted
test_plot: aggregate_minos_output_energy

#####################################
# SIPHER 7 Equivalent Income Outcomes (lol)
#####################################

S7_outcomes:
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/equivalent_income_out.Rmd')"
	# open html file in firefox
	firefox file://$(OUTCOMES)/equivalent_income_out.html

S7_batch_outcomes:
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/equivalent_income_out_batch.Rmd')"
	# open html file in firefox
	firefox file://$(OUTCOMES)/equivalent_income_out_batch.html

S7_batch_outcomes_2:
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/EI_allScen_Plots.Rmd')"
	# open html file in firefox
	firefox file://$(OUTCOMES)/EI_allScen_Plots.html

#S7_clustering:
#	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7/',intervention='livingWageIntervention'))"
#	firefox file://$(OUTCOMES)/clustering_EI.html
#	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7/',intervention='hhIncomeChildUplift'))"
#	firefox file://$(OUTCOMES)/clustering_EI.html
#	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7/',intervention='hhIncomePovertyLineChildUplift'))"
#	firefox file://$(OUTCOMES)/clustering_EI.html
#	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7/',intervention='energyDownlift'))"
#	firefox file://$(OUTCOMES)/clustering_EI.html
#	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7/',intervention='energyDownliftNoSupport'))"
#	firefox file://$(OUTCOMES)/clustering_EI.html

S7_clustering_batch:
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7_sum/',intervention='livingWageIntervention', clusters='3', baseline='baseline'))"
	firefox file://$(TESTING)/clustering_EI.html
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7_sum/',intervention='hhIncomeChildUplift', clusters='3', baseline='baseline'))"
	firefox file://$(TESTING)/clustering_EI.html
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7_sum/',intervention='hhIncomePovertyLineChildUplift', clusters='3', baseline='baseline'))"
	firefox file://$(TESTING)/clustering_EI.html
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7_sum/',intervention='energyDownlift', clusters='3', baseline='energyDownliftNoSupport'))"
	firefox file://$(TESTING)/clustering_EI.html


S7_cluster_test:
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/num_clusters_test.Rmd', param=list(out_path='SIPHER7_sum/',intervention='livingWageIntervention', baseline='baseline'))"
	firefox file://$(TESTING)/num_clusters_test.html
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/num_clusters_test.Rmd', param=list(out_path='SIPHER7_sum/',intervention='hhIncomeChildUplift', baseline='baseline'))"
	firefox file://$(TESTING)/num_clusters_test.html
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/num_clusters_test.Rmd', param=list(out_path='SIPHER7_sum/',intervention='hhIncomePovertyLineChildUplift', baseline='baseline'))"
	firefox file://$(TESTING)/num_clusters_test.html
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/num_clusters_test.Rmd', param=list(out_path='SIPHER7_sum/',intervention='energyDownliftNoSupport', baseline='energyDownlift'))"
	firefox file://$(TESTING)/num_clusters_test.html

S7_quick_test:
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/num_clusters_test.Rmd', param=list(out_path='SIPHER7_sum/',intervention='energyDownliftNoSupport', baseline='energyDownlift'))"
	firefox file://$(TESTING)/num_clusters_test.html

S7_comp_change_boxplot:
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/S7_comp_change_boxplot.Rmd', param=list(out_path='SIPHER7/',intervention='livingWageIntervention'))"
	#firefox file://$(TESTING)/S7_comp_change_boxplot.html
	mv $(TESTING)/S7_comp_change_boxplot.html $(TESTING)/S7_comp_change_boxplot_livingWageIntervention.html
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/S7_comp_change_boxplot.Rmd', param=list(out_path='SIPHER7/',intervention='hhIncomeChildUplift'))"
	#firefox file://$(TESTING)/S7_comp_change_boxplot.html
	mv $(TESTING)/S7_comp_change_boxplot.html $(TESTING)/S7_comp_change_boxplot_hhIncomeChildUplift.html
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/S7_comp_change_boxplot.Rmd', param=list(out_path='SIPHER7/',intervention='hhIncomePovertyLineChildUplift'))"
	#firefox file://$(TESTING)/S7_comp_change_boxplot.html
	mv $(TESTING)/S7_comp_change_boxplot.html $(TESTING)/S7_comp_change_boxplot_hhIncomePovertyLineChildUplift.html


#$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/clustering_EI.Rmd', param=list(out_path='SIPHER7_sum/',intervention='energyDownliftNoSupport', clusters='', baseline='baseline'))"
 #	firefox file://$(TESTING)/clustering_EI.html
#	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/num_clusters_test.Rmd', param=list(out_path='SIPHER7_sum/',intervention='energyDownlift'))"
 #	firefox file://$(TESTING)/num_clusters_test.html


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

default_all_lineplots: ALIVE=who_alive
default_all_lineplots: BOOSTED=who_boosted
default_all_lineplots: LIVING_WAGE=who_below_living_wage
default_all_lineplots: POVERTY=who_below_poverty_line_and_kids
default_all_lineplots: CHILD=who_kids
default_all_lineplots: all_lineplots

all_lineplots: aggregate_minos_output_living_wage aggregate_minos_output_all_child_uplift aggregate_minos_output_poverty_child_uplift aggregate_minos_output_energy
vulnerable_groups_lineplots: aggregate_combined_vulnerable aggregate_minos_output_all_child_uplift aggregate_minos_output_disabled_child_uplift aggregate_minos_output_minority_child_uplift aggregate_minos_output_three_child_uplift aggregate_minos_output_young_adult_child_uplift aggregate_minos_output_uneducated_child_uplift


###################### COMBINED PLOTTING FUNCTIONS ######################
# The following section contains targets for plotting all scenarios     #
# contained in the combined targets seen in scripts/Makefile (usually   #
# named something like `S7_all_scenarios`.								#
# To generate plots for a single intervention, you will need to create  #
# a new target in which you set the MODE and AGG_VAR parameters. For    #
# example:																#
#																		#
# lineplot_livingWage: MODE=SIPHER7										#
# lineplot_livingWage: AGG_VAR=equivalent_income						#
# lineplot_livingWage: aggregate_minos_output_living_wage				#
#																		#
# This target would generate a lineplot for only the living wage 		#
# intervention scenario, using the SIPHER7 - Equivalent Income 			#
# experiment, focusing on equivalent_income as it's target variable.	#
#																		#
#							########									#
#																		#
# Also, if you wish to generate plots for all vulnerable groups, we can #
# achieve this with the following make target:							#
#																		#
# vulnerable_groups_lineplot_MCS: MODE=default_config					#
# vulnerable_groups_lineplot_MCS: AGG_VAR=SF_12							#
# vulnerable_groups_lineplot_MCS: vulnerable_groups_lineplots			#
#																		#
# This would generate lineplots for each of the vulnerable groups 		#
# defined by the Scottish government, using SF_12_MCS as the target 	#
# variable.																#
#########################################################################

######## SF_12 PLOTS ########

.PHONY: all_lineplots_MCS all_lineplots_PCS

# will change to SF_12_MCS when PCS is implemented
all_lineplots_MCS: MODE=default_config
all_lineplots_MCS: AGG_VAR=SF_12
all_lineplots_MCS: default_all_lineplots

# PCS COMING SOON THIS WON'T WORK YET!
all_lineplots_PCS: MODE=default_config
all_lineplots_PCS: AGG_VAR=SF_12_PCS
all_lineplots_PCS: default_all_lineplots

lineplot_livingWage: MODE=default_config
lineplot_livingWage: AGG_VAR=SF_12
lineplot_livingWage: aggregate_minos_output_living_wage
lineplot_livingWage:
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/testing_livingWage_intervention.Rmd')"
	# open html file in firefox
	firefox file://$(TESTING)/testing_livingWage_intervention.html

######## Equivalent Income PLOTS ########

# NOTE: Equivalent Income is only implemented in the SIPHER7 experiment, so MODE should always be set to SIPHER7 when
# trying to generate lineplots for equivalent_income.

.PHONY: all_lineplots_EI all_lineplots_EI_glasgow

all_lineplots_EI: MODE=SIPHER7
all_lineplots_EI: AGG_VAR=equivalent_income
all_lineplots_EI: default_all_lineplots

all_lineplots_EI_glasgow: MODE=SIPHER7_glasgow
all_lineplots_EI_glasgow: AGG_VAR=equivalent_income
all_lineplots_EI_glasgow: REGION=glasgow_synthetic
all_lineplots_EI_glasgow: default_all_lineplots

##########################################################################


aggregate_minos_output:
aggregate_minos_output:	DIRECTORIES = baseline,hhIncomeChildUplift,livingWageIntervention,energyDownlift
aggregate_minos_output:	DIRECTORY_TAGS = "Baseline,£25 All Child Uplift,Living Wage,Energy Downlift"
aggregate_minos_output:	SUBSET_FUNCTIONS = "who_alive,who_alive,who_alive,who_alive"
aggregate_minos_output:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(DIRECTORIES) $(DIRECTORY_TAGS) $(DIRECTORY_SUBSETS) "all" $(AGG_VAR) $(REGION)


aggregate_minos_output_treated:	TREATED_DIRECTORIES = baseline,hhIncomeChildUplift,hhIncomePovertyLineChildUplift,livingWageIntervention,energyDownlift
aggregate_minos_output_treated:	TREATED_DIRECTORY_TAGS="Baseline,£25 All Child Uplift,£25 Poverty Line Child Uplift, Living Wage,Energy Crisis"
aggregate_minos_output_treated:	TREATED_DIRECTORY_SUBSETS = $(ALIVE),$(BOOSTED),$(BOOSTED),$(BOOSTED),$(BOOSTED)
aggregate_minos_output_treated:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(TREATED_DIRECTORIES) $(TREATED_DIRECTORY_TAGS) $(TREATED_DIRECTORY_SUBSETS) "treated" $(AGG_VAR) $(REGION)

aggregate_minos_output_living_wage:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,livingWageIntervention "Baseline,Living Wage Intervention" who_below_living_wage,who_boosted "living_wage" $(AGG_VAR) $(REGION)

aggregate_minos_output_poverty_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomePovertyLineChildUplift "Baseline,Poverty Line Uplift" who_below_poverty_line_and_kids,who_boosted "poverty_line_child_uplift" $(AGG_VAR) $(REGION)

aggregate_minos_output_all_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,All Children Uplift" who_kids,who_boosted "all_child_uplift" $(AGG_VAR) $(REGION)

#aggregate_minos_output_all_child_uplift:
#	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift,hhIncomePovertyLineChildUplift "Baseline,All Children Uplift,Poverty Line Child Uplift" who_kids,who_boosted,who_boosted "all_vs_poverty_child_uplift" $(AGG_VAR)

aggregate_minos_output_disabled_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,Disabled Children Uplift" who_disabled,who_disabled "disabled_child_uplift" $(AGG_VAR) $(REGION)

aggregate_minos_output_minority_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,Minority Children Uplift" who_ethnic_minority,who_ethnic_minority "minority_child_uplift" $(AGG_VAR) $(REGION)

aggregate_minos_output_three_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,Three Children Uplift" who_three_kids,who_three_kids "three_child_uplift" $(AGG_VAR) $(REGION)

# omitted due to lack of sample size
aggregate_minos_output_young_mother_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,Young Mother Children Uplift" who_young_mother,who_young_mother "young_mother_child_uplift" $(AGG_VAR) $(REGION)

aggregate_minos_output_young_adult_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,Young Single Parent Children Uplift" who_young_adults,who_young_adults "young_adult_child_uplift" $(AGG_VAR) $(REGION)

aggregate_minos_output_uneducated_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,Low Education Children Uplift" who_no_formal_education,who_no_formal_education "low_education_child_uplift" $(AGG_VAR) $(REGION)


aggregate_minos_output_scottish: MODE=default_config
aggregate_minos_output_scottish: DIRECTORIES=baseline,hhIncomeChildUplift,livingWageIntervention,energyDownlift
aggregate_minos_output_scottish: DIRECTORY_TAGS="Baseline,£25 All Child Uplift,Living Wage,Energy Downlift"
aggregate_minos_output_scottish: SUBSET_FUNCTIONS=who_scottish,who_scottish,who_scottish,who_scottish
aggregate_minos_output_scottish:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(DIRECTORIES) $(DIRECTORY_TAGS) $(SUBSET_FUNCTIONS) "who_scottish?" $(AGG_VAR) $(REGION)

aggregate_minos_output_living_wage_scot:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,livingWageIntervention "Baseline,Living Wage Intervention" who_scottish,who_scottish "living_wage_treated" $(AGG_VAR) $(REGION)

aggregate_minos_output_all_child_uplift_scot:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,All Children Uplift" who_scottish,who_scottish "all_child_uplift" $(AGG_VAR) $(REGION)

aggregate_minos_output_poverty_child_uplift_scot:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomePovertyLineChildUplift "Baseline,Poverty Line Uplift" who_scottish,who_scottish "poverty_line_child_uplift" $(AGG_VAR) $(REGION)

aggregate_minos_output_energy_scot:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,energyDownlift "Baseline,Energy Downlift" who_scottish,who_scottish "energy_downlift" $(AGG_VAR) $(REGION)

lineplots_national_scottish_subsample: aggregate_minos_output_living_wage_scot aggregate_minos_output_all_child_uplift_scot aggregate_minos_output_poverty_child_uplift_scot aggregate_minos_output_energy_scot aggregate_minos_output_scottish

aggregate_combined_vulnerable:MODE=default_config
aggregate_combined_vulnerable:VULNERABLE_DIRECTORIES=baseline,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift
aggregate_combined_vulnerable:VULNERABLE_DIRECTORY_TAGS="Baseline,All Children Uplift,Disabled Children Uplift,Minority Children Uplift,Three Children Uplift,Young Single Parent Children Uplift,Low Education Children Uplift"
aggregate_combined_vulnerable:VULNERABLE_DIRECTORY_SUBSETS=who_alive,who_kids,who_disabled,who_ethnic_minority,who_three_kids,who_young_adults,who_no_formal_education
aggregate_combined_vulnerable:
	bash minos/outcomes/make_lineplot.sh $(MODE) $(VULNERABLE_DIRECTORIES) $(VULNERABLE_DIRECTORY_TAGS) $(VULNERABLE_DIRECTORY_SUBSETS) "all_vulnerable" $(AGG_VAR) $(REGION)

aggregate_minos_output_energy:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,energyDownlift,energyDownliftNoSupport "Baseline,Energy crisis with the EPCG,Energy crisis with no support" who_uses_energy,who_boosted,who_boosted "epcg" $(AGG_VAR) $(REGION)

aggregate_minos_output_energy_old: # old command not using intervention with no support as well
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,energyDownlift "Baseline,Energy Downlift" who_uses_energy,who_boosted "energy_downlift" $(AGG_VAR) $(REGION)

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

