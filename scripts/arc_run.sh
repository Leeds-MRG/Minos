#!/bin/bash

# This script must be run with qsub if running on Arc

make setup

if [ "$#" -eq 4 ]; then
  echo "Running baseline MINOS simulation"
  python3 'scripts/run.py' -c $2 -o $4 -r $SGE_TASK_ID
elif [ "$#" -eq 6 ]; then
  echo "Running MINOS simulation with $6"
  python3 'scripts/run.py' -c $2 -o $4 -i $6 -r $SGE_TASK_ID
fi
