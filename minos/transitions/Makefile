#####################################
### transitions
#####################################

transitions: | $(TRANSITION_DATA)
transitions: final_data $(TRANSITION_DATA)/hh_income/ols/hh_income_2018_2019.rds

scot_transitions: | $(TRANSITION_DATA)
scot_transitions: final_data $(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds

$(TRANSITION_DATA)/hh_income/ols/hh_income_2018_2019.rds: $(FINALDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R

$(TRANSITION_DATA)/scotland/hh_income/ols/hh_income_2018_2019.rds: $(SCOTDATA)/2020_US_cohort.csv $(TRANSITION_SOURCE)/estimate_transitions.R $(TRANSITION_SOURCE)/model_definitions_SCOTLAND.txt
	$(RSCRIPT) $(SOURCEDIR)/transitions/estimate_transitions.R --scotland

$(TRANSITION_DATA):
	@echo "Creating transition data directory"
	mkdir -p $(TRANSITION_DATA)
