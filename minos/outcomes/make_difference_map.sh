#!/bin/bash
#$1 mode e.g. default_config, scotland_mode
#$2 first intervention to compare against file name. Almost always will be baseline
#$3 second intervention file name e.g. baseline, livingWageIntervention
#$4 region e.g. glasgow/scotland/manchester/sheffield
#$5 year to plot e.g. 2025. Depends on model.
#$6 subset of first population to map for e.g. who_alive, who_below_living_wage. see aggregate_subset_functions.py
#$7 subset of second population to map for e.g. who_alive, who_below_living_wage.
#$8 full path of output pdf plot e.g. plots/test_plot.pdf

# Agggregate geoJSON sf12 data for specified region and interventions.
python3 minos/outcomes/format_spatial_output.py -m $1 -i $2 -r $4 -y $5 -s $6
python3 minos/outcomes/format_spatial_output.py -m $1 -i $3 -r $4 -y $5 -s $7
#
Rscript minos/outcomes/sf12_difference_map.R -m $1 -j $2 -i $3 -r $4 -y $5 -d $8
