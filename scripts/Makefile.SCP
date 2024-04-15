
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

arc4_intervention_10All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '10All'

arc4_intervention_20All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '20All'

arc4_intervention_25All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '25All'

arc4_intervention_30All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '30All'

arc4_intervention_40All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '40All'

arc4_intervention_50All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '50All'

arc4_intervention_60All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '60All'

arc4_intervention_70All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '70All'

arc4_intervention_75All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '75All'

arc4_intervention_80All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '80All'

arc4_intervention_90All: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '90All'

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

arc4_intervention_10UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '10UniversalCredit'

arc4_intervention_20UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '20UniversalCredit'

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

arc4_intervention_60UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '60UniversalCredit'

arc4_intervention_70UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '70UniversalCredit'

arc4_intervention_75UniversalCredit: setup
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '75UniversalCredit'

arc4_intervention_80UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '80UniversalCredit'

arc4_intervention_90UniversalCredit:
	bash scripts/arc_submit.sh -c $(RUN_CONFIG) -o $(MODE) -i '90UniversalCredit'

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

#####################################
## Arc4 Combined Targets
#####################################

arc4_all_scenarios: MODE=default_config
arc4_all_scenarios: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_scenarios: arc4_baseline arc4_intervention_hhIncomeChildUplift arc4_intervention_PovertyLineChildUplift arc4_intervention_livingWage arc4_intervention_energyDownLift arc4_intervention_energyDownLiftNoSupport

arc4_all_child_uplifts: MODE=scaled_glasgow #MODE=default_config
arc4_all_child_uplifts: RUN_CONFIG=$(CONFIG)/glasgow_scaled.yaml#/default.yaml
arc4_all_child_uplifts: arc4_baseline arc4_intervention_25All arc4_intervention_50All arc4_intervention_75All arc4_intervention_100All

arc4_all_child_10_100: MODE=default_config
arc4_all_child_10_100: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_child_10_100: arc4_baseline arc4_intervention_10All arc4_intervention_20All arc4_intervention_30All
arc4_all_child_10_100: arc4_intervention_40All arc4_intervention_50All arc4_intervention_60All arc4_intervention_70All
arc4_all_child_10_100: arc4_intervention_80All arc4_intervention_90All arc4_intervention_100All

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

arc4_UC_10_100: MODE=default_config
arc4_UC_10_100: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_UC_10_100: arc4_baseline arc4_intervention_10UniversalCredit arc4_intervention_20UniversalCredit
arc4_UC_10_100: arc4_intervention_30UniversalCredit arc4_intervention_40UniversalCredit
arc4_UC_10_100: arc4_intervention_50UniversalCredit arc4_intervention_60UniversalCredit
arc4_UC_10_100: arc4_intervention_70UniversalCredit arc4_intervention_80UniversalCredit
arc4_UC_10_100: arc4_intervention_90UniversalCredit arc4_intervention_100UniversalCredit

arc4_UC_5_50: MODE=default_config
arc4_UC_5_50: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_UC_5_50: arc4_intervention_25UniversalCredit arc4_intervention_35UniversalCredit arc4_intervention_45UniversalCredit

arc4_priority_child_uplifts: MODE=scaled_glasgow #MODE=default_config
arc4_priority_child_uplifts: RUN_CONFIG=$(CONFIG)/glasgow_scaled.yaml#/default.yaml
arc4_priority_child_uplifts: arc4_scotland_baseline arc4_intervention_25Priority arc4_intervention_50Priority arc4_intervention_75Priority arc4_intervention_100Priority

arc4_all_25_uplifts: MODE=default_config
arc4_all_25_uplifts: RUN_CONFIG=$(CONFIG)/default.yaml
arc4_all_25_uplifts: arc4_baseline arc4_intervention_25RelativePoverty arc4_intervention_25All arc4_intervention_25UniversalCredit
