source("minos/transitions/utils.R")
require(ordinal)
require(nnet)
require(pscl)
require(bestNormalize)
require(lme4)
require(randomForest)
require(caret)
require(doParallel)
require(parallelly)
require(GLMMadaptive)

################ Model Specific Functions ################

# We can keep these really simple, all they need to do is run the model so
# in most cases will only require the data, the formula, and a flag for whether
# to include the survey weights in estimation (only no for 2009 where no weight
# information available)

estimate_yearly_ols <- function(data, formula, include_weights = FALSE, depend, transform = FALSE) {
  
  if (transform){
    yj <-  yeojohnson(data[, c(depend)], standardize=FALSE)
    data[, c(depend)] <- predict(yj)
  }
  
  if(include_weights) {
    # fit the model including weights (after 2009)
    model <- lm(formula,
                data = data,
                weights = weight)
  } else {
    # fit the model WITHOUT weights (2009)
    model <- lm(formula,
                data = data)
  }
  model[[depend]] <- data[[depend]]
  
  if (transform){
    model$transform <- yj
  }
  return(model)
}

estimate_yearly_clm <- function(data, formula, include_weights = FALSE, depend) {
  
  # Sort out dependent type (factor)
  data[[depend]] <- as.factor(data[[depend]])
  data <- data[, append(all.vars(formula), c("time", 'pidp', 'weight'))]
  data <- replace.missing(data)
  data <- drop_na(data)
  # replace missing ncigs values (if still missing)
  #data[which(data$ncigs==-8), 'ncigs'] <- 0
  if(include_weights) {
    model <- clm(formula,
                 data = data,
                 link = "logit",
                 threshold = "flexible",
                 Hess=T,
                 weights = weight)
  } else {
    model <- clm(formula,
                 data = data,
                 link = "logit",
                 threshold = "flexible",
                 Hess=T)
  }
  model[[depend]] <- data[[depend]]
  n_classes = length(unique(data[[depend]]))
  data[[depend]] <- NULL
  #browser()
  model$class_preds <- predict(model, newdata = data, type='class')
  # cutting off the vcov for the threshold variables (thetas) and keeping only for betas.
  # maybe should randomise both.
  model$cov_matrix <- vcov(model)[-(1:n_classes-1), -(1:n_classes-1)]
  return(model)
}


estimate_yearly_logit <- function(data, formula, include_weights = FALSE, depend) {
  
  # Sort out dependent type (factor)
  data[[depend]] <- as.factor(data[[depend]])
  
  data = replace.missing(data)
  
  if(include_weights) {
    model <- glm(formula, family=binomial(link="logit"), weights = weight, data=data)
  } else {
    model <- glm(formula, family=binomial(link="logit"), data=data)
  }
  # add obs and preds to model object for any later plotting.
  # This is mildly stupid.. 
  model[[depend]] <- data[[depend]]
  model$class_preds <- predict(model)
  model$cov_matrix <- vcov(model)
  return(model)
}


estimate_yearly_nnet <- function(data, formula, include_weights = FALSE, depend) {
  
  data = replace.missing(data)
  # Sort out dependent type (factor)
  data[[depend]] <- as.factor(data[[depend]])
  
  if(include_weights) {
    model <- multinom(formula = formula,
                      data = data,
                      MaxNWts = 10000,
                      maxit = 1000,
                      weights = weight)
  } else {
    model <- multinom(formula = formula,
                      data = data,
                      MaxNWts = 10000,
                      maxit = 1000)
    model[[depend]] <- data[[depend]]
    model$class_preds <- predict(model)
  }
  return(model)
}

estimate_yearly_zip <- function(data, formula, include_weights = FALSE, depend) {
  data <- replace.missing(data)
  
  if(include_weights) {
    model <- zeroinfl(formula = formula,
                      data = data,
                      dist = 'pois',
                      weights = weight,
                      link='logit')
  } else {
    model <- zeroinfl(formula = formula,
                      data = data,
                      dist = 'pois', 
                      link='logit')
  }
  
  #test <- runif(n=length(predict(model, type='zero'))) > predict(model, type='zero')
  #test <- round(test*(predict(model, type='count')))
  #model[[depend]] <- data[[depend]]
  #model$class_preds <- predict(model)
  #model$cov_matrix <- vcov(model)
  #number_count_terms <- length(model$coefficients$count)
  #model$count_cov_matrix <- model$cov_matrix[c(1:number_count_terms), c(1:number_count_terms)]
  #model$zero_cov_matrix <- model$cov_matrix[-c(1:number_count_terms), -c(1:number_count_terms)]
  #print(summary(model))
  #prs<- 1 - (logLik(model)/logLik(zeroinfl(next_ncigs ~ 1, data=dat.subset, dist='negbin', link='logit')))
  #print(prs)
  
  return(model)
}


###################################################
# Longitudinal Transition Probability Functions
###################################################

nanmax <- function(x) { ifelse( !all(is.na(x)), max(x, na.rm=T), NA) }
nanmin <- function(x) { ifelse( !all(is.na(x)), min(x, na.rm=T), NA) }

estimate_longitudinal_lmm <- function(data, formula, include_weights = FALSE, depend, yeo_johnson, reflect) {
  
  data <- replace.missing(data)
  #data <- drop_na(data)
  max_value <- nanmax(data[[depend]])
  if (reflect) {
    data[, c(depend)] <- max_value - data[, c(depend)] 
  }
  if (yeo_johnson) {
    yj <- yeojohnson(data[,c(depend)])
    data[, c(depend)] <- predict(yj)
  }

  if(include_weights) {
    model <- lmer(formula,  
                  weights=weight, 
                  data = data)
  } else {
    model <- lmer(formula, 
                  data = data)
  }
  if (yeo_johnson) {
    attr(model,"transform") <- yj # This is an unstable hack to add attributes to S4 class R objects.
  }
  if (reflect) {
    attr(model,"max_value") <- max_value # Works though.
  }
  browser()
  #model@transform <- yj 
  #model@min_value <- min_value
  #model@max_value <- max_value
  attr(model, "cov_matrix") <- vcov(model)
  return(model)
}


estimate_longitudinal_lmm_diff <- function(data, formula, include_weights = FALSE, depend, reflect, yeo_johnson) {
  
  data <- replace.missing(data)
  data <- drop_na(data)
  if (yeo_johnson){
    yj <- yeojohnson(data[,c(depend)])
    data[, c(depend)] <- predict(yj)
  }

  if(include_weights) {
    model <- lmer(formula,  
                   weights=weight, 
                   data = data)
  } else {
    model <- lmer(formula, 
                   data = data)
  }
  if (yeo_johnson){
    attr(model,"transform") <- yj
  }
  #attr(model,"max_value") <- max_value
  #attr(model,"min_value") <- min_value
  #browser()
  
  #model@transform <- yj # S4 class uses @ rather than $ for assignment. y tho?
  #model@min_value <- min_value
  #model@max_value <- max_value
  return(model)
}

estimate_longitudinal_glmm <- function(data, formula, include_weights = FALSE, depend, yeo_johnson, reflect) {
  
  # Sort out dependent type (factor)
  data <- replace.missing(data)
  #data <- drop_na(data)
  if (reflect) {
    max_value <- nanmax(data[[depend]])
    data[, c(depend)] <- max_value - data[, c(depend)] 
  }
  if (yeo_johnson)
  {
    yj <- yeojohnson(data[,c(depend)])
    data[, c(depend)] <- predict(yj)
  }

  min_value <- nanmin(data[[depend]])
  data[[depend]] <- data[[depend]] - min_value + 0.001
  
  if (depend == 'hourly_wage') {
    # Histogram of hourly_wage_diff
    hist(data$hourly_wage_diff, main = "Distribution of hourly_wage_diff", xlab = "hourly_wage_diff")
  }
  
  
  if(include_weights) {
    model <- glmer(formula,  
                   nAGQ=0, # fast but inaccurate optimiser. nAGQ=1 takes forever..
                   family=Gamma(link='log'), # gamma family with log link.
                   weights=weight, 
                   data = data)
  } else {
    model <- glmer(formula, 
                   nAGQ=0, 
                   family=Gamma(link='log'),
                   data = data)
  }
  attr(model,"min_value") <- min_value
  
  #browser()
  
  if (yeo_johnson){
    attr(model,"transform") <- yj # This is an unstable hack to add attributes to S4 class R objects.
      }
  if (reflect) {
    attr(model,"max_value") <- max_value # Works though.
  }
  attr(model, "cov_matrix") <- vcov(model)
  return(model)
}

estimate_longitudinal_glmm_gauss <- function(data, formula, include_weights = FALSE, depend, yeo_johnson, reflect) {
  
  # Sort out dependent type (factor)
  data <- replace.missing(data)
  #data <- drop_na(data)
  if (reflect) {
    max_value <- nanmax(data[[depend]])
    data[, c(depend)] <- max_value - data[, c(depend)] 
  }
  if (yeo_johnson)
  {
    yj <- yeojohnson(data[,c(depend)])
    data[, c(depend)] <- predict(yj)
  }
  
  min_value <- nanmin(data[[depend]])
  data[[depend]] <- data[[depend]] - min_value + 0.001
  
  if (depend == 'hourly_wage') {
    # Histogram of hourly_wage_diff
    hist(data$hourly_wage_diff, main = "Distribution of hourly_wage_diff", xlab = "hourly_wage_diff")
  }
  
  if(include_weights) {
    model <- lmer(formula,  
                   nAGQ=0, # fast but inaccurate optimiser. nAGQ=1 takes forever..
                   family=gaussian(link='identity'), # Gaussian family with identity link
                   weights=weight, 
                   data = data)
  } else {
    model <- lmer(formula, 
                   nAGQ=0, 
                   family=gaussian(link='identity'),
                   data = data)
  }
  attr(model,"min_value") <- min_value
  
  if (yeo_johnson){
    attr(model,"transform") <- yj # This is an unstable hack to add attributes to S4 class R objects.
  }
  if (reflect) {
    attr(model,"max_value") <- max_value # Works though.
  }
  return(model)
}

estimate_longitudinal_mlogit_gee <- function(data, formula, include_weights=FALSE, depend) 
{
  #data[[depend]] <- as.factor(data[[depend]])
  data <- replace.missing(data)
  data <- drop_na(data)
  if(include_weights) {
    model <- ordgee(formula,
                   id = pidp,
                   waves = time,
                   mean.link = 'logit', # gaussian GEE uses canonical identity link.
                   data = data,
                   weights = weight,
                   corstr="exchangeable") # autogression 1 structure. Depends on previous values of SF12 with exponential decay.
  } else {
    model <- ordgee(formula,
                      id = pidp,
                      waves = time,
                      mean.link = 'logit', # logistic link function (can use probit or cloglog as well.)
                      data = head(data, 100),
                      corstr="independence") # autogression 1 structure. Depends on previous values of SF12 with exponential decay.
  }
  #browser()
  return (model)
}

estimate_longitudinal_clmm <- function(data, formula, depend) 
{
  data <- replace.missing(data)
  data <- drop_na(data)
  data[, c(depend)] <- factor(data[, c(depend)])
  model <- clmm2(formula,
                random=factor(pidp),
                link='probit', # logistic link function (can use probit or cloglog as well.)
                data = tail(data, 1000), # get seg fault if using too many rows :(. clip to most recent data. 
                threshold="flexible",
                nAGQ=1) # negative int values for nAGQ gives fast but sloppy prediction. (see ?clmm2)
  return (model)
}

estimate_RandomForest <- function(data, formula, depend) {
  
  print('Beginning estimation of the RandomForest model. This can take a while, its probably not frozen...')
  
  numCores <- availableCores() / 2
  
  registerDoParallel(cores = numCores)
  
  data <- replace.missing(data)
  data <- drop_na(data)

  print("Training RandomForest with parallel processing...")
  # Train RandomForest with parallel processing
  fitControl <- trainControl(method = "cv", number = 5, allowParallel = TRUE, verboseIter = TRUE)
  set.seed(123)
  
  # Adjusting the model parameters to use fewer trees and limit depth
  rfModel <- train(formula, data = data, 
                   method = "rf",
                   trControl = fitControl,
                   tuneGrid = expand.grid(mtry = 3), 
                   ntree = 100)  # RF Parameters
  
  # expand.grid(mtry = ncol(data) / 3)
  
  
  
  #model <- randomForest(formula, data = data, ntree = 100, do.trace = TRUE)
  
  return(rfModel)
}

# longitudinal (mixed effects) ZIP model
estimate_mixed_zip <- function(data, fixed_formula, include_weights = FALSE, depend) {
  
  data <- replace.missing(data)
  #data <- drop_na(data)

  string_formulae <- strsplit(as.character(fixed_formula[3]), split=' | ', fixed=T)
  counts_formula <- paste0(as.character(fixed_formula[2]), as.character(fixed_formula[1]), string_formulae[[1]][1])
  zero_formula <- paste0("~ ", string_formulae[[1]][2])
  
  #if (depend == "ncigs_new") {
  #  #data$ncigs <- ceiling(data$ncigs/5)
  #  data$ncigs_new <-  ceiling(data$ncigs_new/5)
  #}
  
  #browser()
  model <- mixed_model(#fixed = ncigs_new ~ scale(age) + factor(ethnicity) + factor(sex) + scale(hh_income) + factor(education_state),
    fixed = as.formula(counts_formula),
    random = ~ 1 | pidp,
    zi_fixed = as.formula(zero_formula),
    #zi_random = ~ 1 | pidp,
    #weights=weight,
    iter_EM=0,
    data = data,
    family = zi.poisson(), max_coef_value=50)
    #family = zi.negative.binomial(), max_phis_value=40000)

  # test model with hard coded formulae.
  #model <- mixed_model(#fixed = ncigs_new ~ scale(age) + factor(ethnicity) + factor(sex) + scale(hh_income) + factor(education_state),
  #  fixed = ncigs_new~scale(age) + scale(nutrition_quality) + scale(hh_income) + scale(SF_12),
  #  random = ~ 1|pidp,
  #  #weights=weight,
  #  data = data,
  #  family = zi.poisson(), 
  #  zi_fixed = ~ scale(age) + scale(SF_12))
  
  #browser()
  #test.data <- drop_na(data)
  #test.zeros <- predict(model, newdata = drop_na(data), type='zero')
  #test.nonzero <- runif(n=nrow(test.data)) > test.zeros
  #test.counts2 <- predict(model, newdata = drop_na(data), type='subject_specific')
  #test.counts <- predict(model, newdata = drop_na(data), type='mean_subject')
  
  #test.zeros <- attr(test.counts2, "zi_probs")
  #test.nonzero <- runif(n=nrow(test.data)) > test.zeros
  
  #test.final <- test.nonzero * test.counts2 * 5
  #hist(test.data$ncigs_new*5, xlim=c(0, 30), freq=F, breaks=100)
  #lines(density(test.final),col='red')
  return(model)
}