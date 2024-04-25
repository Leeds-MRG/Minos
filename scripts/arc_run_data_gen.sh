#!/bin/bash
# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=2:00:00
## Email if a run aborts
#$ -m a
## Select memory
#$ -l h_vmem=10G # was 15 for big runs
## Choose cores. See arc website for more details. 5 high memory cores chosen here.
#$ -pe smp 8
## Set logs directories
#$ -o ./logs/data_gen/
#$ -e ./logs/data_gen/

mkdir -p ./logs/data_gen # make dir if not exists
python3 minos/data_generation/US_format_raw.py --source_dir ../UKDA-6614-stata/stata/stata13_se/ # raw data.
python3 minos/data_generation/US_missing_main.py # LOCF and other deterministic correction.
python3 minos/data_generation/generate_composite_vars.py # composite and derived variabes.
python3 minos/data_generation/US_complete_case.py # complete case.
python3 minos/data_generation/generate_stock_pop.py # final adjustments for minos input.