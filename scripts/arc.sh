#!/bin/bash
# Set current working directory
#$ -cwd
# Use current environment variables and modules
#$ -V
# Request hours of runtime
#$ -l h_rt=48:00:00
# Email if a run aborts
#$ -m a
# Select memory
#$ -l h_vmem=15G # was 15 for big runs
# Choose cores
#$ -pe smp 5
# Tell computer this is an array job with tasks from 1 to N
# This number is determined by the length of the param_list list. some way to automate this?
#$ -t 1-2
#Run the executable minos_parallel_run.py
# args $1 and $2 are for script name and config path respectively.
# example bash arc.sh scripts/minos_parallel_run.py config/arcConfig.yaml
# no final ID here as its provided by the scheduler.
python3 $1 $2 $SGE_TASK_ID