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
source("minos/transitions/transition_model_functions.R")

require(argparse)
require(tidyverse)
require(stringr)
require(texreg)

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

################ Main Run Loop ################

run_yearly_models <- function(transitionDir_path,
                              transitionSourceDir_path,
                              mod_def_name,
                              data,
                              mode) {

  ## Read in model definitions from file including formula and model type (OLS,CLM,etc.)
  modDef_path = paste0(transitionSourceDir_path, mod_def_name)
  modDefs <- file(description = modDef_path, open="r", blocking = TRUE)
  
  ## Set some factor levels because R defaults to using alphabetical ordering
  data$housing_quality <- factor(data$housing_quality, 
                                 levels = c('Low',
                                            'Medium',
                                            'High'))
  data$S7_housing_quality <- factor(data$S7_housing_quality, 
                                 levels = c('No to all', 
                                            'Yes to some', 
                                            'Yes to all'))
  data$S7_neighbourhood_safety <- factor(data$S7_neighbourhood_safety,
                                    levels = c('Often', 
                                               'Some of the time', 
                                               'Hardly ever'))
  data$S7_labour_state <- factor(data$S7_labour_state,
                                 levels = c('FT Employed',
                                            'PT Employed',
                                            'Job Seeking',
                                            'FT Education',
                                            'Family Care',
                                            'Not Working'))

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
    #if (tolower(mod.type) == 'ols_diff') {
    #  data <- data %>%
    #    group_by(pidp) %>%
    #    mutate(diff = .data[[dependent]] - lag(.data[[dependent]], order_by = time)) %>%
    #    rename_with(.fn = ~paste0(dependent, '_', .), .cols = diff)  # add the dependent as prefix to the calculated diff
    #}

    ## Yearly model estimation loop

    # Set the time span to estimate models for differently for cross_validation
    # crossval needs to start in 2010, whereas default model can have reduced timespan
    # avoid first year as data is weird and missing in a lot of cases
    if(mode == 'cross_validation') {
      year.range <- seq(max(data$time) - 3, (max(data$time)-1))
    } else {
      year.range <- seq(max(data$time) - 6, (max(data$time) - 1))
      #year.range <- seq(min(data$time), (max(data$time) - 1)) # fit full range for model of models testing purposes
    }

    # set up output directory
    out.path1 <- paste0(transitionDir_path, dependent, '/')
    out.path2 <- paste0(out.path1, tolower(mod.type), '/')
    create.if.not.exists(out.path1)
    create.if.not.exists(out.path2)

    print(paste0('Starting for ', dependent, '...'))

    # add 'next_' keyword to dependent variable
    formula.string.orig <- paste0('next_', formula.string.orig)
    
    valid_yearly_model_types = c("NNET", "OLS", "OLS_DIFF", "CLM", "GLM", "ZIP", "LOGIT", "OLS_YJ")
    
    for(year in year.range) {
      if(!is.element(mod.type, valid_yearly_model_types))
        {
        print(paste0("WARNING. model ", paste0(mod.type, " not valid for yearly models. Skipping..")))
        next
        }# skip this iteration if model not in valid types. 
      
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
      #if(dependent == 'neighbourhood_safety' & !year %in% c(2011, 2014, 2017)) { next }
      if(grepl('neighbourhood_safety', dependent) & !year %in% c(2011, 2014, 2017)) { next }
      if(grepl('neighbourhood_safety', dependent)){ depend.year <- year + 3 } # set up 3 year horizon
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
        select(pidp, all_of(dependent))

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
      #print(formula.string)
      # Now make string into formula
      form <- as.formula(formula.string)



      ## Different model types require different functions
      if(tolower(mod.type) == 'ols') {

        model <- estimate_yearly_ols(data = merged,
                                     formula = form,
                                     include_weights = use.weights,
                                     depend = next.dependent)

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

      } else if (tolower(mod.type)=="logit") {
        model <- estimate_yearly_logit(data = merged,
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
      # writing tex table of coefficients. easy writing for papers and documentation. 
      write_coefs <- F
      if (write_coefs)
      {
        texreg_file <- paste0(out.path2, "coefficients", dependent, '_', year, '_', depend.year, '.rds')
        texreg(model, file=texreg_file, stars = c(0.001, 0.01, 0.05, 0.1), digits=4, dcolumn=T, tabular=T)
      }
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

#TODO: Refactor all this stuff into a single string argument. Can avoid a bit of
# boilerplate and make further development easier.
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

parser$add_argument('-d',
                    '--default',
                    action='store_true',
                    dest='default',
                    default=FALSE,
                    help='Run in default mode. This is the default MINOS 
                    experiment, where the models estimated in this mode 
                    include hh_income as the policy lever, SF12 MCS and
                    PCS as the outcomes of interest, and a series of pathways
                    from hh_income to both outcomes.')

parser$add_argument('-s7',
                    '--sipher7',
                    action='store_true',
                    dest='SIPHER7',
                    default=FALSE,
                    help='Run the SIPHER7 experiment models. In this mode, 
                    only the transition models needed to run the SIPHER7
                    equivalent income experiment are estimated. This includes
                    hh_income as the policy lever, then all the SIPHER7
                    variable models, as well as some demographic models such
                    as education state.')

args <- parser$parse_args()

scotland.mode <- args$scotland
cross_validation <- args$crossval
default <- args$default
sipher7 <- args$SIPHER7

## RUNTIME ARGS
transSourceDir <- 'minos/transitions/'
dataDir <- 'data/final_US/'
modDefFilename <- 'model_definitions_default.txt'
transitionDir <- 'data/transitions/'
mode <- 'default'

create.if.not.exists(transitionDir)


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
  dataDir <- 'data/final_US/cross_validation/'
  mode <- 'cross_validation'
  transitionDir <- paste0(transitionDir, 'cross_validation/')
  create.if.not.exists(transitionDir)
} else if(default) {
  print('Estimating transition models in whole population mode')
}

if(sipher7) {
  print('Estimating models for SIPHER7 Equivalent Income experiment')
  modDefFilename <- 'model_definitions_S7.txt'
}



# we need to generate 5 sets of transition models, based on 4/5 batches of data
# so version 1 uses batches 2,3,4, and 5 for trans models and simulates using batch 1
if (mode == 'cross_validation') {
  print("Estimating transitions in batch mode")
  for (i in 1:5) {
    print(paste0("Creating version ", i, " transition models"))
    # set up batch vector and remove one element each loop
    batch.vec <- c(1,2,3,4,5)
    batch.vec <- batch.vec[!batch.vec %in% i]
    
    # now start new loop to list files in each batch and read data into a single object.
    # open a dataframe for collecting up multiple batches together
    combined.data <- data.frame()
    for (j in batch.vec) {
      batch.path <- paste0(dataDir, 'batch', j, '/')
      batch.filelist <- list.files(batch.path,
                                   include.dirs = FALSE,
                                   full.names = TRUE,
                                   pattern = '[0-9]{4}_US_cohort.csv')
      batch.dat <- do.call(rbind, lapply(batch.filelist, read.csv))
      combined.data <- rbind(combined.data, batch.dat)
    }
    rm(batch.dat, batch.path, batch.filelist)
    
    out.dir <- paste0(transitionDir, 'version', i, '/')
    create.if.not.exists(out.dir)
    
    run_yearly_models(out.dir, transSourceDir, modDefFilename, combined.data, mode)
  }
} else {
  # Load input data depending on mode and previously set params (final_US/)
  filelist <- list.files(dataDir,
                         include.dirs = FALSE,
                         full.names = TRUE,
                         pattern = '[0-9]{4}_US_cohort.csv')
  data <- do.call(rbind, lapply(filelist, read.csv))
  
  run_yearly_models(transitionDir, transSourceDir, modDefFilename, data, mode)
}

print('Generated transition models.')
