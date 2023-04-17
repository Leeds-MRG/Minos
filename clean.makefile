#####################################
### Cleaning
#####################################

.PHONY: clean_out clean_logs clean_data clean_all

clean_all: ### Remove output, log files, generated data files and transition models
clean_all: clean_data clean_out clean_transitions clean_logs

clean_data: ### Remove data files generated in the pipeline
clean_data:
	rm -f data/*/*.csv

clean_out: ### Remove all output files
clean_out:
	rm -rf output/*

#TODO add one for arc4 logs too.
clean_logs: ### Remove log files (including test.log, slurm, and arc logs)
clean_logs:
	rm -rf test.log
	rm -rf logs/*

clean_transitions: ### Remove model .rds files
clean_transitions:
	rm -rf data/transitions/*/*.rds
	rm -rf data/transitions/*/*.txt
	rm -rf data/transitions/*/*/*.rds
	rm -rf data/transitions/*/*/*.txt
	rm -rf data/transitions/scotland/*/*.rds

clean_scotland: ### Clean all files related to Scotland mode
clean_scotland:
	rm -rf data/transitions/scotland/*/*.rds
	rm -rf data/scotland_US/*.csv
	rm -rf data/replenishing/scotland/*.csv

clean_plots: ### Remove all <plot>.pdf files in plots/
	rm -rf plots/*.pdf
