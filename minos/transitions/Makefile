#####################################
### transitions
#####################################

#transitions: ### Run R scripts to generate transition models for each module
#transitions: | $(TRANSITION_DATA)
#transitions: final_data $(TRANSITION_DATA)/hh_income/hh_income_2018_2019.rds $(TRANSITION_DATA)/housing/clm/housing_clm_2018_2019.rds
#transitions: $(TRANSITION_DATA)/mwb/ols/sf12_ols_2018_2019.rds $(TRANSITION_DATA)/labour/nnet/labour_nnet_2018_2019.rds
#transitions: $(TRANSITION_DATA)/neighbourhood/clm/neighbourhood_clm_2014_2017.rds $(TRANSITION_DATA)/tobacco/zip/tobacco_zip_2018_2019.rds
#transitions: $(TRANSITION_DATA)/alcohol/zip/alcohol_zip_2018_2019.rds $(TRANSITION_DATA)/nutrition/ols/nutrition_ols_2018_2019.rds
#transitions: $(TRANSITION_DATA)/loneliness/clm/loneliness_clm_2018_2019.rds

transitions: | $(TRANSITION_DATA)
transitions: final_data $(TRANSITION_DATA)/hh_income/ols/hh_income_2018_2019.rds

scot_transitions: final_data $(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds

$(TRANSITION_DATA)/hh_income/ols/hh_income_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R

$(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds: $(SCOTDATA)/2019_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_SCOTLAND.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --scotland

$(TRANSITION_DATA)/loneliness/clm/loneliness_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/loneliness/loneliness_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/loneliness/loneliness_clm.R

$(TRANSITION_DATA)/neighbourhood_safety/clm/neighbourhood_safety_2014_2017.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R

$(TRANSITION_DATA):
	@echo "Creating transition data directory"
	mkdir -p $(TRANSITION_DATA)

#$(TRANSITION_DATA)/hh_income/hh_income_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/income/income_ols.r
#	# Script needs 3 arguments (which are set as Makefile variables, change there not here):
#	# 1 - Minos root directory (i.e. $(ROOT))
#	# 2 - Input data directory (i.e. data/composite or $(DATADIR))
#	# 3 - Transition model directory (data/transitions or $(TRANSITION_DATA))
#	$(RSCRIPT) $(SOURCEDIR)/transitions/income/income_ols.r --args $(DATADIR) $(TRANSITION_DATA) $(TRANSITION_SOURCE)

$(TRANSITION_DATA)/housing/clm/housing_clm_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/housing/Housing_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/housing/Housing_clm.R

$(TRANSITION_DATA)/mwb/ols/sf12_ols_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/mwb/SF12_OLS.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/mwb/SF12_OLS.R

$(TRANSITION_DATA)/labour/nnet/labour_nnet_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/labour/labour_nnet.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/labour/labour_nnet.R

$(TRANSITION_DATA)/education_state/nnet/education_state_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/education/education_nnet.r
	$(RSCRIPT) $(SOURCEDIR)/transitions/education/education_nnet.r

$(TRANSITION_DATA)/neighbourhood/clm/neighbourhood_clm_2014_2017.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/neighbourhood/neighbourhood_clm.R

$(TRANSITION_DATA)/tobacco/zip/tobacco_zip_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/tobacco/tobacco_zip.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/tobacco/tobacco_zip.R

$(TRANSITION_DATA)/alcohol/zip/alcohol_zip_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/alcohol/alcohol_zip.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/alcohol/alcohol_zip.R

$(TRANSITION_DATA)/nutrition/ols/nutrition_ols_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/nutrition/nutrition_ols.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/nutrition/nutrition_ols.R

$(TRANSITION_DATA)/loneliness/clm/loneliness_clm_2018_2019.rds: $(FINALDATA)/2019_US_cohort.csv $(SOURCEDIR)/transitions/loneliness/loneliness_clm.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/loneliness/loneliness_clm.R
