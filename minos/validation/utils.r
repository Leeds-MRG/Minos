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


# Function to combine two dataframes and pivot_longer for further processing 
# with ggplot or ttests. Must be either simulation output or raw files
combine_and_pivot_long <- function(df1, df1.name, df2, df2.name, var) {
  # get only the columns we want a rename
  df1 <- df1 %>%
    select('pidp', 'time', var) %>%
    set_names(c('pidp', 'time', df1.name))
  df2 <- df2 %>%
    select('pidp', 'time', var) %>%
    set_names(c('pidp', 'time', df2.name))
  # merge on pidp and time
  merged <- merge(df1, df2, by = c('pidp', 'time'))
  pivoted <- pivot_longer(data = merged,
                          cols = df1.name:df2.name,
                          names_to = 'scenario',
                          values_to = var)
  return(pivoted)
}

# Function to plot the means of a single variable from 2 different datasets
# The 2 datasets must either be input data (i.e. final_US) or simulated output
plot_mean_comparison <- function(pivoted.df, var, group.var) {
  merged.byyr <- pivoted.df %>%
    group_by(time, .data[[group.var]]) %>%
    summarise(var = mean(.data[[var]]))
  
  ggplot(data = merged.byyr, mapping = aes(x = time, y = var, color=scenario)) +
    geom_line() +
    ylab(var)
}


compare_boxplot_long <- function(pivoted.df, 
                                 var, 
                                 scen1, 
                                 scen2, 
                                 subset.max = 1000000, 
                                 subset.min = -1000000,
                                 title = NULL) {
  # This chunk finds the mean to be plotted on the boxplot at the end. Not needed but leaving in case
  #means <- c(mean(pivoted[[var]][pivoted[['scenario']] == scen1], na.rm = TRUE),
  #           mean(pivoted[[var]][pivoted[['scenario']] == scen2], na.rm = TRUE))
  
  formula = as.formula(paste0(var, ' ~ scenario'))
  
  # create vectors for subsetting
  pivoted.df$in.range <- (pivoted.df[[var]] < subset.max) & (pivoted.df[[var]] > subset.min)
  
  boxplot(formula,
          data = pivoted.df,
          col = 'lightgray',
          subset = in.range)
  #points(c(1,2), means, pch = 15, col = 'red')
  if(!is.null(title)) {
    mtext(title, side=3, adj=0.1)
  }
}

yearly_box_plots <- function(pivoted.df, 
                             var, 
                             scen1, 
                             scen2, 
                             subset.max = 1000000, 
                             subset.min = -1000000) {
  for(year in unique(pivoted.df$time)) {
    filtered.df <- pivoted.df %>% filter(time == year)
    compare_boxplot_long(filtered.df,
                         var,
                         scen1,
                         scen2,
                         subset.max,
                         subset.min,
                         title = year)
  }
}

two_sample_t_test <- function(df1, df1.name, df2, df2.name, var) {
  # make column list and create empty dataframe to fill in loop
  df1.mean.name <- paste0(df1.name, '.mean')
  df2.mean.name <- paste0(df2.name, '.mean')
  columns <- c('year', df1.mean.name, df2.mean.name, 'p.value')
  df <- data.frame(matrix(nrow = 0, ncol = length(columns)),
                   row.names = NULL)
  colnames(df) <- columns
  
  # loop through years
  for(year in unique(df1$time)) {
    print(paste('T tests for year', year, ':'))
    # filter the year
    tmp.df1 <- df1 %>% filter(time == year)
    tmp.df2 <- df2 %>% filter(time == year)
    
    # check variance and test for equal variance
    var.tmp.df1 <- var(tmp.df1[[var]])
    var.tmp.df2 <- var(tmp.df2[[var]], na.rm = TRUE)
    
    if(var.tmp.df2 > var.tmp.df1) {
      equal.var <- (var.tmp.df1 / var.tmp.df2) < 4
    } else {
      equal.var <- (var.tmp.df2 / var.tmp.df1) < 4
    }
    
    test <- t.test(tmp.df1[[var]], tmp.df2[[var]], var.equal = equal.var)
    print(test)
    
    new.df <- data.frame(year = year,
                         df1.placeholder = test$estimate[1],
                         df2.placeholder = test$estimate[2],
                         p.value = test$p.value,
                         row.names = NULL)
    names(new.df)[names(new.df) == "df1.placeholder"] <- df1.mean.name
    names(new.df)[names(new.df) == "df2.placeholder"] <- df2.mean.name
    
    df <- rbind(df, new.df)
  }
  return(df)
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








