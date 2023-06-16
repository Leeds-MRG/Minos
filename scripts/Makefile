###################
## Test Simulations
###################

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

baseline_default: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config

intervention_livingWage_default: setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/default.yaml -o default_config -i 'livingWageIntervention'

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

all_scenarios: MODE = default_config
all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
all_scenarios: baseline intervention_hhIncomeChildUplift intervention_PovertyLineChildUplift intervention_livingWage intervention_energyDownLift

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

arc4_all_scenarios: MODE=default_config
arc4_all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_scenarios: arc4_baseline arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift

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
	bash scripts/slurm_submit.sh -c config/default.yaml -o $(MODE)

beefy_intervention_hhIncome: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o $(MODE) -i 'hhIncomeIntervention'

beefy_intervention_hhIncomeChildUplift: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o $(MODE) -i 'hhIncomeChildUplift'

beefy_intervention_PovertyLineChildUplift: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o $(MODE) -i 'hhIncomePovertyLineChildUplift'

beefy_intervention_livingWage: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o $(MODE) -i 'livingWageIntervention'

beefy_intervention_energyDownLift: setup
	bash scripts/slurm_submit.sh -c config/default.yaml -o $(MODE) -i 'energyDownlift'

beefy_all_scenarios: MODE=default_config
beefy_all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
beefy_all_scenarios: beefy_baseline beefy_intervention_hhIncomeChildUplift beefy_intervention_PovertyLineChildUplift beefy_intervention_livingWage beefy_intervention_energyDownLift

beefy_all_scot_scenarios: MODE=scotland_mode
beefy_all_scot_scenarios: RUN_CONFIG=$(CONFIG)/scot_default.yaml
beefy_all_scot_scenarios: beefy_baseline beefy_intervention_hhIncomeChildUplift beefy_intervention_PovertyLineChildUplift beefy_intervention_livingWage beefy_intervention_energyDownLift

#####################################
# Validation runs
#####################################

cv_baseline: cv_setup
	$(PYTHON) scripts/run.py -c $(CONFIG)/cross_validation.yaml -o cross_validation
