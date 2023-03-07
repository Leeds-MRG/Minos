# Utils functions for MINOS


# TODO: Write function to read all input files in a directory (i.e. final_US) into a single dataframe

read_output <- function(out.path, scenario) {
  ## Start with scenario name
  # attach full output path
  # get runtime directory
  # list files
  # return do.call(...)
  
  scen.path <- paste0(out.path, scenario)
  scen.path <- get_runtime_subdirectory(scen.path)
  
  files <- list.files(scen.path,
                      pattern = '[0-9]{4}.csv',
                      full.names = TRUE)
  return(do.call(rbind, lapply(files, read.csv)))
}


get_runtime_subdirectory <- function(path) {
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


read_and_collapse_MINOS_batch_output <- function(scenario_out_path, year, var.list) {
  # This function will read all files from a batch run of MINOS for a specific 
  # year, select only a list of variables we are interested in, and collapse
  # them into a single dataframe with a `run_id` variable to denote individual
  # runs.
  
  # This function will likely use a LOT of memory, so we're going to remove 
  # objects wherever we can to avoid problems
  
  # Create file strings using year from args
  target.pattern <- paste0('[0-9]*_run_id_', year, '.csv')
  filepath.list <- list.files(path = scenario_out_path,
                              pattern = target.pattern,
                              full.names = TRUE)
  
  # generate sequence of run IDs from length of the filepath.list
  num.run.ids <- length(filepath.list)
  run.id.vector <- 1:num.run.ids
  
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



collapse_multiple_out_to_summary <- function(big.out) {
  ## NOTE
  # This function will only work for an output file with a specific set of 
  # variables. This is less than perfect but not worth the time to 
  # generalise at present (12/1/23)
  
  grouped <- big.out %>% 
    group_by(pidp) %>%
    summarise(SF_12 = mean(SF_12),
              hh_income = mean(hh_income),
              housing_quality = median(housing_quality),
              neighbourhood_safety = median(neighbourhood_safety),
              loneliness = median(loneliness),
              phealth = mean(phealth),
              ncigs = mean(ncigs),
              nutrition_quality = mean(nutrition_quality))
  
  return(grouped)
}


get_summary_out <- function(scenario_out_path, year, var.list) {
  
  big.out <- read_and_collapse_MINOS_batch_output(scenario_out_path, year, var.list)
  
  grouped <- big.out %>% 
    group_by(pidp) %>%
    summarise(SF_12 = mean(SF_12),
              hh_income = mean(hh_income),
              housing_quality = median(housing_quality),
              neighbourhood_safety = median(neighbourhood_safety),
              loneliness = median(loneliness),
              phealth = mean(phealth),
              ncigs = mean(ncigs),
              nutrition_quality = mean(nutrition_quality))
  
  return(grouped)
}








