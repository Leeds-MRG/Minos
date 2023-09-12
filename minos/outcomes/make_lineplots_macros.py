"""File containing shortcut functions used by makefiles"""

from minos.outcomes.make_lineplots import main as lineplot_main
import sys


def all_child_lineplot():
    directories = "baseline,hhIncomeChildUplift"
    tags = "Baseline,All Child Uplift"
    subset_function_strings = "who_kids,who_boosted"
    prefix="baseline_all_child_uplift"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')


def poverty_line_child_lineplot():
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "Baseline,Poverty Line Child Uplift"
    subset_function_strings = "who_below_poverty_line_and_kids,who_boosted"
    prefix="baseline_poverty_child_uplift"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')


def living_wage_lineplot():
    directories = "baseline,livingWageIntervention"
    tags = "Baseline,Living Wage Intervention"
    subset_function_strings = "who_below_living_wage,who_boosted"
    prefix="baseline_living_wage"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')

def ebss_lineplot():
    directories = "baseline,energyDownlift"
    tags = "Baseline,Energy Downlift"
    subset_function_strings = "who_uses_energy,who_boosted"
    prefix="baseline_energy_downlift"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')


def all_five_lineplots():
    directories = "baseline,hhIncomeChildUplift,hhIncomePovertyLineChildUplift,livingWageIntervention,energyDownlift"
    tags = "Baseline,All Child Uplift,Poverty Line Child Uplift,Living Wage Intervention,Energy Downlift"
    subset_function_strings = "who_alive,who_boosted,who_boosted,who_boosted,who_boosted"
    prefix="all_five_combined"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')


def all_energy_lineplots():
    directories = "baseline,energyDownlift,energyDownliftNoSupport,EPCG,EBSS"
    tags = "No Energy Crisis,Energy Crisis With No Support,EPCG,EPCG + EBSS"
    subset_function_strings = "who_uses_energy,who_boosted,who_boosted,who_boosted"
    prefix="all_five_combined"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12", method='nanmean')



########################################
# glasgow spatial population lineplots #
########################################

def poverty_line_simd_deciles_lineplot():
    directories = "baseline," + ("hhIncomePovertyLineChildUplift," * 10)[:-1] # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = """who_kids,who_kids_first_simd_decile,who_kids_second_simd_decile,who_kids_third_simd_decile,who_kids_fourth_simd_decile,who_kids_fifth_simd_decile,who_kids_sixth_simd_decile,who_kids_seventh_simd_decile,who_kids_eighth_simd_decile,who_kids_ninth_simd_decile,who_kids_tenth_simd_decile"""
    prefix="25_poverty_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_first_decile_lineplot():
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,First"
    subset_function_strings = """who_poverty_kids_first_simd_decile,who_boosted_first_simd_decile"""
    prefix="25_poverty_first_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_tenth_decile_lineplot():
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,Tenth"
    subset_function_strings = """who_poverty_kids_tenth_simd_decile,who_boosted_tenth_simd_decile"""
    prefix="25_poverty_tenth_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    #lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_fifth_decile_lineplot():
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,Fifth"
    subset_function_strings = """who_poverty_kids_fifth_simd_decile,who_boosted_fifth_simd_decile"""
    prefix="25_poverty_fifth_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

def simd_decile_baseline_lineplot():
    directories = ("baseline," * 11)[:-1] # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = "who_alive,who_first_simd_decile,who_second_simd_decile,who_third_simd_decile,who_fourth_simd_decile,who_fifth_simd_decile,who_sixth_simd_decile,who_seventh_simd_decile,who_eighth_simd_decile,who_ninth_simd_decile,who_tenth_simd_decile"
    prefix="baseline_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def epcg_simd_deciles_lineplot():
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
    "all_energy_lineplots": all_energy_lineplots,

    # glasgow synthpop lineplots
    "glasgow_baseline_all_deciles": simd_decile_baseline_lineplot,
    "glasgow_poverty_all_deciles": poverty_line_simd_deciles_lineplot,
    "glasgow_poverty_first": poverty_line_first_decile_lineplot,
    "glasgow_poverty_fifth": poverty_line_fifth_decile_lineplot,
    "glasgow_poverty_tenth": poverty_line_tenth_decile_lineplot,
    "epcg_simd_lineplot": epcg_simd_deciles_lineplot,
}

if __name__ == '__main__':

    plot_choice = sys.argv[1]
    plot_function = string_to_lineplot_function[plot_choice]
    plot_function()
