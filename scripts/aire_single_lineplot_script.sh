#!/bin/bash
################
# Slurm settings
################
#SBATCH --job-name=minos_single_lineplot                 # Job name
#SBATCH --mail-type=FAIL                                # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=gyrc@leeds.ac.uk                    # Where to send mail
#SBATCH --ntasks=1                                      # Run a single task
#SBATCH --cpus-per-task=16                               # Number of CPU cores per task
#SBATCH --mem=10G                                       # Job memory request
#SBATCH --time=01:00:00                                 # Time limit hrs:min:sec
#SBATCH --output=logs/logs/minos_batch-%A-%a.out        # Standard output log.
#SBATCH --error=logs/errors/minos_batch-%A-%a.err       # Standard error log.

python3 minos/outcomes/make_lineplots_macros.py $1 $2 $3