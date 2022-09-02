##!/bin/bash
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

# Choose cores. See arc website for more details. 5 high memory cores chosen here.
#$ -pe smp 5

# Tell computer this is an array job with tasks from 1 to N
# This number is determined by the length of the param_list list. some way to automate this? don't think so.
#$ -t 1-2

#Run the executable minos_batch_run.py
# no final ID here as its provided by the scheduler.
# $SGE_TASK_ID is provided by qsub. It is an integer that corresponds to some combination of minos parameters
# (income uplift amounds and run_id)
# $1 is config file e.g. config/beefyBaseline.yaml
# $SGE_TASK_ID is son of grid engine task id. run id for this minos run.
python3 'scripts/minos_batch_run.py' $1 $SGE_TASK_ID
