## SCRIPT for holding plotting functions for SCP plot script.


SF12.change.full.sample.single <- function(df.list, scen.list) {
  single.mean <- function(data, scen) {
    newvar.name <- paste0(scen, '.SF12')
    data <- data %>%
      select(time, SF_12) %>%
      filter(SF_12 != -8) %>%
      group_by(time) %>%
      summarise(!!sym(newvar.name) := mean(SF_12, na.rm =TRUE))
    return(data)
  }
  
  df.list <- mapply(single.mean, df.list, scen.list, SIMPLIFY = FALSE)
  
  combined <- df.list %>%
    reduce(full_join, by='time')
  
  # List of intervention columns
  int_cols <- grep("int\\d+.SF12", names(combined), value = TRUE)
  
  # Create the new dataframe with differences
  combined <- combined %>%
    mutate(across(all_of(int_cols), ~ . - base.SF12, .names = "diff{col}")) %>%
    select(time, starts_with("diff")) %>%
    rename_with(~ str_replace_all(., "diffint(\\d+).SF12", "diff\\1"))
  
  combined <- combined %>%
    pivot_longer(cols = starts_with('diff'),
                 names_to = 'scen',
                 values_to = 'diff')
  
  #return(combined)
  
  scen.list <- scen.list[-1]
  
  #TODO: Rename factor levels
  #correct factor levels for plot
  # combined$scen <- factor(combined$scen,
  #                         levels = scen.list)
  
  #return(combined)
  
  p1 <- ggplot(combined, aes(x = time, y = diff, group = scen, colour = scen)) +
    geom_line() +
    geom_hline(yintercept = 0, linetype='dashed') +
    labs(title = 'Relative change in SF12 MCS', subtitle = 'Whole population') +
    xlab('Year') +
    ylab('Difference')
  
  print(p1)
}

SF12.change.full.sample.batch <- function(df.list, scen.list) {
  batch.mean <- function(data, scen) {
    newvar.name <- paste0(scen, '.SF12')
    data <- data %>%
      select(time, run_id, SF_12) %>%
      filter(SF_12 != -8) %>%
      group_by(time, run_id) %>%
      summarise(!!sym(newvar.name) := mean(SF_12, na.rm =TRUE))
    return(data)
  }
  
  df.list <- mapply(batch.mean, df.list, scen.list, SIMPLIFY = FALSE)
  
  #df.list <- list(base, int1, int2, int3, int4)
  combined <- df.list %>%
    reduce(full_join, by=c('time', 'run_id'))
  
  # List of intervention columns
  int_cols <- grep("int\\d+.SF12", names(combined), value = TRUE)
  
  # Create the new dataframe with differences
  combined <- combined %>%
    mutate(across(all_of(int_cols), ~ . - base.SF12, .names = "diff{col}")) %>%
    select(time, starts_with("diff")) %>%
    rename_with(~ str_replace_all(., "diffint(\\d+).SF12", "diff\\1"))
  
  combined <- combined %>%
    pivot_longer(cols = starts_with('diff'),
                 names_to = 'scen',
                 values_to = 'diff')
  
  # combined <- combined %>%
  #   select(time, run_id, contains('diff')) %>%
  #   pivot_longer(cols = diff25:diff100,
  #                names_to = 'scen',
  #                values_to = 'diff')
  
  # TODO: Rename factor levels
  # correct factor levels for plot
  # combined$scen <- factor(combined$scen,
  #                         levels = c('diff100', 'diff75', 'diff50', 'diff25'))
  
  p1 <- ggplot(combined, aes(x = time, y = diff, group = scen, colour = scen)) +
    geom_smooth() +
    geom_hline(yintercept = 0, linetype='dashed') +
    labs(title = 'Relative change in SF12 MCS', subtitle = 'Whole population') +
    xlab('Year') +
    ylab('Difference')
  
  print(p1)
}

SF12.change.families.single <- function(df.list, scen.list) {
  single.mean <- function(data, scen) {
    newvar.name <- paste0(scen, '.SF12')
    data <- data %>%
      select(time, SF_12, nkids) %>%
      filter(nkids > 0) %>%
      filter(SF_12 != -8) %>%
      group_by(time) %>%
      summarise(!!sym(newvar.name) := mean(SF_12, na.rm =TRUE))
    return(data)
  }
  ########################################### CHANGE EVERYTHING FROM WEIGHTED MEAN TO MEAN ###########################################
  
  df.list <- mapply(single.mean, df.list, scen.list, SIMPLIFY = FALSE)
  
  combined <- df.list %>%
    reduce(full_join, by='time')
  
  # List of intervention columns
  int_cols <- grep("int\\d+.SF12", names(combined), value = TRUE)
  
  # Create the new dataframe with differences
  combined <- combined %>%
    mutate(across(all_of(int_cols), ~ . - base.SF12, .names = "diff{col}")) %>%
    select(time, starts_with("diff")) %>%
    rename_with(~ str_replace_all(., "diffint(\\d+).SF12", "diff\\1"))
  
  combined <- combined %>%
    pivot_longer(cols = starts_with('diff'),
                 names_to = 'scen',
                 values_to = 'diff')
  
  p1 <- ggplot(combined, aes(x = time, y = diff, group = scen, colour = scen)) +
    geom_line() +
    geom_hline(yintercept = 0, linetype='dashed') +
    labs(title = 'Relative change in SF12 MCS', subtitle = 'Households with Children') +
    xlab('Year') +
    ylab('Difference')
  
  print(p1)
}

SF12.change.families.batch <- function(df.list, scen.list) {
  batch.mean <- function(data, scen) {
    newvar.name <- paste0(scen, '.SF12')
    data <- data %>%
      select(time, run_id, SF_12, nkids) %>%
      filter(nkids > 0) %>%
      filter(SF_12 != -8) %>%
      group_by(time, run_id) %>%
      summarise(!!sym(newvar.name) := mean(SF_12, na.rm =TRUE))
    return(data)
  }
  
  df.list <- mapply(batch.mean, df.list, scen.list, SIMPLIFY = FALSE)
  
  combined <- df.list %>%
    reduce(full_join, by=c('time', 'run_id'))
  
  # List of intervention columns
  int_cols <- grep("int\\d+.SF12", names(combined), value = TRUE)
  
  # Create the new dataframe with differences
  combined <- combined %>%
    mutate(across(all_of(int_cols), ~ . - base.SF12, .names = "diff{col}")) %>%
    select(time, starts_with("diff")) %>%
    rename_with(~ str_replace_all(., "diffint(\\d+).SF12", "diff\\1"))
  
  combined <- combined %>%
    pivot_longer(cols = starts_with('diff'),
                 names_to = 'scen',
                 values_to = 'diff')
  
  p1 <- ggplot(combined, aes(x = time, y = diff, group = scen, colour = scen)) +
    geom_smooth() +
    geom_hline(yintercept = 0, linetype='dashed') +
    labs(title = 'Relative change in SF12 MCS', subtitle = 'Households with Children') +
    xlab('Year') +
    ylab('Difference')
  
  print(p1)
}

SF12.change.treated.single <- function(df.list, scen.list) {
  single.mean <- function(data, scen, boosted) {
    # define varname
    newvar.name <- paste0(scen, '.SF12')
    # prepare data
    data <- data %>%
      select(time, SF_12) %>%
      filter(boosted == TRUE) %>%
      group_by(time) %>%
      summarise(!!sym(newvar.name) := mean(SF_12, na.rm =TRUE))
    return(data)
  }
  
  #TODO: FIX THIS! NEED DIFFERENT BASELINE FOR EACH INT?? THINK SO!
  # NEED A FUNCTION TO DO THE DIFF CALCULATION AND ANOTHER TO RUN IT THROUGH
  # EACH DF
  # get boosted pidps
  # boosted <- df.list[[2]] %>%
  #   select(pidp, income_boosted) %>%
  #   filter(income_boosted == 'True')
  # rm(tmp)
  
  df.list <- mapply(single.mean, df.list, scen.list, SIMPLIFY = FALSE)
  
  combined <- df.list %>%
    reduce(full_join, by='time')
  
  # List of intervention columns
  int_cols <- grep("int\\d+.SF12", names(combined), value = TRUE)
  
  # Create the new dataframe with differences
  combined <- combined %>%
    mutate(across(all_of(int_cols), ~ . - base.SF12, .names = "diff{col}")) %>%
    select(time, starts_with("diff")) %>%
    rename_with(~ str_replace_all(., "diffint(\\d+).SF12", "diff\\1"))
  
  combined <- combined %>%
    pivot_longer(cols = starts_with('diff'),
                 names_to = 'scen',
                 values_to = 'diff')
  
  p1 <- ggplot(combined, aes(x = time, y = diff, group = scen, colour = scen)) +
    geom_line() +
    geom_hline(yintercept = 0, linetype='dashed') +
    labs(title = 'Relative change in SF12 MCS', subtitle = 'Treated Population') +
    xlab('Year') +
    ylab('Difference')
  
  print(p1)
}

SF12.change.treated.batch <- function(df.list, scen.list) {
  batch.mean <- function(data, scen) {
    # define varname
    newvar.name <- paste0(scen, '.SF12')
    # prepare data
    data <- data %>%
      select(time, boosted, run_id, SF_12) %>%
      filter(boosted == TRUE) %>%
      group_by(time, run_id) %>%
      summarise(!!sym(newvar.name) := mean(SF_12, na.rm =TRUE))
    return(data)
  }
  
  #TODO: FIX THIS! NEED DIFFERENT BASELINE FOR EACH INT?? THINK SO!
  # NEED A FUNCTION TO DO THE DIFF CALCULATION AND ANOTHER TO RUN IT THROUGH
  # EACH DF
  # get boosted pidps
  # boosted <- df.list[[2]] %>%
  #   select(pidp, income_boosted) %>%
  #   filter(income_boosted == 'True')
  
  df.list <- mapply(batch.mean, df.list, scen.list, SIMPLIFY = FALSE)
  
  combined <- df.list %>%
    reduce(full_join, by=c('time', 'run_id'))
  
  return(combined)
  
  # List of intervention columns
  int_cols <- grep("int\\d+.SF12", names(combined), value = TRUE)
  
  # Create the new dataframe with differences
  combined <- combined %>%
    mutate(across(all_of(int_cols), ~ . - base.SF12, .names = "diff{col}")) %>%
    select(time, starts_with("diff")) %>%
    rename_with(~ str_replace_all(., "diffint(\\d+).SF12", "diff\\1"))
  
  combined <- combined %>%
    pivot_longer(cols = starts_with('diff'),
                 names_to = 'scen',
                 values_to = 'diff')
  
  p1 <- ggplot(combined, aes(x = time, y = diff, group = scen, colour = scen)) +
    geom_smooth() +
    geom_hline(yintercept = 0, linetype='dashed') +
    labs(title = 'Relative change in SF12 MCS', subtitle = 'Treated Population') +
    xlab('Year') +
    ylab('Difference')
  
  print(p1)
}

SF12.by.simd.deciles <- function(df.list, scen.list, start.year = 2020, batch=FALSE) {
  single.mean <- function(data, scen, start.year) {
    newvar.name <- paste0(scen, '.SF12')
    data <- data %>%
      select(time, simd_decile, SF_12) %>%
      filter(time >= start.year) %>%
      group_by(time, simd_decile) %>%
      summarise(!!sym(newvar.name) := mean(SF_12, na.rm =TRUE))
    return(data)
  }
  batch.mean <- function(data, scen, start.year) {
    newvar.name <- paste0(scen, '.SF12')
    data <- data %>%
      select(time, simd_decile, run_id, SF_12) %>%
      filter(time >= start.year) %>%
      group_by(time, simd_decile, run_id) %>%
      summarise(!!sym(newvar.name) := mean(SF_12))
    return(data)
  }
  
  if (batch) {
    mod.list <- mapply(batch.mean, int.list, scen.list, start.year, SIMPLIFY = FALSE)
    combined <- mod.list %>%
      reduce(full_join, by=c('time', 'simd_decile', 'run_id'))
  } else {
    mod.list <- mapply(single.mean, int.list, scen.list, start.year, SIMPLIFY = FALSE)
    combined <- mod.list %>%
      reduce(full_join, by=c('time', 'simd_decile'))
  }
  
  combined$simd_decile <- as.factor(combined$simd_decile)
  
  int.labels <- scen.list[-1]
  
  for (int in int.labels) {
    int.name <- paste0(int, '.SF12')
    if (batch) {
      p1 <- ggplot(combined, aes(x = time, group = simd_decile, colour = simd_decile)) +
        geom_smooth(aes(y = base.SF12)) +
        geom_smooth(aes(y = .data[[int.name]]), linetype='dashed') +
        labs(title = 'SF12 MCS Deciles', subtitle = paste0('Baseline vs ', int)) +
        xlab('Year') +
        ylab('Difference')
    } else {
      p1 <- ggplot(combined, aes(x = time, group = simd_decile, colour = simd_decile)) +
        geom_line(aes(y = base.SF12)) +
        geom_line(aes(y = .data[[int.name]]), linetype='dashed') +
        labs(title = 'SF12 MCS Deciles', subtitle = int) +
        xlab('Year') +
        ylab('Difference')
    }
    print(p1)
  }
}

SF12.change.by.deciles <- function(df.list, scen.list, start.year = 2020, batch = FALSE) {
  single.mean <- function(data, scen, start.year) {
    newvar.name <- paste0(scen, '.SF12')
    data <- data %>%
      select(time, simd_decile, SF_12) %>%
      filter(time >= start.year) %>%
      group_by(time, simd_decile) %>%
      summarise(!!sym(newvar.name) := mean(SF_12, na.rm =TRUE))
    return(data)
  }
  batch.mean <- function(data, scen, start.year) {
    newvar.name <- paste0(scen, '.SF12')
    data <- data %>%
      select(time, simd_decile, run_id, SF_12) %>%
      filter(time >= start.year) %>%
      group_by(time, simd_decile, run_id) %>%
      summarise(!!sym(newvar.name) := mean(SF_12))
    return(data)
  }
  
  if (batch) {
    mod.list <- mapply(batch.mean, int.list, scen.list, start.year, SIMPLIFY = FALSE)
    combined <- mod.list %>%
      reduce(full_join, by=c('time', 'simd_decile', 'run_id'))
  } else {
    mod.list <- mapply(single.mean, int.list, scen.list, start.year, SIMPLIFY = FALSE)
    combined <- mod.list %>%
      reduce(full_join, by=c('time', 'simd_decile'))
  }
  
  combined$simd_decile <- as.factor(combined$simd_decile)
  
  # List of intervention columns
  int_cols <- grep("int\\d+.SF12", names(combined), value = TRUE)
  
  # Create the new dataframe with differences
  combined <- combined %>%
    mutate(across(all_of(int_cols), ~ . - base.SF12, .names = "diff{col}")) %>%
    select(time, simd_decile, starts_with("diff")) %>%
    rename_with(~ str_replace_all(., "diffint(\\d+).SF12", "diff\\1"))
  
  combined <- combined %>%
    pivot_longer(cols = starts_with('diff'),
                 names_to = 'scen',
                 values_to = 'diff')
  
  if (batch) {
    p1 <- ggplot(combined, aes(x = time, y = diff, group = simd_decile, colour = simd_decile)) +
      geom_smooth() +
      geom_hline(yintercept = 0, linetype='dashed') +
      facet_wrap(. ~ scen, ncol=1) +
      labs(title = 'Relative change in SF12 MCS', subtitle = 'Whole population') +
      xlab('Year') +
      ylab('Difference')
  } else {
    p1 <- ggplot(combined, aes(x = time, y = diff, group = simd_decile, colour = simd_decile)) +
      geom_line() +
      geom_hline(yintercept = 0, linetype='dashed') +
      facet_wrap(. ~ scen, ncol=1) +
      labs(title = 'Relative change in SF12 MCS', subtitle = 'Whole population') +
      xlab('Year') +
      ylab('Difference')
  }
  
  ggsave(filename = 'test_plot.png',
         plot = p1,
         path = here::here('plots', 'SCOTGOVWORK'),
         width = 9,
         height = 20)
  
  print(p1)
}

