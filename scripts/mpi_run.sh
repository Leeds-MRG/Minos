#!/bin/bash

# Default values
CONFIG=""
OUTPUT=""
INTERVENTION=""

# Set the current date and time
TIME=$(date +%Y_%m_%d_%H_%M_%S)

# Parse command-line arguments
while getopts "c:o:i:" opt; do
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
    \? )
      echo "Usage: $0 -c <config> -o <output> [-i <intervention>]"
      exit 1
      ;;
  esac
done

# Check if mandatory arguments are set
if [ -z "$CONFIG" ] || [ -z "$OUTPUT" ]; then
  echo "Error: Both -c <config> and -o <output> are required."
  exit 1
fi

# Build the command
CMD="python scripts/run.py -c ${CONFIG} -o ${OUTPUT} -t ${TIME} -r \${OMPI_COMM_WORLD_RANK}"

# Add intervention argument if provided
if [ -n "$INTERVENTION" ]; then
    CMD+=" -i ${INTERVENTION}"
fi

# Run the command
echo "Running command: $CMD"
eval $CMD
