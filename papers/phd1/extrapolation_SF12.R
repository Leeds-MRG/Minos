source('minos/transitions/utils.R')
library(jtools) # for forest plots
library(sjPlot) # forest plots
library(strucchange) # CHOW TEST
source("papers/phd1/paper_plots.R")

get.extrapolated_weight.files <- function(source, year1, year2){
  # get files for year 1 and year 2 respectively.
  file_name <- get_US_file_names(source, year1, ".csv")
  data <- get_US_data(file_name)
  file_name2 <- get_US_file_names(source, year2, ".csv")
  data2 <- get_US_data(file_name2)
  data_files <- list("data1" = data, "data2" = data2)
  return(data_files)
}


main <- function(years){
  
  sctest(y ~ time, data=data, type='Chow', point=10)
  
  data <- data.frame()
  source <- 'data/extrapolated_weights_data_'
  for (year in years){
    data_files <- get.extrapolated_weight.files(source, year, year+1)
    new_data <- data_files$data1
    new_data2 <- data_files$data2
    
    # only look at individuals with data in both waves.
    common <- intersect(new_data$pidp, new_data2$pidp)
    new_data <- new_data[which(new_data$pidp %in% common), ]
    new_data2 <- new_data2[which(new_data2$pidp %in% common), ]
    new_data2 <- new_data2[, c("pidp", "SF_12")]
    colnames(new_data2) <- c("pidp", "y")
    new_data <- merge(new_data, new_data2, "pidp")
    #new_data <- new_data[complete.cases(new_data),]
    
    year0_weight <- paste0(paste0("X", year), "_weight")
    year5_weight <- paste0(paste0("X", year+5), "_weight")
    year10_weight <-  paste0(paste0("X", year+10), "_weight")
    colnames(new_data)[which(colnames(new_data)==year0_weight)] <- 'year0_weight'
    colnames(new_data)[which(colnames(new_data)==year5_weight)] <- 'year5_weight'
    colnames(new_data)[which(colnames(new_data)==year10_weight)] <- 'year10_weight'
    
    data <- rbind(data, new_data)
  }
  
  data$ethnicity <- relevel(factor(data$ethnicity), ref="WBI")
  #data$education_state <- relevel(factor(data$education_state), ref=0)
  data$region <- relevel(factor(data$region), ref="London")
  data$sex <- factor(data$sex)
  data$labour_state <- factor(data$labour_state)
  data$job_sec <- relevel(factor(data$job_sec), ref=1)
  data$gross_hh_income <- data$gross_hh_income
  data$age <- data$age
  data$job_sec <- factor(data$job_sec)
  
  formula <- "y ~ sex + 
                  ethnicity + 
                  age + 
                  education_state + 
                  labour_state + 
                  job_sec +
                  region +
                  scale(hh_income)"
  
  sf12.lm.weighted.2013 <- lm(formula, weights = year0_weight, data = data)
  print(summary(sf12.lm))
  
  pdf('papers/phd1/plots/extrapolated_SF12_forest_2013.pdf')
  print(plot_models(sf12.lm.weighted.2013, p.shape=T, legend.title = NULL, m.labels=NULL))
  dev.off()
  
  sf12.lm.weighted.2018 <- lm(formula, weights = year5_weight, data = data)
  print(summary(sf12.lm))
  
  png('papers/phd1/plots/extrapolated_SF12_forest_2018.png')
  plot_models(sf12.lm.weighted.2018, p.shape=T, legend.title = NULL, m.labels=NULL)
  dev.off()

  
  weights_2013 <- data$year0_weight
  save(weights_2013, file="papers/phd1/data/US_2013_weights.RData")
  weights_2018 <- data$year5_weight
  save(weights_2018, file="papers/phd1/data/US_2018_weights.RData")
  
  ######
  #LASSO
  ######
  
  x <- model.matrix(y ~ sex + 
                      ethnicity + 
                      age + 
                      education_state + 
                      labour_state + 
                      job_sec +
                      region +
                      scale(hh_income), data=data)
  
  y <- data$y
  weights.2013 <- data$year0_weight
  weights.2018 <- data$year5_weight
  
  # Fit LASSO
  cv.lasso <- cv.glmnet(x, y, family = "gaussian", weights=weights.2013)
  lasso <- glmnet(x, y, alpha = 1,  family = "gaussian", weights = weights.2013)
  
  pdf('papers/phd1/plots/ols_lasso_2013.pdf')
  plot(lasso, xvar = "lambda", label = T) 
  abline(v = log(cv.lasso$lambda.min), col = "blue",lty=2)
  abline(v = log(cv.lasso$lambda.1se), col = "red", lty=3)
  legend('bottomright', legend=c("Minimum Standard Error", "First Standard Error"), col=c('blue', 'red'), lty=c(2, 3))
  dev.off()
  
  pdf('papers/phd1/plots/ols_cv_lasso_2013.pdf')
  plot(cv.lasso)
  dev.off()
  
  coef(cv.lasso, s = "lambda.min")
  
  # same again with 2018 weights.
  cv.lasso2 <- cv.glmnet(x, y, family = "gaussian", weights=weights.2018)
  lasso2 <- glmnet(x, y, alpha = 1, family = "gaussian", weights = weights.2018)
  
  
  pdf('papers/phd1/plots/ols_lasso_2018.pdf')
  plot(lasso2, xvar = "lambda", label = T) 
  abline(v = log(cv.lasso2$lambda.min), col = "blue",lty=2)
  abline(v = log(cv.lasso2$lambda.1se), col = "red", lty=3)
  legend('bottomright', legend=c("Minimum Standard Error", "First Standard Error"), col=c('blue', 'red'), lty=c(2, 3))
  dev.off()
  
  pdf('papers/phd1/plots/ols_cv_lasso_2018.pdf')
  plot(cv.lasso2)
  dev.off()
  coef(cv.lasso2, s = "lambda.min")
}

years <- c(2011, 2012, 2013)
main(years)