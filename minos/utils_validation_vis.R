## Validation plotting functions for MINOS
require(ggplot2)
require(ggridges)
require(viridis)

miss.values <- c(-10, -9, -8, -7, -3, -2, -1,
                 -10., -9., -8., -7., -3., -2., -1.)

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

density_ridges <- function(data, v, save=FALSE, save.path=NULL, filename.tag=NULL)
{
  data_plot <- data[, c("time", v)]
  # Remove missing values
  data_plot <- data_plot %>%
    filter(!data_plot[[v]] %in% miss.values)
  if (min(data_plot$time) < 2020) {
    handover <- TRUE
  }
  
  data_plot$time <- factor(data_plot$time)
  data_plot <- data_plot[order(data_plot$time),]
  output_plot <- ggplot(data_plot, aes(x=!!sym(v), y=time)) +
                 geom_density_ridges(aes(y=time, color=time, linetype=time), alpha=0.6) +
                 #scale_color_viridis_d() +
                 scale_color_cyclical(values=c("#F8766D", "#00BA38","#619CFF")) +
                 scale_linetype_cyclical(values=c(1, 2, 3))
  
  if(save) {
    if(is.null(save.path)) {
      stop('ERROR: save.path must be defined when saving the plot')
    }
    # add handover to filename if handover
    if (handover) {
      save.filename <- paste0('density_ridges_handover_', v, '.png')
    } else {
      save.filename <- paste0('density_ridges_output_', v, '.png')
    }
    # add tag to filename if provided
    if (!is.null(filename.tag)) {
      save.filename <- paste0(filename.tag, '_', save.filename)
    }
    
    ggsave(filename = save.filename,
           plot = output_plot,
           path = save.path)
  }
  return(output_plot)
}
