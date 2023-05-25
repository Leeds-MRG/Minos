################ ESTIMATING TRANSITION MODELS FOR MINOS ################
# Author: Luke Archer
# Date: 30/11/22
#
# This script will be responsible for estimating any and all transition models
# for use in the MINOS microsimulation.
# At the time of writing we estimate 4 different model types (OLS, CLM, NNET, ZIP)
# and each of these will require some specific processing. Therefore each 
# model type will have its own function for the preprocessing, and we will have
# a main function to read in the parameters from model_definitions.txt and 
# execute the loop.
########################################################################

################ Utilities ################

source("minos/transitions/utils.R")

require(argparse)
require(tidyverse)
require(ordinal)
require(nnet)
require(stringr)
require(pscl)

# Take the line from the model_definitions.txt and pull out what we need
digest_params <- function(line) {
  # Get model type
  split1 <- str_split(line, pattern = " : ")[[1]]
  mod.type <- split1[1]
  
  # Get dependent and independents
  split2 <- str_split(split1[2], pattern = " ~ ")[[1]]
  dependent <- split2[1]
  independents <- split2[2]
  
  # formula
  form <- as.formula(split1[2])
  #print(form)
  
  return.list <- c(dependent, independents, form)
  
  return(return.list)
}


################ Model Specific Functions ################

# We can keep these really simple, all they need to do is run the model so
# in most cases will only require the data, the formula, and a flag for whether
# to include the survey weights in estimation (only no for 2009 where no weight
# information available)

estimate_yearly_ols <- function(data, formula, include_weights = FALSE, depend) {
  
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
  return(model)
}

estimate_yearly_ols_diff <- function(data, formula, depend) {
  
  #orig.depend <- gsub("^.*?_", "", depend)
  #pred.var <- paste0(orig.depend, '_change')
  #data[[pred.var]] <- data[[depend]] - data[[orig.depend]]
  #formula.preds <- gsub("^.*?~", "~", formula)
  
  # Split string on the tilda and keep the right hand side (predictors)
  formula.right <- unlist(str_split(as.character(formula), pattern = '~')[3])
  # Add diff to the formula now using the depend argument
  formula2 <- paste0(depend, ' ~ ', formula.right)
  # Now we have the original right hand side of the formula, and the diff as the
  # dependent variable
  
  # diff models are much more likely to have missing data if respondent wasn't
  # in previous wave, so have to do some more null handling here
  #data <- data[!is.na(data[[depend]])]
  
  data <- data %>%
    drop_na(.data[[depend]])
    
  
  # no need to worry about weights as we can't fit this model in first year (2009)
  model <- lm(formula2,
              data = data,
              weights = weight)
  
  model[[depend]] <- data[[depend]]
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
  }
  return(model)
}

estimate_yearly_zip <- function(data, formula, include_weights = FALSE, depend) {
  
  if(depend == 'next_ncigs' | depend == 'ncigs') {
    # first subset just the columns we want
    cols <- c('pidp', depend, 'age', 'sex', 'education_state', 'SF_12', 'job_sec', 
              'hh_income', 'ethnicity', 'weight')
    dat.subset <- data[, cols]
    
    # Replace missing values with NA (util func)
    dat.subset = replace.missing(dat.subset)
    
    # now set NA to 0
    dat.subset[[depend]][is.na(dat.subset[[depend]])] <- 0
    
    # finally run complete cases
    dat.subset <- dat.subset[complete.cases(dat.subset),]
  }
  
  if(include_weights) {
    model <- zeroinfl(formula = formula,
                      data = dat.subset,
                      dist = 'pois',
                      weights = weight,
                      link='logit')
  } else {
    model <- zeroinfl(formula = formula,
                      data = dat.subset,
                      dist = 'pois', 
                      link='logit')
  model[[depend]] <- data[[depend]]
  }
  
  #print(summary(model))
  #prs<- 1 - (logLik(model)/logLik(zeroinfl(next_ncigs ~ 1, data=dat.subset, dist='negbin', link='logit')))
  #print(prs)
  
  return(model)
}

calculate_diff <- function(data, cont.var) {
  data <- data %>%
    group_by(pidp) %>%
    mutate(diff.hh_income = hh_income - lag(hh_income, order_by = time))
}



################ Main Run Loop ################

run_yearly_models <- function(transitionDir_path, 
                              transitionSourceDir_path, 
                              mod_def_name, 
                              data, 
                              mode) {
  
  ## Read in model definitions from file including formula and model type (OLS,CLM,etc.)
  modDef_path = paste0(transitionSourceDir_path, mod_def_name)
  modDefs <- file(description = modDef_path, open="r", blocking = TRUE)
  
  # read file
  repeat{
    def = readLines(modDefs, n = 1) # Read one line from the connection.
    if(identical(def, character(0))){break} # If the line is empty, exit.
    
    # Get model type
    split1 <- str_split(def, pattern = " : ")[[1]]
    mod.type <- split1[1]
    
    # Get dependent and independents
    split2 <- str_split(split1[2], pattern = " ~ ")[[1]]
    dependent <- split2[1]
    independents <- split2[2]
    
    # formula
    formula.string.orig <- split1[2]
    
    ## Calculate diff for rate of change models
    # only applicable to hh_income and SF_12 for now
    if (tolower(mod.type) == 'ols_diff') {
      data <- data %>%
        group_by(pidp) %>%
        mutate(diff = .data[[dependent]] - lag(.data[[dependent]], order_by = time))
    }
    
    ## Yearly model estimation loop
    
    # Set the time span to estimate models for differently for cross_validation
    # crossval needs all years, whereas default model can have reduced timespan
    if(mode == 'cross_validation') {
      year.range <- seq(min(data$time), (max(data$time) - 1))
    } else {
      #year.range <- seq(max(data$time) - 5, (max(data$time) - 1))
      year.range <- seq(min(data$time), (max(data$time) - 1)) # fit full range for model of models testing purposes
    }
    
    # set up output directory
    out.path1 <- paste0(transitionDir_path, dependent, '/')
    out.path2 <- paste0(out.path1, tolower(mod.type), '/')
    create.if.not.exists(out.path1)
    create.if.not.exists(out.path2)
    
    print(paste0('Starting for ', dependent, '...'))
    
    ## Implement the 'next_' functionality to male sure were not doing dodgy prediction when using lags
    # add 'next_' keyword to dependent variable
    formula.string.orig <- paste0('next_', formula.string.orig)
    
    for(year in year.range) {
      
      # reset the formula string for each year
      formula.string <- formula.string.orig
      
      ## dependent year data is always year + 1 unless data requires something different
      # (as in neighbourhood estimation, does a t+3 model due to data)
      depend.year <- year + 1
      
      #TODO: Replace all these if statements with a check for data in that year
      #   i.e. if colsum == (-9 * length(column)) 
      #   then all elements == -9 as they would have been assigned that due to missing
      
      ## Some models don't run in certain years (data issues) so break here
      # nutrition_quality only estimated for 2018
      if(dependent == 'nutrition_quality' & !year %in% c(2014, 2016, 2018)) { next }
      # labour_state only estimated for 2018
      if(dependent == 'education_state' & year != 2018) { next }
      # loneliness only estimated for waves starting 2017 and 2018
      if(dependent == 'loneliness' & !year > 2016) { next }
      # neighbourhood only estimated for wave 2011, 2014, and 2017
      if(dependent == 'neighbourhood_safety' & !year %in% c(2011, 2014, 2017)) { next }
      if(dependent == 'neighbourhood_safety'){ depend.year <- year + 3 } # set up 3 year horizon
      # tobacco model only estimated for 2013 onwards
      if(dependent == 'ncigs' & year < 2013) { next }
      #TODO: Maybe copy values from wave 2 onto wave 1? Assuming physical health changes slowly?
      # SF_12 predictor (physical health score) not available in wave 1
      if(dependent == 'SF_12' & year == 2009) { next }
      # OLS_DIFF models can only start from wave 2 (no diff in first wave)
      if(tolower(mod.type) == 'ols_diff' & year == 2009) { next }
      
      print(paste0('Starting estimation for ', dependent, ' in ', year))
      
      # set up new dependent var name
      next.dependent <- paste0('next_', dependent)

      # independents from time T (current)
      indep.df <- data %>% 
        filter(time == year)
      # dependent from T+1 (rename to 'next_{dependent}' soon)
      depen.df <- data %>% 
        filter(time == depend.year) %>% 
        select(pidp, .data[[dependent]])
      
      # rename to next_{dependent}
      next.colnames <- c('pidp', paste0('next_', dependent))
      colnames(depen.df) <- next.colnames
      
      # smash them together
      merged <- merge(depen.df, indep.df, by='pidp')
      
      # no weight var in 2009 (wave 1)
      if(year == 2009) {
        use.weights <- FALSE
      } else {
        use.weights <- TRUE
      }
      
      #print(formula.string)
      ## For the SF_12 model alone, we need to modify the formula on the fly
      # as neighbourhood_safety, loneliness, nutrition_quality and ncigs are 
      # not present every year
      if(dependent == 'SF_12') {
        if(!year %in% c(2011, 2014, 2017, 2020)) {
          formula.string <- str_remove(formula.string, " \\+ factor\\(neighbourhood_safety\\)")
        }
        if(!year > 2016) {
          formula.string <- str_remove(formula.string, " \\+ factor\\(loneliness\\)")
        }
        if(!year %in% c(2015, 2017, 2019)) {
          formula.string <- str_remove(formula.string, " \\+ nutrition_quality")
        }
        if(year < 2013) {
          formula.string <- str_remove(formula.string, " \\+ ncigs")
        }
      }
      #print(formula.string)
      # Now make string into formula
      form <- as.formula(formula.string)
      
      
      
      ## Different model types require different functions
      if(tolower(mod.type) == 'ols') {
        
        model <- estimate_yearly_ols(data = merged, 
                                     formula = form, 
                                     include_weights = use.weights,
                                     depend = next.dependent)
        
      } else if(tolower(mod.type) == 'ols_diff') {
        
        model <- estimate_yearly_ols_diff(data = merged, 
                                     formula = form,
                                     depend = 'diff')
        
      } else if(tolower(mod.type) == 'clm') {
        
        # set ordinal dependent to factor
        model <- estimate_yearly_clm(data = merged,
                                     formula = form, 
                                     include_weights = use.weights, 
                                     depend = next.dependent)
        
      } else if(tolower(mod.type) == 'nnet') {
        
        model <- estimate_yearly_nnet(data = merged, 
                                      formula = form, 
                                      include_weights = use.weights, 
                                      depend = next.dependent)
        
      } else if(tolower(mod.type) == 'zip') {
        
        model <- estimate_yearly_zip(data = merged,
                                     formula = form,
                                     include_weights = use.weights,
                                     depend = next.dependent)
        
      }
      
      
      #return(model)
      
      #print(typeof(model$coefficients))
      #print(model$coefficients)
      #return(model$coefficients)
      # getting coefficients for checking and debugging
      #coefs <- as.data.frame(model$coefficients)
      #coefs <- data.frame(Variables=row.names(coefs), coefs)
      #rownames(coefs) <- NULL
      
      # save model & coefficients to file (in their own folder)
      #coef.filepath <- paste0(out.path2, '/', dependent, '_', year, '_', depend.year, '_coefficients.txt')
      #write_csv(coefs, file = coef.filepath)
      saveRDS(model, file=paste0(out.path2, dependent, '_', year, '_', depend.year, '.rds'))
      print(paste0(mod.type, ' model for ', dependent, ' generated for years ', year, ' - ', depend.year))
      
    }
    print(paste0("Finished for ", dependent, '.'))
  }
  # close and remove connection object from memory
  close(modDefs)
  rm(modDefs)
}


################ Last Minute Data Prep & Execute Script ################


#### IMPORTANT!!
## Because some variables are not present in every wave (i.e. neighbourhood_safety, loneliness) we need to handle this.
## There is a decent solution that comes partly because we are estimating a different model for every year
## We need to check when we are in the correct years, and remove a string subset from the formula
## i.e. in 2015 no neighbourhood_safety, so remove 'relevel(factor(neighbourhood_safety), ref = '1')'


## Argparse stuff
parser = ArgumentParser()
parser$add_argument('-s', 
                    '--scotland', 
                    action='store_true', 
                    dest='scotland', 
                    default=FALSE,
                    help='Run in Scotland mode - MORE HELP NEEDED HERE')

parser$add_argument('-c', 
                    '--cross_validation',
                    action='store_true',
                    dest='crossval',
                    default=FALSE,
                    help='Run in cross validation mode. Transition models are
                    fitted to half the population, before running simulations
                    with the other half.')

args <- parser$parse_args()

scotland.mode <- args$scotland

cross_validation <- args$crossval

## RUNTIME ARGS
transSourceDir <- 'minos/transitions/'
dataDir <- 'data/final_US/'
modDefFilename <- 'model_definitions.txt'
transitionDir <- 'data/transitions/'
mode <- 'default'


# Set different paths for scotland mode, cross-validation etc.
if(scotland.mode) {
  print('Estimating transition models in Scotland mode')
  dataDir <- 'data/scotland_US/'
  modDefFilename <- 'model_definitions_SCOTLAND.txt'
  mode <- 'scotland'
  transitionDir <- paste0(transitionDir, 'scotland/')
  create.if.not.exists(transitionDir)
} else if(cross_validation) {
  print('Estimating cross validation models')
  dataDir <- 'data/final_US/cross_validation/transition/'
  mode <- 'cross_validation'
  transitionDir <- paste0(transitionDir, 'cross_validation/')
  create.if.not.exists(transitionDir)
} else {
  print('Estimating transition models in whole population mode')
}


# Load input data (final_US/)
filelist <- list.files(dataDir,
                       include.dirs = FALSE,
                       full.names = TRUE,
                       pattern = '[0-9]{4}_US_cohort.csv')
data <- do.call(rbind, lapply(filelist, read.csv))

run_yearly_models(transitionDir, transSourceDir, modDefFilename, data, mode)

print('Generated transition models.')
