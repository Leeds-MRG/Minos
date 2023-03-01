## Empty for now but will contain targets to run the validation notebooks in the current directory

VALIDATION = $(ROOT)/minos/validation

# Better define Rscript variable for all the knitting
RSCRIPT = Rscript

# Unfortunately cant do dependencies properly as the runtime sub-directory changes too often. Possibly could use the
# output/baseline directory as a target? Need to look into that. Won't matter much for now as these scripts run fast
handovers:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/handovers.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/handovers.nb.html


validation_replenishing:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/replenishing.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/replenishing.nb.html


validation_mwb_pathways:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/mwb_pathways.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/mwb_pathways.nb.html

validation_debug:
	$(RSCRIPT) -e "require(rmarkdown); render('$(VALIDATION)/DEBUG.Rmd')"
	# open html file in firefox
	firefox file://$(VALIDATION)/DEBUG.nb.html
