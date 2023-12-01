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
#$ -l h_vmem=10G # was 15 for big runs
## Choose cores. See arc website for more details. 30 high memory cores chosen here.
#$ -pe smp 30
## Set logs directories
#$ -o ./logs/log
#$ -e ./logs/errors

############## SET NUMBER OF RUNS HERE ##############
## Tell computer this is an array job with tasks from 1 to N
#$ -t 1-1

# create these if they dont exist. Will crash arc4 if you dont do this.

Rscript minos/outcomes/mice_bash_script_paper1.R
