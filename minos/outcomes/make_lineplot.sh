#!/bin/bash
# bash script for generating minos line plot maps.

# Has a series of positional arguments
# $1 minos mode. default_config or scotland_mode for now
# $2 A list of directories. Where are the data for required interventions stored. For example. baseline,livingWageIntervention will pull files from
# 2 baseline,livingWageIntervention
#who_alive,who_below_living_wage

Help()
{
   # Display Help
   echo "Function for aggregating minos data and making line plots to compare the effect of interventions on SF12."
   echo " "
   echo "Has a number of positional arguments"
   echo "\$1 contains the subdirectory where data are stored in output. Usually default_config or scotland_mode because
   data are in output/default_config or output/scotland_mode"
   echo " "
   echo "\$2 Are the directories containing intervention specific data seperated by commas."
   echo "E.g. baseline,livingWageIntervention tells the script to aggregate data from output/default_config/baseline"
   echo "and output/default_config/livingWageIntervention"
   echo " "
   echo "\$3 indicates the tags for these variables seperated by commas. These are labels assigned to aggregate values "
   echo "from each intervention that go into pandas labels and plot legends. E.g.  'Baseline, Living Wage Intervention'"
   echo " "
   echo "\$4 indicates the subset functions to use for each intervention seperated by commas. "
   echo "For example, who_alive,who_living_wage_intervention will apply the subset functions who_alive and who_living_wage_intervention"
   echo "found in aggregate_subset_functions.py. This will take some subset of the population such as those who are alive"
   echo "before calculating population aggregates. If we are only interested in comparing differences in SF12 for treated "
   echo "populations this is useful. "
   echo " "
   echo "\$5 simply indicates the prefix of the final line plot. E.g. if set to XXXX the plot will be save as XXXX_lineplot.pdf"
   echo " "
   echo "\$6 indicates the variable of which we are plotting. Before 19/10/23 SF_12_MCS was the only variable we were "
   echo "interested in plotting, but this has now expanded to include equivalent_income and soon will include SF_12_PCS."
   echo " "
   echo "There are some other variables here such as aggregation method set to nanmean for now but open to others later."
   echo " "
   echo "\$6 indicates the variable of which we are plotting. Before 19/10/23 SF_12_MCS was the only variable we were "
   echo "interested in plotting, but this has now expanded to include equivalent_income and soon will include SF_12_PCS."
   echo " "
}

while getopts ":h" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

AGG_METHOD="nanmean"
#AGG_VAR="SF_12_MCS"
# custom baseline for living wage only.
python3 minos/outcomes/aggregate_minos_output.py -m "$1" -d "$2" -t "$3" -a $AGG_METHOD -f "$4" -v "$6"
# stack aggregated files into one long array.
python3 minos/outcomes/aggregate_long_stack.py -m "$1" -s "$2" -t "$3" -r Baseline -a $AGG_METHOD -v "$6"
# make line plot.
python3 minos/outcomes/aggregate_lineplot.py -m "$1" -s "$2" -d "plots" -a $AGG_METHOD -p "$5" -v "$6" -r "$7"
