library(here)
library(tidyverse)
library(data.table)
require(parallelly)
require(future)
require(future.apply)

# Suppress summarise info
options(dplyr.summarise.inform = FALSE)

###################### HELPER FUNCTIONS  ######################

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

# extract run_id from filepath string, so it can be attached to each output file
extract_run_id <- function(filepath) {
  # Extracts the run_id using a regular expression
  run_id <- gsub(".*/(\\d+)_run_id_\\d+\\.csv$", "\\1", filepath)
  return(run_id)
}

# remove any dead people from each run
drop_dead <- function(data) {
  data <- data %>%
    filter(alive != 'dead') %>%
    select(-alive)
  return(data)
}

drop_zero_weight <- function(data) {
  # Drop zero weight or missing weight individuals
  data <- data %>%
    filter(weight != 0) %>%
    filter(weight > 0)
  return(data)
}

drop_unnecessary_cols <- function(data, scen, year) {
  # Only keep specific columns to reduce memory requirements
  
  # cols we always need
  keep.cols <- c('pidp', 'hidp', 'time', 'alive', 'weight', 'sex', 'age', 'ethnicity', 
                 'child_ages', 'S7_labour_state', 'hh_income', 'SF_12', 'nkids',
                 'nkids_ind', 'init_relative_poverty', 'init_absolute_poverty', 
                 'universal_credit', 'income_quintile')
  
  # cols only needed in intervention summaries
  int.cols <- c('boost_amount', 'income_boosted')
  
  # if not baseline, we need intervention cols
  if (stringr::str_detect(scen, 'baseline', negate = TRUE)) {
    if (year != 2020) {
      keep.cols <- c(keep.cols, int.cols)
    }
  }
  
  # , 'simd_quintile'
  
  data <- data %>%
    select(all_of(keep.cols))
  
  # if baseline, create intervention cols
  if (stringr::str_detect(scen, 'baseline') | year == 2020) {
    data$income_boosted <- 'FALSE'
    data$boost_amount <- 0.0
  }
  
  return(data)
}

select_keep_cols <- function(scen, year) {
  # Only keep specific columns to reduce memory requirements
  
  # cols we always need
  keep.cols <- c('pidp', 'hidp', 'time', 'alive', 'weight', 'sex', 'age', 'ethnicity', 
                 'child_ages', 'S7_labour_state', 'hh_income', 'SF_12', 'nkids',
                 'nkids_ind', 'init_relative_poverty', 'init_absolute_poverty', 
                 'universal_credit', 'income_quintile')
  
  # cols only needed in intervention summaries
  int.cols <- c('boost_amount', 'income_boosted')
  
  # if not baseline, we need intervention cols
  if (stringr::str_detect(scen, 'baseline', negate = TRUE)) {
    if (year != 2020) {
      keep.cols <- c(keep.cols, int.cols)
    }
  }
  
  # , 'simd_quintile'
  
  data <- data %>%
    select(all_of(keep.cols))
  
  # if baseline, create intervention cols
  if (stringr::str_detect(scen, 'baseline') | year == 2020) {
    data$income_boosted <- 'FALSE'
    data$boost_amount <- 0.0
  }
  
  return(data)
}

create.if.not.exists <- function(path) {
  if(!file.exists(path)) {
    dir.create(path = path)
  }
}

add_scenario <- function(data, scenario) {
  data$scenario <- scenario
  return(data)
}


###################### READ FUNCTIONS  ######################

# Step 1: Load Data for One Year
load_data_for_year <- function(scen.path, year, scen) {
  
  # Create file strings using year from args
  file_pattern <- sprintf("*_run_id_%d.csv", year)
  file_list <- list.files(path = scen.path,
                          pattern = file_pattern,
                          full.names = TRUE)
  
  # no_cores <- availableCores(omit=1)
  # plan(multisession, workers = no_cores)  # Set up parallel plan
  
  # Use future_lapply with file_paths and fread
  #data_list <- future_lapply(file_list, fread, stringsAsFactors = TRUE)
  
  #data_list <- lapply(file_list, read.csv)
  data_list <- lapply(file_list, fread)
  data_list <- lapply(data_list, as.data.frame)
  
  # Keep only certain columns (check function above for list)
  data_list <- lapply(data_list, drop_unnecessary_cols, scen, year)
  
  # Now drop dead and zero weight
  data_list <- lapply(data_list, drop_dead)
  data_list <- lapply(data_list, drop_zero_weight)
  
  # Add run_id to each dataframe
  for (i in seq_along(data_list)) {
    run_id <- extract_run_id(file_list[i])
    data_list[[i]]$run_id <- as.numeric(str_remove(run_id, "^0+"))
  }
  
  return(data_list)
}

# Step 2: Generate Summary CSVs
generate_summary_csv <- function(combined_list, year, summary_funcs, save.path) {
  for (summary_name in names(summary_funcs)) {
    summary_func <- summary_funcs[[summary_name]]
    summary_filename <- sprintf("%s/summary_%s_%d.csv", save.path, summary_name, year)
    summary_data <- lapply(combined_list, summary_func)
    #rm(data_list)
    combined_summary <- do.call(rbind, summary_data)
    rm(summary_data)
    write.csv(combined_summary, file = summary_filename, row.names = FALSE)
    rm(combined_summary)
  }
}

# Step 3: Combine Summaries Across Years
combine_summaries_across_years <- function(summary_funcs, save.path1, save.path2) {
  for (summary_name in names(summary_funcs)) {
    print(sprintf('About to combine summaries for %s', summary_name))
    combined_summary <- NULL
    for (year in start.year:end.year) {
      summary_filename <- sprintf("%s/summary_%s_%d.csv", save.path2, summary_name, year)
      year_summary <- read.csv(summary_filename)
      year_summary$year <- year
      combined_summary <- rbind(combined_summary, year_summary)
    }
    combined_summary_filename <- sprintf("%s/combined_summary_%s.csv", save.path1, summary_name)
    write.csv(combined_summary, file = combined_summary_filename, row.names = FALSE)
  }
}

###################### SUMMARY FUNCTIONS ####################

treated_summary <- function(data) {
  boosted.pidps <- data %>%
    filter(scenario == 'intervention') %>%
    filter(income_boosted == 'TRUE') %>%
    select(pidp)
  
  output <- data %>%
    inner_join(boosted.pidps, by = 'pidp') %>%
    group_by(run_id, scenario) %>%
    summarise(count = n(),
              hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
              SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
              total_cost = sum(boost_amount),
              mean_cost = mean(boost_amount))
  
  return(output)
}


###################### RUN THIS STUFF! ######################

args <- commandArgs(trailingOnly=TRUE)
#args <- list('default_batch', 'cpr_summary_out_test', 'ChildPovertyReductionRELATIVE_2', 2020)

# constants
# start.year <- 2020
# end.year <- 2035

out.path <- here::here('output', args[1])
#out.path <- '/home/luke/Documents/WORK/MINOS/Minos/output/default_config/'
save.path.base <- here::here(out.path, args[2])
save.path1 <- here::here(save.path.base, args[3])
save.path2 <- here::here(save.path1, 'intermediates')
scen <- args[[3]]
year <- as.numeric(args[[4]])



create.if.not.exists(save.path.base)
create.if.not.exists(save.path1)
create.if.not.exists(save.path2)

# Set paths for baseline and intervention scenario

base.path <- here::here(out.path, 'baseline')
base.path <- get_latest_runtime_subdirectory(base.path)
scen.path <- here::here(out.path, scen)
scen.path <- get_latest_runtime_subdirectory(scen.path)


# Create named list of summary functions to go through
summary_funcs <- c(treated = treated_summary)


# Load the datafiles for each of baseline and intervention for a single year
print(sprintf('Starting for year %s', year))
base_list <- load_data_for_year(base.path, year, 'baseline')
scen_list <- load_data_for_year(scen.path, year, scen)
print(sprintf('Finished for year %s', year))

# add a scenario column for downstream processing
base_list <- lapply(base_list, add_scenario, 'baseline')
scen_list <- lapply(scen_list, add_scenario, 'intervention')

# combine the lists such that baseline run_id 1 and intervention run_id 1 are 
# row bound into a single dataframe, resulting in a single list
combined_list <- mapply(function(base_df, int_df) {
  combined <- rbind(base_df, int_df)
  return(combined)
}, base_list, scen_list, SIMPLIFY = FALSE)
rm(base_list, scen_list)

# generate the summary csv using the list of summary funcs created above
generate_summary_csv(combined_list, year, summary_funcs, save.path2)
