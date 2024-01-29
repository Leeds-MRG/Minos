library(mice)
library(here)
source("minos/utils_datain.R")
source("minos/transitions/utils.R")
main <- function(){
  
  do_mice <- F
  if (do_mice) {
    cached <- TRUE
    imp_columns <- c("SF_12", # continuous variables.
                     "age", 
                     "hh_income",
                     "yearly_energy",
                     # discrete variables,
                     'sex',
                     "job_sec",
                     "education_state",
                     "S7_labour_state", 
                     "region", 
                     "ethnicity", 
                     "housing_quality",
                     "housing_tenure",
                     "job_sector",
                     "financial_situation",
                     "nkids_ind",
                     'marital_status')
    
    method <-   c('pmm',
                  'pmm',#'polr',
                  'pmm',
                  'pmm',
                  'pmm', #'polr',
                  'pmm',
                  'pmm',
                  'pmm',
                  'pmm',
                  'pmm',
                  'pmm',
                  'pmm',
                  'pmm',
                  'pmm',
                  'pmm',
                  'pmm')
    
    start.data <- read_raw_data_out(here::here("data/"), "composite_US") 
    other.data <- start.data[, !names(start.data) %in% imp_columns]
    mice.data <- start.data[, c(imp_columns)]
    mice.data <- replace.missing(mice.data)
    
    if (cached) {
      mice_set <- readRDS("data/transitions/MICE_set2.rds")
    }
    else {
      data <- cbind(mice.data, other.data)
      mice_set <- futuremice(data = data[,imp_columns], method=method,
                       m = 1, max_iter = 10,
                       remove.collinear=T)
      # add weights, time and pidps back in. 
      #final.mice.data <- cbind(final.mice.data, other.data)
    }
    final.mice.data <- complete(mice_set, 1)
    print(nrow(final.mice.data))
    print(nrow(other.data))
    final.mice.data <- cbind(final.mice.data, other.data)
    
  } else {
    final.mice.data <- read_raw_data_out(here::here("data/"), "composite_US") 
  }
  create.if.not.exists("data/mice_US")
  save_raw_data_in(final.mice.data, "data/mice_US/")
}#


main()
