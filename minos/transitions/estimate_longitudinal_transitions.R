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

###################################
# Main loop for longitudinal models 
###################################

run_longitudinal_models <- function(transitionDir_path, transitionSourceDir_path, mod_def_name, data)
{
  # process is much simpler here than the yearly models. 
  # get model type and some data frame containing X years of data.
  # fit models to this grand data frame.
  modDef_path = paste0(transitionSourceDir_path, mod_def_name)
  modDefs <- file(description = modDef_path, open="r", blocking = TRUE)
  
  valid_longitudnial_model_types <- c("GEE", "LMM", "LMM_DIFF", "GLMM", "GEE_YJ", "GEE_YJ_GAMMA", "GEE_DIFF","ORDGEE", "CLMM")
  
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
    year.range <- seq(max(data$time)-6, (max(data$time)))
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
      do.reflect = TRUE
    }
    else {
      do.reflect=FALSE
    }
    
    if (dependent == "SF_12" && mod.type == "GEE"){
      temp.dependent <- "I(max(SF_12) - SF_12 + 0.001)"
      formula.string <- paste0(temp.dependent, " ~ ", independents)
      form <- as.formula(formula.string)     
    } 
    else if (dependent == "hh_income" && mod.type == "GEE") {
      temp.dependent <- "I(hh_income - min(hh_income) + 0.001)" # shift income to left to avoid negative values.
      formula.string <- paste0(temp.dependent, " ~ ", independents)
      form <- as.formula(formula.string)      
    } 
    else if (dependent == "hh_income" && mod.type == "GEE_DIFF") {
      temp.dependent <-  paste0(dependent, "_diff") # shift income to left to avoid negative values.
      formula.string <- paste0(temp.dependent, " ~ ", independents)
      form <- as.formula(formula.string)      
    }
    else if (mod.type == "LMM" && dependent != "SF_12") {
      temp.dependent <-  paste0(dependent, "_new") # shift income to left to avoid negative values.
      formula.string <- paste0(temp.dependent, " ~ ", independents)
      form <- as.formula(formula.string)      
    } 
    else if (mod.type == "LMM_DIFF") {
      temp.dependent <-  paste0(dependent, "_diff") # shift income to left to avoid negative values.
      formula.string <- paste0(temp.dependent, " ~ ", independents)
      form <- as.formula(formula.string)      
    } 
    
    else if (mod.type == "ORDGEE") {
      temp.dependent <- paste0("ordered(", dependent, ")") # make dependent variable into ordered factor.
      formula.string <- paste0(temp.dependent, " ~ ", independents)
      form <- as.formula(formula.string)      
    } 
    else if (mod.type == "CLMM") {
      formula.string <- paste0(dependent, " ~ ", independents)
      form <- as.formula(formula.string)      
    } 
    else{
      formula.string <- paste0(dependent, " ~ ", independents)
      form <- as.formula(formula.string)
    }
    

    # data frame needs sorting by pidp and time for gee to work.
    # get columns used by formula and sort them by pidp and time. 
    
    # differencing data for difference models using dplyr lag.
    if (tolower(mod.type) == 'gee_diff' || tolower(mod.type) == "lmm_diff")  {
      data <- data %>%
        group_by(pidp) %>%
        #mutate(diff = .data[[dependent]] - lag(.data[[dependent]], order_by = time)) %>%
        mutate(diff = lead(.data[[dependent]], order_by = time) - .data[[dependent]]) %>%
        rename_with(.fn = ~paste0(dependent, '_', .), .cols = diff)  # add the dependent as prefix to the calculated diff
    }

    # differencing data for difference models using dplyr lag.
    if (tolower(mod.type) == "lmm" && dependent == "hh_income")  {
      data <- data %>%
        group_by(pidp) %>%
        #mutate(diff = .data[[dependent]] - lag(.data[[dependent]], order_by = time)) %>%
        mutate(new = lead(.data[[dependent]], order_by = time)) %>%
        rename_with(.fn = ~paste0(dependent, '_', .), .cols = new)  # add the dependent as prefix to the calculated diff
    }
    if (tolower(mod.type) == "lmm" && dependent == "SF_12")  {
      data <- data %>%
        group_by(pidp) %>%
        #mutate(diff = .data[[dependent]] - lag(.data[[dependent]], order_by = time)) %>%
        mutate(last = lag(.data[[dependent]], order_by = time)) %>%
        rename_with(.fn = ~paste0(dependent, '_', .), .cols = last)  # add the dependent as prefix to the calculated diff
    }
    
    df <- data[, append(all.vars(form), c("time", 'pidp', 'weight'))]
    sorted_df <- df[order(df$pidp, df$time),]
    
    if(tolower(mod.type) == 'glmm') {
      
      model <- estimate_longitudnial_glmm(data = sorted_df,
                                          formula = form, 
                                          include_weights = use.weights, 
                                          depend = dependent)
      
    } else if(tolower(mod.type) == 'lmm') {
      if ( dependent == "hh_income") {
        dependent <- paste0(dependent, "_new")
      }
      model <- estimate_longitudinal_lmm(data = sorted_df,
                                        formula = form, 
                                        include_weights = use.weights, 
                                        reflect = do.reflect,
                                        depend = dependent)
      
    } else if(tolower(mod.type) == 'lmm_diff') {
      
      model <- estimate_longitudinal_lmm_diff(data = sorted_df,
                                            formula = form, 
                                            include_weights = use.weights, 
                                            reflect = FALSE,
                                            depend = paste0(dependent, '_diff'))
      
    } else if(tolower(mod.type) == 'gee') {
      
      model <- estimate_longitudnial_gamma_gee(data = sorted_df,
                                               formula = form, 
                                               include_weights = FALSE, 
                                               depend = dependent,
                                               reflect = do.reflect)
    } else if(tolower(mod.type) == 'gee_diff') {
      
        model <- estimate_longitudnial_gaussian_gee_diff(data = sorted_df,
                                                 formula = form, 
                                                 include_weights = FALSE, 
                                                 depend = paste0(dependent, '_diff'))

    } else if (tolower(mod.type) == "gee_yj") {
      
      model <- estimate_longitudnial_yj_gaussian_gee(data = sorted_df,
                                               formula = form, 
                                               include_weights = FALSE, 
                                               depend = dependent,
                                               reflect = do.reflect)
      
    } else if (tolower(mod.type) == "gee_yj_gamma") {
      
      model <- estimate_longitudnial_yj_gamma_gee(data = sorted_df,
                                                     formula = form, 
                                                     include_weights = FALSE, 
                                                     depend = dependent,
                                                     reflect = do.reflect)
      
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

run_longitudinal_models(transitionDir, transSourceDir, modDefFilename, data)

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
