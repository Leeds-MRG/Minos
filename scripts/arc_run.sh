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
#$ -l h_vmem=15G # was 15 for big runs
## Choose cores. See arc website for more details. 5 high memory cores chosen here.
#$ -pe smp 5
## Set logs directories
#$ -o /logs/log
#$ -e /logs/errors

############## SET NUMBER OF RUNS HERE ##############
## Tell computer this is an array job with tasks from 1 to N
#$ -t 1-2

if [ "$#" -eq 4 ]; then
  echo "Running baseline MINOS simulation"
  python3 'scripts/run.py' -c $2 -o $4 -r $SGE_TASK_ID
elif [ "$#" -eq 6 ]; then
  echo "Running MINOS simulation with $6"
  python3 'scripts/run.py' -c $2 -o $4 -i $6 -r $SGE_TASK_ID
fi
