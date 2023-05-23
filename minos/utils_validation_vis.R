## Validation plotting functions for MINOS



spaghetti_plot <- function(data, v)
{
  # spaghetti plot displaying trajectories over time for continuous variable v
  # data: list Some dataset to plot. Needs v, time and pidp variables.
  # v : some continuous variable to plot. 
  #TODO convert this to pure ggplot2 as with joint spaghetti plot below. Far more flexible and doesnt need stupid wide format conversion. 
  data_plot <- data[, c("time", "pidp", v)]
  output_plot <- ggplot(data_plot, aes(x = time, y = !!sym(v), group = pidp)) + 
    ggplot2::labs(x = "time", y = v) + 
    ggplot2::theme_classic() + 
    ggplot2::theme(text = ggplot2::element_text(size = 12)) + 
    ggplot2::scale_colour_viridis_d()+ 
    #ggplot2::geom_smooth(colour="blue") +
    ggplot2::geom_line(colour="blue", alpha=0.2) +
    ggplot2::geom_point()
  
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
  
  violin_long <- ggplot(data, aes_string(x = 'time', y = v)) +
    geom_violin() +
    geom_boxplot(width = 0.1, outlier.colour = "blue") +
    theme_classic() + 
    scale_y_continuous(limits = quantile(data[, c(v)], c(0.001, 0.999), na.rm =TRUE))
  return(violin_long)
}

