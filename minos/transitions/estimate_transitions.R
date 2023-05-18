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

require(argparse) # read variables from command line.
require(tidyverse) # data manipulation
require(ordinal) # CLMs
require(nnet) # multinomial regression
require(stringr) #String parsing.
require(pscl) # ZIPs
# require(lme4) # GLMMs
# require(geepack) #GEEs
require(bestNormalize) #yeo johnson Normalise

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

estimate_yearly_ols <- function(data, formula, include_weights = FALSE, depend, transform = FALSE, reflect=FALSE) {
  
  if (reflect) 
  {
    max_value <- max(data[, c(depend)])
    data[, c(depend)] <- max_value - data[, c(depend)]
  }
  
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



################ Main Run Loop ################

run_yearly_models <- function(transitionDir_path, transitionSourceDir_path, mod_def_name, data) {
  
  ## Read in model definitions from file including formula and model type (OLS,CLM,etc.)
  modDef_path = paste0(transitionSourceDir_path, mod_def_name)
  modDefs <- file(description = modDef_path, open="r", blocking = TRUE)
  
  valid_yearly_model_types = c("NNET", "OLS", "CLM", "GLM", "ZIP", "LOGIT", "OLS_YJ", "OLS_REFLECT_YJ")
  
  # read file
  repeat{
    def = readLines(modDefs, n = 1) # Read one line from the connection.
    if(identical(def, character(0))){break} # If the line is empty, exit.
    
    # Get model type
    split1 <- str_split(def, pattern = " : ")[[1]]
    mod.type <- split1[1]
    if(!is.element(mod.type, valid_yearly_model_types)){next} # break if not in valid list of yearly models. e.g. GEE.
    
    # Get dependent and independents
    split2 <- str_split(split1[2], pattern = " ~ ")[[1]]
    dependent <- split2[1]
    independents <- split2[2]
    
    # formula
    formula.string.orig <- split1[2]
    
    ## Yearly model estimation loop
    # Need to construct dataframes for each year that have independents from time T and dependents from time T+1
    year.range <- seq(max(data$time)-5, (max(data$time) - 1))
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
      
      ## Some models don't run in certain years (data issues) so break here
      # nutrition_quality only estimated for 2018
      if(dependent == 'nutrition_quality' & !year %in% c(2014, 2016, 2018)) { next }
      # labour_state only estimated for 2018
      if(dependent == 'education_state' & year != 2018) { next }
      # loneliness only estimated for waves starting 2017 and 2018
      if(dependent == 'loneliness' & !year > 2016) { next }
      # neighbourhood only estimated for wave 2011 and 2014
      if(dependent == 'neighbourhood_safety' & !year %in% c(2011, 2014)) { next }
      if(dependent == 'neighbourhood_safety'){ depend.year <- year + 3 } # set up 3 year horizon
      # tobacco model only estimated for 2013 onwards
      if(dependent == 'ncigs' & year < 2013) { next }
      #TODO: Maybe copy values from wave 2 onto wave 1? Assuming physical health changes slowly?
      # SF_12 predictor (physical health score) not available in wave 1
      if(dependent == 'SF_12' & year == 2009) { next }
      
      print(paste0('Starting estimation for ', dependent, ' in ', year))
      
      # set up new dependent var name
      next.dependent <- paste0('next_', dependent)
      
      # independents from time T (current)
      indep.df <- data %>% 
        filter(time == year) %>%
        select(append(all.vars(as.formula(split1[2])), c("time", 'pidp', 'weight'))) # grab all vars in formula including universal variables. 
      
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
      
      
      ## For the SF_12 model alone, we need to modify the formula on the fly
      # as neighbourhood_safety, loneliness, nutrition_quality and ncigs are 
      # not present every year
      if(dependent == 'SF_12') {
        if(!year %in% c(2011, 2014, 2017)) {
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
      # Now make string into formula
      form <- as.formula(formula.string)
      
      
      ## Different model types require different functions
      if(tolower(mod.type) == 'ols') {
        
        model <- estimate_yearly_ols(data = merged, 
                                     formula = form, 
                                     include_weights = use.weights,
                                     depend = next.dependent)
        
      } else if(tolower(mod.type) == 'ols_yj') {
        
        model <- estimate_yearly_ols(data = merged, 
                                     formula = form, 
                                     include_weights = use.weights,
                                     depend = next.dependent,
                                     transform=TRUE)
        
      } else if(tolower(mod.type) == 'ols_reflect_yj') {
        
        model <- estimate_yearly_ols(data = merged, 
                                     formula = form, 
                                     include_weights = use.weights,
                                     depend = next.dependent,
                                     transform=TRUE,
                                     reflect=TRUE)
        
      } else if(tolower(mod.type) == 'clm') {
        
        # set ordinal dependent to factor
        model <- estimate_yearly_clm(data = merged,
                                     formula = form, 
                                     include_weights = use.weights, 
                                     depend = next.dependent)
        
      } else if(tolower(mod.type) == 'logit') {
        
        # set ordinal dependent to factor
        model <- estimate_yearly_logit(data = merged,
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


###################################
# Main loop for longitudinal models 
###################################

# run_longitudinal_models <- function(transitionDir_path, transitionSourceDir_path, mod_def_name, data)
# {
#   # process is much simpler here than the yearly models. 
#   # get model type and some data frame containing X years of data.
#   # fit models to this grand data frame.
#   modDef_path = paste0(transitionSourceDir_path, mod_def_name)
#   modDefs <- file(description = modDef_path, open="r", blocking = TRUE)
#   
#   valid_longitudnial_model_types = c("GEE", "GLMM")
#   
#   repeat{
#     def = readLines(modDefs, n = 1) # Read one line from the connection.
#     if(identical(def, character(0))){break} # If the line is empty, exit.
#     
#     # Get model type
#     split1 <- str_split(def, pattern = " : ")[[1]]
#     mod.type <- split1[1]
#     if(!is.element(mod.type, valid_longitudnial_model_types)){next} # break if not in valid list of longitudinal models. e.g. OLS.
#     
#     # Get dependent and independents
#     split2 <- str_split(split1[2], pattern = " ~ ")[[1]]
#     dependent <- split2[1]
#     independents <- split2[2]
#     
#     ## Yearly model estimation loop
#     # Need to construct dataframes for each year that have independents from time T and dependents from time T+1
#     year.range <- seq(max(data$time)-5, (max(data$time) - 1))
#     # set up output directory
#     out.path1 <- paste0(transitionDir_path, dependent, '/')
#     out.path2 <- paste0(out.path1, tolower(mod.type), '/')
#     create.if.not.exists(out.path1)
#     create.if.not.exists(out.path2)
#     
#     print(paste0('Starting for ', dependent, '...'))
#     
#     # no weight var in 2009 (wave 1)
#     use.weights <- FALSE
#     # TODO strange behaviour using weights for gees/glmms. Needs scaling? disabling for now..
#     #if(year == 2009) {
#     #  use.weights <- FALSE
#     #} else {
#     #  use.weights <- TRUE
#     #}
#     
#     if (dependent == "SF_12" && mod.type == "GEE"){
#       temp.dependent <- "I(max(SF_12) - SF_12 + 0.001)"
#       formula.string <- paste0(temp.dependent, " ~ ", independents)
#       form <- as.formula(formula.string)     
#     } else{
#       formula.string <- paste0(dependent, " ~ ", independents)
#       form <- as.formula(formula.string)
#     }
#     
#     # data frame needs sorting by pidp and time for gee to work.
#     
#     
#     
#     # get columns used by formula and sort them by pidp and time. 
#     df <- data[, append(all.vars(form), c("time", 'pidp', 'weight'))]
#     sorted_df <- df[order(df$pidp, df$time),]
#     
#     if(tolower(mod.type) == 'glmm') {
#       
#       # set ordinal dependent to factor
#       model <- estimate_longitudnial_glmm(data = sorted_df,
#                                           formula = form, 
#                                           include_weights = use.weights, 
#                                           depend = dependent)
#       
#     } else if(tolower(mod.type) == 'gee') {
#       
#       # set ordinal dependent to factor
#       model <- estimate_longitudnial_gamma_gee(data = sorted_df,
#                                                formula = form, 
#                                                include_weights = use.weights, 
#                                                depend = dependent)
#       
#     } 
#     
#     saveRDS(model, file=paste0(out.path2, dependent, "_", mod.type, '.rds')) # shorter file name with no years..
#     print(paste0(mod.type, ' model for ', dependent, ' generated for years ', min(year.range), ' - ', max(year.range)))
#     print(paste0("Finished for ", dependent, ", mod type ", mod.type, '.'))
#   }
#   # close and remove connection object from memory
#   close(modDefs)
#   rm(modDefs)
# }



################ Last Minute Data Prep & Execute Script ################


#### IMPORTANT!!
## Because some variables are not present in every wave (i.e. neighbourhood_safety, loneliness) we need to handle this.
## There is a decent solution that comes partly because we are estimating a different model for every year
## We need to check when we are in the correct years, and remove a string subset from the formula
## i.e. in 2015 no neighbourhood_safety, so remove 'relevel(factor(neighbourhood_safety), ref = '1')'


## Argparse stuff
parser = ArgumentParser()
parser$add_argument('-s', '--scotland', action='store_true', dest='scotland', 
                    default=FALSE,
                    help='Run in Scotland mode - MORE HELP NEEDED HERE')
args <- parser$parse_args()

scotland.mode <- args$scotland

# Set paths (handle scotland mode here)
if(scotland.mode) {
  dataDir <- 'data/scotland_US/'
  modDefFilename <- 'model_definitions_SCOTLAND.txt'
} else {
  dataDir <- 'data/final_US/'
  modDefFilename <- 'model_definitions.txt'
}

transitionDir <- 'data/transitions/'
transSourceDir <- 'minos/transitions/'



# Load input data (final_US/)
filelist <- list.files(dataDir)
filelist <- paste0(dataDir, filelist)
data <- do.call(rbind, lapply(filelist, read.csv))

run_yearly_models(transitionDir, transSourceDir, modDefFilename, data)
print('Generated all yearly transition models.')

run_longitudinal_models(transitionDir, transSourceDir, modDefFilename, data)
print("Generated all longitudinal transition models")


whole.pop.mode.file <- paste0(transitionDir, 'whole_population_mode.txt')
scotland.mode.file <- paste0(transitionDir, 'scotland_mode.txt')

# For output and graceful handling with Makefile
if(args$scotland) {
  if(file.exists(whole.pop.mode.file)) { # if the other mode file is there, remove
    file.remove(whole.pop.mode.file)
  }
  file.create(paste0(transitionDir, 'scotland_mode.txt'))
} else {
  if(file.exists(scotland.mode.file)) { # if the other mode file is there, remove
    file.remove(scotland.mode.file)
  }
  file.create(paste0(transitionDir, 'whole_population_mode.txt'))
}