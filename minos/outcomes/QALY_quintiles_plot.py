
from minos.outcomes.QALY_plot import QALY_quintiles_lineplot, ICER_quintiles_lineplot
from minos import  utils
import os
import pandas as pd

def main(mode, intervention, tag):
    # downlaod three qaly datasets

    subset_function_strings = ["who_first_simd_quintile", "who_second_simd_quintile",
                               "who_third_simd_quintile", "who_fourth_simd_quintile", "who_fifth_simd_quintile"]
    qaly_data = pd.DataFrame()
    #tags = (["Baseline"] * 5) + ([tag] * 5)

    for i, plot_intervention in enumerate(["baseline", intervention]):
        file_dir = os.path.join('output/', mode, plot_intervention)
        runtime_list = os.listdir(os.path.abspath(file_dir))
        runtime = utils.get_latest_subdirectory(runtime_list)
        batch_source = os.path.join(file_dir, runtime)
        if plot_intervention == "baseline":
            tag = "Baseline"
        tags = [tag] * 5

        for i, subset_function_string in enumerate(subset_function_strings):
            qaly_subset = pd.read_csv(batch_source + "/" + subset_function_string + '_qalys.csv')
            qaly_subset['tag'] =tags[i]
            qaly_data = pd.concat([qaly_data, qaly_subset])

    print(qaly_data)

    # plot just qalys
    QALY_quintiles_lineplot(qaly_data, f"{mode}_{intervention}_energy_combined_QALY_lineplot")

    # plot icer ratios.
    ICER_quintiles_lineplot(qaly_data, f"{mode}_{intervention}_simd_quintiles_energy_combined_ICR_lineplot")

if __name__ == '__main__':
    main("energy_manchester_scaled", "GBIS", "GBIS")
    main("energy_manchester_scaled", "EPCG", "EPCG")
    main("energy_manchester_scaled", "EPCGandGBIS", "EPCG and GBIS")