# create these if they dont exist. Will crash arc4 if you dont do this.
mkdir -p logs
mkdir -p logs/sum
mkdir -p logs/sum/log
mkdir -p logs/sum/errors




echo "Generating summary outputs for $3 in $1"
echo "Files will be saved in $2"

qsub scripts/arc_SCP_summarise.sh $1 $2 $3