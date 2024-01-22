library(mice)
library(here)
library(argparse)
library(logr)
source("minos/utils_datain.R")
source("minos/transitions/utils.R")

main <- function(n_imputations, iterations_per_imputation){
  
  log_file_path <- file.path(here::here("data", "mice_US"), "test.log")
  create.if.not.exists(paste0(here::here("data"),"/mice_US/"))
  lf <- log_open(log_file_path)
  log_print("loading data.")
  # load in all post LOCFcorrected data? maybe composite?
  # MICE impuation from notebook
  # save to individual waves.
  # get composite/complete case this data instead. I.E. slot into current pipeline and makes. 
  start.data <- read_all_UKHLS_waves(here::here("data/"), "composite_US") 
  start.data <- start.data[which(start.data$time>=2018),]
    
  mice_columns <- c("age", 
                    "region", 
                    #"heating", 
                    "job_sec", 
                    "ncigs",
                    "education_state",            
                    "ethnicity",
                    "loneliness",
                    "sex", 
                    "SF_12",
                    #"SF_12p",
                    #"smoker",
                    "nkids",       
                    "behind_on_bills",
                    "financial_situation",
                    "future_financial_situation",
                    "likely_move",
                    "ghq_depression",
                    "ghq_happiness",
                    "clinical_depression", 
                    "scsf1",
                    "health_limits_social",
                    #"hhsize",
                    #"housing_tenure",
                    #"urban", 
                    "housing_quality",
                    "hh_income",
                    "neighbourhood_safety",
                    "S7_labour_state",
                    "yearly_energy",
                    "nutrition_quality",
                    "job_hours",
                    "nkids_ind",
                    "housing_tenure",
                    "job_sector",
                    "marital_status"
                    #"hh_comp", 
                    #"marital_status"
  )
  
  other.data <- start.data[, !names(start.data) %in% mice_columns]
  mice.data <- start.data[, c(mice_columns)]
  mice.data <- replace.missing(mice.data)

  #cached <- TRUE
  #  print("Loading Cached MICE data.")
  #if (cached == TRUE) {
  #  mice.set <- readRDS("data/transitions/MICE_set.rds")
  #  final.mice.data <- complete(mice.set, 1)
  #  final.mice.data <- cbind(final.mice.data, other.data)
  #}
  #else 
  log_print("Starting MICE with parameters.")
  log_print("")
  log_print("Number of Imputated Populations: ")
  log_print(n_imputations)
  log_print("MICE iterations per imputed population: ")
  log_print(iterations_per_imputation)
  
  print("Starting MICE. Will take about 20 minutes on an arc4 node (subject to getting a node).")
  start.time <- Sys.time()
  
  if (n_imputations == 1) {
    mice_set <- mice(data = mice.data[, mice_columns],
                     m = n_imputations, maxit = iterations_per_imputation,
                     remove.collinear=T)
    final.mice.data <- complete(mice_set, 1)
  }
  else {
    mice_set <- futuremice(data = mice.data[,mice_columns],
                     m = n_imputations, maxit = iterations_per_imputation,
                     remove.collinear=T)
    final.mice.data <- complete(mice_set, 1)
  }
  
  end.time <- Sys.time()
  log_print("")
  log_print("Time Elapsed: ")
  log_print(end.time-start.time)
  log_print("")
  log_print("Adding other data back in")
  final.mice.data <- cbind(final.mice.data, other.data)   
  
  # adding other necessary components back in.
  save.path <- here::here("data", "mice_US/")
  # saving output data. 
  log_print("")
  log_print("MICE set saved to: ")
  log_print(save.path)
  save_raw_data_in(final.mice.data, save.path)
  log_print("MICE data saved to data/mice_US")
  log_close()
}#




parser <- ArgumentParser(description="MICE Imputation Script for MINOS.")
parser$add_argument('-n', '--n_imputed_populations', 
                    help='Number of MICE imputation experiments to run.')
parser$add_argument('-i', '--itererations_per_population',
                    help='How many iterations per imputed population?')

args <- parser$parse_args()
n_imputed_populations <- as.numeric(args$n_imputed_populations)
itererations_per_population <- as.numeric(args$itererations_per_population)

main(n_imputed_populations, itererations_per_population)
