library(geepack)
library(lme4)
library(MuMIn)
library(ggridges)
library(ggplot2)
library(car) # levene test
library(texreg) # model outputs to tex tables. 
library(strucchange) # CHOW TEST
library(car) # levene test
library(viridis)
#library(tidyr) # for extract

#leveneTest(y~factor(time), data=data)kai
#leveneTest(y~factor(pidp), data=data)

source("papers/phd1/paper_plots.R")


main <- function(){
  load('papers/phd1/data/mice_pidps.RData')
  load('papers/phd1/data/mice_data.RData')
  load('papers/phd1/data/baseline_OLS.RData')
  load('papers/phd1/data/mice_lm_object.RData')
  data2 <- mice.data
  data2$pidp <- pidps
  #leveneTest(y~factor(time), data=data2)
  #leveneTest(y~factor(pidp), data=data2)
  
  sf12.lm.oneterm <- lm(y ~ sex + 
                          ethnicity + 
                          age + 
                          education_state + 
                          labour_state + 
                          job_sec +
                          region +
                          scale(hh_income) + 
                          SF_12, data=data2)
  
  print(AIC(sf12.lm.oneterm))
  #pdf("papers/phd1/plots/ols_oneterm_densities.pdf")
  #compare_densities_plot(predict(sf12.lm.oneterm), data2$y, "SF_12")
  #dev.off()
  
  dep.gee <- geeglm(y ~ sex + 
                      ethnicity + 
                      age + 
                      education_state + 
                      labour_state + 
                      job_sec +
                      region +
                      scale(hh_income) + 1:time , data = data2[with(data2, order(pidp, time)), ], family = gaussian, id=pidp
                    , corstr="ar1")
  
  gee.preds <- predict(dep.gee, data2)
  print(summary(dep.gee))
  #print(QIC(dep.gee))
  
  dep.glmm <- lmer(y ~ sex + 
                     ethnicity + 
                     age + 
                     education_state + 
                     labour_state + 
                     job_sec +
                     region +
                     scale(hh_income) +
                     (1|pidp), data = data2)
  
  glmm.sum <- summary(dep.glmm)
  print(glmm.sum)
  print(AIC(dep.glmm))
  #r.squaredGLMM(dep.glmm)
  
  #glmm.preds <- predict(dep.glmm)
  #pdf("papers/ph1/plots/glmm_densities.pdf")
  #compare_densities_plot(glmm.preds, data2$y, "SF_12")
  #dev.off()
  
  max_sf12 <- max(data2$y)
  dep.glmm.gamma <- glmer(max_sf12 - y + 0.001  ~
                            sex + 
                            ethnicity + 
                            age + 
                            education_state + 
                            labour_state + 
                            job_sec +
                            region +
                            scale(hh_income) +
                            (1|pidp),  nAGQ=0, family=Gamma(link='log'), data = data2)
  #r.squaredGLMM(dep.glmm.gamma)
  
  glmm.gamma.sum <- summary(dep.glmm.gamma)
  print(glmm.gamma.sum)
  print(AIC(dep.glmm.gamma))
  #r.squaredGLMM(dep.glmm.gamma)
  glmm.gamma.preds <- predict(dep.glmm.gamma, type='response')
  glmm.gamma.preds <- max_sf12 - glmm.gamma.preds
  
  #pdf("papers/ph1/plots/glmm_gamma_densities.pdf")
  #compare_densities_plot(glmm.gamma.preds, data2$y, "SF_12")
  #dev.off()
  
  texreg.onemore <- sf12.lm.oneterm
  texreg.gee <- texreg::extract(dep.gee)
  texreg.glmm <- texreg::extract(dep.glmm)
  texreg.glmm.gamma <- texreg::extract(dep.glmm.gamma)
  texreg.glmm.gamma@coef <- exp(-texreg.glmm.gamma@coef)
  
  # texreg(list(texreg.onemore, texreg.gee, texreg.glmm, texreg.glmm.gamma), dcolumn=T, booktabs=T, file='papers/ph1/plots/heterogeneity_coefficients.txt', title="SF12 Heterogeneity Coefficients", custom.model.names=c("OLS + Oneterm", "GEE", "GLMM", "GLMM Gamma"), single.row=T)
  texreg(list(sf12.lm, mice.lm.object, texreg.onemore, texreg.gee, texreg.glmm, texreg.glmm.gamma), 
         dcolumn=T, 
         booktabs=T,
         file='papers/phd1/data/combined_coefficients.txt', 
         title="SF12 All Coefficients", 
         custom.model.names=c("OLS", "MICE OLS", "OLS + Oneterm", "GEE", "GLMM", "GLMM Gamma"), 
         single.row=T, 
         leading.zero=F)
  
  fit.objects <- list(data2$SF_12, predict(sf12.lm), predict(sf12.lm.oneterm, data2),
                      predict(dep.gee, data2), predict(dep.glmm, data2), max_sf12 - predict(dep.glmm.gamma, data2, type='response'))
  names <- list("Real", "OLS", "OLS + Oneterm", "GEE", "GLMM", "GLMM Gamma")
  density.data <- c()
  
  for (i in seq(length(fit.objects))){
    new_densities <- as.data.frame(fit.objects[i])
    new_densities$type <- c(names[i])
    colnames(new_densities) <- c("SF_12", "Model")
    density.data <- rbind(density.data, new_densities)
  }
  density.data <- as.data.frame(lapply(density.data, unlist))
  # !! notation allows for general argument v. see aes_string deprecation note.
  ols.densities <- ggplot(density.data, aes(x=SF_12, y=Model, fill=Model, color=Model, lty=Model)) +
    geom_density_ridges_gradient(scale=3, rel_min_height = 0.0001, gradient_lwd = 1)  +
    xlim(20, 70) +
    scale_fill_viridis_d(name = 'Model', alpha=0.7) +
    scale_color_grey(start=1, end=0)
  #scale_color_manual(values = viridis::viridis(n = length(fit.objects), alpha=0.4)) # cividis colours
  ols.densities
  pdf('papers/phd1/plots/combined_sf12_densities.pdf') 
  print(ols.densities)
  dev.off()
  
  
  residual.objects <- list(rnorm(500000), 
                           scale(residuals(sf12.lm)), 
                           #scale(residuals(pooled_lm)), 
                           scale(residuals(sf12.lm.oneterm)),
                           scale(residuals(dep.gee)), 
                           scale(residuals(dep.glmm)), scale(max(data2$y)- residuals(dep.glmm.gamma, type='response')))
  residual.names <- list("Normal", "OLS", "OLS + Oneterm", "GEE", "GLMM", "GLMM Gamma")
  
  residual.data <- c()
  for (i in seq(length(residual.objects))){
    new_residuals <- as.data.frame(residual.objects[i])
    new_residuals$type <- c(residual.names[i])
    colnames(new_residuals) <- c("SF_12", "Model")
    residual.data <- rbind(residual.data, new_residuals)
  }
  
  residual.data <- as.data.frame(lapply(residual.data, unlist))
  residual.data <- residual.data[complete.cases(residual.data), ]
  # !! notation allows for general argument v. see aes_string deprecation note.
  residual.densities <- ggplot(residual.data, aes(x=SF_12, y=Model, fill=Model, color=Model, lty=Model)) +
    geom_density_ridges_gradient(scale=3, rel_min_height = 0.001, gradient_lwd = 1)  +
    scale_fill_viridis_d(name = 'Model', alpha=0.7) +
    scale_color_grey(start=1, end=0) +
    xlim(-4, 4)
  #scale_color_manual(values = viridis::viridis(n = length(fit.objects), alpha=0.4)) # cividis colours
  residual.densities
  pdf('papers/phd1/plots/combined_sf12_residuals.pdf') 
  print(residual.densities)
  dev.off()
  
  dep.glmm.gamma@beta <- -dep.glmm.gamma@beta
  forest_plot(dep.glmm.gamma, "papers/phd1/plots/glmm_gamma_forest.pdf", c(0.77, 1.11))
  qq_plot(resid(dep.glmm.gamma), "papers/phd1/plots/glmm_gamma_qq.pdf")
  residual_density_plot(res=resid(dep.glmm.gamma), file_name="papers/phd1/plots/glmm_gamma_residual_density.pdf", guide="normal")
  
  squareRootRes <- sqrt(abs(scale(resid(dep.glmm.gamma))))
  fitted_residuals <- as.data.frame(cbind(fitted(dep.glmm.gamma), squareRootRes))
  colnames(fitted_residuals) <- c("fitted", "sqrt_residuals")
  fitted_residual_plot(fitted_residuals, 'papers/phd1/plots/glmm_gamma_fitted_residual_plot.pdf')
  
}

main()