### Utilities for Equivalent Income Analyses


simplified_component_change <- function(base.batch, int.batch, group.var, var, print = FALSE) {
  
  # it would be lovely if this was completely generic, but for some things that
  # is more hassle than its worth. Handling string vars here is one of these 
  # things
  
  if (var == 'S7_housing_quality') {
    base.batch$S7_housing_quality <- as.numeric(factor(base.batch$S7_housing_quality,
                                                       levels = c('No to all',
                                                                  'Yes to some',
                                                                  'Yes to all'),
                                                       labels = c(1, 2, 3)))
    int.batch$S7_housing_quality <- as.numeric(factor(int.batch$S7_housing_quality,
                                                      levels = c('No to all',
                                                                 'Yes to some',
                                                                 'Yes to all'),
                                                      labels = c(1, 2, 3)))
  } else if (var == 'S7_neighbourhood_safety') {
    base.batch$S7_neighbourhood_safety <- as.numeric(factor(base.batch$S7_neighbourhood_safety,
                                                            levels = c('Often',
                                                                       'Some of the time',
                                                                       'Hardly ever'),
                                                            labels = c(1, 2, 3)))
    int.batch$S7_neighbourhood_safety <- as.numeric(factor(int.batch$S7_neighbourhood_safety,
                                                           levels = c('Often',
                                                                      'Some of the time',
                                                                      'Hardly ever'),
                                                           labels = c(1, 2, 3)))
  } else if (var == 'loneliness') {
    base.batch$loneliness <- as.numeric(factor(base.batch$loneliness,
                                               levels = c(1, 2, 3),
                                               labels = c(3, 2, 1)))
    int.batch$loneliness <- as.numeric(factor(int.batch$loneliness,
                                              levels = c(1, 2, 3),
                                              labels = c(3, 2, 1)))
  }
  
  base.sub <- base.batch %>%
    select(pidp, time, run_id, all_of(group.var), all_of(var)) %>%
    rename(Baseline_var = .data[[var]],
           Baseline_group.var = .data[[group.var]])
  
  int.sub <- int.batch %>%
    select(pidp, time, run_id, all_of(group.var), all_of(var)) %>%
    rename(Intervention_var = .data[[var]],
           Intervention_group.var = .data[[group.var]])
  
  merged <- merge(base.sub, int.sub,
                  by=c('pidp', 'time', 'run_id'),
                  all = FALSE)
  
  merged2 <- merged %>%
    mutate(varChange = Intervention_var - Baseline_var,
           effect = case_when(varChange > 0 ~ "Positive",
                              varChange < 0 ~ "Negative",
                              varChange == 0 ~ "No_Change")) %>%
    select(-Baseline_var, -Intervention_var, -Intervention_group.var, -varChange) %>%
    rename(income.quint = Baseline_group.var) %>%
    group_by(time, run_id, .data[[group.var]], effect) %>%
    count() %>%
    group_by(time, run_id, .data[[group.var]]) %>%
    mutate(total = sum(n),
           effect_prop = n / total) %>%
    select(-n, -total) %>%
    group_by(time, .data[[group.var]], effect) %>%
    summarise(effect_prop = mean(effect_prop)) %>%
    pivot_wider(names_from = 'effect',
                values_from = 'effect_prop') %>%
    mutate(change = Positive - Negative) %>%
    select(-Positive, -Negative, -No_Change, -time) %>%
    group_by(.data[[group.var]]) %>%
    summarise(change = sum(change))
  
  p1 <- ggplot(data = merged2, aes(x = .data[[group.var]], y = change)) +
    geom_col() +
    labs(title = paste0('Change in ', var, ' by ', group.var)) +
    ylab('% Change')
  
  if(print) {
    print(p1)
  }
  
  return(merged2)
}



simplified_component_change_BOXPLOT <- function(base.batch, int.batch, group.var, var, print = FALSE) {
  
  # it would be lovely if this was completely generic, but for some things that
  # is more hassle than its worth. Handling string vars here is one of these 
  # things
  
  if (var == 'S7_housing_quality') {
    base.batch$S7_housing_quality <- as.numeric(factor(base.batch$S7_housing_quality,
                                                       levels = c('No to all',
                                                                  'Yes to some',
                                                                  'Yes to all'),
                                                       labels = c(1, 2, 3)))
    int.batch$S7_housing_quality <- as.numeric(factor(int.batch$S7_housing_quality,
                                                      levels = c('No to all',
                                                                 'Yes to some',
                                                                 'Yes to all'),
                                                      labels = c(1, 2, 3)))
  } else if (var == 'S7_neighbourhood_safety') {
    base.batch$S7_neighbourhood_safety <- as.numeric(factor(base.batch$S7_neighbourhood_safety,
                                                            levels = c('Often',
                                                                       'Some of the time',
                                                                       'Hardly ever'),
                                                            labels = c(1, 2, 3)))
    int.batch$S7_neighbourhood_safety <- as.numeric(factor(int.batch$S7_neighbourhood_safety,
                                                           levels = c('Often',
                                                                      'Some of the time',
                                                                      'Hardly ever'),
                                                           labels = c(1, 2, 3)))
  } else if (var == 'loneliness') {
    base.batch$loneliness <- as.numeric(factor(base.batch$loneliness,
                                               levels = c(1, 2, 3),
                                               labels = c(3, 2, 1)))
    int.batch$loneliness <- as.numeric(factor(int.batch$loneliness,
                                              levels = c(1, 2, 3),
                                              labels = c(3, 2, 1)))
  }
  
  base.sub <- base.batch %>%
    select(pidp, time, run_id, all_of(group.var), all_of(var)) %>%
    rename(Baseline_var = .data[[var]],
           Baseline_group.var = .data[[group.var]])
  
  int.sub <- int.batch %>%
    select(pidp, time, run_id, all_of(group.var), all_of(var)) %>%
    rename(Intervention_var = .data[[var]],
           Intervention_group.var = .data[[group.var]])
  
  merged <- merge(base.sub, int.sub,
                  by=c('pidp', 'time', 'run_id'),
                  all = FALSE)
  
  merged2 <- merged %>%
    mutate(varChange = Intervention_var - Baseline_var,
           effect = case_when(varChange > 0 ~ "Positive",
                              varChange < 0 ~ "Negative",
                              varChange == 0 ~ "No_Change")) %>%
    select(-Baseline_var, -Intervention_var, -Intervention_group.var, -varChange) %>%
    rename(!!group.var := Baseline_group.var) %>%
    group_by(time, run_id, .data[[group.var]], effect) %>%
    count() %>%
    group_by(time, run_id, .data[[group.var]]) %>%
    mutate(total = sum(n),
           effect_prop = n / total) %>%
    select(-n, -total) %>%
    pivot_wider(names_from = 'effect',
                values_from = 'effect_prop') %>%
    mutate(change = Positive - Negative) %>%
    select(-Positive, -Negative, -No_Change) %>%
    group_by(run_id, .data[[group.var]]) %>%
    summarise(sum.change = sum(change))
  
  p1 <- ggplot(data = merged2, aes(x = .data[[group.var]], y = sum.change)) +
    geom_boxplot(notch = FALSE) +
    labs(title = paste0('Change in ', var, ' by ', group.var)) +
    ylab('% Change')
  
  if(print) {
    print(p1)
  }
  
  return(merged2)
}

sccb_all_vars <- function(base.batch, int.batch, group.var, varlist) {
  df <- simplified_component_change(base.batch, energy.batch, group.var = 'income.quint', var = 'S7_housing_quality')
  colnames(df) <- c('Income_Quintile', 'S7_housing_quality')
  for (S7_var in varlist) {
    df2 <- simplified_component_change(base.batch, energy.batch, group.var = 'income.quint', var = S7_var)
    colnames(df2) <- c('Income_Quintile', S7_var)
    df <- merge(df, df2, by = c('Income_Quintile'))
  }
  rm(df2)
  
  # finally pivot_longer for ggplot and facet_wrap to take over
  df2 <- df %>%
    pivot_longer(cols = S7_housing_quality:S7_mental_health,
                 names_to = 'Variable',
                 values_to = 'Change')
  p1 <- ggplot(df2, aes(x = Variable, y = Change, group = Variable, colour = Variable, fill = Variable)) +
    geom_col() +
    facet_wrap(~ Income_Quintile, nrow = 1) +
    theme(legend.position = 'bottom',
          axis.title.x = element_blank(),
          axis.text.x = element_blank(),
          axis.ticks.x = element_blank())
  print(p1)
}

sccb_all_vars_BOXPLOT <- function(base.batch, int.batch, group.var, varlist) {
  df <- simplified_component_change_BOXPLOT(base.batch, energy.batch, group.var = group.var, var = 'S7_housing_quality')
  colnames(df) <- c('run_id', 'Income_Quintile', 'S7_housing_quality')
  for (S7_var in varlist) {
    df2 <- simplified_component_change_BOXPLOT(base.batch, energy.batch, group.var = 'income.quint', var = S7_var)
    colnames(df2) <- c('run_id', 'Income_Quintile', S7_var)
    df <- merge(df, df2, by = c('run_id', 'Income_Quintile'))
  }
  rm(df2)
  
  # finally pivot_longer for ggplot and facet_wrap to take over
  df2 <- df %>%
    pivot_longer(cols = S7_housing_quality:S7_mental_health,
                 names_to = 'Variable',
                 values_to = 'Change')
  
  p1 <- ggplot(df2, aes(x = Variable, y = Change, group = Variable, colour = Variable, fill = Variable)) +
    geom_boxplot(notch = FALSE) +
    facet_wrap(~ Income_Quintile, nrow = 1) +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    theme(legend.position = 'bottom',
          axis.title.x = element_blank(),
          axis.text.x = element_blank(),
          axis.ticks.x = element_blank())
  print(p1)
}