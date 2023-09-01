"""File containing shortcut functions used by makefiles"""

from minos.outcomes.make_lineplots import main as lineplot_main
import sys


def all_child_lineplot(*args):
    directories = "baseline,hhIncomeChildUplift"
    tags = "Baseline,All Child Uplift"
    subset_function_strings = "who_kids,who_boosted"
    prefix="baseline_all_child_uplift"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')


def poverty_line_child_lineplot(*args):
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "Baseline,Poverty Line Child Uplift"
    subset_function_strings = "who_below_poverty_line_and_kids,who_boosted"
    prefix="baseline_poverty_child_uplift"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')


def living_wage_lineplot(*args):
    directories = "baseline,livingWageIntervention"
    tags = "Baseline,Living Wage Intervention"
    subset_function_strings = "who_below_living_wage,who_boosted"
    prefix="baseline_living_wage"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')

def ebss_lineplot(*args):
    directories = "baseline,energyDownlift"
    tags = "Baseline,Energy Downlift"
    subset_function_strings = "who_uses_energy,who_boosted"
    prefix="baseline_energy_downlift"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')


def all_five_lineplots(*args):
    directories = "baseline,hhIncomeChildUplift,hhIncomePovertyLineChildUplift,livingWageIntervention,energyDownlift"
    tags = "Baseline,All Child Uplift,Poverty Line Child Uplift,Living Wage Intervention,Energy Downlift"
    subset_function_strings = "who_alive,who_boosted,who_boosted,who_boosted,who_boosted"
    prefix="all_five_combined"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')


########################################
# glasgow spatial population lineplots #
########################################

def glasgow_deciles_lineplot(config_mode, source, subset_function):
    directories = f"{source}," + (f"{source}," * 10)[:-1] # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = f"""{subset_function},{subset_function}_first_simd_decile,{subset_function}_second_simd_decile,{subset_function}_third_simd_decile,{subset_function}_fourth_simd_decile,{subset_function}_fifth_simd_decile,{subset_function}_sixth_simd_decile,{subset_function}_seventh_simd_decile,{subset_function}_eighth_simd_decile,{subset_function}_ninth_simd_decile,{subset_function}_tenth_simd_decile"""
    prefix="25_f{source}_simd_deciles"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_simd_deciles_lineplot(*args):
    directories = "baseline," + ("hhIncomePovertyLineChildUplift," * 10)[:-1] # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = """who_kids,who_kids_first_simd_decile,who_kids_second_simd_decile,who_kids_third_simd_decile,who_kids_fourth_simd_decile,who_kids_fifth_simd_decile,who_kids_sixth_simd_decile,who_kids_seventh_simd_decile,who_kids_eighth_simd_decile,who_kids_ninth_simd_decile,who_kids_tenth_simd_decile"""
    prefix="25_poverty_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_first_decile_lineplot(*args):
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,First"
    subset_function_strings = """who_poverty_kids_first_simd_decile,who_boosted_first_simd_decile"""
    prefix="25_poverty_first_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_tenth_decile_lineplot(*args):
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,Tenth"
    subset_function_strings = """who_poverty_kids_tenth_simd_decile,who_boosted_tenth_simd_decile"""
    prefix="25_poverty_tenth_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    #lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_fifth_decile_lineplot(*args):
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,Fifth"
    subset_function_strings = """who_poverty_kids_fifth_simd_decile,who_boosted_fifth_simd_decile"""
    prefix="25_poverty_fifth_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

def simd_decile_baseline_lineplot(*args):
    directories = ("baseline," * 11)[:-1] # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = "who_alive,who_first_simd_decile,who_second_simd_decile,who_third_simd_decile,who_fourth_simd_decile,who_fifth_simd_decile,who_sixth_simd_decile,who_seventh_simd_decile,who_eighth_simd_decile,who_ninth_simd_decile,who_tenth_simd_decile"
    prefix="baseline_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def epcg_simd_deciles_lineplot(*args):
    directories = ("EBSS," * 11)[:-1] # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = "who_alive,who_first_simd_decile,who_second_simd_decile,who_third_simd_decile,who_fourth_simd_decile,who_fifth_simd_decile,who_sixth_simd_decile,who_seventh_simd_decile,who_eighth_simd_decile,who_ninth_simd_decile,who_tenth_simd_decile"
    prefix="ebss_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

######################################################
# Space for child uplifts split by amount and subset #
######################################################



def all_child(config_mode, boost_amount):
    "nationwide policy"
    directories = f"baseline,{boost_amount}All"
    tags = f"Baseline,£{boost_amount} Nationwide"
    subset_function_strings = "who_kids,who_boosted"
    prefix = f"{boost_amount}_all"
    ref = "Baseline"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def relative_poverty(config_mode, boost_amount):
    "nationwide policy"
    directories = f"baseline,{boost_amount}RelativePoverty"
    tags = f"Baseline,£{boost_amount} Relative Poverty"
    subset_function_strings = "who_below_poverty_line_and_kids,who_boosted"
    prefix = f"{boost_amount}_relative_poverty"
    ref = "Baseline"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

def priority_only(config_mode, boost_amount):
    "universal credit (the actual intervention) only lineplot"
    directories = f"baseline,{boost_amount}Priority"
    tags = f"Baseline,£{boost_amount} Priority Groups"
    subset_function_strings = "who_vulnerable_subgroups,who_boosted"
    prefix = f"{boost_amount}_priority"
    ref = "Baseline"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def UC_priority(config_mode, boost_amount):
    "UC and priority interventions on one lineplot."
    directories = f"baseline,{boost_amount}UniversalCredit,{boost_amount}Priority"
    tags = f"Baseline,£{boost_amount} Universal Credit,£f{boost_amount} Priority Groups"
    subset_function_strings = "who_universal_credit_and_kids,who_boosted,who_boosted"
    prefix= f"{boost_amount}_UC_and_priority"
    ref = "Baseline"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

def incremental_25_to_100(config_mode, intervention_name, intervention_tag):
    "The same intervention in increments from £25 to £100"
    directories = f"baseline,25{intervention_name},50{intervention_name},75{intervention_name},100{intervention_name}"
    tags = f"Baseline,£25 {intervention_tag},£50 {intervention_tag},£75 {intervention_tag},£100 {intervention_tag}"
    subset_function_strings = "who_universal_credit_and_kids,who_boosted,who_boosted,who_boosted"
    prefix=f"25_100_incremental_{intervention_name}_uplift"
    ref = "Baseline"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)



############### #
# main function #
#################

string_to_lineplot_function = {
    # initial line plots
    "all_child": all_child_lineplot,
    "poverty_line_child": poverty_line_child_lineplot,
    "living_wage": living_wage_lineplot,
    "ebss": ebss_lineplot,
    "all_five": all_five_lineplots,

    # glasgow synthpop lineplots
    "glasgow_baseline_all_deciles": glasgow_deciles_lineplot,
    "glasgow_poverty_all_deciles": glasgow_deciles_lineplot,
    "glasgow_universal_credit_all_deciles": glasgow_deciles_lineplot,
    "glasgow_priority_groups_all_deciles": glasgow_deciles_lineplot,

    "glasgow_poverty_first": poverty_line_first_decile_lineplot,
    "glasgow_poverty_fifth": poverty_line_fifth_decile_lineplot,
    "glasgow_poverty_tenth": poverty_line_tenth_decile_lineplot,
    "epcg_simd_lineplot": epcg_simd_deciles_lineplot,

    #incremental boost amounts for UC and Priority populations
    "25_UC_priority": UC_priority,
    "50_UC_priority": UC_priority,
    "75_UC_priority": UC_priority,
    "100_UC_priority": UC_priority,

    "25_all": relative_poverty,
    "50_all": relative_poverty,
    "75_all": relative_poverty,
    "100_all": relative_poverty,

    "25_relative_poverty_": [25],
    "50_relative_poverty": [50],
    "75_relative_poverty": [75],
    "100_relative_poverty": [100],

    "25_universal_credit": relative_poverty,
    "50_universal_credit": relative_poverty,
    "75_universal_credit": relative_poverty,
    "100_universal_credit": relative_poverty,

    "incremental_UC": incremental_25_to_100,
    "incremental_priority": incremental_25_to_100,

}

string_to_lineplot_function_args={

    # glasgow synthpop lineplots
    "glasgow_baseline_all_deciles": ["baseline", "who_kids"],
    "glasgow_poverty_all_deciles": ["baseline", "who_below_poverty_line_and_kids"],
    "glasgow_universal_credit_all_deciles": ["baseline", "who_universal_credit_and_kids"],
    "glasgow_priority_groups_all_deciles": ["baseline", "who_priority_subgroups"],


    "25_UC_priority": [25],
    "50_UC_priority": [50],
    "75_UC_priority": [75],
    "100_UC_priority": [100],

    "25_all": [25],
    "50_all": [50],
    "75_all": [75],
    "100_all": [100],

    "25_universal_credit": [25],
    "50_universal_credit": [50],
    "75_universal_credit": [75],
    "100_universal_credit": [100],

    "25_relative_poverty_": [25],
    "50_relative_poverty": [50],
    "75_relative_poverty": [75],
    "100_relative_poverty": [100],

    "incremental_universal_credit": ["UniversalCredit", "Universal Credit"],
    "incremental_priority_groups": {"Priority", "Priority Groups"},
    "incremental_all_child": {"All", "Nationwide"},
    "incremental_relative_poverty": {"RelativePoverty", "Relative Poverty"},
}

if __name__ == '__main__':

    config_mode = sys.argv[1]
    plot_choice = sys.argv[2]
    plot_function = string_to_lineplot_function[plot_choice]
    if plot_choice in string_to_lineplot_function_args.keys():
        plot_function_args = string_to_lineplot_function_args[plot_choice]
    else:
        plot_function_args = []
    plot_function(config_mode, *plot_function_args)
