#!/bin/bash
INTERVENTION1="energyPriceCapGuarantee"
INTERVENTION2="energyBillSupportScheme"
MODE="glasgow_scaled"
YEAR=2025
SUBSET_FUNCTION1="who_boosted"
SUBSET_FUNCTION2="who_boosted"
PLOT_FILE_NAME=plots/"$REGION"_"$INTERVENTION1"_"$INTERVENTION2"_map.pdf
bash minos/outcomes/make_difference_map.sh "$MODE" "$INTERVENTION1" "$INTERVENTION2" "$REGION" "$YEAR" "$SUBSET_FUNCTION1" "$SUBSET_FUNCTION2" "$PLOT_FILE_NAME"