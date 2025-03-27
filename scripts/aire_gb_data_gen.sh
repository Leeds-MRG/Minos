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
#SBATCH --time=06:00:00                                           # Time limit hrs:min:sec
#SBATCH --output=logs/data_gen/minos_data_gen-%A-%a.out        # Standard output log.
#SBATCH --error=logs/data_gen/minos_data_gen-%A-%a.err       # Standard error log.

set -e # throws error if any command fails. otherwise would just keep going.

make final_data
make gb_scaled_data_summary
