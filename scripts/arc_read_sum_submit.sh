# create these if they dont exist. Will crash arc4 if you dont do this.
mkdir -p logs
mkdir -p logs/sum
mkdir -p logs/sum/log
mkdir -p logs/sum/errors


## Check that 3 arguments have been provided
if [ "$#" -eq 3 ]; then
  echo "You have not submitted the correct number of command line arguments (3). The required arguments in order are:"
  echo "1. Output subdirectory i.e. default_config"
  echo "2. Save directory. This will be created if it does not exist already. i.e. summary_out"
  echo "3. Scenario name i.e. baseline"
  echo
  echo "Usage: $0 <output_subdirectory> <save_directory> <scenario_name>"
  echo "E.g.: $0 default_config summary_out baseline"
  echo "This will summarise datafiles found in default_config/baseline, and save the files to default_config/summary_out/"
  exit 1
fi

# Check if output subdirectory exists, fail if not
if [ ! -d "output/$1" ]; then
  echo "The output subdirectory $1 does not exist. Please check you have correctly specified the name as first argument"
  exit 1
fi
# Check if scenario folder exists, fail if not
if [ ! -d "output/$1/$3" ]; then
  echo "The scenario you have specified is not present in output/$1. Please check you have correctly specified a name"
  echo "that exists in your output subdirectory"
  exit 1
fi

mkdir -p "$1/$2"

echo "Generating summary outputs for $3 in $1"
echo "Files will be saved in $2"

qsub scripts/arc_SCP_summarise.sh $1 $2 $3