########### TESTING NEW DATA IN SUMMARISE FUNCTIONS ######################


require(tidyverse)
require(data.table)
require(parallelly)
require(future)
require(future.apply)



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

# parallel_read_summarise <- function(file_paths, drop.dead = TRUE) {
#   no_cores <- detectCores() - 1  # Reserve one core for the system
#   #print("Number available cores:")
#   #print(no_cores)
#   cl <- makeCluster(no_cores)
#   on.exit(stopCluster(cl))  # Ensure the cluster is stopped when the function exits
#   
#   # Use parLapply directly with file_paths and fread
#   #print('Reading files...')
#   loaded.file.list <- parLapply(cl, file_paths, fread, stringsAsFactors=TRUE)
#   
#   # Optionally convert data.tables to data.frames
#   loaded.file.list <- lapply(loaded.file.list, as.data.frame)
#   
#   if (drop.dead) {
#     loaded.file.list <- lapply(loaded.file.list, drop_dead)
#   }
#   
#   #print('Adding run_id column...')
#   # Add run_id to each dataframe
#   for (i in seq_along(loaded.file.list)) {
#     run_id <- extract_run_id(file_paths[i])
#     loaded.file.list[[i]]$run_id <- as.numeric(str_remove(run_id, "^0+"))
#   }
#   
#   
#   # create list for summarised outputs
#   summary.out.list <- list()
#   
#   # Whole pop SF12 summary stats
#   #print('Generating whole pop summary...')
#   whole.pop.summary <- lapply(loaded.file.list, whole_pop_summarise)
#   #whole.pop.summary <- do.call(rbind, do.call(rbind, whole.pop.summary))
#   whole.pop.summary <- do.call(rbind, whole.pop.summary)
#   #return(whole.pop.summary)
#   #summary.out.list <- list(summary.out.list, whole.pop.summary)
#   summary.out.list[['whole_pop']] <- whole.pop.summary
#   
#   #return(whole.pop.summary)
#   
#   #print('Households with children...')
#   families.summary <- lapply(loaded.file.list, families_summarise)
#   #summary.out.list <- list(summary.out.list, families.summary)
#   families.summary <- do.call(rbind, families.summary)
#   summary.out.list[['families']] <- families.summary
#   
#   #return(families.summary)
#   
#   #print('Treatement on Treated...')
#   treated.summary <- lapply(loaded.file.list, treated_summarise)
#   #summary.out.list <- list(summary.out.list, treated.summary)
#   treated.summary <- do.call(rbind, treated.summary)
#   summary.out.list[['treated']] <- treated.summary
#   
#   #return(treated.summary)
#   
#   #print('SIMD Deciles')
#   SIMD.summary <- lapply(loaded.file.list, group_summarise, 'simd_decile')
#   # summary.out.list <- list(summary.out.list, SIMD.summary)
#   SIMD.summary <- do.call(rbind, SIMD.summary)
#   summary.out.list[['simd_decile']] <- SIMD.summary
#   
#   #return(SIMD.summary)
#   rm(loaded.file.list)
#   
#   #print('Finished creating summary outputs')
#   return(summary.out.list)
#   
#   #return(loaded.file.list)
# }

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
  
  # Create list for summarised outputs and process each type of summary
  summary.out.list <- list(
    whole_pop = do.call(rbind, lapply(loaded.file.list, whole_pop_summarise)),
    families = do.call(rbind, lapply(loaded.file.list, families_summarise)),
    treated = do.call(rbind, lapply(loaded.file.list, treated_summarise)),
    simd_decile = do.call(rbind, lapply(loaded.file.list, group_summarise, 'simd_decile'))
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
  # Extract and bind 'SIMD_decile' tibbles
  treated_simd_decile <- bind_rows(lapply(output, `[[`, "simd_decile"))
  treated_simd_decile$time <- year
  
  combined_output <- list(whole_pop = whole_pop_combined,
                          families = families_combined,
                          treated = treated_combined,
                          simd_decile = treated_simd_decile)
  
  return(combined_output)
}


read_batch_out_all_years_summarise <- function(out.path, scenario, start.year=2020, end.year=2035, verbose=TRUE, drop.dead = TRUE) {
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
            file = here::here(out.path, 'summary_files', paste0(scenario, '_whole_pop_summary.csv')))
  # Extract and bind 'families' tibbles
  families_combined <- bind_rows(lapply(all.years.list, `[[`, "families"))
  families_combined$scenario <- scenario
  write.csv(x = families_combined,
            file = here::here(out.path, 'summary_files', paste0(scenario, '_families_summary.csv')))
  # Extract and bind 'treated' tibbles
  treated_combined <- bind_rows(lapply(all.years.list, `[[`, "treated"))
  treated_combined$scenario <- scenario
  write.csv(x = treated_combined,
            file = here::here(out.path, 'summary_files', paste0(scenario, '_treated_summary.csv')))
  # Extract and bind 'SIMD_deciles' tibbles
  simd_decile <- bind_rows(lapply(all.years.list, `[[`, "simd_decile"))
  simd_decile$scenario <- scenario
  write.csv(x = simd_decile,
            file = here::here(out.path, 'summary_files', paste0(scenario, '_simd_decile_summary.csv')))
  
  print("All output files successfully aggregated and summarised.")
  print("Output csv files saved to: ")
}





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


################################# RUNNING SCRIPT #################################

out.path <- here::here('output', 'scaled_scotland')
save.path <- here::here(out.path, 'summary_files')

create.if.not.exists <- function(path) {
  if(!file.exists(path)) {
    dir.create(path = path)
  }
}

create.if.not.exists(save.path)


read_batch_out_all_years_summarise(out.path,
                                   scenario = 'baseline',
                                   verbose = TRUE)
read_batch_out_all_years_summarise(out.path,
                                   scenario = '25UniversalCredit',
                                   verbose = TRUE)
read_batch_out_all_years_summarise(out.path,
                      scenario = '30UniversalCredit',
                      verbose = TRUE)
read_batch_out_all_years_summarise(out.path,
                      scenario = '35UniversalCredit',
                      verbose = TRUE)
read_batch_out_all_years_summarise(out.path,
                      scenario = '40UniversalCredit',
                      verbose = TRUE)
read_batch_out_all_years_summarise(out.path,
                      scenario = '45UniversalCredit',
                      verbose = TRUE)
read_batch_out_all_years_summarise(out.path,
                                   scenario = '50UniversalCredit',
                                   verbose = TRUE)

print('All complete!')
