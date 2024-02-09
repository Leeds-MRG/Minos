###################
## Test Simulations
###################

# Default parameters
MODE=default_config
RUN_CONFIG=$(CONFIG)/default.yaml

.PHONY: testRun testRun_Intervention test_run

testRun: ### Start a test run of the microsimulation using configuration defined in testConfig.yaml
#testRun: setup
#	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml --output_subdir 'testRun'

#testRun_Intervention: setup
#	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml --output_subdir 'testRun' -i 'livingWageIntervention'

# Just test two baseline and living wage interventions locally before running big jobs on hpcs.
test_run: MODE=default_config
test_run: RUN_CONFIG=$(CONFIG)/default.yaml
test_run: baseline intervention_energyDownLift

test_run_all: MODE=default_config
test_run_all: RUN_CONFIG=$(CONFIG)/default.yaml
test_run_all: baseline intervention_hhIncome intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift

test_scot_run: MODE=scotland_mode
test_scot_run: RUN_CONFIG=$(CONFIG)/scot_default.yaml
test_scot_run: baseline intervention_livingWage

test_SIPHER7_run: MODE=SIPHER7
test_SIPHER7_run: RUN_CONFIG=$(CONFIG)/SIPHER7.yaml
test_SIPHER7_run: SIPHER7_base
SIPHER7_base: setup_S7
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE)



###################
## Experiment Runs
###################

.phony: all_scenarios baseline intervention_hhIncome intervention_hhIncomeChildUplift
.phony: intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift
.phony: all_scenarios all_scot_scenarios

############################################
## Local single runs of MINOS SF12 experiment.
############################################

baseline: ### Baseline run of MINOS, using configuration defined in testConfig.yaml
baseline: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE)

baseline_inflated: setup_inflated
	$(PYTHON) scripts/run.py -c $(CONFIG)/inflated_default.yaml -o inflated_default

intervention_hhIncome: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomeIntervention'

intervention_hhIncomeChildUplift: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomeChildUplift'

###########################################
# Child Uplifts Over Amount and Condition #
###########################################

intervention_25All: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '25All'

intervention_50All: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '50All'

intervention_75All: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '75All'

intervention_100All: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '100All'

##########################################################################
# Relative Poverty Interventions.
##########################################################################

intervention_25RelativePoverty: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '25RelativePoverty'

intervention_50RelativePoverty: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '50RelativePoverty'

intervention_75RelativePoverty: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '75RelativePoverty'

intervention_100RelativePoverty: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '100RelativePoverty'

##########################################################################
# doing a stupid block of six interventions for now from 25 to 50 by £5.
# probably a neater way to do this.
##########################################################################

intervention_25UniversalCredit_scotland: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c config/scotland_scaled.yaml -o scotland_scaled -i '25UniversalCredit'


intervention_25UniversalCredit: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '25UniversalCredit'

intervention_30UniversalCredit: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '30UniversalCredit'

intervention_35UniversalCredit: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '35UniversalCredit'

intervention_40UniversalCredit: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '40UniversalCredit'

intervention_45UniversalCredit: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '45UniversalCredit'

intervention_50UniversalCredit: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '50UniversalCredit'

intervention_75UniversalCredit: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '75UniversalCredit'

intervention_100UniversalCredit: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '100UniversalCredit'

##########################################################################
# Priority Subgroups
##########################################################################

intervention_25Priority: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '25Priority'

intervention_50Priority: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '50Priority'

intervention_75Priority: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '75Priority'

intervention_100Priority: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i '100Priority'

##########################################################################

intervention_PovertyLineChildUplift: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomePovertyLineChildUplift'

############################
# Living Wage Intervention #
############################

intervention_livingWage: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'livingWageIntervention'

###############################
# Energy Crisis Interventions #
###############################

intervention_energyDownLift: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownlift'

intervention_energyDownLiftNoSupport: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownliftNoSupport'

#####################################################
# Short Cut Commands for Many Interventions at Once #
#####################################################

glasgow_baseline: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o "glasgow_scaled" -i 'baseline'

intervention_EPCG: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o "glasgow_scaled" -i 'EPCG'

intervention_EBSS: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o "glasgow_scaled" -i 'EBSS'
	
intervention_childPovertyReduction: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReductionRANDOM'
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReductionSUSTAIN'
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/child_poverty_reduction_vis.Rmd')"
	firefox file://$(OUTCOMES)/child_poverty_reduction_vis.html

# ---
# HR 20/11/23 Some testing for new all-purpose child poverty intervention
intervention_cp1_sustain: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReductionSUSTAIN'

intervention_cp_default: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default_child_poverty.yaml -o child_poverty_config -i 'ChildPovertyIntervention'
# ---

all_scenarios: MODE = default_config
all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
all_scenarios: baseline intervention_hhIncomeChildUplift intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift intervention_energyDownLiftNoSupport

all_child_uplifts: MODE=default_config
all_child_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
all_child_uplifts: baseline intervention_25All intervention_50All intervention_75All intervention_100All

poverty_line_child_uplifts: MODE=default_config
poverty_line_child_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
poverty_line_child_uplifts: baseline intervention_25RelativePoverty intervention_50RelativePoverty intervention_75RelativePoverty intervention_100RelativePoverty

universal_credit_child_uplifts: MODE=default_config
universal_credit_child_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
universal_credit_child_uplifts: baseline intervention_25UniversalCredit intervention_50UniversalCredit intervention_75UniversalCredit intervention_100UniversalCredit

all_scot_scenarios: MODE=scotland_mode
all_scot_scenarios: RUN_CONFIG=$(CONFIG)/scot_default.yaml
all_scot_scenarios: scot_setup baseline intervention_hhIncomeChildUplift intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift


############################################
## Local single runs of MINOS SF12 experiments using the glasgow synthetic population.
############################################

test_baseline:
	$(PYTHON) scripts/run.py -c $(CONFIG)/test_config.yaml -o test_config

baseline: ### Baseline run of MINOS, using configuration defined in testConfig.yaml
baseline_glasgow: setup_glasgow_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o glasgow_scaled

intervention_hhIncome_glasgow: setup_glasgow_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o glasgow_scaled -i 'hhIncomeIntervention'

intervention_hhIncomeChildUplift_glasgow: setup_glasgow_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o glasgow_scaled -i 'hhIncomeChildUplift'

intervention_PovertyLineChildUplift_glasgow: setup_glasgow_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o glasgow_scaled -i 'hhIncomePovertyLineChildUplift'

intervention_livingWage_glasgow: setup_glasgow_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o glasgow_scaled -i 'livingWageIntervention'

intervention_energyDownLift_glasgow: setup_glasgow_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o glasgow_scaled -i 'energyDownlift'

intervention_energyDownLiftNoSupport_glasgow: setup_glasgow_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/glasgow_scaled.yaml -o glasgow_scaled -i 'energyDownliftNoSupport'

############################################
## Local single runs of MINOS SF12 experiments using the scotland synthetic population.
############################################

baseline: ### Baseline run of MINOS, using configuration defined in testConfig.yaml
baseline_scotland: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled

intervention_hhIncome_scotland: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled -i 'hhIncomeIntervention'

intervention_hhIncomeChildUplift_scotland: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled -i 'hhIncomeChildUplift'

intervention_PovertyLineChildUplift_scotland: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled -i 'hhIncomePovertyLineChildUplift'

intervention_livingWage_scotland: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled -i 'livingWageIntervention'

intervention_energyDownLift_scotland: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled -i 'energyDownlift'

intervention_energyDownLiftNoSupport_scotland: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled -i 'energyDownliftNoSupport'


############################################
## Local single runs of MINOS SF12 experiments using the UK (GB) synthetic population.
############################################

baseline: ### Baseline run of MINOS, using configuration defined in testConfig.yaml
baseline_uk: setup_uk_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/uk_scaled.yaml -o uk_scaled

intervention_hhIncome_uk: setup_uk_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/uk_scaled.yaml -o uk_scaled -i 'hhIncomeIntervention'

intervention_hhIncomeChildUplift_uk: setup_uk_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/uk_scaled.yaml -o uk_scaled -i 'hhIncomeChildUplift'

intervention_PovertyLineChildUplift_uk: setup_uk_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/uk_scaled.yaml -o uk_scaled -i 'hhIncomePovertyLineChildUplift'

intervention_livingWage_uk: setup_uk_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/uk_scaled.yaml -o uk_scaled -i 'livingWageIntervention'

intervention_energyDownLift_uk: setup_uk_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/uk_scaled.yaml -o uk_scaled -i 'energyDownlift'

intervention_energyDownLiftNoSupport_uk: setup_uk_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/uk_scaled.yaml -o uk_scaled -i 'energyDownliftNoSupport'


#####################################
## Running MINOS scenarios on Arc4
#####################################

.phony: arc4_baseline arc4_intervention_hhIncome arc4_intervention_hhIncomeChildUplift
.phony: arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift
.phony: arc4_all_scenarios arc4_all_scot_scenarios arc4_cv_baseline

arc4_baseline:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE)

arc4_intervention_hhIncome:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomeIntervention'

arc4_intervention_hhIncomeChildUplift:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomeChildUplift'

arc4_intervention_PovertyLineChildUplift:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomePovertyLineChildUplift'

##########################################################################

arc4_intervention_25All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '25All'

arc4_intervention_50All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '50All'

arc4_intervention_75All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '75All'

arc4_intervention_100All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '100All'

##########################################################################

arc4_intervention_25RelativePoverty:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '25RelativePoverty'

arc4_intervention_50RelativePoverty:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '50RelativePoverty'

arc4_intervention_75RelativePoverty: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '75RelativePoverty'

arc4_intervention_100RelativePoverty: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '100RelativePoverty'

##########################################################################

arc4_intervention_25UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '25UniversalCredit'

arc4_intervention_30UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '30UniversalCredit'

arc4_intervention_35UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '35UniversalCredit'

arc4_intervention_40UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '40UniversalCredit'

arc4_intervention_45UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '45UniversalCredit'

arc4_intervention_50UniversalCredit:
arc4_intervention_50UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '50UniversalCredit'

arc4_intervention_75UniversalCredit: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '75UniversalCredit'

arc4_intervention_100UniversalCredit: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '100UniversalCredit'

##########################################################################

arc4_intervention_25Priority:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '25Priority'

arc4_intervention_50Priority:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '50Priority'

arc4_intervention_75Priority: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '75Priority'

arc4_intervention_100Priority: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '100Priority'

arc4_intervention_livingWage:
arc4_intervention_livingWage:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'livingWageIntervention'

arc4_intervention_energyDownLift:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownlift'

arc4_intervention_energyDownLiftNoSupport:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownliftNoSupport'

arc4_intervention_childPovertyReduction: setup
	bash scripts/arc_submit.sh -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReductionRANDOM'
	bash scripts/arc_submit.sh -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReductionSUSTAIN'

arc4_intervention_cp_default: setup
	bash scripts/arc_submit.sh -c $(CONFIG)/default_child_poverty.yaml -o child_poverty_config -i 'ChildPovertyIntervention'

arc4_glasgow_baseline: setup
	bash scripts/arc_submit.sh -c $(CONFIG)/glasgow_scaled.yaml -o "glasgow_scaled" -i 'baseline'

arc4_glasgow_25_poverty_line: setup
	bash scripts/arc_submit.sh -c $(CONFIG)/glasgow_scaled.yaml -o "glasgow_scaled" -i 'hhIncomePovertyLineChildUplift'

arc4_EPCG: setup
	bash scripts/arc_submit.sh -c $(CONFIG)/glasgow_scaled.yaml -o "glasgow_scaled" -i 'EPCG'

arc4_EBSS: setup
	bash scripts/arc_submit.sh -c $(CONFIG)/glasgow_scaled.yaml -o "glasgow_scaled" -i 'EBSS'


arc4_all_scenarios: MODE=default_config
arc4_all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_scenarios: arc4_baseline arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift arc4_intervention_energyDownLiftNoSupport

arc4_all_child_uplifts: MODE=scaled_glasgow #MODE=default_config
arc4_all_child_uplifts: RUN_CONFIG=$(CONFIG)/glasgow_scaled.yaml#/default.yaml
arc4_all_child_uplifts: arc4_baseline arc4_intervention_25All arc4_intervention_50All arc4_intervention_75All arc4_intervention_100All

arc4_poverty_line_child_uplifts: MODE=default_config
arc4_poverty_line_child_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_poverty_line_child_uplifts: arc4_baseline arc4_intervention_25RelativePoverty arc4_intervention_50RelativePoverty arc4_intervention_75RelativePoverty arc4_intervention_100RelativePoverty

arc4_scotland_universal_credit_child_uplifts:
arc4_scotland_universal_credit_child_uplifts: MODE=scaled_scotland #MODE=default_config
arc4_scotland_universal_credit_child_uplifts: RUN_CONFIG=$(CONFIG)/scotland_scaled.yaml#/default.yaml
arc4_scotland_universal_credit_child_uplifts: arc4_baseline arc4_intervention_25UniversalCredit arc4_intervention_30UniversalCredit arc4_intervention_35UniversalCredit arc4_intervention_40UniversalCredit arc4_intervention_45UniversalCredit arc4_intervention_50UniversalCredit

arc4_universal_credit_child_uplifts:
arc4_universal_credit_child_uplifts: MODE=default_config
arc4_universal_credit_child_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_universal_credit_child_uplifts: arc4_baseline arc4_intervention_25UniversalCredit arc4_intervention_30UniversalCredit arc4_intervention_35UniversalCredit arc4_intervention_40UniversalCredit arc4_intervention_45UniversalCredit arc4_intervention_50UniversalCredit



arc4_priority_child_uplifts: MODE=scaled_glasgow #MODE=default_config
arc4_priority_child_uplifts: RUN_CONFIG=$(CONFIG)/glasgow_scaled.yaml#/default.yaml
arc4_priority_child_uplifts: arc4_scotland_baseline arc4_intervention_25Priority arc4_intervention_50Priority arc4_intervention_75Priority arc4_intervention_100Priority

arc4_all_25_uplifts: MODE=default_config
arc4_all_25_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_25_uplifts: arc4_baseline arc4_intervention_25RelativePoverty arc4_intervention_25All arc4_intervention_25UniversalCredit

arc4_all_scot_scenarios: MODE=scotland_mode
arc4_all_scot_scenarios: RUN_CONFIG=$(CONFIG)/scot_default.yaml
arc4_all_scot_scenarios: arc4_baseline arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift
arc4_all_scenarios: arc4_baseline arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift arc4_intervention_energyDownLiftNoSupport

## All default scenarios
arc4_all_scenarios_default: setup
arc4_all_scenarios_default: MODE=default_config
arc4_all_scenarios_default: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_scenarios_default: arc4_all_scenarios

## All SF12 scenarios using glasgow scaled population
arc4_all_scenarios_glasgow: setup_glasgow_scaled
arc4_all_scenarios_glasgow: MODE=SF12_glasgow_scaled
arc4_all_scenarios_glasgow: RUN_CONFIG=$(CONFIG)/glasgow_scaled.yaml
arc4_all_scenarios_glasgow: arc4_all_scenarios

## All SF12 scenarios using glasgow scaled population
arc4_all_scenarios_uk: setup_uk_scaled
arc4_all_scenarios_uk: MODE=SF12_uk_scaled
arc4_all_scenarios_uk: RUN_CONFIG=$(CONFIG)/uk_scaled.yaml
arc4_all_scenarios_uk: arc4_all_scenarios

## All Scotland scenarios
## DEPRECATED - these have been superseded by the glasgow synthetic population scenarios
arc4_all_scenarios_scot: setup
arc4_all_scenarios_scot: MODE=scotland_mode
arc4_all_scenarios_scot: RUN_CONFIG=$(CONFIG)/scot_default.yaml
arc4_all_scenarios_scot: arc4_all_scenarios

## All SIPHER7 Equivalent Income scenarios
arc4_all_scenarios_S7: setup_S7
arc4_all_scenarios_S7: MODE=SIPHER7
arc4_all_scenarios_S7: RUN_CONFIG=$(CONFIG)/SIPHER7.yaml
arc4_all_scenarios_S7: arc4_all_scenarios

## All SIPHER7 Equivalent Income scenarios with Glasgow synthetic data
arc4_all_scenarios_S7_glasgow: setup_glasgow_scaled_S7
arc4_all_scenarios_S7_glasgow: MODE=SIPHER7_glasgow
arc4_all_scenarios_S7_glasgow: RUN_CONFIG=$(CONFIG)/S7_glasgow_scaled.yaml
arc4_all_scenarios_S7_glasgow: arc4_all_scenarios

arc4_all_social_science_concept_scenarios: MODE=default_config
arc4_all_social_science_concept_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_social_science_concept_scenarios: arc4_baseline arc4_intervention_25UniversalCredit arc4_intervention_25RelativePoverty arc4_intervention_livingWage arc4_intervention_energyDownLift arc4_intervention_energyDownLiftNoSupport arc4_intervention_50UniversalCredit arc4_intervention_50RelativePoverty

arc4_concept_note_child_lineplots: setup
arc4_concept_note_child_lineplots: MODE=default_config
arc4_concept_note_child_lineplots: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_concept_note_child_lineplots: arc4_baseline arc4_intervention_25UniversalCredit arc4_intervention_25RelativePoverty arc4_intervention_50UniversalCredit arc4_intervention_50RelativePoverty

arc4_cv_baseline: cv_setup
	bash scripts/arc_submit.sh -c $(CONFIG)/cross_validation.yaml -o cross_validation

#####################################
# Running scenarios on beefy HPC in LIDA.
#####################################

.phony: beefy_baseline beefy_intervention_hhIncome beefy_intervention_hhIncomeChildUplift
.phony: beefy_intervention_PovertyLineChildUplift beefy_intervention_livingWage beefy_intervention_energyDownLift
.phony: beefy_all_scenarios beefy_all_scot_scenarios

beefy_baseline: ### Baseline run of MINOS on beefy. Runs 100 iterations with no interventions at all. Just status quo.
beefy_baseline: setup
	bash scripts/slurm_submit.sh -c $(RUN_CONFIG) -o $(MODE)

beefy_intervention_hhIncome: setup
	bash scripts/slurm_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomeIntervention'

beefy_intervention_hhIncomeChildUplift: setup
	bash scripts/slurm_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomeChildUplift'

beefy_intervention_PovertyLineChildUplift: setup
	bash scripts/slurm_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomePovertyLineChildUplift'

beefy_intervention_livingWage: setup
	bash scripts/slurm_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'livingWageIntervention'

beefy_intervention_energyDownLift: setup
	bash scripts/slurm_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownlift'

beefy_intervention_energyDownLiftNoSupport: setup
	bash scripts/slurm_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownliftNoSupport'

beefy_all_scenarios: MODE=default_config
beefy_all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
beefy_all_scenarios: beefy_baseline beefy_intervention_hhIncomeChildUplift beefy_intervention_PovertyLineChildUplift beefy_intervention_livingWage beefy_intervention_energyDownLift, beefy_intervention_energyDownLiftNoSupport

beefy_all_scot_scenarios: MODE=scotland_mode
beefy_all_scot_scenarios: RUN_CONFIG=$(CONFIG)/scot_default.yaml
beefy_all_scot_scenarios: beefy_baseline beefy_intervention_hhIncomeChildUplift beefy_intervention_PovertyLineChildUplift beefy_intervention_livingWage beefy_intervention_energyDownLift

#####################################
# Validation runs
#####################################

cv_default: cv_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_default1.yaml -o cv/default1
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_default2.yaml -o cv/default2
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_default3.yaml -o cv/default3
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_default4.yaml -o cv/default4
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_default5.yaml -o cv/default5

cv_SIPHER7: cv_S7_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_S7_1.yaml -o cv/S7_1
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_S7_2.yaml -o cv/S7_2
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_S7_3.yaml -o cv/S7_3
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_S7_4.yaml -o cv/S7_4
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation/cross_validation_S7_5.yaml -o cv/S7_5


#####################################
# SIPHER7 - Equivalent Income
#####################################

S7_all_scenarios: S7_baseline S7_intervention_hhIncomeChildUplift S7_intervention_PovertyLineChildUplift
S7_all_scenarios: S7_intervention_livingWage S7_intervention_energyDownLift S7_intervention_energyDownLiftNoSupport

S7_baseline: setup_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/SIPHER7.yaml -o SIPHER7

S7_intervention_hhIncome: setup_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/SIPHER7.yaml -o SIPHER7 -i 'hhIncomeIntervention'

S7_intervention_hhIncomeChildUplift: setup_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/SIPHER7.yaml -o SIPHER7 -i 'hhIncomeChildUplift'

S7_intervention_PovertyLineChildUplift: setup_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/SIPHER7.yaml -o SIPHER7 -i 'hhIncomePovertyLineChildUplift'

S7_intervention_livingWage: setup_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/SIPHER7.yaml -o SIPHER7 -i 'livingWageIntervention'

S7_intervention_energyDownLift: setup_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/SIPHER7.yaml -o SIPHER7 -i 'energyDownlift'

S7_intervention_energyDownLiftNoSupport: setup_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/SIPHER7.yaml -o SIPHER7 -i 'energyDownliftNoSupport'

#####################################
# SIPHER7 - Equivalent Income - GLASGOW SCALED DATA
#####################################

S7_all_scenarios_glasgow_synthetic: S7_baseline_glasgow S7_intervention_hhIncomeChildUplift_glasgow
S7_all_scenarios_glasgow_synthetic: S7_intervention_PovertyLineChildUplift_glasgow S7_intervention_livingWage_glasgow
S7_all_scenarios_glasgow_synthetic: S7_intervention_energyDownLift_glasgow S7_intervention_energyDownLiftNoSupport_glasgow

S7_baseline_glasgow: setup_glasgow_scaled_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/S7_glasgow_scaled.yaml -o SIPHER7_glasgow

S7_intervention_hhIncome_glasgow: setup_glasgow_scaled_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/S7_glasgow_scaled.yaml -o SIPHER7_glasgow -i 'hhIncomeIntervention'

S7_intervention_hhIncomeChildUplift_glasgow: setup_glasgow_scaled_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/S7_glasgow_scaled.yaml -o SIPHER7_glasgow -i 'hhIncomeChildUplift'

S7_intervention_PovertyLineChildUplift_glasgow: setup_glasgow_scaled_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/S7_glasgow_scaled.yaml -o SIPHER7_glasgow -i 'hhIncomePovertyLineChildUplift'

S7_intervention_livingWage_glasgow: setup_glasgow_scaled_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/S7_glasgow_scaled.yaml -o SIPHER7_glasgow -i 'livingWageIntervention'

S7_intervention_energyDownLift_glasgow: setup_glasgow_scaled_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/S7_glasgow_scaled.yaml -o SIPHER7_glasgow -i 'energyDownlift'

S7_intervention_energyDownLiftNoSupport_glasgow: setup_glasgow_scaled_S7
	$(PYTHON) scripts/run.py -c $(CONFIG)/S7_glasgow_scaled.yaml -o SIPHER7_glasgow -i 'energyDownliftNoSupport'
