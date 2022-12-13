library(broom.mixed) # broom.mixed mice and glmer integration. 
library(lme4) # glmer
library(MuMIn) # glmm gamma
library(ggridges) # see ggridges function.
library(ggplot2) # plots
library(texreg) # model outputs to tex tables. 
library(viridis) # pretty colours
library(mice) # mice
library(zoo) # rollmean
library(sjPlot)
source("papers/phd1/paper_plots.R")

main <- function(){
  
  
  # combine them all together
  # glmm gamma using MICE
  # glmm gamma using weights (using shortened coefficients?)
  # glmm gamma with presentation plots.
  
  load('papers/phd1/data/mice_pidps.RData')
  load('papers/phd1/data/mice_data.RData')
  load('papers/phd1/data/mice_set.RData')
  data2 <- mice.data
  load('papers/phd1/data/mice_weights.RData')
  max_sf12 <- max(data2$y)
  
  glmm.gamma.mice.set <- with(data = mice_set, exp = lme4::glmer((max_sf12 - y + 2)/0.9  ~
                                                                   sex + 
                                                                   ethnicity + 
                                                                   age + 
                                                                   education_state + 
                                                                   labour_state + 
                                                                   job_sec +
                                                                   region +
                                                                   scale(hh_income) +
                                                                   I(scale(hh_income)**2) +
                                                                   factor(time) +
                                                                   (1|pidp),  nAGQ=0, family=Gamma(link='log'), 
                                                                 weights = mice.weights))
  
  #gamma.final.pool <- pool(glmm.gamma.mice.set)
  #predlist <- lapply(glmm.gamma.mice.set$analysis, broom::augment.xxx, se.fit = TRUE, …)
  #predmat <- pool(predlist, …)
  predlist <- lapply(glmm.gamma.mice.set$analyses, predict, type='response')
  predlist <- do.call(cbind, predlist)
  preds <- rowMeans(predlist)
  preds <- max_sf12 - 2 - preds
  
  
  fittedlist <- lapply(glmm.gamma.mice.set$analyses, fitted)
  fittedlist <- do.call(cbind, fittedlist)
  fitted <- rowMeans(fittedlist)
  fitted <- max_sf12 - 2 - fitted
  
  reslist <- lapply(glmm.gamma.mice.set$analyses, residuals, type='working')
  reslist <- do.call(cbind, reslist)
  res <- rowMeans(reslist)
  #res <- res[res != 0]
  #res <- data2$y - fitted
  
  squareRootRes <- sqrt(abs(scale(res)))
  fitted_residuals <- as.data.frame(cbind(fitted, squareRootRes))
  colnames(fitted_residuals) <- c("fitted", "sqrt_residuals")
  fitted_residual_plot(fitted_residuals, 'papers/phd1/plots/combined_glmm_gamma_fitted_residual_plot.pdf')
  
  # need a forest plot with a pseudo gamma object. 
  # get one of analyses and replace its coefs and SEs with those from final pool estimate.
  # get pool of estimates. 
  # get some copy of a glmm object. 
  final_pool <- pool(glmm.gamma.mice.set)
  glmer_plot_object <- glmm.gamma.mice.set$analyses[[1]]
  glmer_plot_object@beta <- -final_pool$pooled$estimate # flip coefficient signs.
  
  file_name <- "papers/phd1/plots/combined_glmm_gamma_forest.pdf"
  limits <-  c(0.77, 1.11)
  forest_plot(glmer_plot_object, file_name, limits)
  # residual/predicted density plot too. 
  
  residual_density_plot(res, "papers/phd1/plots/combined_residual_density.pdf", 'normal')
  qq_plot(res, "papers/phd1/plots/final_glmm_gamma_qqplot.pdf")
}

main()