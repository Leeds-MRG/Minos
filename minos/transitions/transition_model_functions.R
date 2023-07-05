source("minos/transitions/utils.R")
require(ordinal)
require(nnet)
require(pscl)
require(geepack)
require(bestNormalize)
require(lme4)

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



estimate_longitudnial_yj_gamma_gee <- function(data, formula, include_weights = FALSE, depend, reflect) {
  
  data <- replace.missing(data)
  data <- drop_na(data)
  max_value <- max(data[[depend]])
  if (reflect) {
    data[, c(depend)] <- max_value - data[, c(depend)] 
  }
  yj <- yeojohnson(data[[depend]])
  data[[depend]] <- predict(yj)
  min_value <- min(data[[depend]])
  data[[depend]] <- data[[depend]] - min_value + 0.001 # shift so values are strictly positive
  
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
  #model[[depend]] <- data[[depend]]
  #model$class_preds <- predict(model)
  model$transform <- yj
  model$min_value <- min_value
  model$max_value <- max_value
  return(model)
}


estimate_longitudnial_gaussian_gee_diff <- function(data, formula, include_weights=FALSE, depend) {
    data <- replace.missing(data)
    data <- drop_na(data)
    if(include_weights) {
      model <- geeglm(formula,
                      id = pidp,
                      waves = time,
                      family = gaussian, # gaussian GEE uses canonical identity link.
                      #family=Gamma(link='log'),
                      data = data,
                      weights = weight,
                      corstr="ar1") # autogression 1 structure. Depends on previous values of SF12 with exponential decay.
    } else {
      model <- geeglm(formula,
                      id = pidp,
                      waves = time,
                      family = gaussian,
                      #family=Gamma(link='log'),
                      data = data,
                      corstr="ar1")
    }
    #browser()
    return(model)
}


estimate_longitudnial_yj_gaussian_gee <- function(data, formula, include_weights = FALSE, depend, reflect) {
  data <- replace.missing(data)
  data <- drop_na(data)
  max_value <- max(data[[depend]])
  min_value <- max(data[[depend]])
  if (reflect) {
    data[, c(depend)] <- max_value - data[, c(depend)] 
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
  model$min_value <- min_value
  model$max_value <- max_value
  return(model)
}


nanmax <- function(x) { ifelse( !all(is.na(x)), max(x, na.rm=T), NA) }
nanmin <- function(x) { ifelse( !all(is.na(x)), min(x, na.rm=T), NA) }

estimate_longitudinal_lmm <- function(data, formula, include_weights = FALSE, depend, reflect) {
  
  data <- replace.missing(data)
  data <- drop_na(data)
  max_value <- nanmax(data[[depend]])
  min_value <- nanmin(data[[depend]])
  if (reflect) {
    data[, c(depend)] <- max_value - data[, c(depend)] 
  }
  yj <- yeojohnson(data[,c(depend)])
  data[, c(depend)] <- predict(yj)
  
  if(include_weights) {
    model <- lmer(formula,  
                  weights=weight, 
                  data = data)
  } else {
    model <- lmer(formula, 
                  data = data)
  }
  #browser()
  attr(model,"transform") <- yj # This is an unstable hack to add attributes to S4 class R objects.
  attr(model,"max_value") <- max_value # Works though.
  attr(model,"min_value") <- min_value

  #model@transform <- yj 
  #model@min_value <- min_value
  #model@max_value <- max_value
  #browser()
  return(model)
}


estimate_longitudinal_lmm_diff <- function(data, formula, include_weights = FALSE, depend, reflect) {
  
  data <- replace.missing(data)
  #data <- drop_na(data)
  yj <- yeojohnson(data[,c(depend)])
  data[, c(depend)] <- predict(yj)
  
  if(include_weights) {
    model <- lmer(formula,  
                   weights=weight, 
                   data = data)
  } else {
    model <- lmer(formula, 
                   data = data)
  }
  #browser()
  attr(model,"transform") <- yj
  #attr(model,"max_value") <- max_value
  #attr(model,"min_value") <- min_value
  
  #model@transform <- yj # S4 class uses @ rather than $ for assignment. y tho?
  #model@min_value <- min_value
  #model@max_value <- max_value
  return(model)
}

estimate_longitudinal_glmm <- function(data, formula, include_weights = FALSE, depend) {
  
  # Sort out dependent type (factor)
  data[[depend]] <- as.factor(data[[depend]])
  data <- replace.missing(data)
  
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
  browser()
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