### This utilities file deals only with reading in and formatting input and output data files


create.if.not.exists <- function(path) {
  if(!file.exists(path)) {
    dir.create(path = path)
  }
}

## Creating a function to automatically determine between batch and single output
# This makes it easier to switch between local and arc outputs
read_output <- function(out.path, scenario, start.year=2020, end.year=2035, var.list, verbose=FALSE, drop.dead=TRUE) {
  
  #scen.path <- paste0(out.path, scenario)
  scen.path <- here::here(out.path, scenario)
  scen.path <- get_latest_runtime_subdirectory(scen.path)
  
  files <- list.files(scen.path,
                      pattern = '^[0-9]{4}.csv$',
                      full.names = TRUE)
  
  if (length(files) > 0) {
    print('Running in singular output mode')
    # files fit the single run pattern, using singular function
    data <- read_singular_local_out(out.path, scenario, drop.dead)
  } else {
    print('Running in batch output mode')
    data <- read_batch_out_all_years(out.path, scenario, start.year, end.year, var.list, verbose, drop.dead)
  }
  return(data)
}


############################## BATCH READ AND SUMMARISE ##############################

read_files_in_parallel <- function(file_paths) {
  no_cores <- detectCores() - 1  # Reserve one core for the system
  cl <- makeCluster(no_cores)
  on.exit(stopCluster(cl))  # Ensure the cluster is stopped when the function exits
  
  # Use parLapply directly with the file_paths
  loaded.file.list <- parLapply(cl, file_paths, read.csv)
  return(loaded.file.list)
}


extract_run_id <- function(filepath) {
  # Extracts the run_id using a regular expression
  run_id <- gsub(".*/(\\d+)_run_id_\\d+\\.csv$", "\\1", filepath)
  return(run_id)
}


process_files_in_batches_summarise <- function(batch, year, scenario, drop.dead) {
  # Your existing file reading and processing logic here
  # Use 'read_files_in_parallel' for reading files in the batch
  loaded.file.list <- read_files_in_parallel(batch)
  
  # Rest of your processing logic
  # Return the processed batch
  
  ############################# FIND RUN ID FROM STRING AND ASSIGN TO EACH DATAFRAME
  ############### MAYBE BEST TO DO THIS AT END
  
  # Add run_id to each dataframe
  for (i in seq_along(loaded.file.list)) {
    run_id <- extract_run_id(batch[i])
    loaded.file.list[[i]]$run_id <- run_id
  }
  
  
  # remove any dead people from each run
  drop_dead <- function(data) {
    data <- data %>%
      filter(alive != 'dead') %>%
      select(-alive)
    return(data)
  }
  if (drop.dead) {
    loaded.file.list <- lapply(loaded.file.list, drop_dead)
  }
  
  # summarise data
  sum_df_int <- function(df, year) {
    df <- df %>%
      mutate(child_under_one = (substr(child_ages, 1, 1) == 0),
             three_plus_child = (nkids >= 3),
             mother_under_25 = ((nkids_ind > 0) & (age < 25)),
             boosted = (income_boosted == TRUE)) %>%
      group_by(run_id, age, sex, ethnicity, education_state, time, region, nkids, 
               nkids_ind, S7_labour_state, matdep_child, simd_decile, child_under_one,
               three_plus_child, mother_under_25, boosted) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight),
                SF_12 = weighted.mean(SF_12, w=weight),
                boost_amount = weighted.mean(boost_amount, w=weight)) %>%
      mutate(time = year)
  }
  
  sum_df_base <- function(df, year) {
    df <- df %>%
      mutate(child_under_one = (substr(child_ages, 1, 1) == 0),
             three_plus_child = (nkids >= 3),
             mother_under_25 = ((nkids_ind > 0) & (age < 25)),
             boosted = ((universal_credit == 1) & (nkids > 0))) %>%
      group_by(run_id, age, sex, ethnicity, education_state, time, region, nkids, 
               nkids_ind, S7_labour_state, matdep_child, child_under_one,
               three_plus_child, mother_under_25, simd_decile, boosted) %>%
      summarise(count = n(),
                hh_income = weighted.mean(hh_income, w=weight),
                SF_12 = weighted.mean(SF_12, w=weight)) %>%
      mutate(time = year)
  }
  
  if (scenario == 'baseline' | year == 2020) {
    loaded.file.list <- lapply(loaded.file.list, sum_df_base, year)
  } else {
    loaded.file.list <- lapply(loaded.file.list, sum_df_int, year)
  }
  
  
  # Combine and return the processed batch
  combined_batch <- do.call(rbind, loaded.file.list)
  return(combined_batch)
}

read_and_summarise_batch_out_1year <- function(out.path, scenario, year, drop.dead = TRUE, batch.size = 10) {
  scen.path <- scen.path <- here::here(out.path, scenario)
  scen.path <- get_latest_runtime_subdirectory(scen.path)
  
  # Create file strings using year from args
  target.pattern <- paste0('[0-9]*_run_id_', year, '.csv')
  filepath.list <- list.files(path = scen.path,
                              pattern = target.pattern,
                              full.names = TRUE)
  
  # generate sequence of run IDs from length of the filepath.list
  num.run.ids <- length(filepath.list)
  run.id.vector <- 1:num.run.ids
  
  # Split filepath.list into batches
  batches <- split(filepath.list, ceiling(seq_along(filepath.list)/batch.size))
  
  # Process each batch
  processed_batches <- lapply(batches, process_files_in_batches_summarise, year, scenario, drop.dead)
  
  # Combine processed batches
  final <- do.call(rbind, processed_batches)
  
  return(final)
}

read_batch_out_all_years_summarise <- function(out.path, scenario, start.year=2020, end.year=2035, verbose=FALSE, drop.dead = TRUE) {
  print(paste0("Starting aggregation of output files for ", scenario, '...'))
  
  large.df = data.frame()
  for (i in start.year:end.year) {
    if (verbose) { print(paste0("Aggregating files for year ", i)) }
    new.df <- read_and_summarise_batch_out_1year(out.path, scenario, year=i, drop.dead)
    large.df <- rbind(large.df, new.df)
  }
  
  # Add boost vars to baseline (no boost but need the columns)
  if (scenario == 'baseline') {
    large.df$income_boosted <- FALSE
    large.df$boost_amount <- 0
  }
  
  print("All output files successfully aggregated.")
  return(large.df)
}

############################## BATCH OUTPUT ############################## 

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

read_files_in_parallel <- function(file_paths) {
  no_cores <- detectCores() - 1  # Reserve one core for the system
  cl <- makeCluster(no_cores)
  on.exit(stopCluster(cl))  # Ensure the cluster is stopped when the function exits
  
  # Use parLapply directly with the file_paths
  loaded.file.list <- parLapply(cl, file_paths, read.csv)
  return(loaded.file.list)
}


extract_run_id <- function(filepath) {
  # Extracts the run_id using a regular expression
  run_id <- gsub(".*/(\\d+)_run_id_\\d+\\.csv$", "\\1", filepath)
  return(run_id)
}

process_files_in_batches <- function(batch, year, scenario, var.list, drop.dead) {
  # Your existing file reading and processing logic here
  # Use 'read_files_in_parallel' for reading files in the batch
  loaded.file.list <- read_files_in_parallel(batch)
  
  # subset with vars from var.list
  loaded.file.list <- lapply(loaded.file.list, function(x) select(x, all_of(var.list)))
  
  # Add run_id to each dataframe
  for (i in seq_along(loaded.file.list)) {
    run_id <- extract_run_id(batch[i])
    loaded.file.list[[i]]$run_id <- run_id
  }
  
  
  # remove any dead people from each run
  drop_dead <- function(data) {
    data <- data %>%
      filter(alive != 'dead') %>%
      select(-alive)
    return(data)
  }
  if (drop.dead) {
    loaded.file.list <- lapply(loaded.file.list, drop_dead)
  }
  
  # Combine and return the processed batch
  loaded.file.list <- do.call(rbind, loaded.file.list)
  return(loaded.file.list)
}

read_batch_out_1year <- function(out.path, scenario, year, var.list, drop.dead = TRUE, batch.size = 10) {
  scen.path <- scen.path <- here::here(out.path, scenario)
  scen.path <- get_latest_runtime_subdirectory(scen.path)
  
  # Create file strings using year from args
  target.pattern <- paste0('[0-9]*_run_id_', year, '.csv')
  filepath.list <- list.files(path = scen.path,
                              pattern = target.pattern,
                              full.names = TRUE)
  
  # generate sequence of run IDs from length of the filepath.list
  # num.run.ids <- length(filepath.list)
  # run.id.vector <- 1:num.run.ids
  
  # Split filepath.list into batches
  batches <- split(filepath.list, ceiling(seq_along(filepath.list)/batch.size))
  
  # Process each batch
  processed_batches <- lapply(batches, process_files_in_batches, year, scenario, var.list, drop.dead)
  
  # # read each file in the list and store in a different list
  # loaded.file.list <- lapply(filepath.list, read.csv)
  # rm(filepath.list, num.run.ids)
  
  # subset with vars from var.list
  # subsetted.file.list <- lapply(loaded.file.list, function(x) select(x, all_of(var.list)))
  # rm(loaded.file.list)
  
  # add a run_id variable to each df in the list
  # augmented.list <- Map(cbind, subsetted.file.list, run_id = run.id.vector)
  # rm(subsetted.file.list, run.id.vector)
  
  # finally coalesce into a single df
  final <- do.call(rbind, processed_batches)
  rm(processed_batches)
  
  # # remove dead people
  # if(drop.dead) {
  #   final <- final %>%
  #     filter(alive != 'dead')
  # }
  
  return(final)
}

read_batch_out_all_years <- function(out.path, scenario, start.year=2021, end.year=2036, var.list, verbose=FALSE, drop.dead = TRUE) {
  print(paste0("Starting aggregation of output files for ", scenario, '...'))
  
  # variable list defined separately for baseline and interventions (boost vars)
  if (scenario == 'baseline') {
    var.list <- c('pidp', 'hidp', 'time', 'weight', var.list, 'alive')
  } else {
    var.list <- c('pidp', 'hidp', 'time', 'weight', 'boost_amount', 'income_boosted', var.list, 'alive')
  }
  
  large.df = data.frame()
  for (i in start.year:end.year) {
    if (verbose) { print(paste0("Aggregating files for year ", i)) }
    new.df <- read_batch_out_1year(out.path, scenario, year=i, var.list, drop.dead)
    large.df <- rbind(large.df, new.df)
  }
  
  # Add boost vars to baseline (no boost but need the columns)
  if (scenario == 'baseline') {
    large.df$income_boosted <- FALSE
    large.df$boost_amount <- 0
  }
  
  print("All output files successfully aggregated.")
  return(large.df)
}

# Function to identify variable types
variable_type <- function(x) {
  if (is.numeric(x) && !is.integer(x)) {
    return("continuous")  # float values
  } else if (is.numeric(x) && is.integer(x) && length(unique(x)) > 15) {
    return("continuous")  # int but lots of unique values
  } else if (is.numeric(x) && is.integer(x) && length(unique(x)) < 15) {
    return("ordinal")
  } else if (is.character(x)) {
    return("nominal")
  } else {
    return("other")
  }
}

read_batch_out_summarise <- function(out.path, scenario, start.year=2021, end.year=2036, var.list, verbose=FALSE) {
  # First use other function to get batch output
  large_df <- read_batch_out_all_years(out.path, scenario, start.year, end.year, var.list, verbose)
  
  print('LARGE_DF GENERATED...')
  
  #print(colnames(large_df))
  
  # Now identify columns and calculate summary values
  # Define a list of columns to group by
  group_cols <- c("pidp", "time")
  
  # Identify variable types
  var_types <- sapply(large_df, variable_type)
  
  #print("VAR_TYPES:")
  #print(var_types)
  
  # Separate variables by type
  continuous_vars <- names(var_types[var_types == "continuous"])
  ordinal_vars <- names(var_types[var_types == "ordinal"])
  nominal_vars <- names(var_types[var_types == "nominal"])
  
  print("ABOUT TO SUMMARISE")
  
  #return(large_df)
  
  #print("This should not be happening")
  
  # Calculate mean for continuous variables and median for ordinal variables
  result_df <- large_df %>%
    group_by(across(all_of(group_cols))) %>%
    summarize(
      across(all_of(setdiff(continuous_vars, group_cols)), mean, na.rm = TRUE),
      across(all_of(ordinal_vars), ~ mode(.x)),
      across(all_of(nominal_vars), ~ mode(.x))
    )
  return(result_df)
}


############################## SINGULAR OUTPUT ############################## 


# Function to read all output files from a singular (non-batch) local simulation run
# This will read output files for all years within the latest runtime subdirectory
# (which is automatically determined)
# Args: 
#       out.path - path to top level output directory
#       scenario - string scenario name of which output files to read
read_singular_local_out <- function(out.path, scenario, drop.dead = FALSE) {
  ## Start with scenario name
  # attach full output path
  # get runtime directory
  # list files
  # return do.call(...)
  
  scen.path <- here::here(out.path, scenario)
  scen.path <- get_latest_runtime_subdirectory(scen.path)

  files <- list.files(scen.path,
                      pattern = '[0-9]{4}.csv',
                      full.names = TRUE)
  dat <- do.call(rbind, lapply(files, read.csv))
  
  # remove dead people
  if(drop.dead) {
    dat <- dat %>%
      filter(alive != 'dead')
  }
  
  return(dat)
}

read_first_singular_local_out <- function(out.path, scenario, drop.dead = FALSE) {
  ## Start with scenario name
  # attach full output path
  # get runtime directory
  # list files
  # return do.call(...)
  
  print('Starting singular output read...')
  
  scen.path <- here::here(out.path, scenario)
  scen.path <- get_latest_runtime_subdirectory(scen.path)
  
  print(scen.path)
  
  files <- list.files(scen.path,
                      pattern = '0001_run_id_[0-9]{4}.csv',
                      full.names = TRUE)
  dat <- do.call(rbind, lapply(files, read.csv))
  
  # remove dead people
  if(drop.dead) {
    dat <- dat %>%
      filter(alive != 'dead')
  }
  
  return(dat)
}



read_raw_data_out <- function(data.path, section, drop.dead=FALSE) {
  ## get all data 
  
  scen.path <- here::here(data.path, section)
  files <- list.files(scen.path,
                      pattern = '[0-9]{4}_US_cohort.csv',
                      full.names = TRUE)
  dat <- do.call(rbind, lapply(files, read.csv))
  # remove dead people
  if(drop.dead) {
    dat <- dat %>%
      filter(alive != 'dead')
  }
  
  return(dat)
}

save_raw_data_in <- function(data, data.path) {
  ## save all data after processing.
  
  for (year_time in unique(data$time)) {
    yearly_file_name <- paste0(data.path, year_time, "_US_cohort.csv")
    yearly_df <- data[which(data$time == year_time),]
    write.csv(yearly_df, file=yearly_file_name, row.names=FALSE)
    print(paste0("Saved file to: ", yearly_file_name, "."))
  }
}


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
read_agg_subset_batch_out <- function(out.path, scenario, year, var.list) {
  scen.path <- paste0(out.path, scenario)
  scen.path <- get_latest_runtime_subdirectory(scen.path)
  
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


################ NOTE ################

# The following functions are not perfect as they were created for a specific
# purpose previously. They have hard coded variable lists and it's not currently
# worth the effort to generalise. Leaving them here as they can be modified
# for a new purpose, or could be useful as is.


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


extract_child_ages <- function(child_ages_string){
  return (as.numeric(unlist(strsplit(child_ages_string, "_"))))
}
