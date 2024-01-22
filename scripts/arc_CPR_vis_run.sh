#!/bin/bash

# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=6:00:00
## Email if a run aborts
#$ -m a
## Select memory
## Select a full node
#$ -l nodes=1
## Set logs directories
#$ -o ./logs/CPR/log
#$ -e ./logs/CPR/errors

mkdir -p logs/CPR
mkdir -p logs/CPR/log
mkdir -p logs/CPR/errors

Rscript -e "require(rmarkdown); render('minos/outcomes/CPR_vis.Rmd')"
