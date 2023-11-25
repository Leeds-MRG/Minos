#!/bin/bash

# Path variable
base_path="/home/luke/Documents/WORK/MINOS/Minos/output/"

# List of directories
directories=("baseline" "energyDownlift" "energyDownliftNoSupport" "livingWageIntervention")

# Step 1: Ask for user input
read -p "Enter a unique descriptive suffix for the output filename: " suffix

# Step 2: Create a directory
output_dir="QALY_analysis_$suffix"
mkdir "$output_dir"

# Step 3 & 4: Loop over directories and copy/ rename qalys.csv
for dir in "${directories[@]}"; do
    newest_dir=$(ls -t "${base_path}${dir}/" | head -n 1)
    cp "${base_path}${dir}/${newest_dir}/qalys.csv" "$output_dir/qalys_${dir}.csv"
done

# Step 5 & 6: Loop over directories and copy/ rename run_1_minos.log
for dir in "${directories[@]}"; do
    newest_dir=$(ls -t "${base_path}${dir}/" | head -n 1)
    cp "${base_path}${dir}/${newest_dir}/run_1_minos.log" "$output_dir/${dir}_1.log"
done

# Step 7: Copy QALY_comparison_*.html files
cp "${base_path}minos/testing/QALY_comparison_"*.html "$output_dir/"

# Step 8: Compress the directory
tar -czvf "$output_dir.tar.gz" "$output_dir"

echo "Script completed successfully!"

