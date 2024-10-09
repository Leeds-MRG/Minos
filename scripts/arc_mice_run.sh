#!/bin/bash

# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=48:00:00
## Email if a run aborts
#$ -m ae
## Select memory
#$ -l h_vmem=5G # was 15 for big runs
## Choose cores. See arc website for more details.
#$ -pe smp 6
## Set logs directories
#$ -o ./logs/log
#$ -e ./logs/errors

# Not any more...
##### just use one node
##### -l nodes=1

############## SET NUMBER OF RUNS HERE ##############
## Tell computer this is an array job with tasks from 1 to N

Rscript minos/data_generation/US_MICE_imputation.R -n 1 -i 10
