
from minos.outcomes.QALY_plot import QALY_lineplot, ICER_lineplot
from minos import  utils
import os
import pandas as pd


def main(mode, interventions):
    # downlaod three qaly datasets

    subset_function_string = "who_private_rental_and_UC"
    qaly_data = pd.DataFrame()
    tags = ["Baseline", "EPCG", "WHS", "EPCG and WHS"]#, "Good Heating Dummy"
    for i, intervention in enumerate(interventions):
        file_dir = os.path.join('output/', mode, intervention)
        runtime_list = os.listdir(os.path.abspath(file_dir))
        runtime = utils.get_latest_subdirectory(runtime_list)
        batch_source= os.path.join(file_dir, runtime)
        qaly_subset = pd.read_csv(batch_source + "/" + subset_function_string + '_qalys.csv')
        qaly_subset['tag'] =tags[i]
        qaly_data = pd.concat([qaly_data, qaly_subset])

    # plot just qalys
    QALY_lineplot(qaly_data, f"{mode}_{subset_function_string}_energy_combined_QALY_lineplot")

    # plot icer ratios.
    ICER_lineplot(qaly_data, f"{mode}_{subset_function_string}_energy_combined_ICR_lineplot")

if __name__ == '__main__':
    main("energy_manchester_scaled",["baseline",  "EPCG", "GBIS", "EPCGandGBIS"])#"goodHeatingDummy",