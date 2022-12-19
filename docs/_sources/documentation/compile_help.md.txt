# Compiling this page using sphinx.

Just some brief notes on how to compile this page.\
First needs a python 3.8 environment with the following installed.

conda install sphinx\
conda install myst-parser\
conda install -c conda-forge pandoc\
pip install sphinx-rtd-theme\
pip install sphinxcontrib-bibtex\

Sphinx
Markdown parser
needed for nbsphinx.
read the docs theme. 
bibtex

Then move to the docsrc folder in terminal. Two key files here are index.rst which contains the file tree for the website. 
conf.py contains parameters for sphinx to run and html formatting.
Makefile has one command 'github'. Running this should recompile the website ready to be pushed to github.
When pushed to main branch on github the website should update in under 10 minutes.
Please check the website on your local machine before pushing. 
Open the html files in /docs/ and look at them. Please.