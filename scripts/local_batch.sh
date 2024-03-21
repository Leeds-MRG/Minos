
NUMRUNS=10
declare -a intlist=(50All)

TIME=$(date +%Y_%m_%d_%H_%M_%S)

CONF=glasgow_scaled
OUTPUT_SUBDIR=glasgow_scaled

echo "Running $NUMRUNS runs..."
echo "Starting with baseline..."

## Doing the baseline runs
for i in $(seq 1 $NUMRUNS);
do
    echo "Starting run #$i for the baseline scenario..."
    python3 scripts/run.py -c config/$CONF.yaml -o $OUTPUT_SUBDIR -t "$TIME" -r "$i"
done

## Now intervention runs
for scen in "${intlist[@]}";
do
    for i in $(seq 1 $NUMRUNS);
    do
        echo "Starting run #$i for the $scen scenario..."
        python3 scripts/run.py -c config/$CONF.yaml -o $OUTPUT_SUBDIR -i "$scen" -t "$TIME" -r "$i"
    done
done

echo "COMPLETED A LOCAL BATCH RUN."