

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

QALY_SCP_30_UC: MODE=$(EXPERIMENT)
QALY_SCP_30_UC: INTERVENTION=30UniversalCredit
QALY_SCP_30_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_35_UC: MODE=$(EXPERIMENT)
QALY_SCP_35_UC: INTERVENTION=35UniversalCredit
QALY_SCP_35_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_40_UC: MODE=$(EXPERIMENT)
QALY_SCP_40_UC: INTERVENTION=40UniversalCredit
QALY_SCP_40_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_45_UC: MODE=$(EXPERIMENT)
QALY_SCP_45_UC: INTERVENTION=45UniversalCredit
QALY_SCP_45_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_50_UC: MODE=$(EXPERIMENT)
QALY_SCP_50_UC: INTERVENTION=50UniversalCredit
QALY_SCP_50_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_55_UC: MODE=$(EXPERIMENT)
QALY_SCP_55_UC: INTERVENTION=55UniversalCredit
QALY_SCP_55_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_60_UC: MODE=$(EXPERIMENT)
QALY_SCP_60_UC: INTERVENTION=60UniversalCredit
QALY_SCP_60_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_65_UC: MODE=$(EXPERIMENT)
QALY_SCP_65_UC: INTERVENTION=65UniversalCredit
QALY_SCP_65_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_70_UC: MODE=$(EXPERIMENT)
QALY_SCP_70_UC: INTERVENTION=70UniversalCredit
QALY_SCP_70_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_75_UC: MODE=$(EXPERIMENT)
QALY_SCP_75_UC: INTERVENTION=75UniversalCredit
QALY_SCP_75_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_80_UC: MODE=$(EXPERIMENT)
QALY_SCP_80_UC: INTERVENTION=80UniversalCredit
QALY_SCP_80_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_85_UC: MODE=$(EXPERIMENT)
QALY_SCP_85_UC: INTERVENTION=85UniversalCredit
QALY_SCP_85_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_90_UC: MODE=$(EXPERIMENT)
QALY_SCP_90_UC: INTERVENTION=90UniversalCredit
QALY_SCP_90_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_95_UC: MODE=$(EXPERIMENT)
QALY_SCP_95_UC: INTERVENTION=95UniversalCredit
QALY_SCP_95_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_100_UC: MODE=$(EXPERIMENT)
QALY_SCP_100_UC: INTERVENTION=100UniversalCredit
QALY_SCP_100_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_105_UC: MODE=$(EXPERIMENT)
QALY_SCP_105_UC: INTERVENTION=105UniversalCredit
QALY_SCP_105_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_110_UC: MODE=$(EXPERIMENT)
QALY_SCP_110_UC: INTERVENTION=110UniversalCredit
QALY_SCP_110_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_115_UC: MODE=$(EXPERIMENT)
QALY_SCP_115_UC: INTERVENTION=115UniversalCredit
QALY_SCP_115_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

QALY_SCP_120_UC: MODE=$(EXPERIMENT)
QALY_SCP_120_UC: INTERVENTION=120UniversalCredit
QALY_SCP_120_UC:
	python minos/outcomes/QALY_calculation.py -m $(MODE) -i $(INTERVENTION)

#####################################
# VISUALISATIONS
#####################################

##################
# All Child
##################

QALY_vis_SCP_25_All: QALY_baseline QALY_SCP_25_All
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='25All', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_25_All.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_25_All.html


QALY_vis_SCP_50_All: QALY_baseline QALY_SCP_50_All
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='50All', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_50_All.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_50_All.html

QALY_vis_SCP_75_All: QALY_baseline QALY_SCP_75_All
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='75All', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_75_All.html')"

QALY_vis_SCP_100_All: QALY_baseline QALY_SCP_100_All
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='100All', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_100_All.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_100_All.html

QALY_vis_SCP_25_100_All: EXPERIMENT=default_config
QALY_vis_SCP_25_100_All: STARTYEAR=2021
QALY_vis_SCP_25_100_All: QALY_baseline QALY_SCP_25_All QALY_SCP_50_All QALY_SCP_75_All QALY_SCP_100_All
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('25All', '50All', '75All', '100All'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_25_100_All.html')"

QALYs_all_child: EXPERIMENT=default_config
QALYs_all_child: STARTYEAR=2021
QALYs_all_child: QALY_vis_SCP_25_All QALY_vis_SCP_50_All QALY_vis_SCP_75_All QALY_vis_SCP_100_All

QALYs_all_child_glasgow: EXPERIMENT=glasgow_scaled
QALYs_all_child_glasgow: STARTYEAR=2020
QALYs_all_child_glasgow: QALY_vis_SCP_25_All QALY_vis_SCP_50_All QALY_vis_SCP_100_All

##################
# Universal Credit
##################

QALY_vis_SCP_25_UC: QALY_baseline QALY_SCP_25_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='25UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_25_UC.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_25_UC.html

QALY_vis_SCP_30_UC: QALY_baseline QALY_SCP_30_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='30UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_30_UC.html')"

QALY_vis_SCP_35_UC: QALY_baseline QALY_SCP_35_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='35UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_35_UC.html')"

QALY_vis_SCP_40_UC: QALY_baseline QALY_SCP_40_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='40UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_30_UC.html')"

QALY_vis_SCP_45_UC: QALY_baseline QALY_SCP_45_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='45UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_45_UC.html')"

QALY_vis_SCP_50_UC: QALY_baseline QALY_SCP_50_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='50UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_50_UC.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_50_UC.html

QALY_vis_SCP_55_UC: QALY_baseline QALY_SCP_55_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='55UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_55_UC.html')"

QALY_vis_SCP_60_UC: QALY_baseline QALY_SCP_60_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='60UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_60_UC.html')"

QALY_vis_SCP_65_UC: QALY_baseline QALY_SCP_65_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='65UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_65_UC.html')"

QALY_vis_SCP_70_UC: QALY_baseline QALY_SCP_70_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='70UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_70_UC.html')"

QALY_vis_SCP_75_UC: QALY_baseline QALY_SCP_75_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='75UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_75_UC.html')"

QALY_vis_SCP_80_UC: QALY_baseline QALY_SCP_80_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='80UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_80_UC.html')"

QALY_vis_SCP_85_UC: QALY_baseline QALY_SCP_85_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='85UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_85_UC.html')"

QALY_vis_SCP_90_UC: QALY_baseline QALY_SCP_90_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='90UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_90_UC.html')"

QALY_vis_SCP_95_UC: QALY_baseline QALY_SCP_95_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='95UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_95_UC.html')"

QALY_vis_SCP_100_UC: QALY_baseline QALY_SCP_100_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='100UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_100_UC.html')"
	#firefox file://$(OUTCOMES)/QALY_SCP_100_UC.html

QALY_vis_SCP_105_UC: QALY_baseline QALY_SCP_105_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='105UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_105_UC.html')"

QALY_vis_SCP_110_UC: QALY_baseline QALY_SCP_110_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='110UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_110_UC.html')"

QALY_vis_SCP_115_UC: QALY_baseline QALY_SCP_115_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='115UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_115_UC.html')"

QALY_vis_SCP_120_UC: QALY_baseline QALY_SCP_120_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention='120UniversalCredit', start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_120_UC.html')"

QALYs_UC: EXPERIMENT=default_config
QALYs_UC: STARTYEAR=2021
QALYs_UC: QALY_vis_SCP_25_UC QALY_vis_SCP_50_UC QALY_vis_SCP_75_UC QALY_vis_SCP_100_UC

QALY_vis_SCP_25_100_UC: EXPERIMENT=default_config
QALY_vis_SCP_25_100_UC: STARTYEAR=2021
QALY_vis_SCP_25_100_UC: QALY_baseline QALY_SCP_25_UC QALY_SCP_50_UC QALY_SCP_75_UC QALY_SCP_100_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('25UniversalCredit', '50UniversalCredit', '75UniversalCredit', '100UniversalCredit'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_25_100_UC.html')"

QALYs_UC_glasgow: EXPERIMENT=glasgow_scaled
QALYs_UC_glasgow: STARTYEAR=2020
QALYs_UC_glasgow: QALY_vis_SCP_25_UC QALY_vis_SCP_50_UC QALY_vis_SCP_75_UC QALY_vis_SCP_100_UC

QALYs_UC_scotland: EXPERIMENT=scotland_scaled
QALYs_UC_scotland: STARTYEAR=2020
QALYs_UC_scotland: QALY_vis_SCP_25_UC QALY_vis_SCP_50_UC QALY_vis_SCP_75_UC QALY_vis_SCP_100_UC

QALY_vis_SCP_all_child_glasgow: EXPERIMENT=glasgow_scaled
QALY_vis_SCP_all_child_glasgow: STARTYEAR=2020
QALY_vis_SCP_all_child_glasgow: QALY_baseline QALY_SCP_25_All QALY_SCP_50_All QALY_SCP_75_All QALY_SCP_100_All
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('25All', '50All', '75All', '100All'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_all_child.html')"

QALY_vis_SCP_UC_glasgow: EXPERIMENT=glasgow_scaled
QALY_vis_SCP_UC_glasgow: STARTYEAR=2020
QALY_vis_SCP_UC_glasgow: QALY_baseline QALY_SCP_25_UC QALY_SCP_50_UC QALY_SCP_75_UC QALY_SCP_100_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('25UniversalCredit', '50UniversalCredit', '75UniversalCredit', '100UniversalCredit'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_UC_25_100.html')"

QALY_vis_SCP_UC_glasgow_25_50: EXPERIMENT=glasgow_scaled
QALY_vis_SCP_UC_glasgow_25_50: STARTYEAR=2020
QALY_vis_SCP_UC_glasgow_25_50: QALY_baseline QALY_SCP_25_UC QALY_SCP_30_UC QALY_SCP_35_UC QALY_SCP_40_UC QALY_SCP_45_UC QALY_SCP_50_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('25UniversalCredit', '30UniversalCredit', '35UniversalCredit', '40UniversalCredit', '45UniversalCredit', '50UniversalCredit'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_UC_25_50.html')"

QALY_vis_SCP_UC_glasgow_ALL: EXPERIMENT=glasgow_scaled
QALY_vis_SCP_UC_glasgow_ALL: STARTYEAR=2020
QALY_vis_SCP_UC_glasgow_ALL: QALY_baseline QALY_SCP_25_UC QALY_SCP_30_UC QALY_SCP_35_UC QALY_SCP_40_UC QALY_SCP_45_UC
QALY_vis_SCP_UC_glasgow_ALL: QALY_SCP_50_UC QALY_SCP_55_UC QALY_SCP_60_UC QALY_SCP_65_UC QALY_SCP_70_UC QALY_SCP_75_UC
QALY_vis_SCP_UC_glasgow_ALL: QALY_SCP_80_UC QALY_SCP_85_UC QALY_SCP_90_UC QALY_SCP_95_UC QALY_SCP_100_UC QALY_SCP_105_UC
QALY_vis_SCP_UC_glasgow_ALL: QALY_SCP_110_UC QALY_SCP_115_UC QALY_SCP_120_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('25UniversalCredit', '30UniversalCredit', '35UniversalCredit', '40UniversalCredit', '45UniversalCredit', '50UniversalCredit', '55UniversalCredit', '60UniversalCredit', '65UniversalCredit', '70UniversalCredit', '75UniversalCredit', '80UniversalCredit', '85UniversalCredit', '90UniversalCredit', '95UniversalCredit', '100UniversalCredit', '105UniversalCredit', '110UniversalCredit', '115UniversalCredit', '120UniversalCredit'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_UC_ALL.html')"

QALY_vis_SCP_25_glasgow: EXPERIMENT=glasgow_scaled
QALY_vis_SCP_25_glasgow: STARTYEAR=2020
QALY_vis_SCP_25_glasgow: QALY_baseline QALY_SCP_25_All QALY_SCP_25_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('25UniversalCredit', '25All'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_25.html')"

QALY_vis_SCP_50_glasgow: EXPERIMENT=glasgow_scaled
QALY_vis_SCP_50_glasgow: STARTYEAR=2020
QALY_vis_SCP_50_glasgow: QALY_baseline QALY_SCP_50_All QALY_SCP_50_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('50UniversalCredit', '50All'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_50.html')"

QALY_vis_SCP_75_glasgow: EXPERIMENT=glasgow_scaled
QALY_vis_SCP_75_glasgow: STARTYEAR=2020
QALY_vis_SCP_75_glasgow: QALY_baseline QALY_SCP_75_All QALY_SCP_75_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('75UniversalCredit', '75All'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_75.html')"

QALY_vis_SCP_100_glasgow: EXPERIMENT=glasgow_scaled
QALY_vis_SCP_100_glasgow: STARTYEAR=2020
QALY_vis_SCP_100_glasgow: QALY_baseline QALY_SCP_100_All QALY_SCP_100_UC
	$(RSCRIPT) -e "require(rmarkdown); render('$(OUTCOMES)/QALY_comparison2.Rmd', params = list(experiment='$(EXPERIMENT)/', base='baseline', intervention=c('100UniversalCredit', '100All'), start.year='$(STARTYEAR)'), output_file = 'QALY_SCP_100.html')"

