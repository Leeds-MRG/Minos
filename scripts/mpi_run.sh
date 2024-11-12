#!/bin/bash

CONFIG=""
OUTPUT=""
INTERVENTION=""
TIME=""
BASE_ID=0

# Parse command-line arguments
while getopts "c:o:i:t:b:" opt; do
  case ${opt} in
    c )
      CONFIG=$OPTARG
      ;;
    o )
      OUTPUT=$OPTARG
      ;;
    i )
      INTERVENTION=$OPTARG
      ;;
    t )
      TIME=$OPTARG
      ;;
    b )
      BASE_ID=$OPTARG
      ;;
    \? )
      echo "Usage: $0 -c <config> -o <output> [-i <intervention>] [-t <time>] -b <base_id>"
      exit 1
      ;;
  esac
done

# Set TIME to current date and time if not provided
if [ -z "$TIME" ]; then
  TIME=$(date +%Y_%m_%d_%H_%M_%S)
fi

# Calculate a unique RUN_ID by adding the MPI rank to the BASE_ID
RUN_ID=$((BASE_ID + ${OMPI_COMM_WORLD_RANK:-0}))

# Build the command
CMD="python3 scripts/run.py -c $CONFIG -o $OUTPUT -t $TIME -r $RUN_ID"

# Add intervention if specified
if [ -n "$INTERVENTION" ]; then
  CMD+=" -i $INTERVENTION"
fi

# Run the command
eval $CMD
