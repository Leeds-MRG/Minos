#!/bin/bash

# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=6:00:00
## Email if a run aborts
#$ -m a
## Select memory
#$ -l node_type=40core-768G # use high mem node.
#$ -l h_vmem=100G
# # Choose cores. See arc website for more details. 5 high memory cores chosen here.

mkdir -p ./logs/outcomes # make if not exists.
## Set logs directories
#$ -o ./logs/outcomes
#$ -e ./logs/outcomes

set -e # causes script to exit on first error.
# create these if they dont exist. Will crash arc4 if you dont do this.
make BIG_DADDY_PAPER_3 # run make command.