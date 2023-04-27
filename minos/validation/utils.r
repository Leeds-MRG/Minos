# Utils functions for MINOS


# TODO: Write function to read all input files in a directory (i.e. final_US) into a single dataframe


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


