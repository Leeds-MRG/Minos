library(sjPlot)
library(ggplot2)
library(ggpattern)

main <- function(){
  load("papers/phd1/data/baseline_OLS.RData")
  load("papers/phd1/data/baseline_OLS_data.RData")
  
  
  pdf("papers/phd1/plots/ols_residuals.pdf")
  hist(scale(a$residuals), ylab = "Density", breaks = 100, freq=F, main = '', xlab = 'SF12 Scaled Residuals')
  lines(seq(-4, 4, 1/1000), dnorm(seq(-4, 4, 1/1000)), col='red', lty=2)
  legend('topleft', col='red', lty=2, legend=c('Standard Normal'))
  dev.off()
  
  #pdf("../plots/ols_forest_plot.pdf")
  #plot_summs(sf12.lm)
  #dev.off()
  
  pdf("papers/phd1/plots/ols_forest_plot.pdf")
  print(plot_models(sf12.lm, p.shape=T, legend.title = NULL, m.labels=NULL))
  dev.off()
  
  
  hist(scale(sf12.lm$residuals), col = blue)
  hist(scale(data$SF_12), col=orange, add=T)
  
  hist(scale(sf12.lm$residuals), col = blue, alpha=0.7)
  hist(scale(data$SF_12), col=orange, add=T, alpha=0.7)
  legend('topleft', legend=c("Predicted", "Actual"), col=c(blue, orange), lty=1)
  
  res <- as.data.frame(sf12.lm$fitted)
  real <- as.data.frame(data$SF_12)
  res$type <- c("Predicted")
  real$type <- c("Real")
  colnames(res) <- c("SF12", 'type')
  colnames(real) <- c("SF12", 'type')
  hist.data <- rbind(res,real)
  
  ols.hist <- ggplot(hist.data, aes(x=SF12, fill = type, col=type)) +
    geom_histogram(aes(y=..density..), alpha=0.5, binwidth=2, position='identity')
  
  ols.densities <- ggplot(hist.data) +
    geom_density_pattern(aes(x=SF12, pattern_fill = as.factor(type), pattern_type = as.factor(type)),
                         alpha=0.1,
                         pattern = 'polygon_tiling',
                         pattern_key_scale_factor = 1.2,
                         pattern_alpha=0.4)+        
    scale_pattern_type_manual(values = c("hexagonal", "rhombille"))+
    theme_bw(18) +
    theme(legend.key.size = unit(2, 'cm'))
  
  pdf("papers/phd1/plots/ols_densities.pdf")
  ols.densities
  dev.off()
  
  pdf("papers/phd1/plots/ols_fitted_residuals.pdf")
  plot(sf12.lm, 3)
  dev.off()
  
  pdf("papers/phd1/plots/ols_sf12_leverage.pdf")
  plot(sf12.lm, 5)
  dev.off()
  
  pdf("papers/phd1/plots/ols_sf12_qqplot.pdf")
  plot(sf12.lm, 2)
  dev.off()
  
  texreg(summary(sf12.lm), dcolumn=T, booktabs=T, file="papers/phd1/ols_output.txt", title="SF12 OLS Coefficients", custom.model.names=c("SF12 OLS"), single.row=T, include.aic=T)
}

main()