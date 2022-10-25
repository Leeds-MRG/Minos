library(geepack)
library(lme4)
library(MuMIn)
library(ggridges)
library(ggplot2)
library(car) # levene test

leveneTest(y~factor(time), data=data)
#leveneTest(y~factor(pidp), data=data)

main <- function(){
  load('papers/phd1/data/mice_data.RData')
  data2 <- mice.data
  leveneTest(y~factor(time), data=data)
  leveneTest(y~factor(pidp), data=data)
  
  sf12.lm.oneterm <- lm(y ~ sex + 
                          ethnicity + 
                          age + 
                          education_state + 
                          labour_state + 
                          job_sec +
                          region +
                          scale(hh_income) + 
                          SF_12, data=data2)
  
  
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
                      scale(hh_income) + 1:pidp , data = data2, family = gaussian,id=pidp
                    , corstr="ar1")
  
  gee.preds <- predict(dep.gee, data2)
  #pdf("papers/ph1/plots/gee_densities.pdf")
  #compare_densities_plot(gee.preds, data2$y, "SF_12")
  #dev.off()
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
  AIC(dep.glmm)
  r.squaredGLMM(dep.glmm)
  
  glmm.preds <- predict(dep.glmm)
  pdf("papers/ph1/plots/glmm_densities.pdf")
  compare_densities_plot(glmm.preds, data2$y, "SF_12")
  dev.off()
  
  dep.glmm.gamma <- glmer(max(data2$y) - y + 0.001  ~
                            ethnicity + 
                            age + 
                            education_state + 
                            labour_state + 
                            job_sec +
                            region +
                            scale(hh_income) +
                            (1|pidp),  nAGQ=0, family=Gamma(link='log'), data = data2[complete.cases(data2),])
  #r.squaredGLMM(dep.glmm.gamma)
  
  
  glmm.gamma.sum <- summary(dep.glmm.gamma)
  AIC(dep.glmm.gamma)
  #r.squaredGLMM(dep.glmm.gamma)
  glmm.gamma.preds <- predict(dep.glmm.gamma, type='response')
  glmm.gamma.preds <- glmm.gamma.preds[which(glmm.gamma.preds<100)]
  pdf("papers/ph1/plots/glmm_gamma_densities.pdf")
  compare_densities_plot(glmm.gamma.preds, data2$y, "SF_12")
  dev.off()
  
  texreg.onemore <- sf12.lm.oneterm
  texreg.gee <- extract(dep.gee)
  texreg.glmm <- extract(dep.glmm)
  texreg.glmm.gamma <- extract(dep.glmm.gamma)
  texreg.glmm.gamma@coef <- exp(-texreg.glmm.gamma@coef)
  
  texreg(list(texreg.onemore, texreg.gee, texreg.glmm, texreg.glmm.gamma), dcolumn=T, booktabs=T, file='papers/ph1/plots/heterogeneity_coefficients.txt', title="SF12 Heterogeneity Coefficients", custom.model.names=c("OLS + Oneterm", "GEE", "GLMM", "GLMM Gamma"), single.row=T)
  
  
  texreg(list(sf12.lm, mice.lm.object, texreg.onemore, texreg.gee, texreg.glmm, texreg.glmm.gamma), dcolumn=T, booktabs=T, file='papers/ph1/plots/combined_coefficients.txt', title="SF12 All Coefficients", custom.model.names=c("OLS", "MICE OLS", "OLS + Oneterm", "GEE", "GLMM", "GLMM Gamma"), single.row=T, leading.zero=F)
  
  data3 <- data2[complete.cases(data2), ]
  fit.objects <- list(data3$SF_12, predict(sf12.lm), predict(pooled_lm, data3), predict(sf12.lm.oneterm, data3),
                      predict(dep.gee, data3), predict(dep.glmm, data3), max(data2$y)- predict(dep.glmm.gamma, data3, type='response'))
  names <- list("Real", "OLS", "OLS MICE", "OLS + Oneterm", "GEE", "GLMM", "GLMM Gamma")
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
                           scale(residuals(pooled_lm)), 
                           scale(residuals(sf12.lm.oneterm)),
                           scale(residuals(dep.gee)), 
                           scale(residuals(dep.glmm)), scale(max(data2$y)- residuals(dep.glmm.gamma, type='response')))
  residual.names <- list("Normal", "OLS", "OLS MICE", "OLS + Oneterm", "GEE", "GLMM", "GLMM Gamma")
  
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
}

main()