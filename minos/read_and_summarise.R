########### TESTING NEW DATA IN SUMMARISE FUNCTIONS ######################

require(here)
require(tidyverse)
require(data.table)
require(parallelly)
require(future)
require(future.apply)

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

###################### SUMMARISE FUNCTIONS  ######################

whole_pop_summarise <- function(data) {
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

###################### PRIORITY SUBGROUPS ######################

priority_summarise_ethnicity <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(ethnicity != 'WBI') %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(ethnicity != 'WBI') %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_summarise_child_under_one <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(substr(child_ages, 1, 1) == 0) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(substr(child_ages, 1, 1) == 0) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_summarise_three_plus_children <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter(nkids >= 3) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(nkids >= 3) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_summarise_mother_under_25 <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      filter((age < 25) & (nkids_ind > 0)) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      filter(nkids >= 3) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

priority_summarise_disabled <- function(data) {
  if ('boost_amount' %in% names(data)) {
    data <- data %>%
      group_by(hidp, run_id) %>%
      mutate(disabled_flag = ifelse(any(S7_labour_state) == 'disabled', TRUE, FALSE)) %>%
      filter(disabled_flag == TRUE) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE),
                total_cost = sum(boost_amount),
                mean_cost = mean(boost_amount))
    #TODO: Add number households affected by interventions and other stats
  } else {
    data <- data %>%
      group_by(hidp, run_id) %>%
      mutate(disabled_flag = ifelse(any(S7_labour_state) == 'disabled', TRUE, FALSE)) %>%
      filter(disabled_flag == TRUE) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight, na.rm=TRUE),
                SF_12 = weighted.mean(SF_12, w=weight, na.rm=TRUE)) %>%
      mutate(total_cost = 0,
             mean_cost = 0)
  }
  return(data)
}

###################### READ FUNCTIONS  ######################

parallel_read_summarise <- function(file_paths, drop.dead = TRUE) {
  #no_cores <- detectCores() - 1  # Reserve one core for the system
  no_cores <- availableCores(omit=1)
  plan(multisession, workers = no_cores)  # Set up parallel plan
  
  # Use future_lapply with file_paths and fread
  loaded.file.list <- future_lapply(file_paths, fread, stringsAsFactors = TRUE)
  
  # Optionally convert data.tables to data.frames
  loaded.file.list <- lapply(loaded.file.list, as.data.frame)
  
  if (drop.dead) {
    loaded.file.list <- lapply(loaded.file.list, drop_dead)
  }
  
  # Add run_id to each dataframe
  for (i in seq_along(loaded.file.list)) {
    run_id <- extract_run_id(file_paths[i])
    loaded.file.list[[i]]$run_id <- as.numeric(str_remove(run_id, "^0+"))
  }
  
  # Add SIMD quintiles alongside deciles
  #loaded.file.list <- lapply(loaded.file.list, simd_generate_quintiles)
  
  # Create list for summarised outputs and process each type of summary
  summary.out.list <- list(
    whole_pop = do.call(rbind, lapply(loaded.file.list, whole_pop_summarise)),
    families = do.call(rbind, lapply(loaded.file.list, families_summarise)),
    treated = do.call(rbind, lapply(loaded.file.list, treated_summarise)),
    # simd_decile = do.call(rbind, lapply(loaded.file.list, group_summarise, 'simd_decile')),
    # simd_quintile = do.call(rbind, lapply(loaded.file.list, group_summarise, 'simd_quintile')),
    sex = do.call(rbind, lapply(loaded.file.list, group_summarise, 'sex')),
    UC = do.call(rbind, lapply(loaded.file.list, group_summarise, 'universal_credit')),
    init_relative_poverty = do.call(rbind, lapply(loaded.file.list, group_summarise, 'init_relative_poverty')),
    init_absolute_poverty = do.call(rbind, lapply(loaded.file.list, group_summarise, 'init_absolute_poverty')),
    UC_rel_pov = do.call(rbind, lapply(loaded.file.list, UC_rel_pov_summarise)),
    UC_abs_pov = do.call(rbind, lapply(loaded.file.list, UC_abs_pov_summarise)),
    #UC_gender = do.call(rbind, lapply(loaded.file.list, UC_gender_summarise)),
    # priority_ethnicity = do.call(rbind, lapply(loaded.file.list, priority_summarise_ethnicity)),
    # priority_child_under_one = do.call(rbind, lapply(loaded.file.list, priority_summarise_child_under_one)),
    # priority_three_plus_children = do.call(rbind, lapply(loaded.file.list, priority_summarise_three_plus_children)),
    # priority_mother_under_25 = do.call(rbind, lapply(loaded.file.list, priority_summarise_mother_under_25))
    #priority_disabled = do.call(rbind, lapply(loaded.file.list, priority_summarise_disabled))
  )
  rm(loaded.file.list)
  
  return(summary.out.list)
}

read_and_sumarise_batch_1year <- function(out.path, scenario, year, drop.dead = TRUE, batch.size = 10) {
  scen.path <- here::here(out.path, scenario)
  scen.path <- get_latest_runtime_subdirectory(scen.path)
  
  # Create file strings using year from args
  target.pattern <- paste0('[0-9]*_run_id_', year, '.csv')
  filepath.list <- list.files(path = scen.path,
                              pattern = target.pattern,
                              full.names = TRUE)
  
  #print(paste0("Number of files to process in year ", year, ': ', length(filepath.list)))
  
  # Split filepath.list into batches
  batches <- split(filepath.list, ceiling(seq_along(filepath.list)/batch.size))
  
  output <- lapply(batches, parallel_read_summarise, drop.dead)
  
  # Extract and bind 'whole_pop' tibbles
  whole_pop_combined <- bind_rows(lapply(output, `[[`, "whole_pop"))
  whole_pop_combined$time <- year
  # Extract and bind 'families' tibbles
  families_combined <- bind_rows(lapply(output, `[[`, "families"))
  families_combined$time <- year
  # Extract and bind 'treated' tibbles
  treated_combined <- bind_rows(lapply(output, `[[`, "treated"))
  treated_combined$time <- year
  
  sex_combined <- bind_rows(lapply(output, `[[`, "sex"))
  sex_combined$time <- year
  
  UC_combined <- bind_rows(lapply(output, `[[`, "UC"))
  UC_combined$time <- year
  
  init_rel_pov_combined <- bind_rows(lapply(output, `[[`, "init_relative_poverty"))
  init_rel_pov_combined$time <- year
  
  init_abs_pov_combined <- bind_rows(lapply(output, `[[`, "init_absolute_poverty"))
  init_abs_pov_combined$time <- year
  
  UC_rel_pov_combined <- bind_rows(lapply(output, `[[`, "UC_rel_pov"))
  UC_rel_pov_combined$time <- year
  
  UC_abs_pov_combined <- bind_rows(lapply(output, `[[`, "UC_abs_pov"))
  UC_abs_pov_combined$time <- year
  
  #UC_gender_combined <- bind_rows(lapply(output, `[[`, "UC_gender"))
  #UC_gender_combined$time <- year
  
  # Extract and bind 'SIMD_decile' tibbles
  # treated_simd_decile <- bind_rows(lapply(output, `[[`, "simd_decile"))
  # treated_simd_decile$time <- year
  # # Extract and bind 'SIMD_quintile' tibbles
  # treated_simd_quintile <- bind_rows(lapply(output, `[[`, "simd_quintile"))
  # treated_simd_quintile$time <- year
  # # Extract and bind 'priority_ethnicity' tibbles
  # treated_priority_ethnicity <- bind_rows(lapply(output, `[[`, "priority_ethnicity"))
  # treated_priority_ethnicity$time <- year
  # # Extract and bind 'priority_child_under_one' tibbles
  # treated_priority_child_under_one <- bind_rows(lapply(output, `[[`, "priority_child_under_one"))
  # treated_priority_child_under_one$time <- year
  # # Extract and bind 'priority_three_plus_children' tibbles
  # treated_priority_three_plus_children <- bind_rows(lapply(output, `[[`, "priority_three_plus_children"))
  # treated_priority_three_plus_children$time <- year
  # # Extract and bind 'priority_mother_under_25' tibbles
  # treated_mother_under_25 <- bind_rows(lapply(output, `[[`, "priority_mother_under_25"))
  # treated_mother_under_25$time <- year
  
  combined_output <- list(whole_pop = whole_pop_combined,
                          families = families_combined,
                          treated = treated_combined,
                          sex = sex_combined,
                          UC = UC_combined,
                          init_relative_poverty = init_rel_pov_combined,
                          init_absolute_poverty = init_abs_pov_combined,
                          UC_rel_pov = UC_rel_pov_combined,
                          UC_abs_pov = UC_abs_pov_combined,
                          #UC_gender = UC_gender_combined
                          )
                          # simd_decile = treated_simd_decile,
                          # simd_quintile = treated_simd_quintile,
                          # priority_ethnicity = treated_priority_ethnicity,
                          # priority_child_under_one = treated_priority_child_under_one,
                          # priority_three_plus_children = treated_priority_three_plus_children,
                          # priority_mother_under_25 = treated_mother_under_25)
  
  return(combined_output)
}

read_batch_out_all_years_summarise <- function(out.path, scenario, save.path, start.year=2021, end.year=2036, verbose=TRUE, drop.dead = TRUE) {
  print(paste0("Starting aggregation of output files for ", scenario, '...'))
  
  all.years.list <- list()
  for (i in start.year:end.year) {
    if (verbose) { print(paste0("Aggregating files for year ", i)) }
    one.year.list <- read_and_sumarise_batch_1year(out.path, scenario, year=i, drop.dead)
    all.years.list[[i]] <- one.year.list
  }
  
  # Final step is to collapse all the individual year summary dfs to a combined df over all years
  # Then write to file
  # Extract and bind 'whole_pop' tibbles
  whole_pop_combined <- bind_rows(lapply(all.years.list, `[[`, "whole_pop"))
  whole_pop_combined$scenario <- scenario
  write.csv(x = whole_pop_combined,
            file = here::here(save.path, paste0(scenario, '_whole_pop_summary.csv')))
  # Extract and bind 'families' tibbles
  families_combined <- bind_rows(lapply(all.years.list, `[[`, "families"))
  families_combined$scenario <- scenario
  write.csv(x = families_combined,
            file = here::here(save.path, paste0(scenario, '_families_summary.csv')))
  # Extract and bind 'treated' tibbles
  treated_combined <- bind_rows(lapply(all.years.list, `[[`, "treated"))
  treated_combined$scenario <- scenario
  write.csv(x = treated_combined,
            file = here::here(save.path, paste0(scenario, '_treated_summary.csv')))
  
  sex_combined <- bind_rows(lapply(all.years.list, `[[`, "sex"))
  sex_combined$scenario <- scenario
  write.csv(x = sex_combined,
            file = here::here(save.path, paste0(scenario, '_sex_summary.csv')))
  
  UC_combined <- bind_rows(lapply(all.years.list, `[[`, "UC"))
  UC_combined$scenario <- scenario
  write.csv(x = UC_combined,
            file = here::here(save.path, paste0(scenario, '_UC_summary.csv')))
  
  init_rel_pov_combined <- bind_rows(lapply(all.years.list, `[[`, "init_relative_poverty"))
  init_rel_pov_combined$scenario <- scenario
  write.csv(x = init_rel_pov_combined,
            file = here::here(save.path, paste0(scenario, '_init_rel_pov_summary.csv')))
  
  init_abs_pov_combined <- bind_rows(lapply(all.years.list, `[[`, "init_absolute_poverty"))
  init_abs_pov_combined$scenario <- scenario
  write.csv(x = init_abs_pov_combined,
            file = here::here(save.path, paste0(scenario, '_init_abs_pov_summary.csv')))
  
  UC_rel_pov_combined <- bind_rows(lapply(all.years.list, `[[`, "UC_rel_pov"))
  UC_rel_pov_combined$scenario <- scenario
  write.csv(x = UC_rel_pov_combined,
            file = here::here(save.path, paste0(scenario, '_UC_rel_pov_summary.csv')))
  
  UC_abs_pov_combined <- bind_rows(lapply(all.years.list, `[[`, "UC_abs_pov"))
  UC_abs_pov_combined$scenario <- scenario
  write.csv(x = UC_abs_pov_combined,
            file = here::here(save.path, paste0(scenario, '_UC_abs_pov_summary.csv')))
  
  #UC_gender_combined <- bind_rows(lapply(all.years.list, `[[`, "UC_gender"))
  #UC_gender_combined$scenario <- scenario
  #write.csv(x = UC_gender_combined,
  #          file = here::here(save.path, paste0(scenario, '_UC_gender_summary.csv')))
  
  # # Extract and bind 'SIMD_decile' tibbles
  # simd_decile <- bind_rows(lapply(all.years.list, `[[`, "simd_decile"))
  # simd_decile$scenario <- scenario
  # write.csv(x = simd_decile,
  #           file = here::here(save.path, paste0(scenario, '_simd_decile_summary.csv')))
  # # Extract and bind 'SIMD_quintile' tibbles
  # simd_quintile <- bind_rows(lapply(all.years.list, `[[`, "simd_quintile"))
  # simd_quintile$scenario <- scenario
  # write.csv(x = simd_quintile,
  #           file = here::here(save.path, paste0(scenario, '_simd_quintile_summary.csv')))
  # # Extract and bind 'priority_ethnicity' tibbles
  # priority_ethnicity <- bind_rows(lapply(all.years.list, `[[`, "priority_ethnicity"))
  # priority_ethnicity$scenario <- scenario
  # write.csv(x = priority_ethnicity,
  #           file = here::here(save.path, paste0(scenario, '_priority_ethnicity_summary.csv')))
  # # Extract and bind 'priority_child_under_one' tibbles
  # priority_child_under_one <- bind_rows(lapply(all.years.list, `[[`, "priority_child_under_one"))
  # priority_child_under_one$scenario <- scenario
  # write.csv(x = priority_child_under_one,
  #           file = here::here(save.path, paste0(scenario, '_priority_child_under_one_summary.csv')))
  # # Extract and bind 'priority_three_plus_children' tibbles
  # priority_three_plus_children <- bind_rows(lapply(all.years.list, `[[`, "priority_three_plus_children"))
  # priority_three_plus_children$scenario <- scenario
  # write.csv(x = priority_three_plus_children,
  #           file = here::here(save.path, paste0(scenario, '_priority_three_plus_children_summary.csv')))
  # # Extract and bind 'priority_mother_under_25' tibbles
  # priority_mother_under_25 <- bind_rows(lapply(all.years.list, `[[`, "priority_mother_under_25"))
  # priority_mother_under_25$scenario <- scenario
  # write.csv(x = priority_mother_under_25,
  #           file = here::here(save.path, paste0(scenario, '_priority_mother_under_25_summary.csv')))
  
  print("All output files successfully aggregated and summarised.")
  print("Output csv files saved to: ")
}




################################# RUNNING SCRIPT #################################

args <- commandArgs(trailingOnly=TRUE)

out.path <- here::here('output', args[1])
save.path <- here::here(out.path, args[2])
scen <- args[3]

create.if.not.exists <- function(path) {
  if(!file.exists(path)) {
    dir.create(path = path)
  }
}
create.if.not.exists(save.path)




read_batch_out_all_years_summarise(out.path,
                                   scenario = scen,
                                   save.path = save.path,
                                   verbose = TRUE)

print(paste0('Output files for ', scen, ' successfully summarised.'))
