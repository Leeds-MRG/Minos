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
#$ -o ./logs/SCP/log
#$ -e ./logs/SCP/errors

mkdir -p logs/SCP
mkdir -p logs/SCP/log
mkdir -p logs/SCP/errors

Rscript -e "require(rmarkdown); render('minos/outcomes/SCP_vis.Rmd')"
