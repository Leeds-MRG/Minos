#!/bin/bash
################
# Slurm settings
################
#SBATCH --job-name=parallel_minos_job                 # Job name
#SBATCH --mail-type=FAIL                              # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-type=END
#SBATCH --mail-user=h.p.rice@leeds.ac.uk              # Where to send mail
#SBATCH --array=1-30                                  # Number of runs
###SBATCH --ntasks=1                                    # Number of tasks to run, change as desired - disabled 21/03/24 as distinction with array not clear
#SBATCH --cpus-per-task=1                             # Number of CPU cores per task. Not multithreaded so 1 core works fine. May need minimum of 2 depending on system
#SBATCH --mem=10gb                                    # Job memory request. If running synthpop jobs may need to increase mem and time
#SBATCH --time=01:00:00                               # Time limit hrs:min:sec
#SBATCH --output=logs/errors/minos_batch-%A-%a.out    # Standard output log
#SBATCH --error=logs/logs/minos_batch-%A-%a.err       # Standard output log

echo "Running Minos task $SLURM_JOBID on $SLURM_CPUS_ON_NODE CPU cores"
echo "Running task $SLURM_ARRAY_TASK_ID of $SLURM_ARRAY_TASK_MAX"

# Create these if they don't exist
mkdir -p logs
mkdir -p logs/log
mkdir -p logs/errors


if [ "$#" -eq 6 ]; then
  echo "Running baseline MINOS simulation with config $2, mode $4, run ID $SLURM_ARRAY_TASK_ID"
  python3 scripts/run.py -c $2 -o $4 -t $6 -r $SLURM_ARRAY_TASK_ID
elif [ "$#" -eq 8 ]; then
  echo "Running MINOS simulation with config $2, mode $4, intervention $6, run ID $SLURM_ARRAY_TASK_ID"
  python3 scripts/run.py -c $2 -o $4 -i $6 -t $8 -r $SLURM_ARRAY_TASK_ID
fi

# no errors
exit 0