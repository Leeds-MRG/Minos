# Compiling this page using sphinx.

Just some brief notes on how to compile this page.\
First needs a python 3.8 environment with the following installed.

conda install sphinx\
conda install myst-parser\
conda install sphinx-rtd-theme

Then move to the docsrc folder in terminal.
Makefile there has one command 'github'. Running this should recompile the website ready to be pushed to github.
When pushed to main branch the github page website should update in under 10 minutes.