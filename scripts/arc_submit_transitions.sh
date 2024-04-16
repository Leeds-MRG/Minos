#!/bin/bash
#qrsh -l h_rt=00:15:00,h_vmem=4G -pe smp 2
qsub -pe 8 'scripts/arc_run_transitions.sh'
