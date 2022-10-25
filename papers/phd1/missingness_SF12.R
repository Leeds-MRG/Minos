source("papers/phd1/paper1Utils.R")
library(mice)
library(VIM)
library(ggplot2)
library(ggpattern) # ggpatterns from remotes::install_github("coolbutuseless/ggpattern")
library(tidyr) # for dropna
library(jtools) # for forest plots
library(sjPlot) # forest plots

format_sf12_mice_transition_data <- function(source, years, v){
  main_data <- c()
  for (year in years){
    print(year)
    print(year+1)
    data_source<- source
    data_files <- get_US_files(data_source, year, year+1)
    data <- data_files$data1
    data2 <- data_files$data2
    columns <- c("pidp",
                 "SF_12", 
                 "job_sec",
                 "education_state",
                 "sex",
                 "labour_state", 
                 "region", 
                 "ethnicity", 
                 "age", 
                 "time", "hh_income", 
                 'behind_on_bills',
                 'financial_situation',  
                 'future_financial_situation',
                 'likely_move',
                 'ghq_depression',
                 'ghq_happiness',
                 'clinical_depression',
                 'scsf1',
                 'phealth_limits_work',
                 'mhealth_limits_work',
                 'health_limits_social')
    
    data <- data[, columns]
    data2 <- data2[, c("pidp", v)]
    
    data <- replace.missing(data)
    data2 <- replace.missing(data2)
    
    # only look at individuals with data in both waves.
    #common <- intersect(data$pidp, data2$pidp)
    #data <- data[which(data$pidp %in% common), ]
    #data2 <- data2[which(data2$pidp %in% common), ]
    
    colnames(data2) <- c("pidp", "y")
    data <- merge(data, data2,"pidp")
    main_data <- rbind(main_data, data)
  }
  return(main_data)
}

main <- function(){
  data <- format_sf12_mice_transition_data("data/composite_US/", c(2011,2012, 2013), "SF_12")
  data$ethnicity <- relevel(factor(data$ethnicity), ref="WBI")
  data$education_state <- factor(data$education_state)
  data$region <- relevel(factor(data$region), ref="London")
  data$sex <- factor(data$sex)
  data$labour_state <- factor(data$labour_state)
  data$job_sec <- relevel(factor(data$job_sec), ref=1)
  data$gross_hh_income <- data$gross_hh_income
  data$age <- data$age
  data$job_sec <- factor(data$job_sec)
  
  
  imp_columns <- c('pidp',
                    "SF_12",
                   'y',
                   'sex',
                   "job_sec",
                   "education_state",
                   "sex",
                   "labour_state", 
                   "region", 
                   "ethnicity", 
                   "age", 
                   "time", 
                   "hh_income"
  )
  method <- c("pmm",
              "pmm",
              'pmm',
              'pmm',
              'pmm',
              'polr',
              'pmm',
              'polr',
              'pmm',
              'pmm',
              'pmm',
              'pmm',
              'pmm'
  )
  
  pdf("papers/phd1/plots/total_missingness_structure2.pdf")
  aggr(subset(data, select=-c(y)), sortVars=T,  oma=c(8,4,4,4), numbers=T, cex.axis=1.0, col = c(blue, orange), prop=F, combined=T, cex.numbers=0.5)
  dev.off()
  
  mice_set <- mice(data = data[,imp_columns], method=method,
                   m = 10, maxit = 20,
                   remove.collinear=T)
  
  pdf("papers/phd1/plots/ols_mice_convergence.pdf")
  plot(mice_set, y = SF_12 + y ~ .it | .ms)
  dev.off()
  
  mice.sf12.lm <- with(mice_set, lm(y ~ sex + 
                                      ethnicity + 
                                      age + 
                                      education_state + 
                                      labour_state + 
                                      job_sec +
                                      region +
                                      scale(hh_income)))
  final.pool<- pool(mice.sf12.lm)
  
  mice.data <- complete(mice_set) 
  save(mice.data, file = 'papers/phd1/data/mice_data.RData')
  
  pooled_lm <- mice.sf12.lm$analyses[[1]]
  pool.sum <- summary(final.pool)
  pooled_lm$coefficients = pool.sum$estimate
  mice.preds<- predict(pooled_lm)
  
  pool.r.squared(final.pool)
  
  # mice objects dont go in forest plot annoyingly. move coefficients over to a
  # dummy lm that plot_models can read.
  mice.lm.object <- summary(lm(y ~ sex + 
                                 ethnicity + 
                                 age + 
                                 education_state + 
                                 labour_state + 
                                 job_sec +
                                 region +
                                 scale(hh_income), data = complete(mice_set)))
  mice.lm.object$coefficients[,1] <- pool.sum$estimate
  mice.lm.object$coefficients[,2] <- pool.sum$std.error
  mice.lm.object$coefficients[,3] <- pool.sum$statistic
  mice.lm.object$coefficients[,4] <- pool.sum$p.value
  
  #texreg(mice.lm.object, dcolumn=T, booktabs=T, file='../plots/mice_ols_coefficients.txt', title="SF12 MICE OLS Coefficients", custom.model.names=c("SF12 OLS"), single.row=T, include.aic=T)
  
  res <- as.data.frame(predict(pooled_lm))
  real <- as.data.frame(data$SF_12)
  res$type <- c("Predicted")
  real$type <- c("Real")
  colnames(res) <- c("SF12", 'type')
  colnames(real) <- c("SF12", 'type')
  hist.data <- rbind(res,real)
  hist.data <- drop_na(hist.data)
  
  ols.hist <- ggplot(hist.data, aes(x=SF12, fill = type, col=type)) +
    geom_histogram(aes(y=..density..), alpha=0.5, binwidth=2, position='identity')
  
  mice.ols.densities <- ggplot(hist.data) +
    geom_density_pattern(aes(x=SF12, pattern_fill = as.factor(type), pattern_type = as.factor(type)),
                         alpha=0.1,
                         pattern = 'polygon_tiling',
                         pattern_key_scale_factor = 1.2,
                         pattern_alpha=0.4)+        
    scale_pattern_type_manual(values = c("hexagonal", "rhombille"))+
    theme_bw(18) +
    theme(legend.key.size = unit(2, 'cm'))
  
  pdf('papers/phd1/plots/mice_ols_densitie s.pdf')
  print(mice.ols.densities)
  dev.off()
  
  pdf('papers/phd1/plots/mice_SF12_forest.pdf')
  print(plot_models(mice.lm.object, p.shape=T, legend.title = NULL, m.labels=NULL))
  dev.off()
}

main()
