#!/bin/bash

# uplift for population on long term sick/disability
disabled_uplift ()
{
  SOURCES="baseline,hhIncomeChildUplift"
  TAGS="Baseline,Disabled Children Uplift"
  SUBSETS="who_disabled,who_disabled"
  SAVE_PREFIX= "disabled_child_uplift"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

# uplift for ethnic minority families
minority_uplift () {
  SOURCES="baseline,hhIncomeChildUplift"
  TAGS="Baseline,Minority Children Uplift"
  SUBSETS="who_ethnic_minority,who_ethnic_minority"
  SAVE_PREFIX= "minority_child_uplift"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

# uplift for families with at least three children
three_child_uplift ()
{
 SOURCES="baseline,hhIncomeChildUplift"
  TAGS="Baseline,Three Children Uplift"
  SUBSETS="who_three_kids,who_three_kids"
  SAVE_PREFIX= "three_child_uplift"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

# omitted due to low sample size and not relationship status variables yet.
young_single_mother_uplift ()
{
  SOURCES="baseline,hhIncomeChildUplift"
  TAGS="Baseline,Young Mother Children Uplift"
  SUBSETS="who_young_mother,who_young_mother"
  SAVE_PREFIX= "young_mother_child_uplift"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

young_adult_uplift ()
{
  SOURCES="baseline,hhIncomeChildUplift"
  TAGS="Baseline,Young Adult Children Uplift"
  SUBSETS="who_young_adults,who_young_adults"
  SAVE_PREFIX= "young_adult_child_uplift"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

uneducated_uplift ()
{
  SOURCES="baseline,hhIncomeChildUplift"
  TAGS="Baseline,Low Education Children Uplift"
  SUBSETS="who_no_formal_education,who_no_formal_education"
  SAVE_PREFIX= "uneducated_child_uplift"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

vulnerable_combined_uplift ()
{
  SOURCES="baseline,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift,hhIncomeChildUplift"
  TAGS="Baseline,All Children Uplift,Disabled Children Uplift,Minority Children Uplift,Three Children Uplift,Young Single Parent Children Uplift,Low Eduction Children Uplift"
  SUBSETS="who_alive,who_kids,who_disabled,who_ethnic_minority,who_three_kids,who_young_adults,who_no_formal_education"
  SAVE_PREFIX= "all_vulnerable"
  # custom baseline for living wage only.
  bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"
}

all_vulnerable_uplifts ()
{
  disabled_uplift
  minority_uplift
  three_child_uplift
  #young_single_mother_uplift # omitted due to low sample size.
  young_adult_uplift
  uneducated_uplift
  vulnerable_combined_uplift
}

# Specify MINOS mode to use. Should be the config name e.g. default_config or scotland_mode.
read -p "Please specify mode name (e.g. default_config/scotland_mode)." MODE

# Ask for both single and combined plots.
read -p "Make all vulnerable subgroup lineplots? (y/n)" qAllVulnerable
if [ "$qMainThree" == "y" ];
then
  all_vulnerable_uplifts
  exit 1 # end here if just running all plots at once.
fi

# TODO do the individual plots here later.