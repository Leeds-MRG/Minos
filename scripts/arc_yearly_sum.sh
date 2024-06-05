#!/bin/bash

# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=6:00:00
## Email if a run aborts
#$ -m ae
## Select memory
#$ -l h_vmem=10G # was 15 for big runs
## Choose cores. See arc website for more details.
#$ -pe smp 8
## Set logs directories
#$ -o ./logs/sum/log
#$ -e ./logs/sum/errors


#Rscript -e "require(rmarkdown); render('minos/utils_datain_test.Rmd')"
Rscript minos/read_summarise_1year.R $1 $2 $3 $4
