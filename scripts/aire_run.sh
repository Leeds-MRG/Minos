#!/bin/bash
################
# Slurm settings
################
#SBATCH --job-name=minos_data_gen                                 # Job name
#SBATCH --mail-type=FAIL                                          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=gyrc@leeds.ac.uk                              # Where to send mail
#SBATCH --ntasks=1                                                # Run a single task
#SBATCH --cpus-per-task=32                                        # Number of CPU cores per task
#SBATCH --mem=30G                                                 # Job memory request
#SBATCH --time=03:00:00                                           # Time limit hrs:min:sec
#SBATCH --output=logs/data_gen/minos_data_gen-%A-%a.out        # Standard output log.
#SBATCH --error=logs/data_gen/minos_data_gen.err-%A-%a.err       # Standard error log.


# the LOCF annoyingly won't run on arc4 without shedloads of memory so running it in login node and then the rest on a job.
# new HPC so going to rag this one instead and see if it will work.
mkdir -p logs/data_gen # make dir if not exists
python3 minos/data_generation/US_format_raw.py --source_dir ../UKDA-6614-stata/stata/stata13_se/ # raw data.
python3 minos/data_generation/US_missing_main.py # LOCF and other deterministic correction.

python3 minos/data_generation/generate_composite_vars.py # composite and derived variabes.
Rscript minos/data_generation/US_MICE_imputation.R -n 1 -i 10 # MICE.
python3 minos/data_generation/US_complete_case.py # complete case.
python3 minos/data_generation/generate_stock_pop.py

Rscript minos/transitions/estimate_transitions.R --default
Rscript minos/transitions/estimate_longitudinal_transitions.R --default

python3 minos/data_generation/US_household_upscaling.py -r 'manchester' -p 10
python3 minos/data_generation/generate_repl_pop.py --region 'manchester'