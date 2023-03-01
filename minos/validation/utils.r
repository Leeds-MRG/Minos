# Utils functions for MINOS

################# Reading output files #################

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


################# Plotting Pathway Comparisons #################

compare_housing_out <- function(base, int) {
  
  housing.base <- base %>% 
    select(pidp, time, housing_quality)
  
  housing.int <- int %>% 
    select(pidp, time, housing_quality, income_boosted)
  
  # first rename and cbind
  housing.b <- rename(housing.base, base = housing_quality)
  housing.i <- rename(housing.int, int = housing_quality)
  
  housing.merged <- merge(housing.b, housing.i, by=c('pidp', 'time'))
  
  housing.merged <- pivot_longer(data = housing.merged,
                                 cols = base:int,
                                 names_to = 'scenario',
                                 values_to = 'housing')
  
  housing.merged.byyr <- housing.merged %>%
    group_by(time, scenario) %>%
    summarise(housing = mean(housing))
  
  ggplot(data = housing.merged.byyr, mapping = aes(x = time, y = housing, color=scenario)) +
    geom_line() +
    labs(title = 'Housing Quality') +
    xlab('Year') +
    ylab('Average')
}


compare_neighbourhood_out <- function(base, int) {
  
  neighbourhood.base <- base %>% 
    select(pidp, time, neighbourhood_safety)
  
  neighbourhood.int <- int %>% 
    select(pidp, time, neighbourhood_safety, income_boosted)
  
  # first rename and cbind
  neighbourhood.b <- rename(neighbourhood.base, base = neighbourhood_safety)
  neighbourhood.i <- rename(neighbourhood.int, int = neighbourhood_safety)
  
  neighbourhood.merged <- merge(neighbourhood.b, neighbourhood.i, by=c('pidp', 'time'))
  
  neighbourhood.merged <- pivot_longer(data = neighbourhood.merged,
                                 cols = base:int,
                                 names_to = 'scenario',
                                 values_to = 'neighbourhood')
  
  neighbourhood.merged.byyr <- neighbourhood.merged %>%
    group_by(time, scenario) %>%
    summarise(neighbourhood = mean(neighbourhood))
  
  ggplot(data = neighbourhood.merged.byyr, mapping = aes(x = time, y = neighbourhood, color=scenario)) +
    geom_line() +
    labs(title = 'Neighbourhood Safety') +
    xlab('Year') +
    ylab('Average')
}


compare_ncigs_out <- function(base, int) {
  ncigs.base <- base %>% 
    select(pidp, time, ncigs)
  
  ncigs.int <- int %>% 
    select(pidp, time, ncigs, income_boosted)
  
  # first rename and cbind
  ncigs.b <- rename(ncigs.base, base = ncigs)
  ncigs.i <- rename(ncigs.int, int = ncigs)
  
  ncigs.merged <- merge(ncigs.b, ncigs.i, by=c('pidp', 'time'))
  
  ncigs.merged <- pivot_longer(data = ncigs.merged,
                               cols = base:int,
                               names_to = 'scenario',
                               values_to = 'ncigs')
  
  ncigs.merged.byyr <- ncigs.merged %>%
    group_by(time, scenario) %>%
    summarise(ncigs = mean(ncigs))
  
  ggplot(data = ncigs.merged.byyr, mapping = aes(x = time, y = ncigs, color=scenario)) +
    geom_line() +
    labs(title = 'Tobacco Use', subtitle = 'Cigarettes per day') +
    xlab('Year') +
    ylab('Average')
}


compare_nutrition_out <- function(base, int) {
  nut.base <- base %>% 
    select(pidp, time, nutrition_quality)
  
  nut.int <- int %>% 
    select(pidp, time, nutrition_quality, income_boosted)
  
  # first rename and cbind
  nut.b <- rename(nut.base, base = nutrition_quality)
  nut.i <- rename(nut.energy, int = nutrition_quality)
  
  nut.merged <- merge(nut.b, nut.i, by=c('pidp', 'time'))
  
  nut.merged <- pivot_longer(data = nut.merged,
                             cols = base:int,
                             names_to = 'scenario',
                             values_to = 'nutrition')
  
  nut.merged.byyr <- nut.merged %>%
    group_by(time, scenario) %>%
    summarise(nutrition = mean(nutrition))
  
  ggplot(data = nut.merged.byyr, mapping = aes(x = time, y = nutrition, color=scenario)) +
    geom_line() +
    labs(title = 'Nutrition Quality') +
    xlab('Year') +
    ylab('Average')
}


compare_loneliness_out <- function(base, int) {
  lnly.base <- base %>% 
    select(pidp, time, loneliness)
  
  lnly.int <- int %>% 
    select(pidp, time, loneliness, income_boosted)
  
  # first rename and cbind
  lnly.b <- rename(lnly.base, base = loneliness)
  lnly.i <- rename(lnly.energy, int = loneliness)
  
  lnly.merged <- merge(lnly.b, lnly.i, by=c('pidp', 'time'))
  
  lnly.merged <- pivot_longer(data = lnly.merged,
                              cols = base:int,
                              names_to = 'scenario',
                              values_to = 'loneliness')
  
  lnly.merged.byyr <- lnly.merged %>%
    group_by(time, scenario) %>%
    summarise(loneliness = mean(loneliness))
  
  ggplot(data = lnly.merged.byyr, mapping = aes(x = time, y = loneliness, color=scenario)) +
    geom_line() +
    labs(title = 'Loneliness') +
    xlab('Year') +
    ylab('Average')
}

