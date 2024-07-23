

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
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_all_child"

aggregate_poverty_line_child_uplifts: MODE="default_config"
aggregate_poverty_line_child_uplifts:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_relative_poverty"

aggregate_universal_credit_child_uplifts: MODE="glasgow_scaled"
aggregate_universal_credit_child_uplifts:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_universal_credit"

aggregate_priority_groups_child_uplifts: MODE= "glasgow_scaled"
aggregate_priority_groups_child_uplifts:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_priority_groups"

aggregate_25_relative_poverty: MODE="default_config"
aggregate_25_relative_poverty:
	bash minos/outcomes/make_lineplots_macros.sh "25_relative_poverty"

aggregate_25_all_children: MODE="default_config"
aggregate_25_all_children:
	bash minos/outcomes/make_lineplots_macros.sh $(MODE) "25_all"

#############################################################
# Default config visualisations of universal credit uplifts #
#############################################################

aggregate_25_universal_credit: MODE="default_config"
aggregate_25_universal_credit:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "25_universal_credit"

aggregate_30_universal_credit: MODE="default_config"
aggregate_30_universal_credit:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "30_universal_credit"

aggregate_35_universal_credit: MODE="default_config"
aggregate_35_universal_credit:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "35_universal_credit"

aggregate_40_universal_credit: MODE="default_config"
aggregate_40_universal_credit:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "40_universal_credit"

aggregate_45_universal_credit: MODE="default_config"
aggregate_45_universal_credit:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "45_universal_credit"

aggregate_50_universal_credit: MODE="default_config"
aggregate_50_universal_credit:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "50_universal_credit"

##########################################
# Custom subset for social science paper #
##########################################

social_science_lineplots:
	python3 minos/outcomes/make_lineplots_macros.py "default_config" "social_science_all_plots"

#################################
# Custom subset for scotgov piece
#################################

####################################
# Initial work for 25 UC and 25 Priority subgroups.
#####################################

aggregate_25_UC_vulnerable: MODE="glasgow_scaled"
aggregate_25_UC_vulnerable:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "25_UC_priority"

aggregate_50_UC_vulnerable: MODE="glasgow_scaled"
aggregate_50_UC_vulnerable:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "50_UC_priority"

aggregate_75_UC_vulnerable: MODE="glasgow_scaled"
aggregate_75_UC_vulnerable:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "75_UC_priority"

aggregate_100_UC_vulnerable: MODE="glasgow_scaled"
aggregate_100_UC_vulnerable:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "100_UC_priority"

all_uc_vuln: aggregate_25_UC_vulnerable aggregate_50_UC_vulnerable aggregate_75_UC_vulnerable aggregate_100_UC_vulnerable aggregate_universal_credit_child_uplifts aggregate_priority_groups_child_uplifts

#############################################################
# £25 TO £25 BY £5 increments treatment on treated lineplots.
##############################################################

aggregate_25_UC_scotland: MODE="scaled_scotland"
aggregate_25_UC_scotland:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "25_universal_credit"

aggregate_30_UC_scotland: MODE="scaled_scotland"
aggregate_30_UC_scotland:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "30_universal_credit"

aggregate_35_UC_scotland: MODE="scaled_scotland"
aggregate_35_UC_scotland:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "35_universal_credit"

aggregate_40_UC_scotland: MODE="scaled_scotland"
aggregate_40_UC_scotland:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "40_universal_credit"

aggregate_45_UC_scotland: MODE="scaled_scotland"
aggregate_45_UC_scotland:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "45_universal_credit"

aggregate_50_UC_scotland: MODE="scaled_scotland"
aggregate_50_UC_scotland:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "50_universal_credit"

all_25_50_by_5_UC_scotland_uplifts: MODE="scaled_scotland"
all_25_50_by_5_UC_scotland_uplifts:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_25_50_by_5_universal_credit"

all_25_50_by_5_together_UC_scotland_uplifts: MODE="scaled_scotland"
all_25_50_by_5_together_UC_scotland_uplifts:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_25_50_by_5_together_universal_credit"

################################
# priority subgroups
################################

aggregate_25_UC_single_mothers: MODE="scaled_scotland"
aggregate_25_UC_single_mothers:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "scotland_25_universal_credit_young_mothers"

aggregate_25_UC_any_priority_subgroup: MODE="scaled_scotland"
aggregate_25_UC_any_priority_subgroup:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "scotland_25_universal_any_priority_subgroup"

aggregate_25_UC_many_priority_groups: MODE="scaled_scotland"
aggregate_25_UC_many_priority_groups:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "scotland_25_universal_many_priority_subgroups"

all_priority_subgroup_lineplots: aggregate_25_UC_single_mothers, aggregate_25_UC_any_priority_subgroup aggregate_25_UC_many_priority_groups

########################################################
# SIMD decile lineplots for glasgow using spatial data #
########################################################

baseline_all_deciles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_baseline_all_deciles"

poverty_all_deciles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_poverty_all_deciles"

universal_credit_all_deciles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_universal_credit_all_deciles"

priority_group_all_deciles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_priority_groups_all_deciles"

poverty_first_decile_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_poverty_first"

poverty_fifth_decile_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_poverty_fifth"

poverty_tenth_decile_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_poverty_tenth"

baseline_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_baseline_quintile"

25RelativePoverty_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_relative_poverty_quintile"

25UniversalCredit_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_universal_credit_quintile"

epcg_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_epcg_quintile"

living_wage_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "glasgow_scaled" "glasgow_living_wage_quintile"


##########################################
# All Scotland 25 UC Quintiles
##########################################


baseline_scotland_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "scotland_baseline_quintiles"

baseline_glasgow_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "glasgow_baseline_quintiles"

baseline_edinburgh_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "edinburgh_baseline_quintiles"

25UniversalCredit_scotland_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "scotland_25_universal_credit_quintiles"

25UniversalCredit_glasgow_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "glasgow_25_universal_credit_quintiles"

25UniversalCredit_edinburgh_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "edinburgh_25_universal_credit_quintiles"

# increasing increments dont have the full suite of vis yet.
# maybe a better way of encoding the increasing number of combinations with lists?
30UniversalCredit_scotland_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "scotland_30_universal_credit_quintiles"

35UniversalCredit_scotland_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "scotland_35_universal_credit_quintiles"

40UniversalCredit_scotland_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "scotland_40_universal_credit_quintiles"

45UniversalCredit_scotland_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "scotland_45_universal_credit_quintiles"

50UniversalCredit_scotland_all_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "scaled_scotland" "scotland_50_universal_credit_quintiles"

all_25_UC_quintiles: baseline_scotland_quintiles baseline_glasgow_quintiles baseline_edinburgh_quintiles 25UniversalCredit_scotland_all_quintiles 25UniversalCredit_glasgow_all_quintiles 25UniversalCredit_edinburgh_all_quintiles


# grand daddy makefile for every scotland plot for £25 universal credit
# WARNING: this will take 2+ hours on scotland scaled data.
every_single_scotland_plot: all_25_50_by_5_UC_scotland_uplifts all_priority_subgroup_lineplots all_25_UC_quintiles all_25_UC_scotland_maps

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
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,livingWageIntervention "Baseline,Living Wage Intervention" who_below_living_wage,who_boosted "living_wage" $(AGG_VAR) $(REGION)

aggregate_minos_output_poverty_child_uplift:
	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomePovertyLineChildUplift "Baseline,Poverty Line Uplift" who_below_poverty_line_and_kids,who_boosted "poverty_line_child_uplift"

aggregate_minos_output_child_poverty_reductionRANDOM:
	bash minos/outcomes/make_lineplot.sh default_config baseline,ChildPovertyReductionRANDOM "Baseline,Child Poverty Reduction RANDOM" who_alive,who_boosted "child_poverty_reduction_RANDOM_who_alive"
	bash minos/outcomes/make_lineplot.sh default_config baseline,ChildPovertyReductionRANDOM "Baseline,Child Poverty Reduction RANDOM" who_kids,who_boosted "child_poverty_reduction_RANDOM_who_kids"
	bash minos/outcomes/make_lineplot.sh default_config baseline,ChildPovertyReductionRANDOM "Baseline,Child Poverty Reduction RANDOM" who_below_poverty_line_and_kids,who_boosted "child_poverty_reduction_RANDOM_who_pov_kids"

aggregate_minos_output_child_poverty_reductionSUSTAIN:
	bash minos/outcomes/make_lineplot.sh default_config baseline,ChildPovertyReductionSUSTAIN "Baseline,Child Poverty Reduction SUSTAIN" who_alive,who_boosted "child_poverty_reduction_SUSTAIN_who_alive"
	bash minos/outcomes/make_lineplot.sh default_config baseline,ChildPovertyReductionSUSTAIN "Baseline,Child Poverty Reduction SUSTAIN" who_kids,who_boosted "child_poverty_reduction_SUSTAIN_who_kids"
	bash minos/outcomes/make_lineplot.sh default_config baseline,ChildPovertyReductionSUSTAIN "Baseline,Child Poverty Reduction SUSTAIN" who_below_poverty_line_and_kids,who_boosted "child_poverty_reduction_SUSTAIN_who_pov_kids"

#aggregate_minos_output_all_child_uplift:
#	bash minos/outcomes/make_lineplot.sh $(MODE) baseline,hhIncomeChildUplift "Baseline,All Children Uplift" who_kids,who_boosted "all_child_uplift"

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





#########################
# Housing Interventions #
#########################

aggregate_minos_good_housing_dummy:
	python3 minos/outcomes/make_lineplots_macros.py "energy_default_config" "good_heating_dummy"

aggregate_minos_GBIS:
	python3 minos/outcomes/make_lineplots_macros.py "energy_default_config" "GBIS"

aggregate_minos_FFRS:
	python3 minos/outcomes/make_lineplots_macros.py "energy_default_config" "fossilFuelReplacementScheme"

aggregate_minos_manchester_good_housing_dummy:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "good_heating_dummy"

aggregate_minos_manchester_GBIS:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "GBIS"

aggregate_minos_manchester_FFRS:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "fossilFuelReplacementScheme"

aggregate_minos_manchester_good_housing_dummy_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "good_heating_dummy_quintiles"

aggregate_minos_manchester_EPCG:
	python3 minos/outcomes/make_lineplots_macros.py  "energy_manchester_scaled" "EPCG"

aggregate_minos_manchester_combined:
	python3 minos/outcomes/make_lineplots_macros.py  "energy_manchester_scaled" "GHD_EPCG_GBIS_combined" "SF_12"

# MCS QUINTILES

aggregate_minos_manchester_EPCG_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "EPCG_quintiles" "SF_12"

aggregate_minos_manchester_good_heating_dummy_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "GHD_quintiles" "SF_12"

aggregate_minos_manchester_GBIS_quintiles:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "GBIS_quintiles" "SF_12"

aggregate_minos_manchester_EPCG_GBIS_SF_12:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "EPCG_GBIS_SF_12" "SF_12"

# BOOST AMOUNT

aggregate_minos_manchester_EPCG_GBIS_intervention_cost:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "EPCG_GBIS_intervention_cost" "boost_amount"

aggregate_minos_manchester_EPCG_GBIS_yearly_energy:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "EPCG_GBIS_yearly_energy" "yearly_energy"

aggregate_minos_manchester_EPCG_GBIS_heating:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "GHD_EPCG_GBIS_combined" "heating"

aggregate_minos_manchester_EPCG_GBIS_combined_yearly_energy:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "GHD_EPCG_GBIS_combined" "yearly_energy"


#############################
# Housing Interventions PCS #
#############################

# seperately and one together.
aggregate_minos_manchester_EPCG_PCS:
	python3 minos/outcomes/make_lineplots_macros.py  "energy_manchester_scaled" "EPCG" "SF_12_PCS"

aggregate_minos_manchester_GBIS_PCS:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "GBIS" "SF_12_PCS"

aggregate_minos_manchester_good_housing_dummy_PCS:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "good_heating_dummy" "SF_12_PCS"

aggregate_minos_manchester_combined_PCS:
	python3 minos/outcomes/make_lineplots_macros.py  "energy_manchester_scaled" "GHD_EPCG_GBIS_combined" "SF_12_PCS"

#################
# PCS Quintiles #
#################

#####################
# Intervention Cost #
#####################


# seperately and one together.
aggregate_minos_manchester_EPCG_cost:
	python3 minos/outcomes/make_lineplots_macros.py  "energy_manchester_scaled" "EPCG" "boost_amount"

aggregate_minos_manchester_GBIS_cost:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "GBIS" "boost_amount"

aggregate_minos_manchester_good_housing_dummy_cost:
	python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "good_heating_dummy" "boost_amount"

aggregate_minos_manchester_combined_cost:
	python3 minos/outcomes/make_lineplots_macros.py  "energy_manchester_scaled" "GHD_EPCG_GBIS_combined_intervention_cost" "intervention_cost"

#################
# PCS Quintiles #
#################

################
# QALY #########
################


QALY_baseline: MODE=$(EXPERIMENT)
QALY_baseline: INTERVENTION=baseline
QALY_baseline:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_GHD: MODE=$(EXPERIMENT)
QALY_GHD: INTERVENTION=goodHeatingDummy
QALY_GHD:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_EPCG: MODE=$(EXPERIMENT)
QALY_EPCG: INTERVENTION=EPCG
QALY_EPCG:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_GBIS: MODE=$(EXPERIMENT)
QALY_GBIS: INTERVENTION=GBIS
QALY_GBIS:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

all_energy_QALY: EXPERIMENT=energy_manchester_scaled
all_energy_QALY: QALY_baseline QALY_GHD QALY_EPCG QALY_GBIS
all_energy_QALY:
	python3 minos/outcomes/QALY_plot.py



QALYs_GHB: EXPERIMENT=scotland_scaled
QALYs_: STARTYEAR=2020
QALY_vis_GHB: QALY_baseline
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='good_heating_dummy', start.year='$(STARTYEAR)'), output_file = 'QALY_GHD.html')"

QALY_vis_EPCG: QALY_baseline
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='EPCG', start.year='$(STARTYEAR)'), output_file = 'QALY_EPCG.html')"

QALY_vis_GBIS: QALY_baseline
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='GBIS', start.year='$(STARTYEAR)'), output_file = 'QALY_GBIS.html')"


QALYs_UC_scotland: EXPERIMENT=scotland_scaled
QALYs_UC_scotland: STARTYEAR=2020
QALYs_UC_scotland: QALY_vis_SCP_25_UC QALY_vis_SCP_50_UC QALY_vis_SCP_75_UC QALY_vis_SCP_100_UC

# running everything needed for paper 3.
BIG_DADDY_PAPER_3:
BIG_DADDY_PAPER_3: aggregate_minos_manchester_GBIS_quintiles aggregate_minos_manchester_EPCG_quintiles
BIG_DADDY_PAPER_3: GBIS_GMCA_map EPCG_GMCA_map
BIG_DADDY_PAPER_3: aggregate_minos_manchester_combined aggregate_minos_manchester_combined_PCS
BIG_DADDY_PAPER_3: aggregate_minos_manchester_combined_cost aggregate_minos_manchester_EPCG_GBIS_combined_yearly_energy
BIG_DADDY_PAPER_3: all_energy_QALY
