#!/bin/bash
MODE="glasgow_scaled"
SOURCES="baseline,EPCG,EBSS"
TAGS="Baseline,Energy Price Cap Guarantee,Energy Bill Support Scheme"
SUBSETS="who_alive,who_boosted,who_boosted"
SAVE_PREFIX="all_child_uplift"
# custom baseline for living wage only.
bash minos/outcomes/make_lineplot.sh "$MODE" "$SOURCES" "$TAGS" "$SUBSETS" "$SAVE_PREFIX"