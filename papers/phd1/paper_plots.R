library(ggplot2)


forest_plot <- function(model, file_name, limits=NULL){
  pdf(file_name)
  p <- plot_model(model,
                  title = "") + aes(shape=p.stars)
  p$data$p.stars[p$data$p.stars == ""] <- "n.s." # force empty shape strings to n.s. so they show up in legend.
  p <- p +  scale_shape_manual(name='Significance Level',
                               breaks=c('n.s.', "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  if (!is.null(limits)){
    p <- p + scale_y_log10(limits = limits)
  }
  plot(p)
  dev.off()
}

residual_density_plot <- function(res, file_name, guide=NULL){
  # res - residuals of plotted model
  # guide - expected residual distribution. usually standard normal. 
  pdf(file_name)
  hist(scale(res), breaks=1000, freq=F)
  if (guide=="normal"){
    x <- seq(-4, 4, 1/10000) # reference normal line in red.
    lines(x, dnorm(x), col='red')
  }
  dev.off()
  print("saved residual density plot to")
  print(file_name)
}


qq_plot <- function(res, file_name){
  pdf(file_name)
  print(qqnorm(scale(res)))
  print(qqline(scale(res)))
  dev.off()
  print("saved qq plot to")
  print(file_name)
}

fitted_residual_plot <- function(fitted_residuals, file_name){
  residual_fitted_plot <- ggplot(fitted_residuals, aes(fitted, sqrt_residuals)) +
    geom_point(shape=1) +
    geom_smooth(colour="red") +
    #geom_line(aes(y=rollmean(sqrt_residuals, 10000, na.pad=TRUE)), col='red') +
    theme_bw()
  pdf(file_name)
  print(residual_fitted_plot)
  dev.off()
  print("saved fitted-residual plot to")
  print(file_name)
}