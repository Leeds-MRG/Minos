#!/bin/bash
# File for running slurm jobs. If you use this please make sure to change parameters.
# Particularly the email address, number of tasks, and number of nodes.
# Needs fine tuning according to machine. This script will be tuned to Nik's UoL HPC machine (AKA beefy).
#SBATCH --job-name=parallel_job      # Job name
#SBATCH --mail-type=FAIL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user= gyrc@leeds.ac.uk    # Where to send mail
#SBATCH --nodes=16                    # Run all processes on a single node
#SBATCH --ntasks=2                  # Run a single task
#SBATCH --cpus-per-task=4            # Number of CPU cores per task
#SBATCH --mem=1gb                    # Job memory request
#SBATCH --time=01:00:00              # Time limit hrs:min:sec
#SBATCH --output=parallel_%j.log     # Standard output and error log
pwd; hostname; date

echo "Running Minos task $SLURM_JOBID on $SLURM_CPUS_ON_NODE CPU cores"

python3 scripts/minos_parallel_run.py --c config/slurmConfig.yaml $SLURM_JOBID # run minos paralell run with job_id j

date