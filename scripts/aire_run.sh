#!/bin/bash
################
# Slurm settings
################
#SBATCH --job-name=parallel_minos_job                   # Job name
#SBATCH --mail-type=FAIL                                # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=gyrc@leeds.ac.uk                    # Where to send mail. if this is not you change it or I will forward them all.
#SBATCH --array=1-30                                    # Run a single task. Chance size as desired.
#SBATCH --cpus-per-task=1                               # Number of CPU cores per array task.
#SBATCH --mem=50G                                       # Job memory request. Needs a lot for synthpop jobs.
#SBATCH --time=12:00:00                                 # Time limit hrs:min:sec
#SBATCH --output=logs/logs/minos_batch-%A-%a.out        # Standard output log.
#SBATCH --error=logs/errors/minos_batch-%A-%a.err       # Standard error log.

# IF THESE DIRECTORIES DON'T EXIST THE MODEL WIILL NOT RUN.
mkdir -p logs #make logs directory if it doesn't exist.
mkdir -p logs/logs #make logs directory if it doesn't exist.
mkdir -p logs/errors #make logs directory if it doesn't exist.

# Printout for model run id.
echo "Running Minos task $SLURM_JOBID on $SLURM_CPUS_ON_NODE CPU cores"
echo "Running task $SLURM_ARRAY_TASK_ID of $SLURM_ARRAY_TASK_MAX"

# print out if an intervention is applied and run main MINOS python script.
if [ "$#" -eq 6 ]; then
  echo "Running baseline MINOS simulation"
  python3 scripts/run.py -c $2 -o $4 -t $6 -r $SLURM_ARRAY_TASK_ID
elif [ "$#" -eq 8 ]; then
  echo "Running MINOS simulation with $6"
  python3 scripts/run.py -c $2 -o $4 -i $6 -t $8 -r $SLURM_ARRAY_TASK_ID
fi

# no errors
exit 0