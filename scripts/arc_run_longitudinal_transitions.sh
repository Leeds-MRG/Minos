#!/bin/bash
# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=2:00:00
## Email if a run aborts
#$ -m a
## Select memory
#$ -l h_vmem=2G # was 15 for big runs
## Choose cores. See arc website for more details. 5 high memory cores chosen here.
#$ -pe smp 8
## Set logs directories
#$ -o ./logs/data_gen/
#$ -e ./logs/data_gen/

mkdir -p ./logs/data_gen
Rscript minos/transitions/estimate_longitudinal_transitions.R