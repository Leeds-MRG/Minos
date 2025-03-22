#!/bin/bash
#SBATCH --job-name=fertility_validation               # Job name
#SBATCH --mail-type=FAIL                              # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-type=END
#SBATCH --mail-user=h.p.rice@leeds.ac.uk              # Where to send mail
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --mem=64gb
#SBATCH --output=minos/validation/fertility-validation-%j.out

echo
echo "******************************************************************************************************"
echo "Running fertility validation notebook, Aire version"
echo "Change Slurm settings at the top of this script, validation/fertility_validation.sh"
echo "******************************************************************************************************"
echo

srun jupyter nbconvert --execute --to html minos/validation/fertility_validation.ipynb
