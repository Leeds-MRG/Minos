#!/bin/bash
# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=00:30:00
## Email if a run aborts
#$ -m a
## Select memory
#$ -l h_vmem=20G # was 15 for big runs
## Choose cores. See arc website for more details. 5 high memory cores chosen here.
#$ -pe smp 1
## Set logs directories
#$ -o ./logs/transitions/
#$ -e ./logs/transitions/

mkdir -p ./logs/transitions
Rscript minos/transitions/estimate_transitions.R
python3 minos/data_generation/generate_repl_pop.py
python3 minos/data_generation/US_household_upscaling.py -r 'manchester' -p 10
python3 minos/data_generation/generate_repl_pop.py --region 'manchester'
