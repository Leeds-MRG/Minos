# Utils functions for MINOS


# TODO: Write function to read all input files in a directory (i.e. final_US) into a single dataframe


# Function to combine two dataframes and pivot_longer for further processing 
# with ggplot or ttests. Must be either simulation output or raw files
combine_and_pivot_long <- function(df1, df1.name, df2, df2.name, var) {
  # first set up vector of missing values to remove
  miss.vals <- c(-9, -8, -7, -3, -2, -1)
  # get only the columns we want a rename
  df1 <- df1 %>%
    select('pidp', 'time', all_of(var)) %>%
    filter(!var %in% miss.vals) %>%
    set_names(c('pidp', 'time', df1.name))
  df2 <- df2 %>%
    select('pidp', 'time', all_of(var)) %>%
    filter(!var %in% miss.vals) %>%
    set_names(c('pidp', 'time', df2.name))
  # merge on pidp and time
  merged <- merge(df1, df2, by = c('pidp', 'time'), all=TRUE)
  pivoted <- pivot_longer(data = merged,
                          cols = df1.name:df2.name,
                          names_to = 'scenario',
                          values_to = var)
  return(pivoted)
}

# Function to plot the means of a single variable from 2 different datasets
# The 2 datasets must either be input data (i.e. final_US) or simulated output
plot_mean_comparison <- function(pivoted.df, var, group.var, save=FALSE, save.path=NULL) {
  merged.byyr <- pivoted.df %>%
    filter(.data[[var]] != -9) %>%
    group_by(time, .data[[group.var]]) %>%
    summarise(var = mean(.data[[var]]))
  
  p <- ggplot(data = merged.byyr, mapping = aes(x = time, y = var, color=scenario)) +
    geom_line() +
    labs(title = paste0('Cross-Validation: ', var)) +
    ylab('Mean') +
    xlab('Year')
  
  print(p)
  
  if(save) {
    if(is.null(save.path)) {
      stop('ERROR: save.path must be defined when saving the plot')
    }
    save.filename <- paste0('cv_', var, '_continuous.png')
    ggsave(filename = save.filename,
           plot = p,
           path = save.path,
           width = 9,
           height = 5)
  }
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

# Function to plot both count and proportion comparisons between raw and 
# simulated data using cross-validation outputs.
cv_ordinal_plots <- function(pivoted.df, var, save=FALSE, save.path) {
  df <- pivoted.df %>%
    group_by(time, scenario, .data[[var]]) %>%
    summarise(n = n())
  
  df$scenario <- factor(df$scenario)
  df[[var]] <- factor(df[[var]])
  
  df <- df %>% filter(.data[[var]] != -9)
  
  p1 <- ggplot(data = df, aes(x = time, y = n, group = interaction(scenario, .data[[var]]), color = .data[[var]], linetype = scenario)) +
    geom_line() + 
    geom_point() +
    labs(title = paste0('Cross-Validation: ', var), subtitle = 'Count') +
    xlab('Year') +
    ylab('Count')
  
  print(p1)
  
  if(save) {
    if(is.null(save.path)) {
      stop('ERROR: save.path must be defined when saving the plot')
    }
    save.filename <- paste0('cv_', var, '_count.png')
    ggsave(filename = save.filename,
           plot = p1,
           path = save.path,
           width = 9,
           height = 5)
  }
  
  df <- df %>%
    group_by(time, scenario) %>%
    mutate(prop = n / sum(n))
  
  p2 <- ggplot(data = df, aes(x = time, y = prop, group = interaction(scenario, .data[[var]]), color = .data[[var]], linetype = scenario)) +
    geom_line() + 
    geom_point() +
    labs(title = paste0('Cross-Validation: ', var), subtitle = 'Proportion') +
    xlab('Year') +
    ylab('Proportion')
  
  print(p2)
  
  if(save) {
    if(is.null(save.path)) {
      stop('ERROR: save.path must be defined when saving the plot')
    }
    save.filename <- paste0('cv_', var, '_proportion.png')
    ggsave(filename = save.filename,
           plot = p2,
           path = save.path,
           width = 9,
           height = 5)
  }
}


find_mode <- function(x) {
  u <- unique(x)
  tab <- tabulate(match(x, u))
  u[tab == max(tab)]
}

