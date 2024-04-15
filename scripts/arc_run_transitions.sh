#!/bin/bash

# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
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
## just use one node
#$ -l nodes=1
## Set logs directories
#$ -o ./logs/transitions/
#$ -e ./logs/transitions/

mkdir -p ./logs/transitions

Rscript minos/transitions/estimate_longitudinal_transitions.R
Rscript minos/transitions/estimate_transitions.R