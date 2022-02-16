#!/usr/bin/env python3
"""parallel_run: Run 'run.py' (Dynamic Microsimulation) in parallel

Examples
--------
# example (run over 16 LADs):
python scripts/Daedalus_parallel_run.py -c config/default_config.yaml --path_pop_files "data/ssm_*ppp*csv" --pop_start_index 0 --pop_end_index 16 --input_data_dir data --persistent_data_dir persistent_data --output_dir output --process_np 8

# example (run over all LADs):
python scripts/Daedalus_parallel_run.py -c config/default_config.yaml --path_pop_files "data/ssm_*ppp*csv" --input_data_dir data --persistent_data_dir persistent_data --output_dir output --process_np 8
"""

# TODO: RC adapt this to AM to allow parallel computing on ARC4.

import argparse
from datetime import datetime
from glob import glob
import multiprocessing
import os
import time

from run import run_pipeline

# ----------------------
def run_pipeline_location_list(configuration_file, 
                               location_list=None, 
                               input_data_dir=None, 
                               persistent_data_dir=None, 
                               output_dir=None):
    """Run `run.py` for a list of locations."""

    for one_location in location_list:
        start_time = datetime.now()
        try:
            run_pipeline(configuration_file, 
                        one_location, 
                        input_data_dir, 
                        persistent_data_dir, 
                        output_dir)
        except Exception as err:
            fio = open(os.path.join(output_dir, "error_log.txt"), "a+")
            fio.writelines(err + "\n")
            fio.close()
        print("Time to process/simulation, {}: {}".format(one_location, datetime.now() - start_time))

# ----------------------
def check_par_jobs(jobs, sleep_time=1):
    """
    check if all the parallel jobs are finished
    :param jobs:
    :param sleep_time:
    :return:
    """
    pp_flag = True
    while pp_flag:
        for proc in jobs:
            if proc.is_alive():
                time.sleep(sleep_time)
                pp_flag = True
                break
            else:
                pp_flag = False
    if not pp_flag:
        print('\n\n================================')
        print('All %s processes are finished...' % len(jobs))
        print('================================')

# ----------------------
def run_parallel(target_func, location_list, start, end, process_np=8, **kwds):
    """Run target_func in parallel using multiprocessing

    Args:
        target_func: function to be run in parallel
        location_list: list of locations/LADs
        start: start index, i.e., location_list[start:end] will be used
        end: end index, i.e., location_list[start:end] will be used
        process_np (int, optional): Number of CPUs to be used. Defaults to 8.
    """
    
    if end < 0:
        end = len(location_list)

    req_proc = min(end, process_np)

    step = int((end - start) / req_proc + 1)

    jobs = []
    for index in range(req_proc):
        starti = start + index * step
        endi = min(start + (index + 1) * step, end)
        if starti >= endi:
            break

        location_list_one_node = location_list[starti:endi]
        p = multiprocessing.Process(target=target_func,
                                    args=(kwds["configuration_file"],
                                          location_list_one_node, 
                                          kwds["input_data_dir"], 
                                          kwds["persistent_data_dir"], 
                                          kwds["output_dir"]))
        #print(location_list_one_node)
        jobs.append(p)
    for i in range(len(jobs)):
        jobs[i].start()
        
    check_par_jobs(jobs)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run Dynamic Microsimulation in parallel")

    parser.add_argument("-c", "--config", required=True, type=str, metavar="config-file",
                        help="the model config file (YAML)")
    parser.add_argument('--path_pop_files', help='path to population files, wildcard accepted', default=None)
    parser.add_argument('--pop_start_index', help='pop_files[pop_start_index:pop_end_index] will be used', type=int, default=0)
    parser.add_argument('--pop_end_index', help='pop_files[pop_start_index:pop_end_index] will be used. If < 0, all files will be used.', type=int, default=-1)
    parser.add_argument('--input_data_dir', help='directory where the input data is', default=None)
    parser.add_argument('--persistent_data_dir', help='directory where the persistent data is', default=None)
    parser.add_argument('--output_dir', type=str, help='directory where the output data is saved', default=None)
    parser.add_argument('--process_np', type=int, help='number of processors to be used', default=8)

    args = parser.parse_args()

    list_pop_files = glob(args.path_pop_files)
    
    list_all_LADs = []
    for one_file in list_pop_files:
        list_all_LADs.append(os.path.basename(one_file).split("_")[1])
    list_all_LADs.sort()

    run_parallel(run_pipeline_location_list, 
                 list_all_LADs,
                 args.pop_start_index, 
                 args.pop_end_index,
                 process_np=args.process_np,
                 configuration_file=args.config,
                 input_data_dir=args.input_data_dir,
                 persistent_data_dir=args.persistent_data_dir,
                 output_dir=args.output_dir)
