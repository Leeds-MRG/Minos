################ ESTIMATING TRANSITION MODELS FOR MINOS ################
# Author: Luke Archer
# Date: 01/06/23
#
# This script will be responsible for estimating any and all longitudinal transition models
# for use in the MINOS microsimulation.
# At the time of writing we estimate 1 different model type (GEE)
# and each of these will require some specific processing. Therefore each 
# model type will have its own function for the preprocessing, and we will have
# a main function to read in the parameters from model_definitions.txt and 
# execute the loop.
########################################################################

source("minos/transitions/utils.R")
source("minos/transitions/transition_model_functions.R")

require(argparse)
require(tidyverse)
require(stringr)
require(texreg)
require(dplyr)

###################################
# Main loop for longitudinal models 
###################################

run_longitudinal_models <- function(transitionDir_path, transitionSourceDir_path, mod_def_name, data, mode)
{
  # process is much simpler here than the yearly models. 
  # get model type and some data frame containing X years of data.
  # fit models to this grand data frame.
  modDef_path = paste0(transitionSourceDir_path, mod_def_name)
  modDefs <- file(description = modDef_path, open="r", blocking = TRUE)
  
  valid_longitudnial_model_types <- c("LMM", "LMM_DIFF", "GLMM", "GEE_DIFF","ORDGEE", "CLMM")
  
  data[which(data$ncigs==-8), 'ncigs'] <- 0
  
  
  repeat{
    def = readLines(modDefs, n = 1) # Read one line from the connection.
    if(identical(def, character(0))){break} # If the line is empty, exit.
    
    # Get model type
    split1 <- str_split(def, pattern = " : ")[[1]]
    mod.type <- split1[1]
    if(!is.element(mod.type, valid_longitudnial_model_types))
    {
      print(paste0("WARNING. model ", paste0(mod.type, " not valid for longitudinal models. Skipping..")))
      next
    }# skip this iteration if model not in valid types. 
    

    # Get dependent and independents
    split2 <- str_split(split1[2], pattern = " ~ ")[[1]]
    dependent <- split2[1]
    independents <- split2[2]
    

    ## Yearly model estimation loop
    # Need to construct dataframes for each year that have independents from time T and dependents from time T+1
    if(mode == 'cross_validation') {
      year.range <- seq(min(data$time) , (max(data$time)))
    } else {
      year.range <- seq(max(data$time) - 5, (max(data$time)))
      #year.range <- seq(min(data$time), (max(data$time) - 1)) # fit full range for model of models testing purposes
    }
    

    # set up output directory
    out.path1 <- paste0(transitionDir_path, dependent, '/')
    out.path2 <- paste0(out.path1, tolower(mod.type), '/')
    create.if.not.exists(out.path1)
    create.if.not.exists(out.path2)
    
    print(paste0('Starting for ', dependent, '...'))
    
    # no weight var in 2009 (wave 1)
    use.weights <- FALSE
    # TODO strange behaviour using weights for gees/glmms. Needs scaling? disabling for now..
    #if(year == 2009) {
    #  use.weights <- FALSE
    #} else {
    #  use.weights <- TRUE
    #}
    
    if (dependent == "SF_12") {
      do.reflect = TRUE # only SF12 continuous data is reflected to be left skewed. 
    }
    else {
      do.reflect=FALSE
    }
    
    if (dependent == "SF_12" || dependent == "hh_income") {
      do.yeo.johnson = T #
    }
    else {
      do.yeo.johnson = F
    }
    
    # experimental ordinal long models. ignore. 
    # if (mod.type == "ORDGEE") { 
    #   temp.dependent <- paste0("ordered(", dependent, ")") # make dependent variable into ordered factor.
    #   formula.string <- paste0(temp.dependent, " ~ ", independents)
    #   form <- as.formula(formula.string)      
    # } 
    # else if (mod.type == "CLMM") {
    #   formula.string <- paste0(dependent, " ~ ", independents)
    #   form <- as.formula(formula.string)      
    # } else {
    #   formula.string <- paste0(dependent, " ~ ", independents)
    #   form <- as.formula(formula.string)
    # }
    

    # differencing data for difference models using dplyr lag.
    # NOTE NEED TO UPDATE MODEL DEFINITIONS TO HAVE _DIFF IN RESPONSE VARIABLE NAME. 
    if (tolower(mod.type) == "lmm_diff")  {
      data <- data %>%
        group_by(pidp) %>%
        #mutate(diff = .data[[dependent]] - lag(.data[[dependent]], order_by = time)) %>%
        mutate(diff = lead(.data[[dependent]], order_by = time) - .data[[dependent]]) %>%
        rename_with(.fn = ~paste0(dependent, '_', .), .cols = diff)  # add the dependent as prefix to the calculated diff
        # update model formula with _diff variable. 
        dependent <-  paste0(dependent, "_diff")
        formula.string <- paste0(dependent, " ~ ", independents)
        form <- as.formula(formula.string) 
        }

    # if using glmms need to be careful which time the outcome variable is from.
    # for nutrition quality and SF12 using previous wave information to predict next 
    # state so create response income_new that is the lead value.
    # I.E. using 2019 information to predict income_new values from 2020.
    # For SF12 predicting current state given changes in all other information and previous SF12 value. 
    # I.E. using 2020 information and 2019 SF12 to estimate 2020 SF12.
    # We have SF_12_last in the model formula for 2019 SF12. 
    if (dependent == "nutrition_quality" || dependent == "hh_income")  {
      # get leading nutrition/income value and label with _new.
       data <- data %>%
         group_by(pidp) %>%
         #mutate(diff = .data[[dependent]] - lag(.data[[dependent]], order_by = time)) %>%
         mutate(new = lead(.data[[dependent]], order_by = time)) %>%
         rename_with(.fn = ~paste0(dependent, '_', .), .cols = new)  # add the dependent as prefix to the calculated diff
         dependent <-  paste0(dependent, "_new")
         formula.string <- paste0(dependent, " ~ ", independents)
         form <- as.formula(formula.string) 
       }
    else if (dependent == "SF_12")  {
      # get lagged SF12 value and label with _last.
      data <- data %>%
        group_by(pidp) %>%
        #mutate(diff = .data[[dependent]] - lag(.data[[dependent]], order_by = time)) %>%
        mutate(last = lag(.data[[dependent]], order_by = time)) %>%
        rename_with(.fn = ~paste0(dependent, '_', .), .cols = last)  # add the dependent as prefix to the calculated diff
      # data <- data %>%
      #   group_by(pidp) %>%
      #   mutate(diff = .data[[dependent]] - lag(.data[[dependent]], order_by = time)) %>%
      #   rename_with(.fn = ~paste0(dependent, '_', .), .cols = diff)
      # 
      formula.string <- paste0(dependent, " ~ ", independents)
      form <- as.formula(formula.string)
      }
    # get only required variables and sort by pidp/time. 
    df <- data[, append(all.vars(form), c("time", 'pidp', 'weight'))]
    sorted_df <- df[order(df$pidp, df$time),]
    
    # function call and parameters based on model type. 
    if(tolower(mod.type) == 'glmm') {
      #
      model <- estimate_longitudinal_glmm(data = sorted_df,
                                          formula = form, 
                                          include_weights = use.weights, 
                                          depend = dependent,
                                          reflect=do.reflect,
                                          yeo_johnson = do.yeo.johnson)
      
    } else if(tolower(mod.type) == 'lmm') {
      
      model <- estimate_longitudinal_lmm(data = sorted_df,
                                        formula = form, 
                                        include_weights = use.weights, 
                                        reflect = do.reflect,
                                        yeo_johnson = F,
                                        depend = dependent)
      
    } else if(tolower(mod.type) == 'lmm_diff') {
      
      model <- estimate_longitudinal_lmm_diff(data = sorted_df,
                                            formula = form, 
                                            include_weights = use.weights, 
                                            reflect = FALSE,
                                            depend = dependent,
                                            yeo_johnson = TRUE)
      
    } else if (tolower(mod.type) == "ordgee") {
      
      model <- estimate_longitudinal_mlogit_gee(data = sorted_df,
                                                  formula = form, 
                                                  include_weights = FALSE, 
                                                  depend = dependent)
      
    } else if (tolower(mod.type) == "clmm") {
      
      model <- estimate_longitudinal_clmm(data = sorted_df,
                                          formula = form, 
                                          depend = dependent)
      
    }
    
    write_coefs <- F
    if (write_coefs)
    {
      texreg_file <- paste0(out.path2, "coefficients", dependent, '_', mod.type, '.rds')
      texreg(model, file=texreg_file, stars = c(0.001, 0.01, 0.05, 0.1), digits=4, dcolumn=T, tabular=T)
    }
    saveRDS(model, file=paste0(out.path2, dependent, "_", mod.type, '.rds')) # shorter file name with no years..
    print(paste0(mod.type, ' model for ', dependent, ' generated for years ', min(year.range), ' - ', max(year.range)))
    print(paste0("Finished for ", dependent, ", mod type ", mod.type, '.'))
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
#cross_valdation <- T

# Set different paths for scotland mode, cross-validation etc.
if(scotland.mode) {
  print('Estimating transition models in Scotland mode')
  dataDir <- 'data/scotland_US/'
  modDefFilename <- 'model_definitions_SCOTLAND.txt'
  mode <- 'scotland'
  transitionDir <- paste0(transitionDir, 'scotland/')
  create.if.not.exists(transitionDir)
} else if(cross_validation) {
  print('Estimating cross validation longitudinal models')
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
    
    run_longitudinal_models(out.dir, transSourceDir, modDefFilename, combined.data, mode)
  }
} else {
  # Load input data depending on mode and previously set params (final_US/)
  filelist <- list.files(dataDir,
                         include.dirs = FALSE,
                         full.names = TRUE,
                         pattern = '[0-9]{4}_US_cohort.csv')
  data <- do.call(rbind, lapply(filelist, read.csv))
  
  run_longitudinal_models(transitionDir, transSourceDir, modDefFilename, data, mode)
}
  
print("Generated all longitudinal transition models")

# 
# whole.pop.mode.file <- paste0(transitionDir, 'whole_population_mode.txt')
# scotland.mode.file <- paste0(transitionDir, 'scotland_mode.txt')
# 
# # For output and graceful handling with Makefile
# if(args$scotland) {
#   if(file.exists(whole.pop.mode.file)) { # if the other mode file is there, remove
#     file.remove(whole.pop.mode.file)
#   }
#   file.create(paste0(transitionDir, 'scotland_mode.txt'))
# } else {
#   if(file.exists(scotland.mode.file)) { # if the other mode file is there, remove
#     file.remove(scotland.mode.file)
#   }
#   file.create(paste0(transitionDir, 'whole_population_mode.txt'))
# }
