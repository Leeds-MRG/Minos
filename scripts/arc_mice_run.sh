#!/bin/bash

# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=48:00:00
## Email if a run aborts
#$ -m a
## Select memory
## just use one node
##$ -l nodes=1
#$ -pe ib 30
## Set logs directories
#$ -o ./logs/log


############## SET NUMBER OF RUNS HERE ##############
## Tell computer this is an array job with tasks from 1 to N
#$ -t 1-1

Rscript minos/data_generation/mice_bash_script_paper1.R