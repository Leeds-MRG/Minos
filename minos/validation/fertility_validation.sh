#!/bin/bash
#SBATCH --time=01:00:00
#SBATCH --nodes=1

echo
echo "******************************************************************************************************"
echo "Running fertility validation notebook, Aire version"
echo "Change Slurm settings at the top of this script, validation/fertility_validation.sh"
echo "******************************************************************************************************"
echo

srun jupyter nbconvert --execute --to html minos/validation/fertility_validation.ipynb
