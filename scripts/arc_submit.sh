#!/bin/bash

## Run the executable minos_batch_run.py
# no final ID here as its provided by the scheduler.
# $SGE_TASK_ID is provided by qsub. It is an integer that corresponds to some combination of minos parameters
# (income uplift amounds and run_id)
# $1 is config file e.g. config/beefyBaseline.yaml
# $SGE_TASK_ID is son of grid engine task id. run id for this minos run.

echo "Please note the number of runs is defined by a variable in the 'scripts/arc_run.sh' script, and cannot "
echo "be defined by a command line argument, or otherwise automated."

# if number of args submitted is less than 2 (4 with flags), print some help
if [ "$#" -lt 4 ]; then
  echo "You have not submitted enough command line arguments. Config file and output subdirectory are required."
  echo "Usage: $0 -c <config-file> -o <output_subdirectory> (OPTIONAL: -i <intervention>)"
  echo  "e.g. $0 -c config/test_config.yaml -o testRun -i livingWageIntervention"
  echo "run_id is generated by the SGE submission script and will be automatically assigned"
  exit 1
elif [ "$#" -gt 6 ]; then
  echo "You have submitted too many arguments"
  echo "Usage: $0 -c <config-file> -o <output_subdirectory> (OPTIONAL: -i <intervention>)"
  echo "e.g. $0 -c config/test_config.yaml -o testRun -i livingWageIntervention"
  echo "run_id is generated by the SGE submission script and will be automatically assigned"
  exit 1
elif [ $(expr $# % 2) -ne 0 ]; then
  echo "You have submitted an odd number of arguments"
  echo "Have you submitted a flag without an argument or vice versa? (Flags are counted as arguments)"
  echo "Usage: $0 -c <config-file> -o <output_subdirectory> (OPTIONAL: -i <intervention>)"
  echo "e.g. $0 -c config/test_config.yaml -o testRun -i livingWageIntervention"
  echo "run_id is generated by the SGE submission script and will be automatically assigned"
  exit 1
fi

if [ "$#" -eq 4 ]; then
  echo "Running baseline MINOS simulation"
  qsub 'scripts/arc_run.sh' -c $2 -o $4 -r $SGE_TASK_ID
elif [ "$#" -eq 6 ]; then
  echo "Running MINOS simulation with $6"
  qsub 'scripts/arc_run.sh' -c $2 -o $4 -i $6 -r $SGE_TASK_ID
fi
