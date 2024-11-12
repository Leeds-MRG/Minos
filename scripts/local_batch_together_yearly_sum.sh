

echo $1
echo $2
echo $3
echo $4
echo $5

mkdir -p "$1/$2"

echo "Generating summary outputs for $3 in $1"
echo "Files will be saved in $2"


for ((i = $4; i <= $5; i++))
do
  Rscript minos/read_sum_together_1year.R $1 $2 $3 $i
done
