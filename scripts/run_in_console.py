from scripts.run import run_pipeline
from scripts.minos_parallel_run import Minos
import itertools

if __name__ == "__main__":

    configuration_file = "config/arcConfig.yaml"
    input_data_dir = "data"
    persistent_data_dir = "persistent_data"
    output_dir = "output"

    #simulation = run_pipeline(configuration_file, input_data_dir, persistent_data_dir, output_dir)
    input_kwargs = {}
    #parameter_lists = [item for item in itertools.product(*[uplift, percentage_uplift, run_id])]
    #input_kwargs['parameter_lists'] = parameter_lists

    minos_run = Minos(True, **input_kwargs)
    minos_run.main()
