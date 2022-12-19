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
	bash compile_rmd_rst.sh "documentation/notebooks/summarise_transitions_2.Rmd" "documentation/modules/summarise_transitions_2.rst"

github: render_rmd
	@$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR) # build and write to /docs output directory or it defaults to /html.
	@$(SPHINXAPIBUILD) -f -o $(SOURCEDIR) $(BUILDDIR) # likewise
	#@cp -af _build/html/. "$(BUILDIR)"
