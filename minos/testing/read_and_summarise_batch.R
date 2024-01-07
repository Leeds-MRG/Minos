## Read batch output and generate a summary output document over the 100 runs

require(tidyverse)
require(ggplot2)
require(knitr)
require(here)

# Function to find the latest runtime subdirectory (most recent)
# Reads all directories in a given path and returns the most recent subdir
# This requires all folders in the given path to be named with a specific
# format, which is a datetime from Year to Second. If any directories in the
# path are not in this format, the function will fail somewhow.
# Args:
#       path - path to a directory containing runtime subdirectories
get_latest_runtime_subdirectory <- function(path) {
  # first select only the path (not filenames)
  out.folders <- list.files(path)

  # if more than 1, take the most recent
  if(length(out.folders) == 1) {
    path = paste0(path, '/', out.folders[1], '/')
  }
  else if(length(out.folders) > 1) {
    out.folders.date <- as.POSIXlt(out.folders, format='%Y_%m_%d_%H_%M_%S')

    max.date <- max(out.folders.date)

    # Collecting these objects here as they have to be formatted
    yr <- max.date$year + 1900 # year is years since 1900
    month <- formatC(max.date$mon + 1, width=2, flag='0') # months are zero indexed (WHY??)
    day <- formatC(max.date$mday, width=2, flag='0')
    hour <- formatC(max.date$hour, width=2, flag='0')
    min <- formatC(max.date$min, width=2, flag='0')
    sec <- formatC(max.date$sec, width=2, flag='0')

    str.date <- paste0(yr, '_',
                       month, '_',
                       day, '_',
                       hour, '_',
                       min, '_',
                       sec)

    path <- paste0(path, '/', str.date, '/')
  }
  return(path)
}

# This function will read all files from a batch run of MINOS for a specific
# year, select only a list of variables we are interested in, and collapse
# them into a single dataframe with a `run_id` variable to denote individual
# runs.
# This function will likely use a LOT of memory, so we're going to remove
# objects wherever we can to avoid problems
# Args:
#       out.path - path to top level output directory
#       scenario - string scenario name of which output files to read
#       year - single year of batch output to aggregate
#       var.list - list of variables to keep in the returned dataframe
read_batch_out_1year <- function(out.path, scenario, year, var.list) {
  print(paste0('Reading batch files for year ', year))
  scen.path <- paste0(out.path, scenario)
  scen.path <- get_latest_runtime_subdirectory(scen.path)

  print(paste0('Path is: ', scen.path))

  # Create file strings using year from args
  target.pattern <- paste0('[0-9]*_run_id_', year, '.csv')
  filepath.list <- list.files(path = scen.path,
                              pattern = target.pattern,
                              full.names = TRUE)

  # generate sequence of run IDs from length of the filepath.list
  num.run.ids <- length(filepath.list)
  run.id.vector <- 1:num.run.ids

  print(paste0('Run ID ranges from ', min(run.id.vector), ' to ', max(run.id.vector)))

  # read each file in the list and store in a different list
  loaded.file.list <- lapply(filepath.list, read.csv)
  rm(filepath.list, num.run.ids)

  # subset with vars from var.list
  subsetted.file.list <- lapply(loaded.file.list, function(x) select(x, all_of(var.list)))
  rm(loaded.file.list)

  # add a run_id variable to each df in the list
  augmented.list <- Map(cbind, subsetted.file.list, run_id = run.id.vector)
  rm(subsetted.file.list, run.id.vector)

  # finally coalesce into a single df
  final <- do.call(rbind, augmented.list)
  rm(augmented.list)

  return(final)
}

read_batch_out_all_years <- function(out.path, scenario, start.year=2021, end.year=2036, var.list, verbose=FALSE) {
  print(paste0("Starting aggregation of output files for ", scenario, '...'))
  var.list <- c('pidp', 'hidp', 'time', 'weight', var.list, 'alive')
  large.df = data.frame()
  for (i in start.year:end.year) {
    if (verbose) { print(paste0("Aggregating files for year ", i)) }
    new.df <- read_batch_out_1year(out.path, scenario, year=i, var.list)
    new.df <- new.df %>%
      filter(alive != 'dead') %>%
      select(-alive)
    large.df <- rbind(large.df, new.df)
  }
  print("All output files successfully aggregated.")
  return(large.df)
}

# Function to identify variable types
# variable_type <- function(x) {
#   if (is.numeric(x) && !is.integer(x)) {
#     return("continuous")  # float values
#   } else if (is.numeric(x) && is.integer(x) && length(unique(x)) > 15) {
#     return("continuous")  # int but lots of unique values
#   } else if (is.numeric(x) && is.integer(x) && length(unique(x)) < 15) {
#     return("ordinal")
#   } else if (is.character(x)) {
#     return("nominal")
#   } else {
#     return("other")
#   }
# }

# Custom function to calculate mode for non-numeric variables
mode_function_ord <- function(x) {
  unique_x <- unique(x)
  freq_x <- table(x)
  mode_value <- unique_x[which.max(freq_x)]
  return(mode_value)
}

# Custom function to calculate mode for non-numeric variables
mode_function_nom <- function(x) {
  unique_x <- unique(x)
  freq_x <- table(x)
  mode_value <- unique_x[which.max(freq_x)]
  return(as.character(mode_value))
}


read_batch_out_summarise <- function(out.path, scenario, start.year=2021, end.year=2036, var.list, verbose=FALSE) {
  # First use other function to get batch output
  large_df <- read_batch_out_all_years(out.path, scenario, start.year, end.year, var.list, verbose)

  # converting nominal vars to ordinal
  large_df$S7_housing_quality <- as.numeric(factor(large_df$S7_housing_quality,
                                                   levels = c('No to all',
                                                              'Yes to some',
                                                              'Yes to all'),
                                                   labels = c(1, 2, 3)))

  large_df$S7_neighbourhood_safety <- as.numeric(factor(large_df$S7_neighbourhood_safety,
                                                        levels = c('Often',
                                                                   'Some of the time',
                                                                   'Hardly ever'),
                                                        labels = c(1, 2, 3)))

  large_df$loneliness <- as.numeric(factor(large_df$loneliness,
                                           levels = c(1, 2, 3),
                                           labels = c(3, 2, 1)))

  #return(large_df)

  print(unique(large_df$S7_housing_quality))
  print(unique(large_df$S7_neighbourhood_safety))
  print(unique(large_df$loneliness))

  print('LARGE_DF GENERATED...')

  #print(colnames(large_df))

  # Now identify columns and calculate summary values
  # Define a list of columns to group by
  group_cols <- c("pidp", "time")

  # Identify variable types
  #var_types <- sapply(large_df, variable_type)

  #print("VAR_TYPES:")
  #print(var_types)

  # # Separate variables by type
  # continuous_vars <- names(var_types[var_types == "continuous"])
  # ordinal_vars <- names(var_types[var_types == "ordinal"])
  # nominal_vars <- names(var_types[var_types == "nominal"])
  #
  # print(continuous_vars)
  # print(ordinal_vars)
  # print(nominal_vars)

  nominal_vars <- c('S7_labour_state')
  ordinal_vars <- c('S7_housing_quality', 'S7_neighbourhood_safety', 'S7_physical_health', 'S7_mental_health', 'loneliness', 'job_sec', 'education_state')
  continuous_vars <- c('hh_income', 'equivalent_income', 'weight', 'age', 'nkids_ind', 'hourly_wage')
  static_vars <- c('ethnicity', 'region', 'sex')

  #print(nominal_vars)

  print("ABOUT TO SUMMARISE")

  # # Do some type casting first just to be certain
  # large_df <- large_df %>%
  #   mutate(across(all_of(nominal_vars), as.factor),
  #          across(all_of(ordinal_vars), as.factor),
  #          across(all_of(continuous_vars), as.numeric))

  #return(large_df)

  #print("This should not be happening")

  # print(levels(large_df$S7_housing_quality))
  # print(levels(large_df$S7_labour_state))
  # print(levels(large_df$region))

  # Calculate mean for continuous variables and median for ordinal variables
  result_df <- large_df %>%
    group_by(across(all_of(group_cols))) %>%
    summarize(
      across(all_of(static_vars), first),
      across(all_of(continuous_vars), mean, na.rm = TRUE),
      across(all_of(ordinal_vars), ~ mode_function_ord(.x)),
      across(all_of(nominal_vars), ~ mode_function_nom(.x))
    )
  return(result_df)
}


# just do all scenarios for now cos we need them all

scenarios <- c('baseline', 'livingWageIntervention', 'energyDownlift', 'energyDownliftNoSupport', 'hhIncomeChildUplift', 'hhIncomePovertyLineChildUplift')

out.path <- 'output/SIPHER7/'

S7.var.list <- c('hh_income', 'equivalent_income',  # Income variables
                 'S7_housing_quality', 'S7_neighbourhood_safety', 'S7_physical_health', 'S7_mental_health', 'S7_labour_state', 'loneliness',  # SIPHER 7 variables
                 'ethnicity', 'age', 'sex', 'region', 'job_sec', 'education_state', 'nkids_ind', 'hourly_wage')


# dat <- read_batch_out_summarise(out.path, 'livingWageIntervention_Short', start.year = 2021, var.list = S7.var.list, verbose=TRUE)
# write.csv(dat, file = 'livingWageIntervention_summary.csv')


for (scen in scenarios) {
  print(paste0('Starting aggregation for ', scen))
  dat <- read_batch_out_summarise(out.path, scen, start.year = 2021, var.list = S7.var.list, verbose=FALSE)
  write.csv(dat, file = paste0('output/', scen, '_summary.csv'))
}
