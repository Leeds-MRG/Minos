scenarios=('livingWageIntervention' 'energyDownlift' 'energyDownliftNoSupport' 'hhIncomeChildUplift' 'hhIncomePovertyLineChildUplift')


for i in "${scenarios[@]}"
do
  echo "Aggregating output files for scenario: $i"
	qsub scripts/arc_S7_boxplot.sh "$i"
done
