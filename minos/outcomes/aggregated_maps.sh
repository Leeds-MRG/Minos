# TODO same thing again for maps.

baseline_single_map ()
{
  INTERVENTION="baseline"
  YEAR=2025
  SUBSET_FUNCTION="who_alive"
  bash minos/outcomes/make_single_map.sh "$MODE" "$INTERVENTION" "$REGION" "$YEAR" "$SUBSET_FUNCTION" plots/"$REGION"_baseline_map.pdf
}

baseline_all_child_comparison_map ()
{
  INTERVENTION1="baseline"
  INTERVENTION2="hhIncomeChildUplift"
  YEAR=2025
  SUBSET_FUNCTION1="who_kids"
  SUBSET_FUNCTION2="who_boosted"
  PLOT_FILE_NAME=plots/"$REGION"_"$INTERVENTION1"_"$INTERVENTION2"_map.pdf
  bash minos/outcomes/make_difference_map.sh "$MODE" "$INTERVENTION1" "$INTERVENTION2" "$REGION" "$YEAR" "$SUBSET_FUNCTION1" "$SUBSET_FUNCTION2" "$PLOT_FILE_NAME"
}

baseline_all_child_comparison_map ()
{
  INTERVENTION1="baseline"
  INTERVENTION2="hhIncomeChildUplift"
  YEAR=2025
  SUBSET_FUNCTION1="who_alive"
  SUBSET_FUNCTION2="who_boosted"
  PLOT_FILE_NAME=plots/"$REGION"_"$INTERVENTION1"_"$INTERVENTION2"_map.pdf
  bash minos/outcomes/make_difference_map.sh "$MODE" "$INTERVENTION1" "$INTERVENTION2" "$REGION" "$YEAR" "$SUBSET_FUNCTION1" "$SUBSET_FUNCTION2" "$PLOT_FILE_NAME"
}

baseline_poverty_line_child_comparison_map()
{
  INTERVENTION1="baseline"
  INTERVENTION2="hhIncomePovertyLineChildUplift"
  YEAR=2025
  SUBSET_FUNCTION1="who_below_poverty_line_and_kids"
  SUBSET_FUNCTION2="who_boosted"
  PLOT_FILE_NAME=plots/"$REGION"_"$INTERVENTION1"_"$INTERVENTION2"_map.pdf
  bash minos/outcomes/make_difference_map.sh "$MODE" "$INTERVENTION1" "$INTERVENTION2" "$REGION" "$YEAR" "$SUBSET_FUNCTION1" "$SUBSET_FUNCTION2" "$PLOT_FILE_NAME"
}

baseline_living_wage_comparison_map ()
{
  INTERVENTION1="baseline"
  INTERVENTION2="livingWageIntervention"
  YEAR=2025
  SUBSET_FUNCTION1="who_below_living_wage"
  SUBSET_FUNCTION2="who_boosted"
  PLOT_FILE_NAME=plots/"$REGION"_"$INTERVENTION1"_"$INTERVENTION2"_map.pdf
  bash minos/outcomes/make_difference_map.sh "$MODE" "$INTERVENTION1" "$INTERVENTION2" "$REGION" "$YEAR" "$SUBSET_FUNCTION1" "$SUBSET_FUNCTION2" "$PLOT_FILE_NAME"
}

baseline_energy_cap_comparison_map ()
{
  INTERVENTION1="baseline"
  INTERVENTION2="energyDownlift"
  YEAR=2025
  SUBSET_FUNCTION1="who_alive"
  SUBSET_FUNCTION2="who_boosted"
  PLOT_FILE_NAME=plots/"$REGION"_"$INTERVENTION1"_"$INTERVENTION2"_map.pdf
  bash minos/outcomes/make_difference_map.sh "$MODE" "$INTERVENTION1" "$INTERVENTION2" "$REGION" "$YEAR" "$SUBSET_FUNCTION1" "$SUBSET_FUNCTION2" "$PLOT_FILE_NAME"
}

map_all_four ()
{
  baseline_single_map
  baseline_all_child_comparison_map
  baseline_living_wage_comparison_map
  baseline_energy_cap_comparison_map
}

map_all_five ()
{
  baseline_single_map
  baseline_all_child_comparison_map
  baseline_poverty_line_child_comparison_map
  baseline_living_wage_comparison_map
  baseline_energy_cap_comparison_map
}

###################################
#
###################################

# choose config

read -p "Please specify mode name (1=default_config/2=scotland_mode)." MODE

if [ "$MODE" == "1" ];
then
  MODE="default_config"
fi

if [ "$MODE" == "2" ];
then
  MODE="scotland_mode"
fi

# choose location.

read -p "Please specify location name (1=manchester, 2=glasgow, 3 =scotland, 4=sheffield)" REGION

if [ "$REGION" == "1" ];
then
  REGION= "manchester"
fi

if [ "$REGION" == "2" ];
then
  REGION="glasgow"
fi

if [ "$REGION" == "3" ];
then
  REGION="scotland"
fi

if [ "$REGION" == "4" ];
then
  REGION="sheffield"
fi

read -p "Make all five maps (baseline only, baseline vs all child uplift, poverty line uplift, living wage intervention, and energy price cap)? (y/n)" qAllFiveMaps
if [ "$qAllFiveMaps" == "y" ];
then
  all_map_all_five
  exit 1 # end here if just running all plots at once.
fi

read -p "Make all four maps (baseline only, baseline vs all child uplift, living wage intervention, and energy price cap)? (y/n)" qAllFourMaps
if [ "$qAllFourMaps" == "y" ];
then
  all_map_all_five
  exit 1 # end here if just running all plots at once.
fi

read -p "Make baseline only map? (y/n)" qBaselineOnly
if [ "$qBaselineOnly" == "y" ];
then
  baseline_single_map
fi

read -p "Make baseline vs all child uplift map? (y/n)" qAllChild
if [ "$qAllChild" == "y" ];
then
  baseline_all_child_comparison_map
fi

read -p "Make baseline vs poverty line child uplift map? (y/n)" qPovertyChild
if [ "$qPovertyChild" == "y" ];
then
  baseline_poverty_line_child_comparison_map
fi

read -p "Make baseline vs living wage map? (y/n)" qLivingWage
if [ "$qLivingWage" == "y" ];
then
  baseline_living_wage_comparison_map
fi

read -p "Make baseline vs energy cap map? (y/n)" qEnergyCap
if [ "$qEnergyCap" == "y" ];
then
  baseline_energy_cap_comparison_map
fi