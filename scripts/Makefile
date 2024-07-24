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

intervention_PovertyLineChildUplift: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomePovertyLineChildUplift'

intervention_livingWage: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'livingWageIntervention'

intervention_energyDownLift: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownlift'

intervention_energyDownLiftNoSupport: setup
	$(PYTHON) scripts/run.py -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownliftNoSupport'

all_scenarios: MODE = default_config
all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
all_scenarios: baseline intervention_hhIncomeChildUplift intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift intervention_energyDownLiftNoSupport

all_scot_scenarios: MODE=scotland_mode
all_scot_scenarios: RUN_CONFIG=$(CONFIG)/scot_default.yaml
all_scot_scenarios: scot_setup baseline intervention_hhIncomeChildUplift intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift

############### CHILD POVERTY REDUCTION RUNS ###############

intervention_childPovertyReduction: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReduction'

intervention_childPovertyReductionSUSTAIN: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReductionSUSTAIN'

intervention_childPovertyReductionRelative: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReductionRELATIVE'

intervention_childPovertyReductionRelative_2: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReductionRELATIVE_2'

intervention_childPovertyReductionAbsolute: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config -i 'ChildPovertyReductionABSOLUTE'

child_pov_runs: baseline intervention_childPovertyReductionRelative intervention_childPovertyReductionRelative_2 intervention_childPovertyReductionAbsolute

############### CHILD POVERTY REDUCTION RUNS - SCOTLAND ###############

intervention_childPovertyReduction_SCOTLAND: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled -i 'ChildPovertyReduction'

intervention_childPovertyReductionRelative_2_SCOTLAND: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled -i 'ChildPovertyReductionRELATIVE_2'

intervention_childPovertyReductionAbsolute_SCOTLAND: setup_scotland_scaled
	$(PYTHON) scripts/run.py -c $(CONFIG)/scotland_scaled.yaml -o scotland_scaled -i 'ChildPovertyReductionABSOLUTE'

child_pov_runs_SCOTLAND: baseline_scotland intervention_childPovertyReductionRelative_2_SCOTLAND intervention_childPovertyReductionAbsolute_SCOTLAND

######### NO REPLENISH TESTING #########

baseline_no_replenish:
	$(PYTHON) scripts/run.py -c config/default_noReplenish.yaml -o default_config

intervention_childPovertyReductionRelative_2_no_replenish: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default_noReplenish.yaml -o default_config -i 'ChildPovertyReductionRELATIVE_2'

intervention_childPovertyReductionAbsolute_no_replenish: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default_noReplenish.yaml -o default_config -i 'ChildPovertyReductionABSOLUTE'

child_pov_no_replenish: baseline_no_replenish intervention_childPovertyReductionRelative_2_no_replenish
child_pov_no_replenish: intervention_childPovertyReductionAbsolute_no_replenish

############### PRIORITY SUBGROUP ONLY RUNS RUNS ###############

baseline_psub: setup_scot_priority_sub
	$(PYTHON) scripts/run.py -c $(CONFIG)/priority_subgroup.yaml -o priority_subgroup

intervention_childPovertyReductionRelative_psub: setup_scot_priority_sub
	$(PYTHON) scripts/run.py -c $(CONFIG)/priority_subgroup.yaml -o priority_subgroup -i 'ChildPovertyReductionRELATIVE_psub'

intervention_childPovertyReductionAbsolute_psub: setup_scot_priority_sub
	$(PYTHON) scripts/run.py -c $(CONFIG)/priority_subgroup.yaml -o priority_subgroup -i 'ChildPovertyReductionABSOLUTE_psub'

child_pov_psub: baseline_psub intervention_psub_childPovertyReductionRELATIVE_psub intervention_childPovertyReductionABSOLUTE_psub

############################################
## Local single runs of MINOS SF12 experiments using the glasgow synthetic population.
############################################

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

arc4_intervention_livingWage:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'livingWageIntervention'

arc4_intervention_energyDownLift:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownlift'

arc4_intervention_energyDownLiftNoSupport:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownliftNoSupport'

arc4_all_scenarios: arc4_baseline arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift arc4_intervention_energyDownLiftNoSupport

arc4_baseline_cpr:
	bash scripts/arc_submit.sh -c $(CONFIG)/default.yaml -o $(SUBDIR)

arc4_intervention_childPovertyReduction:
	bash scripts/arc_submit.sh -c $(CONFIG)/default.yaml -o $(SUBDIR) -i 'ChildPovertyReduction'

arc4_intervention_childPovertyReductionRELATIVE:
	bash scripts/arc_submit.sh -c $(CONFIG)/default.yaml -o $(SUBDIR) -i 'ChildPovertyReductionRELATIVE'

arc4_intervention_childPovertyReductionSUSTAIN:
	bash scripts/arc_submit.sh -c $(CONFIG)/default.yaml -o $(SUBDIR) -i 'ChildPovertyReductionSUSTAIN'

arc4_intervention_childPovertyReductionRELATIVE_2:
	bash scripts/arc_submit.sh -c $(CONFIG)/default.yaml -o $(SUBDIR) -i 'ChildPovertyReductionRELATIVE_2'

arc4_intervention_ChildPovertyReductionABSOLUTE:
	bash scripts/arc_submit.sh -c $(CONFIG)/default.yaml -o $(SUBDIR) -i 'ChildPovertyReductionABSOLUTE'

arc4_child_pov_interventions: SUBDIR=default_cpr
arc4_child_pov_interventions: arc4_baseline_cpr arc4_intervention_childPovertyReduction arc4_intervention_childPovertyReductionRELATIVE
arc4_child_pov_interventions: arc4_intervention_childPovertyReductionRELATIVE_2 arc4_intervention_ChildPovertyReductionABSOLUTE

arc4_baseline_cpr_scotland:
	bash scripts/arc_submit.sh -c $(CONFIG)/scotland_scaled.yaml -o $(SUBDIR)

arc4_intervention_childPovertyReduction_scotland:
	bash scripts/arc_submit.sh -c $(CONFIG)/scotland_scaled.yaml -o $(SUBDIR) -i 'ChildPovertyReduction'

arc4_intervention_childPovertyReductionRELATIVE_scotland:
	bash scripts/arc_submit.sh -c $(CONFIG)/scotland_scaled.yaml -o $(SUBDIR) -i 'ChildPovertyReductionRELATIVE'

arc4_intervention_childPovertyReductionSUSTAIN_scotland:
	bash scripts/arc_submit.sh -c $(CONFIG)/scotland_scaled.yaml -o $(SUBDIR) -i 'ChildPovertyReductionSUSTAIN'

arc4_intervention_childPovertyReductionRELATIVE_2_scotland:
	bash scripts/arc_submit.sh -c $(CONFIG)/scotland_scaled.yaml -o $(SUBDIR) -i 'ChildPovertyReductionRELATIVE_2'

arc4_intervention_ChildPovertyReductionABSOLUTE_scotland:
	bash scripts/arc_submit.sh -c $(CONFIG)/scotland_scaled.yaml -o $(SUBDIR) -i 'ChildPovertyReductionABSOLUTE'

arc4_child_pov_scotland: SUBDIR=scotland_cpr_XGB_scaled
arc4_child_pov_scotland: arc4_baseline_cpr_scotland arc4_intervention_childPovertyReduction_scotland
arc4_child_pov_scotland: arc4_intervention_childPovertyReductionRELATIVE_2_scotland arc4_intervention_ChildPovertyReductionABSOLUTE_scotland
# arc4_intervention_childPovertyReductionRELATIVE_scotland

arc4_cp_scot_reduced: SUBDIR=scotland_cpr_XGB_scaled
arc4_cp_scot_reduced: arc4_baseline_cpr_scotland arc4_intervention_childPovertyReduction_scotland

############### PRIORITY SUBGROUP ONLY RUNS RUNS ###############

arc4_baseline_psub:
	bash scripts/arc_submit.sh -c $(CONFIG)/priority_subgroup.yaml -o priority_subgroup

arc4_intervention_childPovertyReductionRelative_psub:
	bash scripts/arc_submit.sh -c $(CONFIG)/priority_subgroup.yaml -o priority_subgroup -i 'ChildPovertyReductionRELATIVE_psub'

arc4_intervention_childPovertyReductionAbsolute_psub:
	bash scripts/arc_submit.sh -c $(CONFIG)/priority_subgroup.yaml -o priority_subgroup -i 'ChildPovertyReductionABSOLUTE_psub'

arc4_child_pov_psub: arc4_baseline_psub arc4_intervention_childPovertyReductionRelative_psub arc4_intervention_childPovertyReductionAbsolute_psub

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
