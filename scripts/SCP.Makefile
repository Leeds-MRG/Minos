
# Default parameters
MODE=default_config
RUN_CONFIG=$(CONFIG)/default.yaml



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

intervention_25UniversalCredit_glasgow: setup_glasgow_scaled
	$(PYTHON) scripts/run.py -c config/glasgow_scaled.yaml -o glasgow_scaled -i '25UniversalCredit'

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



all_child_uplifts: MODE=default_config
all_child_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
all_child_uplifts: baseline intervention_25All intervention_50All intervention_75All intervention_100All

poverty_line_child_uplifts: MODE=default_config
poverty_line_child_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
poverty_line_child_uplifts: baseline intervention_25RelativePoverty intervention_50RelativePoverty intervention_75RelativePoverty intervention_100RelativePoverty

universal_credit_child_uplifts: MODE=default_config
universal_credit_child_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
universal_credit_child_uplifts: baseline intervention_25UniversalCredit intervention_50UniversalCredit intervention_75UniversalCredit intervention_100UniversalCredit


#####################################
## Running MINOS scenarios on Arc4
#####################################

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

arc4_intervention_75RelativePoverty:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '75RelativePoverty'

arc4_intervention_100RelativePoverty:
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
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '50UniversalCredit'

arc4_intervention_55UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '55UniversalCredit'

arc4_intervention_60UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '60UniversalCredit'

arc4_intervention_65UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '65UniversalCredit'

arc4_intervention_70UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '70UniversalCredit'

arc4_intervention_75UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '75UniversalCredit'

arc4_intervention_80UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '80UniversalCredit'

arc4_intervention_85UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '85UniversalCredit'

arc4_intervention_90UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '90UniversalCredit'

arc4_intervention_95UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '95UniversalCredit'

arc4_intervention_100UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '100UniversalCredit'

arc4_intervention_105UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '105UniversalCredit'

arc4_intervention_110UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '110UniversalCredit'

arc4_intervention_115UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '115UniversalCredit'

arc4_intervention_120UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '120UniversalCredit'

##########################################################################

arc4_intervention_25Priority:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '25Priority'

arc4_intervention_50Priority:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '50Priority'

arc4_intervention_75Priority: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '75Priority'

arc4_intervention_100Priority: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '100Priority'

#####################################
## Arc4 Combined Targets
#####################################

arc4_all_scenarios: MODE=default_config
arc4_all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_scenarios: arc4_baseline arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift arc4_intervention_energyDownLiftNoSupport

arc4_all_child_uplifts: MODE=default_config #MODE=scaled_glasgow
arc4_all_child_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml #/glasgow_scaled.yaml
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

#####################################
## Arc4 QALY Combined Targets
#####################################

arc4_qaly_SCPs_Scotland: setup_scotland_scaled
arc4_qaly_SCPs_Scotland: MODE=scotland_scaled
arc4_qaly_SCPs_Scotland: RUN_CONFIG=$(CONFIG)/scotland_scaled.yaml
arc4_qaly_SCPs_Scotland: arc4_baseline arc4_intervention_25UniversalCredit arc4_intervention_50UniversalCredit
arc4_qaly_SCPs_Scotland: arc4_intervention_75UniversalCredit arc4_intervention_100UniversalCredit

arc4_qaly_SCPs_UC_glasgow: setup_glasgow_scaled
arc4_qaly_SCPs_UC_glasgow: MODE=glasgow_scaled
arc4_qaly_SCPs_UC_glasgow: RUN_CONFIG=$(CONFIG)/glasgow_scaled.yaml
arc4_qaly_SCPs_UC_glasgow: arc4_baseline
arc4_qaly_SCPs_UC_glasgow: arc4_intervention_25UniversalCredit arc4_intervention_30UniversalCredit arc4_intervention_35UniversalCredit
arc4_qaly_SCPs_UC_glasgow: arc4_intervention_40UniversalCredit arc4_intervention_45UniversalCredit arc4_intervention_50UniversalCredit
arc4_qaly_SCPs_UC_glasgow: arc4_intervention_55UniversalCredit arc4_intervention_60UniversalCredit arc4_intervention_65UniversalCredit
arc4_qaly_SCPs_UC_glasgow: arc4_intervention_70UniversalCredit arc4_intervention_75UniversalCredit arc4_intervention_80UniversalCredit
arc4_qaly_SCPs_UC_glasgow: arc4_intervention_85UniversalCredit arc4_intervention_90UniversalCredit arc4_intervention_95UniversalCredit
arc4_qaly_SCPs_UC_glasgow: arc4_intervention_100UniversalCredit arc4_intervention_105UniversalCredit arc4_intervention_110UniversalCredit
arc4_qaly_SCPs_UC_glasgow: arc4_intervention_115UniversalCredit arc4_intervention_120UniversalCredit
