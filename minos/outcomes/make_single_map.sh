#!/bin/bash

#$1 mode e.g. default_config, scotland_mode
#$2 intervention file name e.g. baseline, livingWageIntervention
#$3 region e.g. glasgow/scotland/manchester/sheffield
#$4 year to plot e.g. 2025. Depends on model.
#$5 subset of population to map for e.g. who_alive, who_below_living_wage. see aggregate_subset_functions.py
#$6 full path of output pdf plot e.g. plots/test_plot.pdf

python3 minos/outcomes/format_spatial_output.py -m "$1" -i "$2" -r "$3" -y "$4" -s "$5"
Rscript minos/outcomes/sf12_single_map.R -m $1 -i $2 -r $3 -y $4 -d $6
