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
## Local single runs of MINOS interventions.
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

#####################################
## Running MINOS scenarios on Arc4
#####################################

.phony: arc4_baseline arc4_intervention_hhIncome arc4_intervention_hhIncomeChildUplift
.phony: arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift
.phony: arc4_all_scenarios arc4_all_scot_scenarios arc4_cv_baseline

arc4_baseline: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE)

arc4_intervention_hhIncome: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomeIntervention'

arc4_intervention_hhIncomeChildUplift: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomeChildUplift'

arc4_intervention_PovertyLineChildUplift: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'hhIncomePovertyLineChildUplift'

arc4_intervention_livingWage: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'livingWageIntervention'

arc4_intervention_energyDownLift: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownlift'

arc4_intervention_energyDownLiftNoSupport: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i 'energyDownliftNoSupport'

arc4_all_scenarios: MODE=default_config
arc4_all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_scenarios: arc4_baseline arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift arc4_intervention_energyDownLiftNoSupport

arc4_all_scot_scenarios: MODE=scotland_mode
arc4_all_scot_scenarios: RUN_CONFIG=$(CONFIG)/scot_default.yaml
arc4_all_scot_scenarios: arc4_baseline arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift

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
