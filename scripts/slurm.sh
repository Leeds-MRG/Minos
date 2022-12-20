#!/bin/bash
#SBATCH --job-name=parallel_minos_job      # Job name
#SBATCH --mail-type=FAIL             # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=gyrc@leeds.ac.uk # Where to send mail
#SBATCH --nodes=1                    # Run all processes on a single node       
#SBATCH --ntasks=1                   # Run a single task                
#SBATCH --cpus-per-task=2            # Number of CPU cores per task
#SBATCH --mem=2gb                     # Job memory request
#SBATCH --time=00:15:00               # Time limit hrs:min:sec
#SBATCH --output=logs/minos_batch-%A-%a.out   # Standard output and error log

pwd; hostname; date

echo "Running Minos task $SLURM_JOBID on $SLURM_CPUS_ON_NODE CPU cores"
echo "Running task $SLURM_ARRAY_TASK_ID of $SLURM_ARRAY_TASK_MAX"

python3 scripts/minos_batch_run.py -c $1 --run_id $SLURM_ARRAY_TASK_ID  # run minos parallel run with job_id j

# no errors
exit 0










