

#####################################
# QALY Calculations
#####################################

.phony: QALY QALY_baseline QALY_energyDownlift QALY_energyDownliftNoSupport

QALY:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

## Default QALYs

QALY_baseline: MODE=$(EXPERIMENT)
QALY_baseline: INTERVENTION=baseline
QALY_baseline:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_energyDownlift: MODE=default_config
QALY_energyDownlift: INTERVENTION=energyDownlift
QALY_energyDownlift:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_energyDownliftNoSupport: MODE=default_config
QALY_energyDownliftNoSupport: INTERVENTION=energyDownliftNoSupport
QALY_energyDownliftNoSupport:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_livingWage: MODE=default_config
QALY_livingWage: INTERVENTION=livingWageIntervention
QALY_livingWage:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALYs: QALY_baseline QALY_energyDownlift QALY_energyDownliftNoSupport QALY_livingWage
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_energyCrises_diff.Rmd')"
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_livingWage.Rmd')"

QALY_comparison_livingWage: QALY_baseline QALY_livingWage
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_livingWage.Rmd')"
	firefox file://$(TESTING)/QALY_comparison_livingWage.html

QALY_comparison_energyCrises: QALY_energyDownlift QALY_energyDownliftNoSupport
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_energyCrises_diff.Rmd')"
	firefox file://$(TESTING)/QALY_comparison_energyCrises_diff.html

QALY_comparisons: QALY_comparison_livingWage QALY_comparison_energyCrises

##################################################################################
# ^ GENERIC QALY SCRIPT ^
##################################################################################

## No Replenishment QALYs (cohort)

QALY_baseline_norepl: MODE=default_no_replenishment
QALY_baseline_norepl: INTERVENTION=baseline
QALY_baseline_norepl:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_energyDownlift_norepl: MODE=default_no_replenishment
QALY_energyDownlift_norepl: INTERVENTION=energyDownlift
QALY_energyDownlift_norepl:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_energyDownliftNoSupport_norepl: MODE=default_no_replenishment
QALY_energyDownliftNoSupport_norepl: INTERVENTION=energyDownliftNoSupport
QALY_energyDownliftNoSupport_norepl:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_livingWage_norepl: MODE=default_no_replenishment
QALY_livingWage_norepl: INTERVENTION=livingWageIntervention
QALY_livingWage_norepl:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALYs_norepl: QALY_baseline_norepl QALY_energysupport_norepl QALY_energynosupport_norepl QALY_livwage_norepl
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_energyCrises_diff.Rmd')"
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_livingWage.Rmd')"

QALY_comparison_livingWage_norepl: QALY_baseline_norepl QALY_livwage_norepl
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_livingWage.Rmd')"
	firefox file://$(TESTING)/QALY_comparison_livingWage.html

##################################################################################
# Glasgow QALYs
##################################################################################

QALY_baseline_glasgow: MODE=glasgow_scaled
QALY_baseline_glasgow: INTERVENTION=baseline
QALY_baseline_glasgow:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_energysupport_glasgow: MODE=glasgow_scaled
QALY_energysupport_glasgow: INTERVENTION=energyDownlift
QALY_energysupport_glasgow:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_energynosupport_glasgow: MODE=glasgow_scaled
QALY_energynosupport_glasgow: INTERVENTION=energyDownliftNoSupport
QALY_energynosupport_glasgow:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_livwage_glasgow: MODE=glasgow_scaled
QALY_livwage_glasgow: INTERVENTION=livingWageIntervention
QALY_livwage_glasgow:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALYs_glasgow: QALY_baseline_glasgow QALY_energysupport_glasgow QALY_energynosupport_glasgow QALY_livwage_glasgow
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_energyCrises_diff.Rmd')"
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_livingWage.Rmd')"

QALY_comparison_livingWage_glasgow: QALY_baseline_glasgow QALY_livwage_glasgow
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_livingWage.Rmd')"
	firefox file://$(TESTING)/QALY_comparison_livingWage.html

##################################################################################
# UK scale QALYs
##################################################################################

QALY_baseline_uk: MODE=SF12_uk_scaled
QALY_baseline_uk: INTERVENTION=baseline
QALY_baseline_uk:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_energysupport_uk: MODE=SF12_uk_scaled
QALY_energysupport_uk: INTERVENTION=energyDownlift
QALY_energysupport_uk:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_energynosupport_uk: MODE=SF12_uk_scaled
QALY_energynosupport_uk: INTERVENTION=energyDownliftNoSupport
QALY_energynosupport_uk:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_livwage_uk: MODE=SF12_uk_scaled
QALY_livwage_uk: INTERVENTION=livingWageIntervention
QALY_livwage_uk:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALYs_uk: QALY_baseline_uk QALY_energysupport_uk QALY_energynosupport_uk QALY_livwage_uk
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_energyCrises_diff.Rmd')"
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_livingWage.Rmd')"

QALY_comparison_livingWage_uk: QALY_baseline_uk QALY_livwage_uk
	$(RSCRIPT) -e "require(rmarkdown); render('$(TESTING)/QALY_comparison_livingWage.Rmd')"
	firefox file://$(TESTING)/QALY_comparison_livingWage.html


############################################################################################
# Scottish Child Payment
############################################################################################

#####################################
# All Child
#####################################

QALY_SCP_25_All: MODE=$(EXPERIMENT)
QALY_SCP_25_All: INTERVENTION=25All
QALY_SCP_25_All:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_50_All: MODE=$(EXPERIMENT)
QALY_SCP_50_All: INTERVENTION=50All
QALY_SCP_50_All:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_75_All: MODE=$(EXPERIMENT)
QALY_SCP_75_All: INTERVENTION=75All
QALY_SCP_75_All:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_100_All: MODE=$(EXPERIMENT)
QALY_SCP_100_All: INTERVENTION=100All
QALY_SCP_100_All:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

#####################################
# Universal Credit
#####################################

QALY_SCP_25_UC: MODE=$(EXPERIMENT)
QALY_SCP_25_UC: INTERVENTION=25UniversalCredit
QALY_SCP_25_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_50_UC: MODE=$(EXPERIMENT)
QALY_SCP_50_UC: INTERVENTION=50UniversalCredit
QALY_SCP_50_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_75_UC: MODE=$(EXPERIMENT)
QALY_SCP_75_UC: INTERVENTION=75UniversalCredit
QALY_SCP_75_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_100_UC: MODE=$(EXPERIMENT)
QALY_SCP_100_UC: INTERVENTION=100UniversalCredit
QALY_SCP_100_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

#####################################
# VISUALISATIONS
#####################################

##################
# All Child
##################

QALY_vis_SCP_25_All: QALY_baseline QALY_SCP_25_All
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='25All'), output_file = 'QALY_SCP_25_All.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_25_All.html

QALY_vis_SCP_50_All: QALY_baseline QALY_SCP_50_All
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='50All'), output_file = 'QALY_SCP_50_All.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_50_All.html

QALY_vis_SCP_100_All: QALY_baseline QALY_SCP_100_All
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='100All'), output_file = 'QALY_SCP_100_All.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_100_All.html

QALYs_all_child: EXPERIMENT=default_config
QALYs_all_child: QALY_vis_SCP_25_All QALY_vis_SCP_50_All QALY_vis_SCP_100_All

QALYs_all_child_glasgow: EXPERIMENT=glasgow_scaled
QALYs_all_child_glasgow: QALY_vis_SCP_25_All QALY_vis_SCP_50_All QALY_vis_SCP_100_All

##################
# Universal Credit
##################

QALY_vis_SCP_25_UC: QALY_baseline QALY_SCP_25_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='25UniversalCredit'), output_file = 'QALY_SCP_25_UC.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_25_UC.html

QALY_vis_SCP_50_UC: QALY_baseline QALY_SCP_50_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='50UniversalCredit'), output_file = 'QALY_SCP_50_UC.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_50_UC.html

QALY_vis_SCP_100_UC: QALY_baseline QALY_SCP_100_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='100UniversalCredit'), output_file = 'QALY_SCP_100_UC.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_100_UC.html

QALYs_UC: EXPERIMENT=default_config
QALYs_UC: QALY_vis_SCP_25_UC QALY_vis_SCP_50_UC QALY_vis_SCP_100_UC

QALYs_UC_glasgow: EXPERIMENT=glasgow_scaled
QALYs_UC_glasgow: QALY_vis_SCP_25_UC QALY_vis_SCP_50_UC QALY_vis_SCP_100_UC
