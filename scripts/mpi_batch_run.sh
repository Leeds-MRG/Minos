#!/bin/bash

CONFIG=""
OUTPUT=""
TIME=""
INTERVENTION=""
TOTAL_RUNS=0
BATCH_SIZE=0

# Parse command-line arguments
while getopts "c:o:t:i:r:b:" opt; do
  case ${opt} in
    c )
      CONFIG=$OPTARG
      ;;
    o )
      OUTPUT=$OPTARG
      ;;
    t )
      TIME=$OPTARG
      ;;
    i )
      INTERVENTION=$OPTARG
      ;;
    r )
      TOTAL_RUNS=$OPTARG
      ;;
    b )
      BATCH_SIZE=$OPTARG
      ;;
    \? )
      echo "Usage: $0 -c <config> -o <output> -t <time> -r <total_runs> -b <batch_size> [-i <intervention>]"
      exit 1
      ;;
  esac
done

# Set TIME to current time if not provided
if [ -z "$TIME" ]; then
  TIME=$(date +%Y_%m_%d_%H_%M_%S)
fi

RUN_COUNTER=0

# Run simulations in batches until the total number is reached
while [ "$RUN_COUNTER" -lt "$TOTAL_RUNS" ]; do
  BATCH_END=$((RUN_COUNTER + BATCH_SIZE - 1))

  if [ "$BATCH_END" -ge "$TOTAL_RUNS" ]; then
    BATCH_END=$((TOTAL_RUNS - 1))
  fi

  echo "Starting batch with run IDs $RUN_COUNTER to $BATCH_END..."

  mpiexec -n "$BATCH_SIZE" bash scripts/mpi_run.sh -c "$CONFIG" -o "$OUTPUT" -t "$TIME" -i "$INTERVENTION" -b "$RUN_COUNTER"

  RUN_COUNTER=$((RUN_COUNTER + BATCH_SIZE))
done
