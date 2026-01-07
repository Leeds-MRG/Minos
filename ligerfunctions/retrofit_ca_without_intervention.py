
import random
import time
import os
import numpy as np
import pandas as pd

from scripts.run import run

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(ROOT_DIR)

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def retrofit_ca_without_intervention():
    # 1. Read the population file for intervention and upgrade the house adequate heating
    df = pd.read_csv(os.path.join('data/scaled_manchester_aligned_US', '2020_US_cohort_original.csv'))

    # save the new population
    df.to_csv(os.path.join('data/scaled_manchester_aligned_US', '2020_US_cohort.csv'), index=False)

    # 2. Run the pipeline (part-1)
    args = Namespace(config=os.path.join(ROOT_DIR, 'config/energy_manchester_scaled_part1.yaml'),
                     intervention=None,
                     runID=None,
                     runtime=None,
                     subdir='energy_manchester')
    run(args)
    return

if __name__ == "__main__":

    random.seed(10)
    np.random.seed(10)

    start = time.time()
    retrofit_ca_without_intervention()
    print(f"{(time.time() - start):.2f} Seconds ")
