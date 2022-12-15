
## ARC4 Setup Guide

Using ARC4 over ARC3 is preferable mainly due to its ability to use conda environments. This section shows how to get onto ARC4 from some local mac terminal (or any bash terminal, just be warned the directories will be different).
Note Use of ARC4 will soon be deprecated. Will be moving to a new machine with the slurm scheduler (https://www.schedmd.com/).

We have an example initialisation in ARC4 below which we will break down here. 

1 First, we log onto ARC4 using ssh. This is either done directly if on site at Leeds or via remote access if not. If you don't have an arc4 account apply for one here. https://arcdocs.leeds.ac.uk/getting_started/logon.html
2 The personal user storage is fairly small and so we then create and move to our own /nobackup folder on ARC4 with significantly more (albeit not backed up) storage. 
3 Clone the dust repository into /nobackup.
4 Build a conda virtual environment. Note this is built outside of the git repo so if you wish to reuse the same conda environment and reclone the repo for new experiments you can. Just ignore steps 4 and 5 again in the future. Also placed in /nobackup.
5  Activate the environment and load any desired packages into conda either via `conda install` or in the command to originally create the environment.
6  Move to the minos directory top level in which we perform our experiments.

```
Example initialisation. To use this yourself change all instances of <USERNAME> to your own Leeds username.

# log in to arc4 using ssh.
# note if not on site at Leeds we also need to log in via remote-access
# note will need to be whitelisted on arc4. Ask IT helpdesk.
# other way to do this permanently to avoid logging in twice. add this in..
# ssh <USERNAME>@remote-access.leeds.ac.uk
ssh <USERNAME> @arc4.leeds.ac.uk   
# move to /nobackup
# if no directory in /nobackup create one with 
# mkdir /nobackup/<USERNAME> 
cd /nobackup/<USERNAME>
# clone dust repo into nobackup
git clone https://github.com/Leeds-MRG/Minos

Command "make conda" does the following
# load anaconda
module load python anaconda
# Create virtual environment. Note this is technically outside the git clone and does not need to be run again for future work if you wish.
#Note we can automatically load packages by naming them at the end of this line
conda create -p conda_minos python=3.8
#activate the conda environment.
source activate conda_minos

Then using 'make install' to install minos module and its requirements.
pip install -v -e .
Rscript install.R
```


## Running an Example Experiment in ARC4

We are now ready to run experiments given some experiment module. We use the file 'scripts/minos_parallel_run.py'. This module has two key parameters, namely the agent population (`num_age`) and the proportion of agents observed (`props`). Say we wish to run experiments for 5 and 10 agent populations, 0.5 and 1.0 (50% and 100%) proportion observed. If we also wish to run 20 repeat experiments for each `num_age` and `props` pair we also introduce a third `run_id` parameter giving each repeated experiment a unique intiger id.  We go into `arc.py` and change the inputs for the `ex1_input` function as follows:

```
#open text editor, given we are in the `arc` folder.
nano scripts/minos_parallel_run.py

#default experiment parameters:  0, 50 amount uplifted. 25, 50, 75% prop uplifted. 50 runs.
    uplift = [0, 50]  # assimilation rates
    percentage_uplift = [10, 25, 75] #gaussian observation noise standard deviation
    run_id = np.arange(1, 50+1, 1)  # 30 repeats for each combination of the above parameters


# new desired parameters: 0, 20, 50 uplifed. 10 20 30% prop uplifted. 100 runs.
uplift = [0, 1000, 10000]  # assimilation rates
percentage_uplift = [10, 25, 75] #gaussian observation noise standard deviation
run_id = np.arange(1, 50+1, 1)  # 30 repeats for each combination of the above parameters

```

With our new parameters defined we now calculate the total number of experiments. This is simply multiplying the length of each parameter list (num_age, props, and run_id) together to get the number of unique experiment combinations. In this case we have N = 3x3x100 = 900 experiments and must update `arc.sh` with this number such that it runs exactly the right number of experiments. If this number is say 2 it will only run the first 2 experiments and ignore the remaining 78. Likewise, if we choose 82 runs we will have two dead runs that can throw errors unneccesarily.

```
nano scripts/arc.sh #open text editor

# change number of minos runs from 3 (test value) to  900 (actual value of new parameters)
#$ -t 1-3 #run tasks 1 through 3

becomes

#$ -t 1-900 # run tasks 1 through 900
```

Note there are a number of other items in this bash script that define the minos run. The type of arc4 nodes assigned and vram can improve throughput times but are well discussed in the arc documentation. Now everything is ready to run the experiment in arc. To do this we use the simple command `qsub`.

```
qsub scripts/arc.sh 
```

```
qstat - gives various progress diagnostics for all running jobs.
qdel <job_id> - cancel current job with given job_id.
```

We can also check the active progress or errors of any individual experiment using the .o (output) and .e (errors) files generated for each experiment. For example, if we ran the all 80 experiments above and wish to check upon the first one (index starts at 1 here.) we do the following:

```
# call desired .o or .e file using format
# nano arc.sh.o<job_id>.<task_id> 
#e.g. say we have a run with id 1373131 and check the first experiment.
nano arc.sh.o.1373131.1

## Hosts assigned to job 1373131.1:
##
## dc2s5b3d.arc3.leeds.ac.uk 5 slots
##
## Resources granted:
##
## h_vmem = 15G (per slot)
## h_rt   = 48:00:00
## disk   = 1G (per slot)

UKF params: {'Sensor_Noise': 1, 'Process_Noise': 1, 'sample_rate': 1, 'do_restr$
Model params: {'pop_total': 5, 'width': 200, 'height': 100, 'gates_in': 3, 'ga$
        Iteration: 0/3600
        Iteration: 100/3600
        Iteration: 200/3600
        Iteration: 300/3600
        Iteration: 400/3600
0:27:34.378509

#for any errors that occur
#nano arc.sh.e<job_id>.<task_id>
#e.g.
nano arc.sh.e.1373131.1
OMP: Warning #181: GOMP_CPU_AFFINITY: ignored because KMP_AFFINITY has been def$

# This is from the UKF work. Get a minos log instead..
```

## Analysis

If the experiment runs successfully it will output 900 csv instances which we wish to analyse. I did this by copying the files back into linux and performing post-hoc analysis locally. Could easily run scripts on the machine and download the final figures instead. To copy the files use your LOCAL unix terminal (Not the arc4 terminal).

```
scp -r <USERNAME>@leeds.ac.uk:source_in_arc/* random_source/minos/output/ex1/.

e.g.
scp -r <USERNAME>@arc3.leeds.ac.uk:/nobackup/<USERNAME>/dust/Projects/ABM_DA/experiments/ukf_experiments/ukf_results/* /home/rob/dust/Projects/ABM_DA/experiments/ukf_experiments/ukf_results/.
```

NOT NECESSARY ANYMORE BUT USEFUL TO KNOW.
If we are accessing arc remotely we have an intermediate server to go through and so use proxy jump. The remote access server at Leeds struggles as is so don't scp directly it unless you want a complementary lecture from the arc team.

https://superuser.com/questions/276533/scp-files-via-intermediate-host
With the format:

scp -oProxyJump=user@remote-access.leeds.ac.uk
e.g.
```
scp -oProxyJump=medrclaa@remote-access.leeds.ac.uk medrclaa@arc4.leeds.ac.uk:/nobackup/medrclaa/dust/Projects/ABM_DA/experiments/ukf_experiments/results/agg* /Users/medrclaa/new_aggregate_results
```

These files can then be used as desired. Currently this is a lot of aggregating SF-12 means and projecting them over spatial data (I.E. sheffield). 
