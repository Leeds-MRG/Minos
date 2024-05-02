
library(here)
library(tidyverse)
library(data.table)

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

create.if.not.exists <- function(path) {
  if(!file.exists(path)) {
    dir.create(path = path)
  }
}

###################### SUMMARISE FUNCTIONS  ######################

whole_pop_summarise <- function(data) {
  
  print(data$hh_income)
  print(data$SF_12)
  
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

families_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(nkids > 0) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(nkids > 0) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

treated_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    print(head(data))
    data <- data %>%
      filter(income_boosted == TRUE) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter((universal_credit == 1) & (nkids > 0)) %>%
      group_by(run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  
  write.csv(x = data,
            file = '/nobackup/medlarc/Minos/tmp/testing_treated.csv')
  
  return(data)
}

group_summarise <- function(data, group.var) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(.data[[group.var]], run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      group_by(.data[[group.var]], run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

simd_generate_quintiles <- function(data) {
  data[['simd_quintile']] <- round(data[['simd_decile']] / 2)
  return(data)
}

UC_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(universal_credit, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      group_by(universal_credit, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

UC_rel_pov_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(universal_credit, init_relative_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      group_by(universal_credit, init_relative_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

UC_abs_pov_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(universal_credit, init_absolute_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      group_by(universal_credit, init_absolute_poverty, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

UC_gender_summarise <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(universal_credit, sex, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      group_by(universal_credit, sex, run_id) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

###################### READ FUNCTIONS  ######################

# Step 1: Load Data for One Year
load_data_for_year <- function(scen.path, year) {
  
  # Create file strings using year from args
  file_pattern <- sprintf("*_run_id_%d.csv", year)
  file_list <- list.files(path = scen.path,
                          pattern = file_pattern,
                          full.names = TRUE)
  data_list <- lapply(file_list, read.csv)
  
  # Add run_id to each dataframe
  for (i in seq_along(data_list)) {
    run_id <- extract_run_id(file_list[i])
    data_list[[i]]$run_id <- as.numeric(str_remove(run_id, "^0+"))
  }
  
  return(data_list)
}

# Step 2: Summary Functions
calculate_summary_by_group <- function(data, group_var) {
  summary <- aggregate(. ~ group_var, data = data, FUN = sum)  # Example summary calculation
  return(summary)
}

# Step 3: Generate Summary CSVs
generate_summary_csv <- function(data_list, year, summary_funcs, save.path) {
  for (summary_name in names(summary_funcs)) {
    summary_func <- summary_funcs[[summary_name]]
    summary_filename <- sprintf("%s/summary_%s_%d.csv", save.path, summary_name, year)
    summary_data <- lapply(data_list, summary_func)
    combined_summary <- do.call(rbind, summary_data)
    write.csv(combined_summary, file = summary_filename, row.names = FALSE)
  }
}

# Step 4: Combine Summaries Across Years
combine_summaries_across_years <- function(summary_funcs, save.path1, save.path2) {
  for (summary_name in names(summary_funcs)) {
    print(sprintf('About to combine summaries for %s', summary_name))
    combined_summary <- NULL
    for (year in 2021:2036) {
      summary_filename <- sprintf("%s/summary_%s_%d.csv", save.path2, summary_name, year)
      year_summary <- read.csv(summary_filename)
      year_summary$year <- year
      combined_summary <- rbind(combined_summary, year_summary)
    }
    combined_summary_filename <- sprintf("%s/combined_summary_%s.csv", save.path1, summary_name)
    write.csv(combined_summary, file = combined_summary_filename, row.names = FALSE)
  }
}


###################### RUN THIS STUFF! ######################

args <- commandArgs(trailingOnly=TRUE)
#args <- list('default_config', 'scp_summary_out', 'baseline')

out.path <- here::here('output', args[1])
save.path1 <- here::here(out.path, args[2], args[3])
save.path2 <- here::here(save.path1, 'intermediates')
scen <- args[3]

create.if.not.exists(save.path1)
create.if.not.exists(save.path2)

scen.path <- here::here(out.path, scen)
scen.path <- get_latest_runtime_subdirectory(scen.path)

# Create named list of summary functions to go through
summary_funcs <- c(whole_pop = whole_pop_summarise,
                   families = families_summarise,
                   treated = treated_summarise,
                   UC = UC_summarise,
                   UC_rel_pov = UC_rel_pov_summarise,
                   UC_abs_pov = UC_abs_pov_summarise,
                   UC_gender = UC_gender_summarise)

# Step 5: Script Execution
for (year in 2021:2036) {
  print(sprintf('Starting for year %s', year))
  data_list <- load_data_for_year(scen.path, year)
  generate_summary_csv(data_list, year, summary_funcs, save.path2)
  print(sprintf('Finished for year %s', year))
}

# # Combine summaries across years for each type of summary
# for (summary_type in summary_funcs) {
#   combine_summaries_across_years(summary_type, save.path)
# }

combine_summaries_across_years(summary_funcs, save.path1, save.path2)
