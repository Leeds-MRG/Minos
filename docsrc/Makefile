# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXAPIBUILD   ?= sphinx-apidoc
SOURCEDIR     = .
BUILDDIR      = ../docs

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

	
render_rmd:
	# convert markdowns to rst.
	pandoc --citeproc -s "documentation/notebooks/education.md" -o "documentation/modules/education.rst"
	pandoc --citeproc -s "documentation/notebooks/replenishment.md" -o "documentation/modules/replenishment.rst"
	pandoc --citeproc -s "documentation/notebooks/modules_intro.md" -o "documentation/modules/modules_intro.rst"
	pandoc --citeproc -s "documentation/notebooks/nutrition.md" -o "documentation/modules/nutrition.rst"

	# Render R notebooks for each MINOS module. Any media outputs are saved to doscrc/figure.
	bash compile_rmd_rst.sh "documentation/notebooks/tobacco.Rmd" "documentation/modules/tobacco.rst"
	bash compile_rmd_rst.sh "documentation/notebooks/household_income.Rmd" "documentation/modules/household_income.rst"
	bash compile_rmd_rst.sh "documentation/notebooks/housing.Rmd" "documentation/modules/housing.rst"
	bash compile_rmd_rst.sh "documentation/notebooks/mental_well_being.Rmd" "documentation/modules/mental_well_being.rst"
	bash compile_rmd_rst.sh "documentation/notebooks/labour.Rmd" "documentation/modules/labour.rst"
	bash compile_rmd_rst.sh "documentation/notebooks/loneliness.Rmd" "documentation/modules/loneliness.rst"
	bash compile_rmd_rst.sh "documentation/notebooks/neighbourhood.Rmd" "documentation/modules/neighbourhood.rst"
	rm -rf documentation/modules/figure # check new plot directory is empty. delete if not empty.
	mv -f figure documentation/modules/figure # stupid trick to move generated rst figures from source directory docsrc/ to their position specified in rst filepaths of docsrc/documentation/modules/
	# probably a better way to do this without force replacing with pandoc --extract-media..

github: render_rmd
	@$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR) # build and write to /docs output directory or it defaults to /html.
	@$(SPHINXAPIBUILD) -f -o $(SOURCEDIR) $(BUILDDIR) # likewise
	#@cp -af _build/html/. "$(BUILDIR)"
