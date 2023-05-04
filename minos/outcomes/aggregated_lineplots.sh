#!/bin/bash

# File for specifying minos aggregate plots.
# Takes one argument mode

# Function for all child uplift below the poverty line lineplot.
poverty_line_child_uplift ()
{
  SOURCES="baseline,hhIncomePovertyLineChildUplift"
  TAGS="Baseline,Poverty Line Children Uplift"
  SUBSETS="who_below_poverty_line_and_kids,who_boosted"
  SAVE_PREFIX="poverty_line_child_uplift"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

# Function for all child uplift lineplot.
all_child_uplift ()
{
  SOURCES="baseline,hhIncomeChildUplift"
  TAGS="Baseline,All Children Uplift"
  SUBSETS="who_kids,who_kids"
  SAVE_PREFIX="all_child_uplift"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

# Function for plotting living wage intervention lineplot.
living_wage ()
{
  SOURCES="baseline,livingWageIntervention"
  TAGS="Baseline,Living Wage Intervention"
  SUBSETS="who_below_living_wage,who_boosted"
  SAVE_PREFIX="living_wage_treated"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

# Function for plotting energy downlift lineplot.
energy_downlift ()
{
  SOURCES="baseline,energyDownlift"
  TAGS="Baseline,Energy Downlift"
  SUBSETS=" who_alive,who_alive"
  SAVE_PREFIX= "energy_downlift"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

# Plot for all child uplift, poverty line child uplift, and energy downlift plots together.
main_three_interventions_combined () {
  SOURCES="baseline,hhIncomePovertyLineChildUplift,livingWageIntervention,energyDownlift"
  TAGS="Baseline,Poverty Line Children Uplift,Living Wage,Energy Downlift"
  SUBSETS="who_alive,who_alive,who_alive,who_alive"
  SAVE_PREFIX= "all_four"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}


# Plot for all child uplift, poverty line child uplift, living wage, and energy downlift lineplots together.
main_four_interventions_combined () {
  SOURCES="baseline,hhIncomeChildUplift,hhIncomePovertyLineChildUplift,livingWageIntervention,energyDownlift"
  TAGS="Baseline,£25 All Child Uplift,Poverty Line Children Uplift,Living Wage,Energy Downlift"
  SUBSETS="who_alive,who_alive,who_alive,who_alive,who_alive"
  SAVE_PREFIX= "all_five"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

all_three_main_plots ()
{
  all_child_uplift
  living_wage
  energy_downlift
  main_three_interventions_combined
}

all_four_main_plots ()
{
  poverty_line_child_uplift
  all_child_uplift
  living_wage
  energy_downlift
  main_four_interventions_combined
}

######################################################
# Main body of script asking for user specified plots.
######################################################

# Specify MINOS mode to use. Should be the config name e.g. default_config or scotland_mode.
read -p "Please specify mode name (1=default_config/2=scotland_mode)." MODE

if [ "$MODE" == "1" ];
then
  MODE="default_config"
fi

if [ "$MODE" == "2" ];
then
  MODE="scotland_mode"
fi

# Ask for both single and combined plots.
read -p "Make lineplots for 3 main interventions with NO POVERTY LINE (all child, living wage, energy downlift)? (y/n)" qMainThree
if [ "$qMainThree" == "y" ];
then
  all_three_main_plots
  exit 1 # end here if just running all plots at once.
fi

read -p "Make lineplots for all 4 main interventions (including poverty line uplift)? (y/n)" qMainFour
if [ "$qMainFour" == "y" ];
then
  all_four_main_plots
  exit 1 # end here if just running all plots at once.
fi

# Ask for individual plots only.
read -p "Make baseline vs poverty line child uplift plot (y/n)?" qPovertyLineOnly
if [ "$qPovertyLineOnly" == "y" ];
then
  poverty_line_child_uplift
fi

read -p "Make baseline vs all child uplift lineplot (y/n)?" qAllChildOnly
if [ "$qAllChildOnly" == "y" ];
then
  all_child_uplift
fi

read -p "Make baseline vs living wage intervention lineplot (y/n)?" qLivingWageOnly
if [ "$qLivingWageOnly" == "y" ];
then
  living_wage
fi

read -p "Make baseline vs energy downlift lineplot (y/n)?" qEnergyDownliftOnly
if [ "$qEnergyDownliftOnly" == "y" ];
then
  energy_downlift
fi

# Ask for combined plots only.
read -p "Make plot with 3 main interventions together (NO POVERTY LINE)? (y/n)?" qCombinedThreeOnly
if [ "$qCombinedThreeOnly" == "y" ];
then
  main_three_interventions_combined
fi

read -p "Make plot with all 4 main interventions together? (y/n)?" qCombinedFourOnly
if [ "$qCombinedFourOnly" == "y" ];
then
  main_four_interventions_combined
fi

exit 1
