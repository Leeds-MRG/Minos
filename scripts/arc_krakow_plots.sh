#!/bin/bash
# This script must be run with qsub if running on Arc

## Set current working directory
#$ -cwd
## Use current environment variables and modules
#$ -V
## Request hours of runtime
#$ -l h_rt=0:30:00
## Email if a run aborts
#$ -m a
## Select memory
#$ -l h_vmem=10G # was 15 for big runs
## Choose cores. See arc website for more details. 5 high memory cores chosen here.
#$ -pe smp 8
## Set logs directories
#$ -o ./logs/krakow_plots/
#$ -e ./logs/krakow_plots/

mkdir -p ./logs/krakow_plots # make dir if not exists

# general lineplots

python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "EPCG_GBIS_SF_12_MCS" "SF_12_MCS"
python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "EPCG_GBIS_intervention_cost" "boost_amount"
python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "EPCG_GBIS_yearly_energy" "yearly_energy"

# quintile plots

python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "EPCG_quintiles" "SF_12_MCS"
python3 minos/outcomes/make_lineplots_macros.py "energy_manchester_scaled" "GBIS_quintiles" "SF_12_MCS"

# maps

python3 minos/outcomes/format_spatial_output.py -i "baseline" -y 2024 -m "energy_manchester_scaled" -s who_poor_heating -p true -r "manchester" -v "SF_12_MCS"
python3 minos/outcomes/format_spatial_output.py -i "EPCG" -y 2024 -m "energy_manchester_scaled" -s who_boosted -p true -r "manchester"  -v "SF_12_MCS"
RScript minos/outcomes/sf12_difference_map.R -m "energy_manchester_scaled" -b "baseline" -i "EPCG" -r "manchester" -y 2024 -v "SF_12_MCS" -s true

python3 minos/outcomes/format_spatial_output.py -i "baseline" -y 2024 -m "energy_manchester_scaled" -s who_poor_heating -p true -r "manchester" -v "SF_12_MCS"
python3 minos/outcomes/format_spatial_output.py -i "GBIS" -y 2024 -m "energy_manchester_scaled" -s who_boosted -p true -r "manchester"  -v "SF_12_MCS"
Rscript minos/outcomes/sf12_difference_map.R -m "energy_manchester_scaled" -b "baseline" -i "GBIS" -r "manchester" -y 2024 -v "SF_12_MCS" -s true


