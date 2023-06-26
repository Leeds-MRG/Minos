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
  o.end <- o.end %>% select(pidp, .data[[var]]) %>% rename(observed = var)
  p.end <- p.end %>% select(pidp, .data[[var]]) %>% rename(predicted = var)
  
  # combine before we plot
  combined <- merge(o.end, p.end, by = 'pidp')
  
  if (var == 'hh_income') {
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
      geom_abline(intercept = 0, scale=1) +
      stat_ellipse(color = 'red') +
      theme(legend.position = c(0.15, 0.9)) +
      labs(title = paste0(var, ' - ', target.year))
  } else {
    # no transformation for other vars
    p <- ggplot(data = combined, aes(x = observed, y = predicted)) +
      geom_point(alpha = 0.6, size=0.1) +
      geom_smooth() +
      geom_abline(intercept = 0, scale=1) +
      stat_ellipse(color = 'red') +
      theme(legend.position = c(0.15, 0.9)) +
      labs(title = paste0(var, ' - ', target.year))
  }
  
  p1 <- ggMarginal(p, type='densigram', xparams = list(position = 'dodge'), yparams=list(position = 'dodge'))
  
  
  plot.name <- paste0('scatter_marg_densigram_', var, '_', target.year, '.png')
  
  if(save) {
    ggsave(filename = plot.name,
           plot = p1,
           path = save.path)
  }
  
  #print(p1)
  
  return(p1)
}
