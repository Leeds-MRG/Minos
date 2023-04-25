#!/bin/bash

# file for specifying minos aggregate plots.
# takes one argument mode

read -p "Please specify mode name (default_config/scotland_mode)" MODE


read -p "Make all 5 plots for given mode (y/n)" q1
if [ "$q1" == "y" ];
then
  echo "buttsbuttsbutts"

  exit 1 # end here if just running all plots at once.
fi

read -p "Make baseline vs all child uplift plot (y/n)?" q2
if [ "$q2" == "y" ];
then
  echo "buttsbuttsbutts1"
fi

read -p "Make baseline vs all child uplift plot (y/n)?" q3
if [ "$q3" == "y" ];
then
  echo "buttsbuttsbutts2"
fi

read -p "Make all 5 plots for given mode (y/n)" q4
if [ "$q4" == "y" ];
then
  echo "buttsbuttsbutts3"
fi

read -p "Make baseline vs all child uplift plot (y/n)?" q5
if [ "$q5" == "y" ];
then
  echo "buttsbuttsbutts4"
fi

read -p "Make plot with all 5 interventions together? (y/n)?" q5
if [ "$q5" == "y" ];
then
  echo "buttsbuttsbutts5"
fi

exit 1