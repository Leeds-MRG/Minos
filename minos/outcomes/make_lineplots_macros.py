"""File containing shortcut functions used by makefiles"""

from minos.outcomes.make_lineplots import main as lineplot_main
import sys


####################
# Old school plots #
####################

def all_child_lineplot(*args):
    directories = "baseline,hhIncomeChildUplift"
    tags = "Baseline,All Child Uplift"
    subset_function_strings = "who_kids,who_boosted"
    prefix = "baseline_all_child_uplift"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12",
                  method='nanmean')


def poverty_line_child_lineplot(*args):
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "Baseline,Poverty Line Child Uplift"
    subset_function_strings = "who_below_poverty_line_and_kids,who_boosted"
    prefix = "baseline_poverty_child_uplift"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12",
                  method='nanmean',region=None)


def living_wage_lineplot(*args):
    directories = "baseline,livingWageIntervention"
    tags = "Baseline,Living Wage Intervention"
    subset_function_strings = "who_below_living_wage,who_boosted"
    prefix = "baseline_living_wage"
    config_mode = "default_config"
    ref="Baseline"
    v="SF_12"
    method = "nanmean"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v,
                  method=method)
    method = 'SF12_AUC'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

def epcg_and_no_support_lineplot(*args):
    directories = "baseline,energyDownlift,energyDownliftNoSupport"
    tags = "Baseline,EPCG,No Support"
    subset_function_strings = "who_uses_energy,who_boosted,who_boosted"
    prefix = "baseline_energy_downlift"
    config_mode = "default_config"
    ref="Baseline"
    v = "SF_12"
    method = "nanmean"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v,
                  method=method)
    method = 'SF12_AUC'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def ebss_lineplot(*args):
    directories = "baseline,energyDownlift"
    tags = "Baseline,Energy Downlift"
    subset_function_strings = "who_uses_energy,who_boosted"
    prefix = "baseline_ebss"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12",
                  method='nanmean')


def all_five_lineplots(*args):
    directories = "baseline,25UniversalCredit,25RelativePoverty,livingWageIntervention,energyDownlift"
    tags = "Baseline,£25 Universal Credit Child Uplift,£25 Poverty Line Child Uplift,Living Wage Intervention, EPCG"
    subset_function_strings = "who_alive,who_boosted,who_boosted,who_boosted,who_boosted"
    prefix = "all_five_combined"
    config_mode = "default_config"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref="Baseline", v="SF_12",
                  method='nanmean')


def social_science_all_plots(config_mode):
    # all social science lineplots together.
    epcg_and_no_support_lineplot(config_mode)
    #UC_relative_poverty(config_mode, 25)
    #UC_relative_poverty(config_mode, 50)
    #all_five_lineplots(config_mode)
    living_wage_lineplot(config_mode)

    incremental_25_to_50(config_mode, "UniversalCredit", "Universal Credit", "who_universal_credit_and_kids")
    incremental_25_to_50(config_mode, "RelativePoverty", "Relative Poverty", "who_below_poverty_line_and_kids")


########################################
# glasgow spatial population lineplots #
########################################

def deciles_lineplot(config_mode, source, tag, subset_function, region=None):
    # directories = f"baseline," + (f"{source}," * 10)[:-1] # repeat 11 times and cut off last comma.
    directories = f"baseline,{source}"  # repeat 11 times and cut off last comma.
    tags = f"Baseline,{tag}"
    subset_function_strings = f"who_kids,who_kids"
    prefix = f"{source}_simd_deciles"
    ref = "Baseline"
    v = "SF_12"
    method = "deciles_separate_baselines"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)

def deciles_lineplot(config_mode, source, tag, subset_function, region=None):
    # directories = f"baseline," + (f"{source}," * 10)[:-1] # repeat 11 times and cut off last comma.
    directories = f"baseline,{source}"  # repeat 11 times and cut off last comma.
    tags = f"Baseline,{tag}"
    subset_function_strings = f"who_kids,who_kids"
    prefix = f"{source}_simd_deciles"
    ref = "Baseline"
    v = "SF_12"
    method = "deciles_separate_baselines"
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)



def glasgow_deciles_lineplot(config_mode, source, subset_function):
    # directories = f"baseline," + (f"{source}," * 10)[:-1] # repeat 11 times and cut off last comma.
    directories = f"{source}," + (f"{source}," * 10)[:-1]  # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    # subset_function_strings = f"""who_kids,who_kids_first_simd_decile,who_kids_second_simd_decile,who_kids_third_simd_decile,who_kids_fourth_simd_decile,who_kids_fifth_simd_decile,who_kids_sixth_simd_decile,who_kids_seventh_simd_decile,who_kids_eighth_simd_decile,who_kids_ninth_simd_decile,who_kids_tenth_simd_decile"""
    subset_function_strings = "who_alive,who_first_simd_decile,who_second_simd_decile,who_third_simd_decile,who_fourth_simd_decile,who_fifth_simd_decile,who_sixth_simd_decile,who_seventh_simd_decile,who_eighth_simd_decile,who_ninth_simd_decile,who_tenth_simd_decile"
    prefix = f"25_{source}_simd_deciles"
    ref = "National Average"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_simd_deciles_lineplot(*args):
    directories = "baseline," + ("hhIncomePovertyLineChildUplift," * 10)[:-1]  # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = """who_kids,who_kids_first_simd_decile,who_kids_second_simd_decile,who_kids_third_simd_decile,who_kids_fourth_simd_decile,who_kids_fifth_simd_decile,who_kids_sixth_simd_decile,who_kids_seventh_simd_decile,who_kids_eighth_simd_decile,who_kids_ninth_simd_decile,who_kids_tenth_simd_decile"""
    prefix = "25_poverty_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_first_decile_lineplot(*args):
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,First"
    subset_function_strings = """who_poverty_kids_first_simd_decile,who_boosted_first_simd_decile"""
    prefix = "25_poverty_first_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_tenth_decile_lineplot(*args):
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,Tenth"
    subset_function_strings = """who_poverty_kids_tenth_simd_decile,who_boosted_tenth_simd_decile"""
    prefix = "25_poverty_tenth_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method = 'nanmean'
    # lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def poverty_line_fifth_decile_lineplot(*args):
    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,Fifth"
    subset_function_strings = """who_poverty_kids_fifth_simd_decile,who_boosted_fifth_simd_decile"""
    prefix = "25_poverty_fifth_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def simd_decile_baseline_lineplot(*args):
    directories = ("baseline," * 11)[:-1]  # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = "who_alive,who_first_simd_decile,who_second_simd_decile,who_third_simd_decile,who_fourth_simd_decile,who_fifth_simd_decile,who_sixth_simd_decile,who_seventh_simd_decile,who_eighth_simd_decile,who_ninth_simd_decile,who_tenth_simd_decile"
    prefix = "baseline_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def epcg_simd_deciles_lineplot(*args):
    directories = ("EBSS," * 11)[:-1]  # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = "who_alive,who_first_simd_decile,who_second_simd_decile,who_third_simd_decile,who_fourth_simd_decile,who_fifth_simd_decile,who_sixth_simd_decile,who_seventh_simd_decile,who_eighth_simd_decile,who_ninth_simd_decile,who_tenth_simd_decile"
    prefix = "ebss_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def quintiles_lineplot(config_mode, source, region):
    directories = (f"{source}," * 6)[:-1]  # repeat 6 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth"
    subset_function_strings = "who_alive,who_first_simd_quintile,who_second_simd_quintile,who_third_simd_quintile,who_fourth_simd_quintile,who_fifth_simd_quintile"
    prefix = f"{source}_{region}_simd_quintiles_"
    ref = "National Average"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)


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
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def relative_poverty(config_mode, boost_amount):
    "nationwide policy"
    directories = f"baseline,{boost_amount}RelativePoverty"
    tags = f"Baseline,£{boost_amount} Relative Poverty"
    subset_function_strings = "who_relative_poverty_and_kids,who_boosted"
    prefix = f"{boost_amount}_relative_poverty"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

def universal_credit(config_mode, boost_amount, region=None):
    "nationwide policy"
    directories = f"baseline,{boost_amount}UniversalCredit"
    tags = f"Baseline,£{boost_amount} Universal Credit"
    subset_function_strings = "who_universal_credit_and_kids,who_boosted"
    prefix = f"{boost_amount}_{region}_universal_credit"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)


def universal_credit_single_priority_group(config_mode, source, tag, subset, region=None):
    "just the single mothers"
    directories = f"baseline,{source}"
    tags = f"Baseline,{tag}"
    subset_function_strings = f"{subset},{subset}"
    prefix = f"{source}_{subset}_single_mothers_universal_credit"
    directories = f"baseline,{source}"
    tags = f"Baseline,{tag}"
    subset_function_strings = f"{subset},{subset}"
    prefix = f"{source}_{subset}_priority_"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)


def universal_credit_priority_subgroups(config_mode, boost_amount, region):
    "any subgroup at all"
    directories = f"baseline,{boost_amount}UniversalCredit"
    tags = f"Baseline,£{boost_amount} Universal Credit"
    subset_function_strings = "who_priority_subgroups_and_kids,who_priority_subgroups_and_kids"
    prefix = f"{boost_amount}_any_subgroup_universal_credit"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v,
                  method=method, region=region)


def universal_credit_multiple_priority_subgroups(config_mode, boost_amount, region):
    "2+ subgroups"
    directories = f"baseline,{boost_amount}UniversalCredit"
    tags = f"Baseline,£{boost_amount} Universal Credit"
    subset_function_strings = "who_multiple_priority_subgroups_and_kids,who_multiple_priority_subgroups_and_kids"
    prefix = f"{boost_amount}_many_subgroups_universal_credit"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v,
                  method=method, region=region)


def priority_only(config_mode, boost_amount):
    "universal credit (the actual intervention) only lineplot"
    directories = f"baseline,{boost_amount}Priority"
    tags = f"Baseline,£{boost_amount} Priority Groups"
    subset_function_strings = "who_vulnerable_subgroups,who_boosted"
    prefix = f"{boost_amount}_priority"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def UC_priority(config_mode, boost_amount):
    "UC and priority interventions on one lineplot."
    directories = f"baseline,{boost_amount}UniversalCredit,{boost_amount}Priority"
    tags = f"Baseline,£{boost_amount} Universal Credit,£{boost_amount} Priority Groups"
    subset_function_strings = "who_universal_credit_and_kids,who_boosted,who_boosted"
    prefix = f"{boost_amount}_UC_and_priority"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

def UC_relative_poverty(config_mode, boost_amount):
    "UC and priority interventions on one lineplot."
    directories = f"baseline,{boost_amount}UniversalCredit,{boost_amount}RelativePoverty"
    tags = f"Baseline,£{boost_amount} Universal Credit,£{boost_amount} All in Relative Poverty"
    subset_function_strings = "who_universal_credit_and_kids,who_boosted,who_boosted"
    prefix = f"{boost_amount}_UC_and_relative_poverty"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)



def incremental_25_to_100(config_mode, intervention_name, intervention_tag, subset_function):
    "The same intervention in increments from £25 to £100"
    directories = f"baseline,25{intervention_name},50{intervention_name},75{intervention_name},100{intervention_name}"
    tags = f"Baseline,£25 {intervention_tag},£50 {intervention_tag},£75 {intervention_tag},£100 {intervention_tag}"
    subset_function_strings = f"{subset_function},who_boosted,who_boosted,who_boosted,who_boosted"
    prefix = f"25_100_incremental_{intervention_name}_uplift"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def incremental_25_to_50(config_mode, intervention_name, intervention_tag, subset_function):
    "The same intervention in increments from £25 to £50"
    directories = f"baseline,25{intervention_name},50{intervention_name}"
    tags = f"Baseline,£25 {intervention_tag},£50 {intervention_tag}"
    subset_function_strings = f"{subset_function},who_boosted,who_boosted"
    prefix = f"25_50_incremental_{intervention_name}_uplift"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)
    method = 'SF12_AUC'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)


def incremental_25_to_50_by_5(config_mode, intervention_name, intervention_tag, subset_function, increment, region):
    uplift_amount = 25
    for _ in range(6):
        "The same intervention in increments from £25 to £50"
        directories = f"baseline,{uplift_amount}{intervention_name}"
        tags = f"Baseline,£{uplift_amount} {intervention_tag}"
        subset_function_strings = f"{subset_function},who_boosted,who_boosted"
        prefix = f"{uplift_amount}_{intervention_name}_uplift"
        ref = "Baseline"
        v = "SF_12"
        method = 'nanmean'
        lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)
        uplift_amount += increment

def incremental_25_to_50_by_5_together(config_mode, intervention_name, intervention_tag, subset_function, region):
        "The same intervention in increments from £25 to £50"
        directories = "baseline"
        tags = "Baseline"
        uplift_amount = 25
        for _ in range(6):
            directories += f",{uplift_amount}{intervention_name}"
            tags += f",£{uplift_amount} {intervention_tag}"
            uplift_amount += 5
        subset_function_strings = f"{subset_function}" + (f",{subset_function}" * 6)
        prefix = f"25_50_by_5_together{intervention_name}_uplift"
        ref = "Baseline"
        v = "SF_12"
        method = 'nanmean'
        lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)

def incremental_25_50(config_mode, source, tag, subset_function, region):
    "The same intervention in increments from £25 to £50"
    directories = f"baseline,25{source},50{source}"
    tags = f"Baseline,£25 {tag},£50 {tag}"
    subset_function_strings = f"{subset_function},who_boosted,who_boosted"
    prefix = f"25_50_{source}_{region}_uplift"
    ref = "Baseline"
    v = "SF_12"
    method = 'weighted_nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix,
                  mode=config_mode, ref=ref, v=v, method=method, region=region)



def single_treatment_on_treated(config_mode, source, tag, subset, region=None):
    "just the single mothers"
    directories = f"baseline,{source}"
    tags = f"Baseline,{tag}"
    subset_function_strings = f"{subset},who_boosted"
    prefix = f"{source}_treated_{subset}_SF_12_aggs_by_year"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)


def single_priority_group(config_mode, source, tag, subset, region=None):
    "just the single mothers"
    directories = f"baseline,{source}"
    tags = f"Baseline,{tag}"
    subset_function_strings = f"{subset},{subset}"
    prefix = f"{source}_priority_{subset}_SF_12_aggs_by_year"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)

def single_priority_groups_together(config_mode, source, region=None):
    "just the single mothers"
    directories = f"baseline,{source}"
    tags = f"Baseline,Ethnic Minority Subgroup,Young Parents Subgroup,Single Mothers Subgroup,Low Education Subgroup,Young Parents Subgroup"
    subset_function_strings = f"who_kids,who_kids"
    prefix = f"{source}_priority_groups_together_SF_12_aggs_by_year"
    ref = "Baseline"
    v = "SF_12"
    method = 'split_priority_groups_weighted_nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method, region=region)


def any_priority_subgroups(config_mode, source, tag, region):
    "any subgroup at all"
    "just the single mothers"
    directories = f"baseline,{source}"
    tags = f"Baseline,{tag}"
    subset_function_strings = "who_priority_subgroups_and_kids,who_priority_subgroups_and_kids"
    prefix = f"{source}_any_subgroup_"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v,
                  method=method, region=region)

def multiple_priority_subgroups(config_mode, source, tag, region):
    "2+ subgroups"
    directories = f"baseline,{source}"
    tags = f"Baseline,{tag}"
    subset_function_strings = "who_multiple_priority_subgroups_and_kids,who_multiple_priority_subgroups_and_kids"
    prefix = f"{source}_many_subgroups_universal_credit_"
    ref = "Baseline"
    v = "SF_12"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v,
                  method=method, region=region)


def income_boost_mean(config_mode, source, tag, subset, region):
    "get mean income boost amount over time for some subet of the population"
    directories = source
    tags = tag
    subset_function_strings = subset
    prefix = f"{source}_{subset}_mean_household_income_boost_"
    ref = "Baseline"
    v = "boost_amount"
    method = 'nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v,
                  method=method, region=region)

def percentage_households_boosted(config_mode, source, tag, subset, region):
    "get mean income boost amount over time for some subet of the population"
    directories = source
    tags = tag
    subset_function_strings = subset
    prefix = f"{source}_{subset}_percentage_households_boosted_"
    ref = "Baseline"
    v = "income_boosted"
    method = 'percentages'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v,
                  method=method, region=region)



#################
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

    # incremental boost amounts for UC and Priority populations
    "25_UC_priority": UC_priority,
    "50_UC_priority": UC_priority,
    "75_UC_priority": UC_priority,
    "100_UC_priority": UC_priority,

    "25_all": all_child,
    "50_all": all_child,
    "75_all": all_child,
    "100_all": all_child,

    "25_relative_poverty_": relative_poverty,
    "50_relative_poverty": relative_poverty,
    "75_relative_poverty": relative_poverty,
    "100_relative_poverty": relative_poverty,

    "25_universal_credit": universal_credit,
    "30_universal_credit": universal_credit,
    "35_universal_credit": universal_credit,
    "40_universal_credit": universal_credit,
    "45_universal_credit": universal_credit,
    "50_universal_credit": universal_credit,
    "75_universal_credit": universal_credit,
    "100_universal_credit": universal_credit,


    # in any priority subgroup
    "25_universal_credit_priority_subgroups": universal_credit_priority_subgroups,
    "30_universal_credit_priority_subgroups": universal_credit_priority_subgroups,
    "35_universal_credit_priority_subgroups": universal_credit_priority_subgroups,
    "40_universal_credit_priority_subgroups": universal_credit_priority_subgroups,
    "45_universal_credit_priority_subgroups": universal_credit_priority_subgroups,
    "50_universal_credit_priority_subgroups": universal_credit_priority_subgroups,
    "75_universal_credit_priority_subgroups": universal_credit_priority_subgroups,
    "100_universal_credit_priority_subgroups": universal_credit_priority_subgroups,

    # in more than one subgroup.
    "25_universal_credit_multiple_priority_subgroups": universal_credit_multiple_priority_subgroups,
    "30_universal_credit_multiple_priority_subgroups": universal_credit_multiple_priority_subgroups,
    "35_universal_credit_multiple_priority_subgroups": universal_credit_multiple_priority_subgroups,
    "40_universal_credit_multiple_priority_subgroups": universal_credit_multiple_priority_subgroups,
    "45_universal_credit_multiple_priority_subgroups": universal_credit_multiple_priority_subgroups,
    "50_universal_credit_multiple_priority_subgroups": universal_credit_multiple_priority_subgroups,
    "75_universal_credit_multiple_priority_subgroups": universal_credit_multiple_priority_subgroups,
    "100_universal_credit_multiple_priority_subgroups": universal_credit_multiple_priority_subgroups,

    "incremental_universal_credit": incremental_25_to_100,
    "incremental_priority_groups": incremental_25_to_100,
    "incremental_25_50_relative_poverty": incremental_25_to_50,

    "25_50_universal_credit": incremental_25_50,
    "incremental_25_50_by_5_universal_credit": incremental_25_to_50_by_5,
    "incremental_25_50_by_5_together_universal_credit": incremental_25_to_50_by_5_together,
    "scotland_25_UC_priority_subgroups_together": single_priority_groups_together,
    "scotland_50_UC_priority_subgroups_together": single_priority_groups_together,

    # sustain intervention 25-50 increments
    "25_50_sustain": incremental_25_50,
    "incremental_25_50_by_5_sustain": incremental_25_to_50_by_5,
    "incremental_25_50_by_5_together_sustain": incremental_25_to_50_by_5_together,


    "social_science_all_plots": social_science_all_plots,

    "glasgow_baseline_quintile": quintiles_lineplot,
    "glasgow_relative_poverty_quintile": quintiles_lineplot,
    "glasgow_universal_credit_quintile": quintiles_lineplot,
    "glasgow_epcg_quintile": quintiles_lineplot,
    "glasgow_living_wage_quintile": quintiles_lineplot,


    # priority subgroups
    "scotland_25_universal_credit_single_mothers": single_priority_group,
    "scotland_25_universal_credit_disabled": single_priority_group,
    "scotland_25_universal_credit_ethnic_minority": single_priority_group,
    "scotland_25_universal_credit_three_children": single_priority_group,
    "scotland_25_universal_credit_young_adult": single_priority_group,
    "scotland_25_universal_credit_uneducated": single_priority_group,
    "scotland_25_universal_credit_newborn": single_priority_group,
    "scotland_25_universal_any_priority_subgroup": universal_credit_priority_subgroups,
    "scotland_25_universal_many_priority_subgroups": universal_credit_multiple_priority_subgroups,


    "scotland_50_universal_any_priority_subgroup": universal_credit_priority_subgroups,


    # deciles
    "scotland_25_universal_credit_deciles": deciles_lineplot,
    "scotland_50_universal_credit_deciles": deciles_lineplot,

    # quintiles
    "scotland_baseline_quintiles": quintiles_lineplot,
    "scotland_25_universal_credit_quintiles": quintiles_lineplot,
    "scotland_30_universal_credit_quintiles": quintiles_lineplot,
    "scotland_35_universal_credit_quintiles": quintiles_lineplot,
    "scotland_40_universal_credit_quintiles": quintiles_lineplot,
    "scotland_45_universal_credit_quintiles": quintiles_lineplot,
    "scotland_50_universal_credit_quintiles": quintiles_lineplot,

    "glasgow_baseline_quintiles": quintiles_lineplot,
    "glasgow_25_universal_credit_quintiles": quintiles_lineplot,
    "glasgow_30_universal_credit_quintiles": quintiles_lineplot,
    "glasgow_35_universal_credit_quintiles": quintiles_lineplot,
    "glasgow_40_universal_credit_quintiles": quintiles_lineplot,
    "glasgow_45_universal_credit_quintiles": quintiles_lineplot,
    "glasgow_50_universal_credit_quintiles": quintiles_lineplot,

    "edinburgh_baseline_quintiles": quintiles_lineplot,
    "edinburgh_25_universal_credit_quintiles": quintiles_lineplot,
    "edinburgh_30_universal_credit_quintiles": quintiles_lineplot,
    "edinburgh_35_universal_credit_quintiles": quintiles_lineplot,
    "edinburgh_40_universal_credit_quintiles": quintiles_lineplot,
    "edinburgh_45_universal_credit_quintiles": quintiles_lineplot,
    "edinburgh_50_universal_credit_quintiles": quintiles_lineplot,

    # scripts for sustain intervention.
    "sustain_sf12_all": single_treatment_on_treated,
    "sustain_sf12_kids": single_treatment_on_treated,
    "sustain_sf12_rp_kids": single_treatment_on_treated,
    "sustain_single_mothers_sf12": single_priority_group,
    "sustain_any_priority_group_sf12": any_priority_subgroups,
    "sustain_multiple_priority_group_sf12": multiple_priority_subgroups,
    "sustain_quintiles_lineplot": quintiles_lineplot,

    # boost amount graphs
    "scotland_25_UC_boost_amount": income_boost_mean,
    "scotland_50_UC_boost_amount": income_boost_mean,
    "scotland_25_UC_any_priority_group_boost_amount": income_boost_mean,
    "scotland_sustain_boost_amount": income_boost_mean,

    # number households boosted graphs
    "scotland_25_UC_percentage_boosted": percentage_households_boosted,
    "scotland_50_UC_percentage_boosted": percentage_households_boosted,
    "scotland_25_UC_any_priority_group_percentage_boosted": percentage_households_boosted,
    "scotland_sustain_percentage_boosted": percentage_households_boosted,
}

string_to_lineplot_function_args = {

    # glasgow synthpop lineplots
    "glasgow_baseline_all_deciles": ["baseline", "who_kids"],
    "glasgow_poverty_all_deciles": ["25RelativePoverty", "who_below_poverty_line_and_kids"],
    "glasgow_universal_credit_all_deciles": ["25UniversalCredit", "who_universal_credit_and_kids"],
    "glasgow_priority_groups_all_deciles": ["25Priority", "who_priority_subgroups"],

    "25_UC_priority": [25],
    "50_UC_priority": [50],
    "75_UC_priority": [75],
    "100_UC_priority": [100],

    "25_all": [25],
    "50_all": [50],
    "75_all": [75],
    "100_all": [100],

    "25_universal_credit": [25, "scotland"],
    "30_universal_credit": [30],
    "35_universal_credit": [35],
    "40_universal_credit": [40],
    "45_universal_credit": [45],
    "50_universal_credit": [50],
    "75_universal_credit": [75],
    "100_universal_credit": [100],

    # priority subgroups
    "scotland_25_universal_credit_single_mothers": ["25UniversalCredit", "£25 UC Young Mothers", "who_young_mothers", "scotland"],
    "scotland_25_universal_credit_disabled": ["25UniversalCredit", "£25 UC Disabled Household Member", "who_disabled", "scotland"],
    "scotland_25_universal_credit_ethnic_minority": ["25UniversalCredit", "£25 UC Ethnic Minorities", "who_ethnic_minority", "scotland"],
    "scotland_25_universal_credit_three_children": ["25UniversalCredit", "£25 UC Three+ Children", "who_three_children", "scotland"],
    "scotland_25_universal_credit_young_adult": ["25UniversalCredit", "£25 UC Young Adult", "who_young_adults", "scotland"],
    "scotland_25_universal_credit_uneducated": ["25UniversalCredit", "£25 UC Uneducated", "who_no_formal_education", "scotland"],
    "scotland_25_universal_credit_newborn": ["25UniversalCredit", "£25 UC Has Newborn", "who_newborn", "scotland"],

    "scotland_25_universal_any_priority_subgroup": [25, "scotland"],
    "scotland_25_universal_many_priority_subgroups": [25, "scotland"],

    "scotland_50_universal_any_priority_subgroup": [50, "scotland"],


    # priority groups for £25 to £50 Increments Together.
    "scotland_50_universal_any_priority_subgroup": [50, "scotland"],
    "scotland_25_50_universal_any_priority_subgroup": [25, "scotland"],
    "scotland_25_50_by_5_universal_any_priority_subgroup": [25, "scotland"],

    "25_universal_credit_priority_subgroups": [25, "scotland"],
    "30_universal_credit_priority_subgroups": [30],
    "35_universal_credit_priority_subgroups": [35],
    "40_universal_credit_priority_subgroups": [40],
    "45_universal_credit_priority_subgroups": [45],
    "50_universal_credit_priority_subgroups": [50],
    "75_universal_credit_priority_subgroups": [75],
    "100_universal_credit_priority_subgroups": [100],

    "25_universal_credit_multiple_priority_subgroups": [25, "scotland"],
    "30_universal_credit_multiple_priority_subgroups": [30],
    "35_universal_credit_multiple_priority_subgroups": [35],
    "40_universal_credit_multiple_priority_subgroups": [40],
    "45_universal_credit_multiple_priority_subgroups": [45],
    "50_universal_credit_multiple_priority_subgroups": [50],
    "75_universal_credit_multiple_priority_subgroups": [75],
    "100_universal_credit_multiple_priority_subgroups": [100],

    "25_relative_poverty_": [25],
    "50_relative_poverty": [50],
    "75_relative_poverty": [75],
    "100_relative_poverty": [100],

    "incremental_universal_credit": ["UniversalCredit", "Universal Credit", "who_universal_credit_and_kids"],
    "incremental_priority_groups": ["Priority", "Priority Groups", "who_priority_subgroups"],
    "incremental_all_child": ["All", "Nationwide", "who_kids"],
    "incremental_relative_poverty": ["RelativePoverty", "Relative Poverty", "who_below_poverty_line_and_kids"],

    "incremental_25_50_relative_poverty": ["RelativePoverty", "Relative Poverty", "who_below_poverty_line_and_kids"],

    "25_50_universal_credit": ["UniversalCredit", " Universal Credit", "who_universal_credit_and_kids", "scotland"],
    "incremental_25_50_by_5_universal_credit": ["UniversalCredit", "UniversalCredit", "who_universal_credit_and_kids", 5, "scotland"],
    "incremental_25_50_by_5_together_universal_credit": ["UniversalCredit", "Universal Credit", "who_universal_credit_and_kids", "scotland"],
    "scotland_25_UC_priority_subgroups_together": ["25UniversalCredit", "scotland"],
    "scotland_50_UC_priority_subgroups_together": ["50UniversalCredit", "scotland"],

    # sustain intervention 25-50 increments
    "25_50_sustain": ["ChildPovertyReductionSUSTAIN", " Sustain Intervention", "who_universal_credit_and_kids", "scotland"],
    "incremental_25_50_by_5_sustain": ["ChildPovertyReductionSUSTAIN", "UniversalCredit", "who_universal_credit_and_kids", 5, "scotland"],
    "incremental_25_50_by_5_together_sustain": ["ChildPovertyReductionSUSTAIN", "Universal Credit", "who_universal_credit_and_kids", "scotland"],


    # glasgow quintiles.
    "glasgow_relative_poverty_quintile": ['25RelativePoverty'],
    "glasgow_universal_credit_quintile": ['25UniversalCredit'],
    "glasgow_epcg_quintile": ['EPCG'],
    "glasgow_living_wage_quintile": ['livingWageIntervention'],


    # deciles
    "scotland_25_universal_credit_deciles": ["25UniversalCredit",
                                             "£25 Universal Credit",
                                             "who_universal_credit_and_kids",
                                             "scotland"],
    "scotland_50_universal_credit_deciles": ["50UniversalCredit",
                                             "£50 Universal Credit",
                                             "who_universal_credit_and_kids",
                                             "scotland"],

    "scotland_baseline_quintiles": ['baseline', "scotland"],
    "scotland_25_universal_credit_quintiles": ['25UniversalCredit', "scotland"],
    "scotland_30_universal_credit_quintiles": ['30UniversalCredit', "scotland"],
    "scotland_35_universal_credit_quintiles": ['35UniversalCredit', "scotland"],
    "scotland_40_universal_credit_quintiles": ['40UniversalCredit', "scotland"],
    "scotland_45_universal_credit_quintiles": ['45UniversalCredit', "scotland"],
    "scotland_50_universal_credit_quintiles": ['50UniversalCredit', "scotland"],

    "glasgow_baseline_quintiles": ['baseline', "glasgow"],
    "glasgow_25_universal_credit_quintiles": ['25UniversalCredit', "glasgow"],
    "glasgow_30_universal_credit_quintiles": ['30UniversalCredit', "glasgow"],
    "glasgow_35_universal_credit_quintiles": ['35UniversalCredit', "glasgow"],
    "glasgow_40_universal_credit_quintiles": ['40UniversalCredit', "glasgow"],
    "glasgow_45_universal_credit_quintiles": ['45UniversalCredit', "glasgow"],
    "glasgow_50_universal_credit_quintiles": ['50UniversalCredit', "glasgow"],

    "edinburgh_baseline_quintiles": ['baseline', "edinburgh"],
    "edinburgh_25_universal_credit_quintiles": ['25UniversalCredit', "edinburgh"],
    "edinburgh_30_universal_credit_quintiles": ['30UniversalCredit', "edinburgh"],
    "edinburgh_35_universal_credit_quintiles": ['35UniversalCredit', "edinburgh"],
    "edinburgh_40_universal_credit_quintiles": ['40UniversalCredit', "edinburgh"],
    "edinburgh_45_universal_credit_quintiles": ['45UniversalCredit', "edinburgh"],
    "edinburgh_50_universal_credit_quintiles": ['50UniversalCredit', "edinburgh"],

    # scripts for sustain intervention.
    "sustain_sf12_all": ["ChildPovertyReductionSUSTAIN", "All Households", "who_alive", "scotland"],
    "sustain_sf12_kids": ["ChildPovertyReductionSUSTAIN", "Households With Children", "who_kids", "scotland"],
    "sustain_sf12_rp_kids": ["ChildPovertyReductionSUSTAIN", "Households In Relative Poverty With Children", "who_below_poverty_line_and_kids", "scotland"],

    "sustain_sf12_below_poverty_line_kids": single_treatment_on_treated,
    "sustain_single_mothers_sf12": ["ChildPovertyReductionSUSTAIN", "10% Relative Poverty Target", "scotland"],
    "sustain_any_priority_group_sf12": ["ChildPovertyReductionSUSTAIN", "10% Relative Poverty Target", "scotland"],
    "sustain_multiple_priority_group_sf12": ["ChildPovertyReductionSUSTAIN", "10% Relative Poverty Target", "scotland"],

    "sustain_quintiles": ["ChildPovertyReductionSUSTAIN", "scotland"], #TODO use better version of plot for quintiles instead of deciles.


    # boost amount graphs
    "scotland_25_UC_boost_amount": ["25UniversalCredit", "£25 Universal Credit", "who_boosted", "scotland"],
    "scotland_50_UC_boost_amount":  ["50UniversalCredit", "£50 Universal Credit", "who_boosted", "scotland"],
    "scotland_25_UC_any_priority_group_boost_amount":  ["25UniversalCredit", "£25 UC Priority Groups", "who_priority_subgroups_and_kids", "scotland"],
    "scotland_sustain_boost_amount":  ["ChildPovertyReductionSUSTAIN", "10% Sustain Intervention", "who_boosted", "scotland"],

    # number households boosted graphs
    "scotland_25_UC_percentage_boosted": ["25UniversalCredit", "£25 Universal Credit", "who_kids", "scotland"],
    "scotland_50_UC_percentage_boosted":  ["50UniversalCredit", "£50 Universal Credit", "who_kids", "scotland"],
    "scotland_25_UC_any_priority_group_percentage_boosted":  ["25UniversalCredit", "£25 UC Priority Groups", "who_kids", "scotland"],
    "scotland_sustain_percentage_boosted":  ["ChildPovertyReductionSUSTAIN", "10% Sustain Intervention", "who_kids", "scotland"],
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
