# bash script for generating minos lineplot maps.
# Has a series of positional arguments
# $1 minos mode. default_config or scotland_mode for now
# $2 list of intervention tags.
# 2 baseline,livingWageIntervention
#who_alive,who_below_living_wage

# custom baseline for living wage only.
python3 minos/validation/aggregate_minos_output.py -m $1 -d $2 -t $3 -a nanmean -v SF_12 -f $4
# stack aggregated files into one long array.
python3 minos/validation/aggregate_long_stack.py -m $1 -s baseline,livingWageIntervention -r baseline -v SF_12 -a nanmean
# make line plot.
python3 minos/validation/aggregate_lineplot.py -m $1 -s baseline,livingWageIntervention -v SF_12 -d plots -m nanmean -p $5
