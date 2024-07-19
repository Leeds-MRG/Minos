source("minos/transitions/utils.R")
library(ordinal)
library(nnet)
library(pscl)
library(bestNormalize)
library(lme4)
library(randomForest)
library(caret)
library(doParallel)
library(parallelly)
library(ranger)
library(earth)
library(xgboost)
library(recipes)
library(LaplacesDemon)

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

  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

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

  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

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

  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

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

  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

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
  model[[depend]] <- data[[depend]]
  model$class_preds <- predict(model)
  model$cov_matrix <- vcov(model)
  number_count_terms <- length(model$coefficients$count)
  model$count_cov_matrix <- model$cov_matrix[c(1:number_count_terms), c(1:number_count_terms)]
  model$zero_cov_matrix <- model$cov_matrix[-c(1:number_count_terms), -c(1:number_count_terms)]
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

estimate_longitudinal_lmm <- function(data, formula, include_weights = FALSE, depend, yeo_johnson, log_transform, reflect) {

  data <- replace.missing(data)
  #data <- drop_na(data)

  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

  # If min == 0, then add small amount before log_transform
  # if (min(data[[depend]] == 0) && (log_transform)) {
  #   print("Adding small value for log_transform")
  #   data[[depend]] <- data[[depend]] + 0.001
  # }

  if ((depend %in% c('SF_12_MCS', 'SF_12')) & log_transform) {
    data[[depend]] <- data[[depend]] + 0.001
  }

  # remove rows with null weight values
  #data <- data[!is.na(data$weight), ]

  max_value <- nanmax(data[[depend]])
  min_value <- nanmin(data[[depend]])

  if (reflect) {
    data[, c(depend)] <- max_value - data[, c(depend)]
  }
  if (yeo_johnson) {
    yj <- yeojohnson(data[,c(depend)])
    data[, c(depend)] <- predict(yj)
  }

  # LA 8/2/24
  ## Log Normal Transformation for SF_12 vars
  if (log_transform) {
    data[[depend]] <- log(data[[depend]])
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

  ## LA 9/2/24
  # Saving min and max value from input data for clipping in r_utils function
  if (depend %in% c('SF_12_PCS', 'SF_12_MCS', 'SF_12')) {
    attr(model,"min_value") <- min_value
    attr(model,"max_value") <- max_value
  }

  #browser()
  #model@transform <- yj
  #model@min_value <- min_value
  #model@max_value <- max_value
  attr(model, "cov_matrix") <- vcov(model)
  return(model)
}


estimate_longitudinal_lmm_diff <- function(data, formula, include_weights = FALSE, depend, reflect, yeo_johnson) {

  data <- replace.missing(data)
  data <- drop_na(data)

  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

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

  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

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

  numCores <- availableCores() - 1

  registerDoParallel(cores = numCores)

  data <- replace.missing(data)
  data <- drop_na(data)

  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

  set.seed(123)

  print("Training RandomForest with parallel processing...")
  # Train RandomForest with parallel processing
  fitControl <- trainControl(method = "cv", number = 5, allowParallel = TRUE, verboseIter = TRUE)

  # Adjusting the model parameters to use fewer trees and limit depth
  rfModel <- train(formula,
                   data = data,
                   method = "rf",
                   trControl = fitControl,
                   tuneGrid = expand.grid(mtry = 3),
                   ntree = 100)  # RF Parameters

  # expand.grid(mtry = ncol(data) / 3)



  #model <- randomForest(formula, data = data, ntree = 100, do.trace = TRUE)

  return(rfModel)
}

estimate_RandomForestOrdinal <- function(data, formula, depend) {

  print('Beginning estimation of the Ordinal RandomForest model...')

  numCores <- availableCores() - 1

  registerDoParallel(cores = numCores)

  data <- replace.missing(data)
  data <- drop_na(data)

  data[[depend]] <- factor(data[[depend]])

  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

  set.seed(123)

  # Train the ranger model
  ranger_model <- ranger(
    formula = formula,
    data = data,
    num.trees = 100,
    probability = TRUE,
    verbose = TRUE
  )

  return(ranger_model)
}

estimate_MARS <- function(data, formula) {

  print('Beginning estimation of the MARS model...')

  data <- replace.missing(data)
  data <- drop_na(data)
  
  print(sprintf("Model is being fit on %d individual records...", nrow(data)))

  model <- earth(formula = formula,
                 data = data,
                 weights = weight)

  return(model)
}

estimate_XGB <- function(data, formula, depend) {
  
  print('Beginning estimation of the XGB model...')
  
  data <- replace.missing(data)
  data <- drop_na(data)
  
  print(sprintf("Model is being fit on %d individual records...", nrow(data)))
  
  # set some vars to factor (important for numeric factors only, nominal handled easier)
  numeric_as_factor <- c('education_state', 'neighbourhood_safety', 'loneliness', 'job_sec')
  # Filter the list to include only columns that exist in the data
  numeric_as_factor <- numeric_as_factor[numeric_as_factor %in% colnames(data)]
  # convert variables to factor
  data[numeric_as_factor] <- lapply(data[numeric_as_factor], as.factor)
  
  # Logit transform the dependent variable if it's SF_12 MCS
  if (depend == "SF_12") {
    browser()
    epsilon <- 1e-6  # Small value to avoid logit issues
    data[[depend]] <- logit((data[[depend]] / 100) + epsilon)
  }
  
  # Define the recipe
  rec <- recipe(formula, data = data) %>%
    step_dummy(all_nominal_predictors())
  
  # Prepare the recipe
  prep_rec <- prep(rec, training = data)
  
  # Apply the recipe to the training data
  train_data <- bake(prep_rec, new_data = data)
  
  # Create the model matrix
  train_matrix <- as.matrix(train_data)
  
  # prepare label and function
  if (depend == 'hh_income') {
    label <- data$hh_income
  } else if (depend == 'SF_12') {
    label <- data$SF_12
  }
  
  dtrain <- xgb.DMatrix(data = train_matrix, label = label)
  
  # train the model
  params <- list(
    objective = "reg:squaredlogerror",
    eta = 0.3,
    max_depth = 6,
    subsample = 1,
    colsample_bytree = 1
  )
  model <- xgb.train(params, dtrain, nround = 100)  # , verbose = 1
  
  #attr(model,"formula_string") <- formula.string
  attr(model, "recipe") <- prep_rec
  
  return(model)
}
