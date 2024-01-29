library(ggplot2)


# forest plot for lm models. 
forest_plot_lm <- function(model, file_name){
  
  sf12_coefs <- summary(model)$coefficients
  sf12_coefs <- cbind(sf12_coefs, sf12_coefs[, 4])
  colnames(sf12_coefs)[5] <- "p.stars"
  what_ns <- which(sf12_coefs[, "Pr(>|t|)"] > 0.05)
  what_one_star <- which(sf12_coefs[, "Pr(>|t|)"] <= 0.05)
  what_two_star <- which(sf12_coefs[, "Pr(>|t|)"] <= 0.01)
  what_three_star <- which(sf12_coefs[, "Pr(>|t|)"] <= 0.001)
  
  sf12_coefs[what_ns, 'p.stars'] <- ""
  sf12_coefs[what_one_star, 'p.stars'] <- "*"
  sf12_coefs[what_two_star, 'p.stars'] <- "**"
  sf12_coefs[what_three_star, 'p.stars'] <- "***"
  p.stars<- sf12_coefs[, 5]
  
  pdf(file_name)
  p <- plot_model(model, transform=NULL,
                  title = "") + aes(shape=p.stars)
  p$data$p.stars[which(p$data$p.stars == "")] <- 'n.s.'
  p <- p +  scale_shape_manual(name='Significance Level',
                               limits=c("n.s.", "*", "**", "***"),
                               breaks=c("n.s.", "*", "**", "***"),
                               values=c(1, 16, 17, 15)) # cast legend to certain title, variable names and shapes.
  plot(p)
  dev.off()
}



# for glmm gamma
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