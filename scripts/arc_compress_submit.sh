#!/bin/bash

# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=24:00:00
## Email if a run aborts
#$ -m ae
## Select memory
#$ -l h_vmem=3G # was 15 for big runs
## Choose cores. See arc website for more details.
#$ -pe smp 10
## Set logs directories
#$ -o ./logs/compress/log
#$ -e ./logs/compress/errors

tar cvf - ./output/default_cpr/baseline | pigz -9 > ./output/default_cpr/baseline.tar.gz
