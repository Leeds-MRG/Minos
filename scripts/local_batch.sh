
NUMRUNS=30
declare -a intlist=(energyDownlift)

TIME=$(date +%Y_%m_%d_%H_%M_%S)

echo "Running $NUMRUNS runs for the Baseline, Living Wage, and Energy Crisis scenarios..."
echo "Starting with baseline..."

## Doing the baseline runs
for i in $(seq 1 $NUMRUNS);
do
    echo "Starting run #$i for the baseline scenario..."
    python3 scripts/run.py -c config/SIPHER7.yaml -o SIPHER7_batch -t "$TIME" -r "$i"
done

## Now intervention runs
for scen in "${intlist[@]}";
do
    for i in $(seq 1 $NUMRUNS);
    do
        echo "Starting run #$i for the $scen scenario..."
        python3 scripts/run.py -c config/SIPHER7.yaml -o SIPHER7_batch -i "$scen" -t "$TIME" -r "$i"
    done
done

echo "COMPLETED A LOCAL BATCH RUN."
