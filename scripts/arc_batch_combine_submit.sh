scenarios=('baseline', 'livingWageIntervention', 'energyDownlift', 'energyDownliftNoSupport', 'hhIncomeChildUplift', 'hhIncomePovertyLineChildUplift')


for i in "${scenarios[@]}"
do
  echo "Aggregating output files for scenario: $i"
	bash scripts/arc_batch_combine.sh "$i"
done
