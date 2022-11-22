#!/bin/bash
# This script must be run with qsub if running on Arc

# Check if we're in a conda environment and exit if not
if [ "$CONDA_DEFAULT_ENV" == "" ]; then
  echo Error, no conda env activated
  exit 1
fi

# if number of args submitted is less than 2 (4 with flags), print some help
if [ "$#" -lt 4 ]; then
  echo "Usage: $0 -c <config-file> -o <output_subdirectory> (OPTIONAL: -i <intervention>)"
  echo  e.g. $0 -c config/test_config.yaml -o testRun -i livingWageIntervention
  exit 1
fi

if [ "$#" -eq 4 ]; then
  echo "Running baseline MINOS simulation"
  python3 'scripts/run.py' -c $2 -o $4
elif [ "$#" -eq 6 ]; then
  echo "Running MINOS simulation with $6"
  python3 'scripts/run.py' -c $2 -o $4 -i $6
elif [ "$#" -gt 6 ]; then
  echo "You have submitted too many arguments"
  echo  e.g. $0 -c config/test_config.yaml -o testRun -i livingWageIntervention
  exit 1
fi
