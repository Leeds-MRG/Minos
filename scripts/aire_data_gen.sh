# the LOCF annoyingly won't run on arc4 without shedloads of memory so running it in login node and then the rest on a job.
mkdir -p ./logs/data_gen # make dir if not exists
python3 minos/data_generation/US_format_raw.py --source_dir ../UKDA-6614-stata/stata/stata13_se/ # raw data.
python3 minos/data_generation/US_missing_main.py # LOCF and other deterministic correction.
qsub 'scripts/arc_run_data_gen.sh'