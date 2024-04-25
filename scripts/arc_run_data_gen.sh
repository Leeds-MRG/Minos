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
#$ -l h_vmem=4G # was 15 for big runs
## Choose cores. See arc website for more details. 5 high memory cores chosen here.
#$ -pe smp 8
## Set logs directories
#$ -o ./logs/transitions/
#$ -e ./logs/transitions/

python3 minos/data_generation/US_format_raw.py --source_dir ../UKDA-6614-stata/stata/stata13_se/
python3 minos/data_generation/US_missing_main.py
python3 minos/data_generation/generate_composite_vars.py
python3 minos/data_generation/US_complete_case.py
python3 minos/data_generation/generate_stock_pop.py
