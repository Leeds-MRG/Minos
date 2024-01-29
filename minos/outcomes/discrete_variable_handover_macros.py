"""

File for making aggregated stacked barplots for discrete variables in MINOS outputs.



"""

from make_lineplots import main as lineplots_main

def main():

    # 25 uplift
    for v in ['housing_quality', 'neighbourhood_safety', 'loneliness']:
        directories = "baseline,25UniversalCredit,50UniversalCredit"
        tags = "Baseline,£25 Universal Credit,£50 Universal Credit"
        subset_function_strings = "who_universal_credit_and_kids,who_boosted,who_boosted"
        prefix = "housing_quality_universal_credit"
        mode = 'default_config'
        ref = "Baseline"
        method = 'percentages'
        lineplots_main(directories, tags, subset_function_strings, prefix, mode, ref, v, method)

        # 50 uplift
        directories = "baseline,25RelativePoverty,50RelativePoverty"
        tags = "Baseline,£25 Relative Poverty,£50 Relative Poverty"
        subset_function_strings = "who_universal_credit_and_kids,who_boosted,who_boosted"
        prefix = "housing_quality_relative_poverty"
        method = 'percentages'
        lineplots_main(directories, tags, subset_function_strings, prefix, mode, ref, v, method)


        # living wage
        directories = "baseline,livingWageIntervention"
        tags = "Baseline,Living Wage Intervention"
        subset_function_strings = "who_below_living_wage,who_boosted"
        prefix = "baseline_living_wage"
        method = 'percentages'
        lineplots_main(directories, tags, subset_function_strings, prefix, mode, ref, v, method)

        # Energy crisis
        directories = "baseline,energyDownliftNoSupport,energyDownlift"
        tags = "Baseline,Energy Crisis With No Support,EPCG"
        subset_function_strings = "who_uses_energy,who_boosted,who_boosted"
        prefix = "housing_quality_energy_crisis"
        method = 'percentages'
        lineplots_main(directories, tags, subset_function_strings, prefix, mode, ref, v, method)




if __name__ == '__main__':
    main()