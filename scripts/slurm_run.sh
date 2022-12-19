#!/bin/bash
################
# Slurm settings
################
#SBATCH --job-name=parallel_minos_job      # Job name
#SBATCH --mail-type=FAIL             # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=gyrc@leeds.ac.uk # Where to send mail
#SBATCH --nodes=1                    # Run all processes on a single node
#SBATCH --ntasks=1                   # Run a single task
#SBATCH --cpus-per-task=2            # Number of CPU cores per task
#SBATCH --mem=2gb                     # Job memory request
#SBATCH --time=00:15:00               # Time limit hrs:min:sec
#SBATCH --output=logs/minos_batch-%A-%a.out   # Standard output and error log.
#SBATCH --gres=gpu:rtx_6000:1 # What GPUs you want: 1

./gpu_burn # GPU logging..? Proves traceback if something goes wrong.

pwd; hostname; date

echo "Running Minos task $SLURM_JOBID on $SLURM_CPUS_ON_NODE CPU cores"
echo "Running task $SLURM_ARRAY_TASK_ID of $SLURM_ARRAY_TASK_MAX"

if [ "$#" -eq 6 ]; then
  echo "Running baseline MINOS simulation"
  python3 scripts/run.py -c $2 -o $4 -t $6 -r $SLURM_ARRAY_TASK_ID
elif [ "$#" -eq 8 ]; then
  echo "Running MINOS simulation with $6"
  python3 scripts/run.py -c $2 -o $4 -i $6 -t $8 -r $SLURM_ARRAY_TASK_ID
fi
