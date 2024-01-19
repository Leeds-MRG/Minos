#!/bin/bash

# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=12:00:00
## Email if a run aborts
#$ -m a
## Select memory
#$ -l h_vmem=192G # was 15 for big runs
## Choose cores. See arc website for more details. 5 high memory cores chosen here.
#$ -pe smp 1
## Set logs directories
#$ -o ./logs/SCP/log
#$ -e ./logs/SCP/errors

############## SET NUMBER OF RUNS HERE ##############
## Tell computer this is an array job with tasks from 1 to N
#$ -t 1-1

mkdir -p logs/SCP
mkdir -p logs/SCP/log
mkdir -p logs/SCP/errors

Rscript -e "require(rmarkdown); render('minos/outcomes/CPR_vis.Rmd')"
