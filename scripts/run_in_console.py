from scripts.run import run_pipeline
from scripts.minos_parallel_run import Minos
import itertools
import numpy as np

if __name__ == "__main__":

    configuration_file = "config/testConfig.yaml"
    input_data_dir = "data"
    persistent_data_dir = "persistent_data"
    output_dir = "output"

    uplift = [0, 1000, 10000]  # uplift amount
    percentage_uplift = [10, 25, 75] # uplift proportion.
    run_id = np.arange(1, 50+1, 1)  # 50 repeats for each combination of the above parameters

    # Assemble lists into grand list of all combinations.
    # Each experiment will use one item of this list.
    input_kwargs = {}
    parameter_lists = [item for item in itertools.product(*[uplift, percentage_uplift, run_id])]
    input_kwargs['parameter_lists'] = parameter_lists

    #simulation = run_pipeline(configuration_file, input_data_dir, persistent_data_dir, output_dir)
    input_kwargs = {}
    #parameter_lists = [item for item in itertools.product(*[uplift, percentage_uplift, run_id])]
    #input_kwargs['parameter_lists'] = parameter_lists

    minos_run = Minos(True, **input_kwargs)
    minos_run.main()
