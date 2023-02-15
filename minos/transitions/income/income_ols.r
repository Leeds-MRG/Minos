source("minos/transitions/utils.R")
#library(texreg)

# Collect command line args from Makefile
#args = commandArgs()
# first 2 args are in positions 7 and 8 weirdly but still work
#dataDir <- paste0(args[7], '/final_US/')
#transitionDir <- args[8]
#transSourceDir <- args[9]

#debug dirs
dataDir <- 'data/final_US/'
transitionDir <- "data/transitions"
transSourceDir <- "minos/transitions"

# Load required packages
suppressPackageStartupMessages(require(stringr))
suppressPackageStartupMessages(require(readr))
suppressPackageStartupMessages(require(tidyverse))

# Load input data (composite_US/)
filelist <- list.files(dataDir)
filelist <- paste0(dataDir, filelist)
data <- do.call(rbind, lapply(filelist, read.csv))

""
estimate_transition_model <- function(data, formula) {

  # Now fit the model
  model <- lm(formula, data = data)

  return(model)
}

run_models <- function(transitionDir_path, transitionSourceDir_path) {

  modDef_path = paste0(transitionSourceDir_path, '/model_definitions.txt')

  # Model Definitions
  modDefs <- file(description = modDef_path, open="r", blocking = TRUE)

  repeat{
    def = readLines(modDefs, n = 1) # Read one line from the connection.
    if(identical(def, character(0))){break} # If the line is empty, exit.

    # Work out the dependant and independants from the formula from txt file
    split <- str_split(def, pattern = " ~ ")[[1]]
    dependant <- split[1]
    independants <- split[2]

    # formula
    form <- as.formula(def)
    # model estimation
    model <- estimate_transition_model(data = data, formula = form)
    # coefficients for checking and debugging
    # getting coefficients
    coefs <- as.data.frame(model$coefficients)
    coefs <- data.frame(Variables=row.names(coefs), coefs)
    rownames(coefs) <- NULL
    # save model & coefficients to file
    write_csv(coefs, path = paste0(transitionDir_path ,'/', dependant ,'_coefficients.txt'))
    saveRDS(model, file=paste0(transitionDir_path ,'/', dependant ,'.rds'))
  }

  # close and remove connection object from memory
  close(modDefs)
  rm(modDefs)
}

#run_models(transitionDir, transSourceDir)


estimate_yearly_ols_model <- function(data, formula, include_weights = FALSE) {

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


run_yearly_models <- function(transitionDir_path, transitionSourceDir_path, data) {

  #modDef_path = paste0(transitionDir, '/model_definitions.txt')
  modDef_path = paste0(transitionSourceDir_path, '/model_definitions.txt')

  # Model Definitions
  modDefs <- file(description = modDef_path, open="r", blocking = TRUE)

  repeat{
    def = readLines(modDefs, n = 1) # Read one line from the connection.
    if(identical(def, character(0))){break} # If the line is empty, exit.

    # Work out the dependent and independents from the formula from txt file
    split <- str_split(def, pattern = " ~ ")[[1]]
    dependent <- "hh_income"
    independents <- split[2]
      
    # This has been edited slightly by Rob to allow redefinition of independent variables to name 'y'.
    # If hh_income is used as a lagged dependent variable need to load hh_income for left and right side but can't have the same name in the formula.
    # Overriding dependent variable hh_income on the left side to y.
    # Note in model_definitions.txt hh_income is declared on left and right side of formula. 
    form <- paste0(dependent, "_next ~ ")
    form <- as.formula(paste0(form, independents))
    
    # old formula calculation. take directly from txt.
    #form <- as.formula(def)
    
    # yearly model estimation
    ## Need to construct dataframes for each year that have independents from time T and dependents from time T+1
    #year.range <- min(data$time):(max(data$time) - 1)
    year.range <- max(data$time-2):(max(data$time) - 1) # Rob changed this to just run the 2018-2019 models for speed. 
    # set up list
    model.list <- list()
    # set up output directory
    out.path <- paste0(transitionDir_path, '/', dependent)
    create.if.not.exists(out.path)
    for(year in year.range) {
      # independents from time T (current) with dependent removed
      indep.df <- data %>% filter(time == year)
      # dependent from T+1
      depen.df <- data %>% filter(time == year + 1) %>% select(pidp, .data[[dependent]])
      # change dependent variable to y. Allows for using time lagged dependen variable hh_income.
      depen.df$hh_income_next <- depen.df$hh_income
      depen.df <- depen.df[, c("hh_income_next", "pidp")]
      # smash them together
      merged <- merge(depen.df, indep.df, by='pidp')

      # no weight var in 2009 (wave 1)
      if(year == 2009) {
        use.weights <- FALSE
      } else {
        use.weights <- TRUE
      }

      # Estimate model using this data
      model <- estimate_yearly_ols_model(data = merged, formula = form, include_weights = use.weights)

      # getting coefficients for checking and debugging
      coefs <- as.data.frame(model$coefficients)
      coefs <- data.frame(Variables=row.names(coefs), coefs)
      rownames(coefs) <- NULL

      # save model & coefficients to file (in their own folder)
      write_csv(coefs, file = paste0(out.path, '/', dependent, '_', year, '_', year+1, '_coefficients.txt'))
      saveRDS(model, file=paste0(out.path, '/', dependent, '_', year, '_', year+1, '.rds'))
      

    }
    test_path <- "data/transitions/test"
    create.if.not.exists(test_path)
    income.testfile.name <- paste0(test_path, '/', dependent, '_', year, '_', year+1, '.rds')
    saveRDS(model, file=income.testfile.name)
    print("Saved to: ")
    print(income.testfile.name)
    # Test texreg conversion of regression coefficient outputs to html.
    # Only doing one year of transitions for now..
    # Assume file is run in root directory (../../..). 
    #htmlreg(model, file='docsrc/Coefficients/test_income_OLS_coefficients.html')
  }

  
  # close and remove connection object from memory
  close(modDefs)
  rm(modDefs)
}

run_yearly_models(transitionDir, transSourceDir, data = data)

print("Income models estimated and saved")
