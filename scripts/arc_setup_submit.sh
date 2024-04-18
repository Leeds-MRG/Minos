#!/bin/bash

# create these if they dont exist. Will crash arc4 if you dont do this.
mkdir -p logs
mkdir -p logs/setup_log
mkdir -p logs/setup_errors

echo "Running default setup..."
qsub 'scripts/arc_setup_run.sh'

# no errors
exit 0