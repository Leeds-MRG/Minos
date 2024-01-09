# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=6:00:00
## Email if a run aborts
#$ -m a
## Select memory
#$ -l h_vmem=20G # Reading lots of reasonably large data files , needs quite a lot of memory
## Choose cores. See arc website for more details. 5 high memory cores chosen here.
#$ -pe smp 1
## Set logs directories
#$ -o logs/batchread/log
#$ -e logs/batchread/errors

# create these if they dont exist. Will crash arc4 if you dont do this.
mkdir -p logs
mkdir -p logs/batchread
mkdir -p logs/batchread/log
mkdir -p logs/batchread/errors

Rscript minos/testing/S7_comp_change_boxplot.Rmd $1