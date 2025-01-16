# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXAPIBUILD   ?= sphinx-apidoc
SOURCEDIR     = .
BUILDDIR      = ../docs
NOTEBOOKDIR = docsrc/documentation/notebooks/
NOTEBOOKOUTPUTDIR = docsrc/documentation/modules/

# Render all Rmd, md, and rst files into rst files that sphinx can read.
render_rmd:
	# convert markdowns to rst.
	pandoc --citeproc -s "docsrc/documentation/notebooks/education.md" -o "docsrc/documentation/modules/education.rst"
	pandoc --citeproc -s "docsrc/documentation/notebooks/replenishment.md" -o "docsrc/documentation/modules/replenishment.rst"
	pandoc --citeproc -s "docsrc/documentation/notebooks/modules_intro.md" -o "docsrc/documentation/modules/modules_intro.rst"
	pandoc --citeproc -s "docsrc/documentation/notebooks/nutrition.md" -o "docsrc/documentation/modules/nutrition.rst"
	pandoc --citeproc -s "docsrc/documentation/notebooks/mortality.md" -o "docsrc/documentation/modules/mortality.rst"
	pandoc --citeproc -s "docsrc/documentation/notebooks/interventions.md" -o "docsrc/documentation/modules/interventions.rst"

	# Render R notebooks for each MINOS module. Any media outputs are saved to doscrc/figure.
	# (cd ..; ) makes a new shell that runs at the top level of the repo.
	# Keeps paths in notebooks tidy and at the top level as well.
	# Looks a bit awkward but allows for running notebooks in RStudio at the same top level (I.E. the Rstudio .RProj working directory)
	# Can run notebooks here and in Rstudio without changing any paths.
	# Probably a cleaner way to do this..

	bash docsrc/compile_rmd_rst.sh "$(NOTEBOOKDIR)mental_well_being.Rmd" "$(NOTEBOOKOUTPUTDIR)mental_well_being.rst"
	bash docsrc/compile_rmd_rst.sh "$(NOTEBOOKDIR)housing.Rmd" "$(NOTEBOOKOUTPUTDIR)housing.rst"
	bash docsrc/compile_rmd_rst.sh "$(NOTEBOOKDIR)household_income.Rmd" "$(NOTEBOOKOUTPUTDIR)household_income.rst"
	bash docsrc/compile_rmd_rst.sh "$(NOTEBOOKDIR)labour.Rmd" "$(NOTEBOOKOUTPUTDIR)labour.rst"
	bash docsrc/compile_rmd_rst.sh "$(NOTEBOOKDIR)loneliness.Rmd" "$(NOTEBOOKOUTPUTDIR)loneliness.rst"
	bash docsrc/compile_rmd_rst.sh "$(NOTEBOOKDIR)neighbourhood.Rmd" "$(NOTEBOOKOUTPUTDIR)neighbourhood.rst"
	bash docsrc/compile_rmd_rst.sh "$(NOTEBOOKDIR)tobacco.Rmd" "$(NOTEBOOKOUTPUTDIR)tobacco.rst"

	# Knitr outputs figures for the documentation in a folder /figure at the top repo level.
	# I couldn't figure out how change where to output them so manually move them instead..
	# Check if a figures folder already exists for the Rmd notebooks.
	# If it does exist remove it and replace it with the new set of figures in the top level folder.
	rm -rf $(NOTEBOOKOUTPUTDIR)figure
	mv -f figure $(NOTEBOOKOUTPUTDIR)figure
	# probably a better way to do this in the compile_rmd_rst.sh replacing with pandoc --extract-media..

sphinx_github: render_rmd
	(cd docsrc; sphinx-build -b html $(SOURCEDIR) $(BUILDDIR)) # build and write to /docs output directory or it defaults to /html.
	(cd docsrc; sphinx-apidoc -f -o $(SOURCEDIR) $(BUILDDIR)) # likewise
	#@cp -af _build/html/. "$(BUILDIR)"

clean_docs:
	# Remove any knitted notebooks leftovers.
	rm "$(NOTEBOOKDIR)*.pdf"
	rm "$(NOTEBOOKDIR)*.html"
	rm "$(NOTEBOOKDIR)*.md"
	rm -rf ../docs/* !(.nojekyll) # should remove everything in docs but nojekyll.