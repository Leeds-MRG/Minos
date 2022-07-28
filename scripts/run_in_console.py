from scripts.run import run_pipeline
from scripts.minos_parallel_run import Minos
import itertools
import numpy as np

if __name__ == "__main__":

    configuration_file = "config/testConfig.yaml"
    minos_run = Minos(configuration_file)
    minos_run.main()
