## Empty for now but will contain targets to run the validation notebooks in the current directory

VALIDATION = $(ROOT)/minos/validation

# Better define Rscript variable for all the knitting
RSCRIPT = Rscript

########### COMBINED ###########

debug: handovers debug_replenishing debug_mwb_pathways debug_interventions debug_debug


########### Debug Scripts ###########

# Unfortunately cant do dependencies properly as the runtime sub-directory changes too often. Possibly could use the
# output/baseline directory as a target? Need to look into that. Won't matter much for now as these scripts run fast
handovers:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/handovers.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/handovers.html

housing_handovers:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/housing_handovers.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/housing_handovers.html

handovers_S7:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/handovers_S7.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/handovers_S7.html

handovers_inflated:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/handovers_inflated.Rmd')"
	firefox file://$(VALIDATION)/handovers_inflated.html

debug_replenishing:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/replenishing.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/replenishing.nb.html

debug_mwb_pathways:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/mwb_pathways.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/mwb_pathways.nb.html

debug_debug:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/DEBUG.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/DEBUG.nb.html

debug_interventions:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/interventions.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/interventions.nb.html

########### Validation ###########

cross_validation_default: cv_setup cv_default cv_render

cv_render:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/cross_validation_default.Rmd')"
	firefox file://$(VALIDATION)/cross_validation_default.html

cross_validation_S7: cv_S7_setup cv_SIPHER7 cv_S7_render

cv_S7_render:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/cross_validation_S7.Rmd')"
	firefox file://$(VALIDATION)/cross_validation_S7.html
