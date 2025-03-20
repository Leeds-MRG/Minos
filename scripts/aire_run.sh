#!/bin/bash
################
# Slurm settings
################
#SBATCH --job-name=parallel_minos_job      # Job name. Can probably name this better...
###SBATCH --mail-type=FAIL             # Mail events (NONE, BEGIN, END, FAIL, ALL) # TURNED FAILURE EMAILS OFF. TURN ON AND CHANGE EMAIL IF YOU WANT THIS.
###SBATCH --mail-user=gyrc@leeds.ac.uk # Where to send mail. please change this.
#SBATCH --ntasks=1                   # Run a single task # THIS IS THE IMPORTANT NUMBER. IF RUNNING BATCH JOBS NEED TO CHANGE THIS MANUALLY! 100 jobs rquired 100 ntasks.
#SBATCH --cpus-per-task=1            # Number of CPU cores per task. Not multithreaded so 1 core works fine. may need minimum of 2 depending on system.
#SBATCH --mem=10gb                     # Job memory request. If running synthpop jobs may need to increase mem and time.
#SBATCH --time=01:00:00               # Time limit hrs:min:sec
#SBATCH --output=logs/errors/minos_batch-%A-%a.out   # Standard output log.
#SBATCH --error=logs/logs/minos_batch-%A-%a.err   # Standard output log.

echo "Running Minos task $SLURM_JOBID on $SLURM_CPUS_ON_NODE CPU cores"
echo "Running task $SLURM_ARRAY_TASK_ID of $SLURM_ARRAY_TASK_MAX"

if [ "$#" -eq 6 ]; then
  echo "Running baseline MINOS simulation"
  python3 scripts/run.py -c $2 -o $4 -t $6 -r $SLURM_ARRAY_TASK_ID
elif [ "$#" -eq 8 ]; then
  echo "Running MINOS simulation with $6"
  python3 scripts/run.py -c $2 -o $4 -i $6 -t $8 -r $SLURM_ARRAY_TASK_ID
fi

# no errors
exit 0