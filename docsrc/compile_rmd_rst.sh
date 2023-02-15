#!/bin/bash
# Script for compiling Rmarkdown notebooks into rst files to use in sphinx.
# Has two positional arguments for the input notebook to knit and the output save file name for the rst.
# E.g. while in docsrc
# compile_rmd_rst.sh modules/notebooks/tobacco.Rmd modules/documentation/tobacco.rst


knitted_md=${1%.Rmd}.md # swap Rmd extension for md extension on input notebook.
# Intermediate markdown file for knitted notebook is required. Compiles plots/tables in it rather than raw R.
# Keep the same name as the input notebook just with different extension.
# This intermediate is converted to rst for sphinx and deleted.

# prints for debugging
#echo "${1}"
#echo "${2}"
#echo "${knitted_md}"

Rscript -e "knitr::knit('${1}', output='${knitted_md}', quiet=TRUE)" # knit notebook in R.
pandoc --citeproc --extract-media=. -s ${knitted_md} -o $2 # convert knitted md to rst.
echo "Knitted ${1} to markdown file ${knitted_md} and converted to rst ${2}."
rm ${knitted_md} # cleanup intermediate markdown.
