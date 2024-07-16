
NUMRUNS=2
declare -a intlist=(ChildPovertyReductionRELATIVE_2)

TIME=$(date +%Y_%m_%d_%H_%M_%S)

echo "Running $NUMRUNS runs for the Baseline, All Child Uplift, and Living Wage scenarios..."
echo "Starting with baseline..."

## Doing the baseline runs
for i in $(seq 1 $NUMRUNS);
do
    echo "Starting run #$i for the baseline scenario..."
    python3 scripts/run.py -c config/default.yaml -o default_config -t "$TIME" -r "$i"
done

## Now intervention runs
for scen in "${intlist[@]}";
do
    for i in $(seq 1 $NUMRUNS);
    do
        echo "Starting run #$i for the $scen scenario..."
        python3 scripts/run.py -c config/default.yaml -o default_config -i "$scen" -t "$TIME" -r "$i"
    done
done

echo "COMPLETED A LOCAL BATCH RUN."
