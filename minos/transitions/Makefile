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

transitions_default: | $(TRANSITION_DATA)
transitions_default: final_data $(TRANSITION_DATA)/SF_12_MCS/ols/SF_12_MCS_2017_2018.rds

transitions_SIPHER7: | $(TRANSITION_DATA)
transitions_SIPHER7: final_data $(TRANSITION_DATA)/S7_mental_health/clm/S7_mental_health_2019_2020.rds

scot_transitions: final_data $(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds

cv_transitions: $(TRANSITION_DATA)/cross_validation/version5/hh_income/ols/hh_income_2018_2019.rds

cv_S7_transitions: | $(TRANSITION_DATA)
cv_S7_transitions: $(TRANSITION_DATA)/cross_validation/version5/S7_mental_health/clm/S7_mental_health_2019_2020.rds

$(TRANSITION_DATA)/SF_12_MCS/ols/SF_12_MCS_2017_2018.rds: $(FINALDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_default.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --default

$(TRANSITION_DATA)/S7_mental_health/clm/S7_mental_health_2019_2020.rds: $(FINALDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_S7.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --sipher7

$(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds: $(SCOTDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_SCOTLAND.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --scotland

$(TRANSITION_DATA)/cross_validation/version5/hh_income/ols/hh_income_2018_2019.rds: $(FINALDATA)/cross_validation/batch5/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_default.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --cross_validation

$(TRANSITION_DATA)/cross_validation/version5/S7_mental_health/clm/S7_mental_health_2019_2020.rds: $(FINALDATA)/cross_validation/batch5/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_S7.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --sipher7 --cross_validation

$(TRANSITION_DATA):
	@echo "Creating transition data directory"
	mkdir -p $(TRANSITION_DATA)

