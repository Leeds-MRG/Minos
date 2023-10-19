"""File containing shortcut functions used by makefiles"""

from minos.outcomes.make_lineplots import main as lineplot_main
import sys

"""
Macros for generating change in SF-12 MCS over time lineplots.

These functions are here to save space in the makefile definig all needed variables here
 and only calling these functions using one argument make commands. These functions will aggregate data from the 
 required intervention using specified aggregation methods, and plot them in a lineplot showing confidence over time.

Setting up these functions requires a few things

1) Create the intervention aggregation and lineplot function. This is essentially a list of arguments passed to the main aggregation functions
in make_lineplots.py. There are several arugments to consider
    
    directories : Which directories are data being pulled from. E.g. livingWageIntervention for living wage intervention 
        data. This is a string with commas seperating each individual file source. e.g.
        `baseline,livingWageIntervention`.
    tags : What are the names given to each intervention in the plot legend. E.g. tag `Living Wage Intervention` for 
    source livingWageIntervention will provide the correct name in the legend. Again this is a string of variables seperated
    by commas `Baseline,Living Wage Intervention`. 
    subset_function_strings: Which subset of the population is used to calculate aggregates. See aggregate_subset_functions.py.
        For example, who_below_living_wage_and_kids selects all households in a population with members under the living wage
        and with children. Used for average treatment effect analysis. If writing new interventions its likely a new subset 
        of the population is needed. Again a string of strings seperated by commas is used. 
        e.g. `who_alive,who_below_living_wage_and_kids`
    prefix : what name goes on the front of the new lineplot to make it unique and stop overwriting.
    config_mode : what MINOS configuration has been used to generate data. usually default_config or glasgow_scaled.
        Also helps to provide output directories.
    aggregation_variable : Which variable is being aggregated? Usually SF_12 but looking to expand to other quantities e.g.
        EI and discrete variables. 
    aggregate_method : what method is used to aggregate the aggregation_variable? For continous values this is usually the nanmean or weighted_nanmean.
    reference_population : if using relative scaling what is the reference population. For example, if using relative scaling
    for SF12 with baseline and living wage interventions. if we have an SF12 score of 50 for baseline and 50.5 for living wage,
    choosing the baseline as the reference population means the change in living wage SF-12 MCS will be recorded as
    (50.5-50)/50 = 1%. Likewise if the living wage population was the reference population change in SF-12 MCS for the baseline
    would be (50-50.5)/50.5 = 100/101 = -0.09901%


    Other aggregators are being tested such as percentage and cumulative counts. see make_lineplots.py
    
    The aggregation function must define all of these variables and provide a call to make_lineplots.main like so:
    
def living_wage_lineplot(*args):
    directories = "baseline,livingWageIntervention"
    tags = "Baseline,Living Wage Intervention"
    subset_function_strings = "who_below_living_wage_and_kids,who_boosted"
    prefix = "baseline_living_wage"
    config_mode = "default_config"
    aggregation_variable = "SF_12"
    aggregate_method = 'nanmean'
    reference_population = "Baseline"
    lineplot_main(directories=directories,
                  tags=tags,
                  subset_function_strings=subset_function_strings,
                  prefix=prefix,
                  mode=config_mode,
                  ref=reference_population,
                  aggregation_variable=aggregation_variable,
                  method=aggregate_method)
       

2) Add this new intervention function to the string_to_lineplot_function dict just above main. The key will be some name
given to the function e.g. `living_wage` and the value will be the corresponding aggregation function e.g. living_wage_lineplot().


3) Write a make command in outcomes/Makefile that calls this new aggregation function. For the living wage lineplot we have

living_wage_lineplot: MODE="default_config"
living_wage_lineplot:
	python3 minos/outcomes/make_lineplots_macros.py $(MODE) "living_wage"

"""


def all_child_lineplot(*args):
    # run using make all_child_lineplot
    directories = "baseline,hhIncomeChildUplift"
    tags = "Baseline,All Child Uplift"
    subset_function_strings = "who_kids,who_boosted"
    prefix = "baseline_all_child_uplift"
    config_mode = "default_config"
    aggregation_variable = "SF_12"
    aggregate_method = 'nanmean'
    reference_population = "Baseline"
    lineplot_main(directories=directories,
                  tags=tags,
                  subset_function_strings=subset_function_strings,
                  prefix=prefix,
                  mode=config_mode,
                  ref=reference_population,
                  aggregation_variable=aggregation_variable,
                  method=aggregate_method)


def poverty_line_child_lineplot(*args):
    # run using make poverty_line_child_lineplot

    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "Baseline,Poverty Line Child Uplift"
    subset_function_strings = "who_below_poverty_line_and_kids,who_boosted"
    prefix = "baseline_poverty_child_uplift"
    config_mode = "default_config"
    aggregation_variable = "SF_12"
    aggregate_method = 'nanmean'
    reference_population = "Baseline"
    lineplot_main(directories=directories,
                  tags=tags,
                  subset_function_strings=subset_function_strings,
                  prefix=prefix,
                  mode=config_mode,
                  ref="Baseline",
                  v=aggregation_variable,
                  method=aggregate_method)


def living_wage_lineplot(*args):
    # run using make living_wage_lineplot
    directories = "baseline,livingWageIntervention"
    tags = "Baseline,Living Wage Intervention"
    subset_function_strings = "who_below_living_wage,who_boosted"
    prefix = "baseline_living_wage"
    config_mode = "default_config"
    aggregation_variable = "SF_12"
    aggregate_method = 'weighted_nanmean'
    reference_population = "Baseline"
    lineplot_main(directories=directories,
                  tags=tags,
                  subset_function_strings=subset_function_strings,
                  prefix=prefix,
                  mode=config_mode,
                  ref=reference_population,
                  aggregation_variable=aggregation_variable,
                  method=aggregate_method)


def epcg_and_no_support_lineplot(*args):
    # run using make all_child_lineplot
    directories = "baseline,energyDownlift,energyDownliftNoSupport"
    tags = "Baseline,EPCG,No Support"
    subset_function_strings = "who_uses_energy,who_boosted,who_boosted"
    prefix = "baseline_energy_downlift"
    config_mode = "default_config"
    aggregation_variable = "SF_12"
    aggregate_method = 'nanmean'
    reference_population = "Baseline"
    lineplot_main(directories=directories,
                  tags=tags,
                  subset_function_strings=subset_function_strings,
                  prefix=prefix,
                  mode=config_mode,
                  ref=reference_population,
                  aggregation_variable=aggregation_variable,
                  method=aggregate_method)


#################
# main function #
#################


string_to_lineplot_function = {
    # initial line plots
    "all_child": all_child_lineplot,
    "poverty_line_child": poverty_line_child_lineplot,
    "living_wage": living_wage_lineplot,
    "epcg": epcg_and_no_support_lineplot
}

string_to_lineplot_function_args = {

}


def main():
    """Get the desired lineplot aggregate functions from the makefile command. plot this function."""
    config_mode = sys.argv[1]  # which config are data being plotted for? default_config by default.

    # which interventions are being plotted.
    # argument given from makefile and corresponds to dictionary of functions above.
    plot_choice = sys.argv[2]
    plot_function = string_to_lineplot_function[plot_choice]

    # get any args associated with the requested plot function from string_to_lineplot_function_args dict.
    if plot_choice in string_to_lineplot_function_args.keys():
        plot_function_args = string_to_lineplot_function_args[plot_choice]
    else:
        plot_function_args = []

    # use the plot function and its args to aggregate and create the lineplot.
    plot_function(config_mode, *plot_function_args)


if __name__ == '__main__':
    main()
