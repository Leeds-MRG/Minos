#!/bin/bash
################
# Slurm settings
################
#SBATCH --job-name=minos_single_lineplot                 # Job name
#SBATCH --mail-type=FAIL                                # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=gyrc@leeds.ac.uk                    # Where to send mail
#SBATCH --ntasks=1                                      # Run a single task
#SBATCH --cpus-per-task=64                               # Number of CPU cores per task
#SBATCH --mem=30G                                       # Job memory request
#SBATCH --time=01:00:00                                 # Time limit hrs:min:sec
#SBATCH --output=logs/logs/minos_single_lineplot-%A-%a.out        # Standard output log.
#SBATCH --error=logs/errors/minos_single_lineplot-%A-%a.err       # Standard error log.

python3 minos/outcomes/make_lineplots_macros.py $1 $2 $3