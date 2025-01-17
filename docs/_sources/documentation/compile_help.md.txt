# Compiling this page using sphinx.

Just some brief notes on how to compile this page.\

## Conda Environment

If you have the existing development conda environment installed just use that instead. Otherwise..

First needs a python 3.8 environment with the following installed.

conda install sphinx\
conda install myst-parser\
conda install -c conda-forge pandoc\
pip install sphinx-rtd-theme\
pip install sphinxcontrib-bibtex\
pip install nbsphinx\

Sphinx
Markdown parser
needed for nbsphinx.
read the docs theme. 
bibtex

## Rendering the website

In docsrc/Makefile we have the make sphinx_github command. 

This will render a lot of Rmd/ md files in this folder into rst format that sphinx can read.

It will then render the sphinx website using the sphinx build commands into the /docs folder.

DEATH WARNING. check docs/index.html before you push to development so the website doesn't crash. 
When pushed to main branch on github the website should update in under 10 minutes.
Open the html files in /docs/ and look at them. Please.

## Key components.

Two key files here are index.rst which contains the toctree file structure for the website. 
If you haven't used restructured text before (rst) its similar to markdown with lots of guides online.

conf.py contains parameters for sphinx to run and html formatting. This includes formatting using readthedocs css.

compile_rmd_rst.sh knits R markdown files into md files and then into rst files so sphinx can read it. 
This uses pandoc package which is really nice for converting these text files between formats. 
It has tonnes of additional arguments so is quite customisable but im scared to touch it.
Only use the argument to shift markdown headers around so the directory on the website loads properly.
Its a bit janky but it works so..

Will get some warnings when rendering the website. 
Its usually .md files used to generate the website that get converted to rst files and aren't used in the website toctree.
So long as its only complaining about md files it should be fine. 
Make sure all the md files it is complaining are missing have rst equivalents that are included in the toctree.


