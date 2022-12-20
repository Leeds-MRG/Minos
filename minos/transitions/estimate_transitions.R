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

estimate_yearly_ols <- function(data, formula, include_weights = FALSE) {
  
  data = replace.missing(data)
  
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
  return(model)
}

estimate_yearly_clm <- function(data, formula, include_weights = FALSE, depend) {
  
  data = replace.missing(data)
  # Sort out dependent type (factor)
  data[[depend]] <- as.factor(data[[depend]])
  
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
  }
  return(model)
}

estimate_yearly_zip <- function(data, formula, include_weights = FALSE, depend) {
  
  # Replace missing values (util func)
  data = replace.missing(data)
  
  # Some more outcome specific processing
  if(depend == 'ncigs') {
    data$ncigs[is.na(data$ncigs)] <- 0 # set NAs to 0. 
    data[which(data$ncigs!=0),]$ncigs <- (data[which(data$ncigs!=0),]$ncigs%/%5) + 1 # round up to nearest 5.
    data$ncigs <- as.integer(data$ncigs)
    print('Prepared ncigs for estimation')
  } else if(depend == 'alcohol_spending') {
    data$alcohol_spending <- data$alcohol_spending %/% 50 # round to nearest 50
    data$alcohol_spending <- as.integer(data$alcohol_spending)
  }
  
  # grep through the formula for the variables to keep before doing complete cases
  # this is because complete cases on the whole dataset removes every row
  # grepl returns true if string found
  
  #data <- data[complete.cases(data),]
  
  if(include_weights) {
    model <- zeroinfl(formula = formula,
                      data = data,
                      dist = 'pois',
                      weights = weight)
  } else {
    model <- zeroinfl(formula = formula,
                      data = data,
                      dist = 'pois')
  }
  return(model)
}



################ Main Run Loop ################

run_yearly_models <- function(transitionDir_path, transitionSourceDir_path, mod_def_name, data) {
  
  ## Read in model definitions from file including formula and model type (OLS,CLM,etc.)
  modDef_path = paste0(transitionSourceDir_path, mod_def_name)
  modDefs <- file(description = modDef_path, open="r", blocking = TRUE)
  
  # read file
  repeat{
    def = readLines(modDefs, n = 1) # Read one line from the connection.
    if(identical(def, character(0))){break} # If the line is empty, exit.
    
    ## Get model parameters
    #model_params <- digest_params(def)
    #dependent <- model_params[[1]]
    #independents <- model_params[[2]]
    #form <- model_params[[3]]
    
    # Get model type
    split1 <- str_split(def, pattern = " : ")[[1]]
    mod.type <- split1[1]
    
    # Get dependent and independents
    split2 <- str_split(split1[2], pattern = " ~ ")[[1]]
    dependent <- split2[1]
    independents <- split2[2]
    
    # formula
    form <- as.formula(split1[2])
    #print(form)
    
    #print(paste0('Dependent: ', dependent))
    #print(paste0('Independents: ', independents))
    #print(paste0('Formula: ', form))
    
    ## Yearly model estimation loop
    # Need to construct dataframes for each year that have independents from time T and dependents from time T+1
    year.range <- min(data$time):(max(data$time) - 1)
    # set up output directory
    out.path1 <- paste0(transitionDir_path, dependent, '/')
    out.path2 <- paste0(out.path1, tolower(mod.type), '/')
    create.if.not.exists(out.path1)
    create.if.not.exists(out.path2)
    
    print(paste0('Starting for ', dependent, '...'))
    
    for(year in year.range) {
      
      ## dependent year data is always year + 1 unless data requires something different
      # (as in neighbourhood estimation, does a t+3 model due to data)
      depend.year <- year + 1
      
      ## Some models don't run in certain years (data issues) so break here
      # nutrition_quality only estimated for 2018
      if(dependent == 'nutrition_quality' & year != 2018) { next }
      # labour_state only estimated for 2018
      if(dependent == 'education_state' & year != 2018) { next }
      # loneliness only estimated for waves starting 2017 and 2018
      if(dependent == 'loneliness' & !year %in% c(2017, 2018)) { next }
      # neighbourhood only estimated for wave 2011 and 2014
      if(dependent == 'neighbourhood_safety' & !year %in% c(2011, 2014)) { next }
      if(dependent == 'neighbourhood_safety'){ depend.year <- year + 3 } # set up 3 year horizon
      # tobacco model only estimated for 2013 onwards
      if(dependent == 'ncigs' & year < 2013) { next }
      #TODO: Maybe copy values from wave 2 onto wave 1? Assuming physical health changes slowly?
      # SF_12 predictor (physical health score) not available in wave 1
      if(dependent == 'SF_12' & year == 2009) { next }
      
      print(paste0('Starting estimation for ', dependent, ' in ', year))
      
      # independents from time T (current) with dependent removed
      indep.df <- data %>% filter(time == year) %>% select(-.data[[dependent]])
      # dependent from T+1
      depen.df <- data %>% filter(time == depend.year) %>% select(pidp, .data[[dependent]])
      # smash them together
      merged <- merge(depen.df, indep.df, by='pidp')
      
      # no weight var in 2009 (wave 1)
      if(year == 2009) {
        use.weights <- FALSE
      } else {
        use.weights <- TRUE
      }
      
      
      ## Different model types require different functions
      if(tolower(mod.type) == 'ols') {
        
        model <- estimate_yearly_ols(data = merged, 
                                     formula = form, 
                                     include_weights = use.weights)
        
      } else if(tolower(mod.type) == 'clm') {
        
        # set ordinal dependent to factor
        model <- estimate_yearly_clm(data = merged, 
                                     formula = form, 
                                     include_weights = use.weights, 
                                     depend = dependent)
        
      } else if(tolower(mod.type) == 'nnet') {
        
        model <- estimate_yearly_nnet(data = merged, 
                                      formula = form, 
                                      include_weights = use.weights, 
                                      depend = dependent)
        
      } else if(tolower(mod.type) == 'zip') {
        
        model <- estimate_yearly_zip(data = merged,
                                     formula = form,
                                     include_weights = use.weights,
                                     depend = dependent)
        
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


################ Execute Script ################

# Set paths
dataDir <- 'data/final_US/'
transitionDir <- 'data/transitions/'
transSourceDir <- 'minos/transitions/'
modDefFilename <- 'model_definitions_NEW.txt'

# Load input data (final_US/)
filelist <- list.files(dataDir)
filelist <- paste0(dataDir, filelist)
data <- do.call(rbind, lapply(filelist, read.csv))

run_yearly_models(transitionDir, transSourceDir, modDefFilename, data)

print('Generated all transition models.')

