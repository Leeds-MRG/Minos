library(sjPlot)
library(ggplot2)
library(ggpattern)
source("papers/phd1/paper_plots.R")

main <- function(){
  load("papers/phd1/data/baseline_OLS.RData")
  load("papers/phd1/data/baseline_OLS_data.RData")
  
  #hist(scale(sf12.lm$residuals), col = blue)
  #hist(scale(data$SF_12), col=orange, add=T)
  
  #hist(scale(sf12.lm$residuals), col = blue, alpha=0.7)
  #hist(scale(data$SF_12), col=orange, add=T, alpha=0.7)
  #legend('topleft', legend=c("Predicted", "Actual"), col=c(blue, orange), lty=1)
  
  #res <- as.data.frame(sf12.lm$fitted)
  #real <- as.data.frame(data$SF_12)
  #res$type <- c("Predicted")
  #real$type <- c("Real")
  #colnames(res) <- c("SF12", 'type')
  #colnames(real) <- c("SF12", 'type')
  #hist.data <- rbind(res,real)
  
  #ols.hist <- ggplot(hist.data, aes(x=SF12, fill = type, col=type)) +
  #  geom_histogram(aes(y=..density..), alpha=0.5, binwidth=2, position='identity')
  
  #ols.densities <- ggplot(hist.data) +
    #geom_density_pattern(aes(x=SF12, pattern_fill = as.factor(type), pattern_type = as.factor(type)),
    #                     alpha=0.1,
    #                     pattern = 'polygon_tiling',
    #                     pattern_key_scale_factor = 1.2,
    #                     pattern_alpha=0.4)+        
    #scale_pattern_type_manual(values = c("hexagonal", "rhombille"))+
    #theme_bw(18) +
    #theme(legend.key.size = unit(2, 'cm'))
  
  forest_plot(sf12.lm, "papers/phd1/plots/presentation_forest.pdf", c(0.77, 1.11))
  qq_plot(resid(sf12.lm), "papers/phd1/plots/presentation_qq.pdf")
  residual_density_plot(res=resid(sf12.lm), file_name="papers/phd1/plots/presentation_residual_density.pdf", guide="normal")
  
  squareRootRes <- sqrt(abs(scale(resid(sf12.lm))))
  fitted_residuals <- as.data.frame(cbind(fitted(sf12.lm), squareRootRes))
  colnames(fitted_residuals) <- c("fitted", "sqrt_residuals")
  fitted_residual_plot(fitted_residuals, 'papers/phd1/plots/presentation_fitted_residual_plot.pdf')
  
  texreg(summary(sf12.lm), dcolumn=T, booktabs=T, file="papers/phd1/ols_output.txt", title="SF12 OLS Coefficients", custom.model.names=c("SF12 OLS"), single.row=T, include.aic=T)
}

main()