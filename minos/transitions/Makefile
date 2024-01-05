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


$(TRANSITION_DATA):
	@echo "Creating transition data directory"
	mkdir -p $(TRANSITION_DATA)


############# Default #############

transitions_default: | $(TRANSITION_DATA)
transitions_default: final_data $(TRANSITION_DATA)/SF_12/glmm/SF_12_GLMM.rds $(TRANSITION_DATA)/ncigs/zip/ncigs_2019_2020.rds

$(TRANSITION_DATA)/ncigs/zip/ncigs_2019_2020.rds: $(FINALDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_default.txt $(TRANSITION_SOURCE)/transition_model_functions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --default

$(TRANSITION_DATA)/SF_12/glmm/SF_12_GLMM.rds: $(FINALDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_longitudinal_transitions.R $(TRANSITION_SOURCE)/model_definitions_default.txt $(TRANSITION_SOURCE)/transition_model_functions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_longitudinal_transitions.R --default

############# SIPHER7 #############

transitions_SIPHER7: | $(TRANSITION_DATA)
transitions_SIPHER7: final_data $(TRANSITION_DATA)/education_state/rf/education_state_RF.rds $(TRANSITION_DATA)/hh_income/glmm/hh_income_new_GLMM.rds

$(TRANSITION_DATA)/education_state/rf/education_state_RF.rds: $(FINALDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_S7.txt $(TRANSITION_SOURCE)/transition_model_functions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --sipher7

$(TRANSITION_DATA)/hh_income/glmm/hh_income_new_GLMM.rds: $(FINALDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_longitudinal_transitions.R $(TRANSITION_SOURCE)/model_definitions_S7.txt $(TRANSITION_SOURCE)/transition_model_functions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_longitudinal_transitions.R --sipher7

############# Default - Cross Validation #############

cv_transitions: $(TRANSITION_DATA)/cross_validation/version5/ncigs/zip/ncigs_2018_2019.rds $(TRANSITION_DATA)/cross_validation/version5/SF_12/glmm/SF_12_GLMM.rds

$(TRANSITION_DATA)/cross_validation/version5/ncigs/zip/ncigs_2018_2019.rds: $(FINALDATA)/cross_validation/batch5/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_default.txt $(TRANSITION_SOURCE)/transition_model_functions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --cross_validation

$(TRANSITION_DATA)/cross_validation/version5/SF_12/glmm/SF_12_GLMM.rds: $(FINALDATA)/cross_validation/batch5/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_longitudinal_transitions.R $(TRANSITION_SOURCE)/model_definitions_default.txt $(TRANSITION_SOURCE)/transition_model_functions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_longitudinal_transitions.R --cross_validation

############# SIPHER7 - Cross Validation #############

cv_S7_transitions: | $(TRANSITION_DATA)
cv_S7_transitions: $(TRANSITION_DATA)/cross_validation/version5/S7_mental_health/rf/S7_mental_health_2019_2020.rds $(TRANSITION_DATA)/cross_validation/version5/hh_income/glmm/hh_income_new_GLMM.rds

$(TRANSITION_DATA)/cross_validation/version5/S7_mental_health/rf/S7_mental_health_2019_2020.rds: $(FINALDATA)/cross_validation/batch5/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_S7.txt $(TRANSITION_SOURCE)/transition_model_functions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --sipher7 --cross_validation

$(TRANSITION_DATA)/cross_validation/version5/hh_income/glmm/hh_income_new_GLMM.rds: $(FINALDATA)/cross_validation/batch5/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_longitudinal_transitions.R $(TRANSITION_SOURCE)/model_definitions_S7.txt $(TRANSITION_SOURCE)/transition_model_functions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_longitudinal_transitions.R --sipher7 --cross_validation

############# Scotland (Pretty much deprecated) #############

scot_transitions: final_data $(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds

$(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds: $(SCOTDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_SCOTLAND.txt $(TRANSITION_SOURCE)/transition_model_functions.R
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --scotland
