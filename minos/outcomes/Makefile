
##############################################################
# SCP & CPR output summary generation in R #
##############################################################

scp_test_sum:
	bash scripts/arc_read_sum_submit.sh default_config scp_summary_out 50UniversalCredit

scp_local_test_sum:
	Rscript minos/read_summarise_2.R default_config scp_summary_out baseline
	Rscript minos/read_summarise_2.R default_config scp_summary_out 50UniversalCredit

scp_summary_yearly:
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out baseline 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 10UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 20UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 25UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 30UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 35UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 40UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 45UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 50UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 60UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 70UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 80UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 90UniversalCredit 2020 2035
	bash scripts/arc_yearly_sum_submit.sh default_config scp_summary_out 100UniversalCredit 2020 2035

scp_summary_allyears:
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out baseline
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 10UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 20UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 25UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 30UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 35UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 40UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 45UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 50UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 60UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 70UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 80UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 90UniversalCredit
	Rscript minos/combine_summaries_all_years.R default_config scp_summary_out 100UniversalCredit

CPR_local_test_sum:
	Rscript minos/read_summarise_2.R default_config cpr_summary_out baseline
	Rscript minos/read_summarise_2.R default_config cpr_summary_out ChildPovertyReductionRELATIVE_2

CPR_all_sum:
	bash scripts/arc_read_sum_submit.sh default_cpr cpr_summary_out baseline
	#bash scripts/arc_read_sum_submit.sh default_cpr cpr_summary_out ChildPovertyReductionRELATIVE
	bash scripts/arc_read_sum_submit.sh default_cpr cpr_summary_out ChildPovertyReductionRELATIVE_2
	bash scripts/arc_read_sum_submit.sh default_cpr cpr_summary_out ChildPovertyReductionABSOLUTE

CPR_baseline_local_test:
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2020
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2021
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2022
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2023
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2024
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2025
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2026
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2027
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2028
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2029
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2030
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2031
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2032
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2033
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2034
	Rscript minos/read_summarise_1year.R default_config cpr_summary_out_test baseline_batch 2035

CPR_baseline_allyears_test:
	Rscript minos/combine_summaries_all_years.R default_config cpr_summary_out baseline_batch

CPR_together_local_test:
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2020
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2021
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2022
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2023
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2024
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2025
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2026
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2027
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2028
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2029
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2030
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2031
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2032
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2033
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2034
	Rscript minos/read_sum_together_1year.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2 2035

CPR_together_relative_allyears_test:
	Rscript minos/combine_together_all_years.R default_batch cpr_summary_out_test ChildPovertyReductionRELATIVE_2

## ARC SUBMISSION SUMMARIES

CPR_baseline_yearly:
	bash scripts/arc_yearly_sum_submit.sh scotland_cpr cpr_sum_out baseline 2020 2035

CPR_relative_new_yearly:
	bash scripts/arc_yearly_sum_submit.sh scotland_cpr cpr_sum_out ChildPovertyReduction 2020 2035
	bash scripts/arc_together_yearly_sum_submit.sh scotland_cpr cpr_sum_out ChildPovertyReduction 2020 2035

CPR_relative_variable_yearly:
	bash scripts/arc_yearly_sum_submit.sh scotland_cpr cpr_sum_out ChildPovertyReductionRELATIVE 2020 2035
	bash scripts/arc_together_yearly_sum_submit.sh scotland_cpr cpr_sum_out ChildPovertyReductionRELATIVE 2020 2035

CPR_relative_yearly:
	bash scripts/arc_yearly_sum_submit.sh scotland_cpr cpr_sum_out ChildPovertyReductionRELATIVE_2 2020 2035
	bash scripts/arc_together_yearly_sum_submit.sh scotland_cpr cpr_sum_out ChildPovertyReductionRELATIVE_2 2020 2035

CPR_absolute_yearly:
	bash scripts/arc_yearly_sum_submit.sh scotland_cpr cpr_sum_out ChildPovertyReductionABSOLUTE 2020 2035
	bash scripts/arc_together_yearly_sum_submit.sh scotland_cpr cpr_sum_out ChildPovertyReductionABSOLUTE 2020 2035

CPR_sustain_yearly:
	bash scripts/arc_yearly_sum_submit.sh scotland_cpr cpr_sum_out ChildPovertyReductionSUSTAIN 2020 2035

CPR_all_yearly: CPR_baseline_yearly CPR_relative_new_yearly CPR_relative_variable_yearly CPR_relative_yearly CPR_absolute_yearly

## COMBINE SUMMARIES

CPR_baseline_allyears:
	Rscript minos/combine_summaries_all_years.R scotland_cpr cpr_sum_out baseline

CPR_relative_new_allyears:
	Rscript minos/combine_summaries_all_years.R scotland_cpr cpr_sum_out ChildPovertyReduction
	Rscript minos/combine_together_all_years.R scotland_cpr cpr_sum_out ChildPovertyReduction

CPR_relative_variable_allyears:
	Rscript minos/combine_summaries_all_years.R scotland_cpr cpr_sum_out ChildPovertyReductionRELATIVE
	Rscript minos/combine_together_all_years.R scotland_cpr cpr_sum_out ChildPovertyReductionRELATIVE

CPR_relative_allyears:
	Rscript minos/combine_summaries_all_years.R scotland_cpr cpr_sum_out ChildPovertyReductionRELATIVE_2
	Rscript minos/combine_together_all_years.R scotland_cpr cpr_sum_out ChildPovertyReductionRELATIVE_2

CPR_absolute_allyears:
	Rscript minos/combine_summaries_all_years.R scotland_cpr cpr_sum_out ChildPovertyReductionABSOLUTE
	Rscript minos/combine_together_all_years.R scotland_cpr cpr_sum_out ChildPovertyReductionABSOLUTE

CPR_sustain_allyears:
	Rscript minos/combine_summaries_all_years.R scotland_cpr cpr_sum_out ChildPovertyReductionSUSTAIN

CPR_all_allyears: CPR_baseline_allyears CPR_relative_new_allyears CPR_relative_variable_allyears CPR_relative_allyears CPR_absolute_allyears

## PRIORITY SUBGROUP

CPR_psub_yearly:
	bash scripts/arc_yearly_sum_submit.sh priority_subgroup cpr_sum_out baseline 2020 2035
	bash scripts/arc_yearly_sum_submit.sh priority_subgroup cpr_sum_out ChildPovertyReductionRELATIVE_psub 2020 2035
	bash scripts/arc_together_yearly_sum_submit.sh priority_subgroup cpr_sum_out ChildPovertyReductionRELATIVE_psub 2020 2035
	bash scripts/arc_yearly_sum_submit.sh priority_subgroup cpr_sum_out ChildPovertyReductionABSOLUTE_psub 2020 2035
	bash scripts/arc_together_yearly_sum_submit.sh priority_subgroup cpr_sum_out ChildPovertyReductionABSOLUTE_psub 2020 2035

CPR_psub_allyears:
	Rscript minos/combine_summaries_all_years.R priority_subgroup cpr_sum_out baseline
	Rscript minos/combine_summaries_all_years.R priority_subgroup cpr_sum_out ChildPovertyReductionRELATIVE_psub
	Rscript minos/combine_together_all_years.R priority_subgroup cpr_sum_out ChildPovertyReductionRELATIVE_psub
	Rscript minos/combine_summaries_all_years.R priority_subgroup cpr_sum_out ChildPovertyReductionABSOLUTE_psub
	Rscript minos/combine_together_all_years.R priority_subgroup cpr_sum_out ChildPovertyReductionABSOLUTE_psub

## DEFAULT US POPULATION

CPR_yearly: SUBDIR=scotland_cpr_MARS
CPR_yearly:
	bash scripts/arc_yearly_sum_submit.sh $(SUBDIR) cpr_sum_out baseline 2020 2035
	bash scripts/arc_yearly_sum_submit.sh $(SUBDIR) cpr_sum_out ChildPovertyReduction 2020 2035
	bash scripts/arc_together_yearly_sum_submit.sh $(SUBDIR) cpr_sum_out ChildPovertyReduction 2020 2035
	bash scripts/arc_yearly_sum_submit.sh $(SUBDIR) cpr_sum_out ChildPovertyReductionRELATIVE_2 2020 2035
	bash scripts/arc_together_yearly_sum_submit.sh $(SUBDIR) cpr_sum_out ChildPovertyReductionRELATIVE_2 2020 2035
	bash scripts/arc_yearly_sum_submit.sh $(SUBDIR) cpr_sum_out ChildPovertyReductionABSOLUTE 2020 2035
	bash scripts/arc_together_yearly_sum_submit.sh $(SUBDIR) cpr_sum_out ChildPovertyReductionABSOLUTE 2020 2035
	# bash scripts/arc_yearly_sum_submit.sh $(SUBDIR) cpr_sum_out ChildPovertyReductionRELATIVE 2020 2035
	# bash scripts/arc_together_yearly_sum_submit.sh $(SUBDIR) cpr_sum_out ChildPovertyReductionRELATIVE 2020 2035

CPR_allyears: SUBDIR=scotland_cpr_MARS
CPR_allyears:
	Rscript minos/combine_summaries_all_years.R $(SUBDIR) cpr_sum_out baseline
	Rscript minos/combine_summaries_all_years.R $(SUBDIR) cpr_sum_out ChildPovertyReduction
	Rscript minos/combine_together_all_years.R $(SUBDIR) cpr_sum_out ChildPovertyReduction
	Rscript minos/combine_summaries_all_years.R $(SUBDIR) cpr_sum_out ChildPovertyReductionRELATIVE_2
	Rscript minos/combine_together_all_years.R $(SUBDIR) cpr_sum_out ChildPovertyReductionRELATIVE_2
	Rscript minos/combine_summaries_all_years.R $(SUBDIR) cpr_sum_out ChildPovertyReductionABSOLUTE
	Rscript minos/combine_together_all_years.R $(SUBDIR) cpr_sum_out ChildPovertyReductionABSOLUTE
	# Rscript minos/combine_summaries_all_years.R $(SUBDIR) cpr_sum_out ChildPovertyReductionRELATIVE
	# Rscript minos/combine_together_all_years.R $(SUBDIR) cpr_sum_out ChildPovertyReductionRELATIVE

##############################################################
# SCP & CPR Visualisation Notebooks #
##############################################################

scp_summary_vis:
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/SCP_vis_summary.Rmd')"

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

vis_25_50_by_5_together_UC: MODE="default_config"
vis_25_50_by_5_together_UC:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_25_50_by_5_together_UC"

vis_10_100_by_10_together_UC: MODE="default_config"
vis_10_100_by_10_together_UC:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_100_by_10_together_UC"

vis_10_50_by_10_together_UC: MODE="default_config"
vis_10_50_by_10_together_UC:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_50_by_10_together_UC"

vis_60_100_by_10_together_UC: MODE="default_config"
vis_60_100_by_10_together_UC:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_60_to_100_by_10_together_UC"

vis_together_UC: vis_25_50_by_5_together_UC vis_10_100_by_10_together_UC
vis_together_UC: vis_10_50_by_10_together_UC vis_60_100_by_10_together_UC

### UC, kids, and RelativePoverty

vis_25_50_by_5_together_UC_RelPov: MODE="default_config"
vis_25_50_by_5_together_UC_RelPov:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_25_50_by_5_together_UC_RelPov"

vis_10_100_by_10_together_UC_RelPov: MODE="default_config"
vis_10_100_by_10_together_UC_RelPov:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_100_by_10_together_UC_RelPov"

vis_10_50_by_10_together_UC_RelPov: MODE="default_config"
vis_10_50_by_10_together_UC_RelPov:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_50_by_10_together_UC_RelPov"

vis_60_100_by_10_together_UC_RelPov: MODE="default_config"
vis_60_100_by_10_together_UC_RelPov:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_60_to_100_by_10_together_UC_RelPov"

vis_together_UC_RelPov: vis_25_50_by_5_together_UC_RelPov vis_10_100_by_10_together_UC_RelPov
vis_together_UC_RelPov: vis_10_50_by_10_together_UC_RelPov vis_60_100_by_10_together_UC_RelPov

#test_vis: MODE="default_config"
#test_vis:
#		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_25_to_100_by_25_together_UC_RelPov"

### UC, kids, and AbsolutePoverty

vis_25_50_by_5_together_UC_AbsPov: MODE="default_config"
vis_25_50_by_5_together_UC_AbsPov:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_25_50_by_5_together_UC_AbsPov"

vis_10_100_by_10_together_UC_AbsPov: MODE="default_config"
vis_10_100_by_10_together_UC_AbsPov:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_100_by_10_together_UC_AbsPov"

vis_10_50_by_10_together_UC_AbsPov: MODE="default_config"
vis_10_50_by_10_together_UC_AbsPov:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_50_by_10_together_UC_AbsPov"

vis_60_100_by_10_together_UC_AbsPov: MODE="default_config"
vis_60_100_by_10_together_UC_AbsPov:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_60_to_100_by_10_together_UC_AbsPov"

vis_together_UC_AbsPov: vis_25_50_by_5_together_UC_AbsPov vis_10_100_by_10_together_UC_AbsPov
vis_together_UC_AbsPov: vis_10_50_by_10_together_UC_AbsPov vis_60_100_by_10_together_UC_AbsPov

### UC, kids, and Gender

vis_25_50_by_5_together_UC_gender: MODE="default_config"
vis_25_50_by_5_together_UC_gender:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_25_50_by_5_together_UC_male"
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_25_50_by_5_together_UC_female"

vis_10_100_by_10_together_UC_gender: MODE="default_config"
vis_10_100_by_10_together_UC_gender:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_100_by_10_together_UC_male"
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_100_by_10_together_UC_female"

vis_10_50_by_10_together_UC_gender: MODE="default_config"
vis_10_50_by_10_together_UC_gender:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_50_by_10_together_UC_male"
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_10_to_50_by_10_together_UC_female"

vis_60_100_by_10_together_UC_gender: MODE="default_config"
vis_60_100_by_10_together_UC_gender:
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_60_to_100_by_10_together_UC_male"
		python3 minos/outcomes/make_lineplots_macros.py $(MODE) "incremental_60_to_100_by_10_together_UC_female"

vis_together_UC_Gender: vis_25_50_by_5_together_UC_gender vis_10_100_by_10_together_UC_gender
vis_together_UC_Gender: vis_10_50_by_10_together_UC_gender vis_60_100_by_10_together_UC_gender



vis_together_all_UC: vis_together_UC vis_together_UC_RelPov vis_together_UC_AbsPov

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
