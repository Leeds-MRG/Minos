## Validation plotting functions for MINOS

require(ggplot2)
require(ggExtra)
require(here)
require(scales)

miss.values <- c(-10, -9, -8, -7, -3, -2, -1,
                 -10., -9., -8., -7., -3., -2., -1.)

############ PREP ############

validation_prep_ordinal <- function(raw.dat, base.dat, var) {
  raw <- raw.dat %>%
    dplyr::select(pidp, time, all_of(var)) %>%
    group_by(time, .data[[var]]) %>%
    count() %>%
    mutate(source = 'US')
  
  base <- base.dat %>%
    dplyr::select(pidp, time, all_of(var)) %>%
    group_by(time, .data[[var]]) %>%
    count() %>%
    mutate(source = 'baseline_output')
  
  combined <- rbind(raw, base)
  combined[[var]] <- as.factor(combined[[var]])
  
  var.norm <- combined %>%
    group_by(time) %>%
    filter(.data[[var]] != -9) %>%
    mutate(total = sum(n)) %>%
    mutate(prct = (n / total))
  
  prepped <- list(var = combined,
                  norm = var.norm)
  
  return(prepped)
}

############ PLOTTING ############

spaghetti_plot <- function(data, v, save=FALSE, save.path=NULL, filename.tag=NULL)
{
  # spaghetti plot displaying trajectories over time for continuous variable v
  # data: list Some dataset to plot. Needs v, time and pidp variables.
  # v : some continuous variable to plot. 
  # save : whether to save the plot
  # save.path : path to save plot at, must be defined if save == TRUE
  
  #TODO convert this to pure ggplot2 as with joint spaghetti plot below. Far more flexible and doesnt need stupid wide format conversion. 
  data_plot <- data[, c("time", "pidp", v)]
  # Remove missing values
  data_plot <- data_plot %>%
    filter(!.data[[v]] %in% miss.values)
  
  # get range of years to figure out if this is handover or not
  if (min(data_plot$time) < 2020) {
    handover <- TRUE
  }
  
  output_plot <- ggplot(data_plot, aes(x = time, y = !!sym(v), group = pidp)) + 
    ggplot2::labs(x = "time", y = v) + 
    ggplot2::theme_classic() + 
    ggplot2::theme(text = ggplot2::element_text(size = 12)) + 
    ggplot2::scale_colour_viridis_d()+ 
    #ggplot2::geom_smooth(colour="blue") +
    ggplot2::geom_line(colour="blue", alpha=0.2) +
    ggplot2::geom_point()
  
  if(save) {
    if(is.null(save.path)) {
      stop('ERROR: save.path must be defined when saving the plot')
    }
    # add handover to filename if handover
    if (handover) {
      save.filename <- paste0('spaghetti_handover_', v, '.png')
    } else {
      save.filename <- paste0('spaghetti_output_', v, '.png')
    }
    # add tag to filename if provided
    if (!is.null(filename.tag)) {
      save.filename <- paste0(filename.tag, '_', save.filename)
    }
    
    ggsave(filename = save.filename,
           plot = output_plot,
           path = save.path)
  }
  
  return (output_plot)
}


violin_plot <- function(data, v)
{
  # plot violins (similar to boxplots) over time for continuous variable v
  # data: list Some dataset to plot. Needs v, time and pidp variables.
  # v : some continuous variable to plot. 
  data <- data[, c("time", "pidp", v)]
  data <- data[order(data$pidp, data$time),]
  data$time <- factor(data$time)
  data <- data %>%
    filter(!.data[[v]] %in% miss.values)
  
  violin_long <- ggplot(data, aes_string(x = 'time', y = v)) +
    geom_violin() +
    geom_boxplot(width = 0.1, outlier.colour = "blue") +
    theme_classic() + 
    scale_y_continuous(limits = quantile(data[, c(v)], c(0.001, 0.999), na.rm =TRUE))
  return(violin_long)
}

# 
marg_dist_densigram_plot_oneyear <- function(observed, 
                                             predicted,
                                             var,
                                             target.year = 2020,
                                             save = FALSE,
                                             save.path = here::here('plots')) {
  # get just one year
  o.end <- observed %>% filter(time == target.year, .data[[var]] != -8.0)
  p.end <- predicted %>% filter(time == target.year, .data[[var]] != -8.0)
  # get just the SF12 columns and rename for later
  o.end <- o.end %>% select(pidp, all_of(var)) %>% rename(observed = var)
  p.end <- p.end %>% select(pidp, all_of(var)) %>% rename(predicted = var)
  
  # combine before we plot
  combined <- merge(o.end, p.end, by = 'pidp')
  
  if (var %in% c('hh_income', 'equivalent_income')) {
    # do inverse hyperbolic sine transformation for hh_income
    asinh_trans <- scales::trans_new(
      "inverse_hyperbolic_sine",
      transform = function(x) {asinh(x)},
      inverse = function(x) {sinh(x)}
    )
    
    p <- ggplot(data = combined, aes(x = observed, y = predicted)) +
      geom_point(alpha = 0.6, size=0.1) +
      geom_smooth() +
      scale_y_continuous(trans=asinh_trans) +
      scale_x_continuous(trans=asinh_trans) +
      geom_abline(intercept = 0) +
      stat_ellipse(color = 'red') +
      theme(legend.position = c(0.15, 0.9)) +
      labs(title = paste0(var, ' - ', target.year),
           subtitle = 'Marginal Distributions - Inverse Hyperbolic Sine transformation')
  } else {
    # no transformation for other vars
    p <- ggplot(data = combined, aes(x = observed, y = predicted)) +
      geom_point(alpha = 0.6, size=0.1) +
      geom_smooth() +
      geom_abline(intercept = 0) +
      stat_ellipse(color = 'red') +
      theme(legend.position = c(0.15, 0.9)) +
      labs(title = paste0(var, ' - ', target.year),
           subtitle = 'Marginal Distributions')
  }
  
  p1 <- ggMarginal(p, type='densigram', xparams = list(position = 'dodge'), yparams=list(position = 'dodge'))
  
  plot.name <- paste0('scatter_marg_densigram_', var, '_', target.year, '.png')
  
  if(save) {
    ggsave(filename = plot.name,
           plot = p1,
           path = save.path)
  }
  return(p1)
}

cv.mean.plots <- function(cv1, cv2, cv3, cv4, cv5, raw, var) {
  cv1.inc <- cv1 %>%
    filter(.data[[var]] != -9) %>%
    group_by(time) %>%
    summarise(mean.var = mean(.data[[var]], na.rm = TRUE))
  cv1.inc$source <- 'cv1'
  cv1.inc$mode <- 'cross-validation'
  cv2.inc <- cv2 %>%
    filter(.data[[var]] != -9) %>%
    group_by(time) %>%
    summarise(mean.var = mean(.data[[var]], na.rm = TRUE))
  cv2.inc$source <- 'cv2'
  cv2.inc$mode <- 'cross-validation'
  cv3.inc <- cv3 %>%
    filter(.data[[var]] != -9) %>%
    group_by(time) %>%
    summarise(mean.var = mean(.data[[var]], na.rm = TRUE))
  cv3.inc$source <- 'cv3'
  cv3.inc$mode <- 'cross-validation'
  cv4.inc <- cv4 %>%
    filter(.data[[var]] != -9) %>%
    group_by(time) %>%
    summarise(mean.var = mean(.data[[var]], na.rm = TRUE))
  cv4.inc$source <- 'cv4'
  cv4.inc$mode <- 'cross-validation'
  cv5.inc <- cv5 %>%
    filter(.data[[var]] != -9) %>%
    group_by(time) %>%
    summarise(mean.var = mean(.data[[var]], na.rm = TRUE))
  cv5.inc$source <- 'cv5'
  cv5.inc$mode <- 'cross-validation'
  
  raw.inc <- raw %>%
    filter(.data[[var]] != -9) %>%
    group_by(time) %>%
    summarise(mean.var = mean(.data[[var]], na.rm = TRUE))
  raw.inc$source <- 'raw'
  raw.inc$mode <- 'raw'
  
  cv.list <- list(cv1.inc, cv2.inc, cv3.inc, cv4.inc, cv5.inc)
  cv.inc <- do.call(rbind, cv.list)
  
  df.list <- list(cv.inc, raw.inc)
  combined <- do.call(rbind, df.list)
  
  # First plot all cv runs separately
  p1 <- ggplot(combined, aes(x = time, y = mean.var, group = source, color = source, linetype = mode)) +
    geom_line() +
    labs(title = paste0(var, ': CV vs raw'), subtitle = 'Individual CV runs') +
    ylab(var)
  print(p1)
  
  cv.inc2 <- cv.inc %>%
    group_by(time) %>%
    summarise(var = mean(mean.var),
              min = min(mean.var),
              max = max(mean.var))
  cv.inc2$source <- 'cross-validation'
  
  raw.inc <- raw.inc %>%
    select(-mode) %>%
    mutate(var = mean.var,
           min = mean.var,
           max = mean.var) %>%
    select(-mean.var)
  
  combined2 <- rbind(cv.inc2, raw.inc)
  
  p2 <- ggplot(combined2, aes(x = time, y = var, group = source, color = source)) +
    geom_line() +
    geom_ribbon(aes(ymin = min, ymax = max, fill = source), 
                alpha = 0.1,
                linetype = 'dashed') +
    labs(title = paste0(var, ': CV vs raw'), subtitle = 'Combined CV runs') +
    ylab(var)
  print(p2)
}

snapshot_OP_plots <- function(raw, cv, var, target.years) {
  cv.snap <- cv %>%
    select(pidp, time, all_of(var)) %>%
    filter(time %in% target.years) %>%
    rename(predicted = .data[[var]])
  
  raw.snap <- raw %>%
    select(pidp, time, all_of(var)) %>%
    filter(time %in% target.years) %>%
    rename(observed = .data[[var]])
  
  snap <- merge(cv.snap, raw.snap,
                by = c('pidp', 'time'))
  
  if (var %in% c('hh_income', 'equivalent_income')) {
    asinh_trans <- scales::trans_new(
      "inverse_hyperbolic_sine",
      transform = function(x) {asinh(x)},
      inverse = function(x) {sinh(x)}
    )
    
    ggplot(snap, aes(x = observed, y = predicted)) +
      geom_point() +
      scale_y_continuous(trans=asinh_trans) +
      scale_x_continuous(trans=asinh_trans) +
      geom_abline(slope=1, intercept=0) +
      stat_ellipse(color='red') +
      facet_wrap(~time) +
      labs(title = paste0(var, ': observed vs predicted'),
           subtitle = 'Inverse Hyperbolic Sine transformation')
  } else {
    ggplot(snap, aes(x = observed, y = predicted)) +
      geom_point() +
      geom_abline(slope=1, intercept=0) +
      stat_ellipse(color='red') +
      facet_wrap(~time) +
      labs(title = paste0(var, ': observed vs predicted'))
  }
}


## Yearly box plots for multiple years, compared between raw and cv runs
multi_year_boxplots <- function(raw, cv, var) {
  raw.var <- raw %>%
    dplyr::select(pidp, time, all_of(var))
  raw.var$source <- 'raw'
  
  cv.var <- cv %>%
    dplyr::select(pidp, time, all_of(var))
  cv.var$source <- 'cross-validation'
  
  combined <- rbind(raw.var, cv.var)
  combined$time <- as.factor(combined$time)
  combined <- drop_na(combined)
  combined <- filter(combined, .data[[var]] != -9)
  
  if (var %in% c('hh_income', 'equivalent_income')) {
    combined <- filter(combined, .data[[var]] < quantile(.data[[var]], 0.99), .data[[var]] > quantile(.data[[var]], 0.01))
  } else if (var == 'ncigs') {
    #combined <- filter(combined, .data[[var]] < quantile(.data[[var]], 0.99))
    combined <- filter(combined, .data[[var]] < quantile(.data[[var]], 0.99), !.data[[var]] == 0)
  }
  
  ggplot(data = combined, aes(x = time, y = .data[[var]], group = interaction(time, source), color = source)) +
    geom_boxplot(notch=TRUE) +
    labs(title = paste0(var, ': Yearly box plots'))
}

q_q_comparison <- function(raw, cv, var) {
  raw.inc <- raw %>%
    select(pidp, time, any_of(var))
  raw.inc$source <- 'raw'
  cv.inc <- cv %>%
    select(pidp, time, any_of(var))
  cv.inc$source <- 'cross-validation'
  
  combined <- rbind(raw.inc, cv.inc)
  combined <- filter(combined, .data[[var]] != -9)
  
  if (var == 'ncigs') {
    print('Removing ncigs == 0 values for this plot')
    combined <- filter(combined, .data[[var]] != 0)
  }
  
  ggplot(combined, aes(sample = .data[[var]], group = source, color = source)) +
    stat_qq() +
    labs(title = paste0(var, ': Q-Q'))
}

