# Collect command line args from Makefile
args = commandArgs()
# first 2 args are in positions 7 and 8 weirdly but still work
dataDir <- paste0(args[7], '/composite_US/')
transitionDir <- args[8]

print(getwd())
# Load required packages
require(stringr)
require(readr)

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

run_models <- function(transitionDir_path) {

  modDef_path = paste0(transitionDir_path, '/model_definitions.txt')

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

run_models(transitionDir)
