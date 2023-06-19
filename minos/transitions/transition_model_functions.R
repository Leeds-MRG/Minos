source("minos/transitions/utils.R")
require(ordinal)
require(nnet)
require(pscl)
require(geepack)
require(bestNormalize)

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
  
  data = replace.missing(data)
  # replace missing ncigs values (if still missing)
  data[which(data$ncigs==-8), 'ncigs'] <- 0
  
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
  data[[depend]] <- NULL
  model$class_preds <- predict(model, newdata = data, type='class')
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
    model[[depend]] <- data[[depend]]
    model$class_preds <- predict(model)
  }
  
  #print(summary(model))
  #prs<- 1 - (logLik(model)/logLik(zeroinfl(next_ncigs ~ 1, data=dat.subset, dist='negbin', link='logit')))
  #print(prs)
  
  return(model)
}


###################################################
# Longitudinal Transition Probability Functions
###################################################



estimate_longitudnial_gamma_gee <- function(data, formula, include_weights = FALSE, depend) {
  
  data = replace.missing(data)
  data <- drop_na(data)
  if(include_weights) {
    model <- geeglm(formula,
                    id = pidp,
                    waves = time,
                    family = Gamma(link='inverse'), # canonical inverse gamma link. Could use log link instead..
                    data = data,
                    weights = weight,
                    corstr="ar1") # autogression 1 structure. Depends on previous values of SF12 with exponential decay.
  } else {
    model <- geeglm(formula,
                    id = pidp,
                    waves = time,
                    family = Gamma(link='inverse'),
                    data = data,
                    corstr="ar1")
  }
  # add obs and preds to model object for any later plotting.
  # This is mildly stupid.. 
  model[[depend]] <- data[[depend]]
  model$class_preds <- predict(model)
  if(depend == "SF_12"){model$class_preds <- max(data$SF_12) - model$class_preds} # flip SF_12 back from right to left skew. 
  return(model)
}



estimate_longitudnial_yj_gaussian_gee <- function(data, formula, include_weights = FALSE, depend, reflect) {
  data = replace.missing(data)
  data <- drop_na(data)
  if (reflect) {
    data[, c(depend)] <- -data[, c(depend)] 
  }
  yj <- yeojohnson(data[,c(depend)])
  data[, c(depend)] <- predict(yj)
  if(include_weights) {
    model <- geeglm(formula,
                    id = pidp,
                    waves = time,
                    family = gaussian, # gaussian GEE uses canonical identity link.
                    data = data,
                    weights = weight,
                    corstr="ar1") # autogression 1 structure. Depends on previous values of SF12 with exponential decay.
  } else {
    model <- geeglm(formula,
                    id = pidp,
                    waves = time,
                    family = gaussian,
                    data = data,
                    corstr="ar1")
    #browser()
  }
  # add obs and preds to model object for any later plotting.
  # This is mildly stupid.. 
  #model[[depend]] <- data[[depend]]
  #model$class_preds <- predict(model)
  model$transform <- yj    
  #browser()
  return(model)
}


estimate_longitudinal_glmm <- function(data, formula, include_weights = FALSE, depend) {
  
  # Sort out dependent type (factor)
  data[[depend]] <- as.factor(data[[depend]])
  
  data = replace.missing(data)
  
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
  # add obs and preds to model object for any later plotting.
  # This is mildly stupid.. 
  model[[depend]] <- data[[depend]]
  model$class_preds <- predict(model)
  return(model)
}