library(mice)
library(here)
source("minos/utils_datain.R")
source("minos/transitions/utils.R")
main <- function(){
  
  # load in all post LOCFcorrected data? maybe composite?
  # MICE impuation from notebook
  # save to individual waves.
  # get composite/complete case this data instead. I.E. slot into current pipeline and makes. 
  start.data <- read_all_UKHLS_waves(here::here("data/"), "composite_US") 
  
  
  # set up MICE and cache data
  # plots of missingness pre and post raw US
  # figures of convergence and difference in distribution.
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
  
  other.data <- start.data[, !names(start.data) %in% imp_columns]
  mice.data <- start.data[, c(imp_columns)]
  mice.data <- replace.missing(mice.data)
  data <- cbind(mice.data, other.data)
  
  

  cached <- TRUE
  if (cached) {
    mice.set <- readRDS("data/mice_US/mice_set.rds")
    final.mice.data <- complete(mice.set, 1)
  }
  else {
    #mice_set <- mice(data = data[,imp_columns], method=method,
    #                 m = 1, maxit = 1,
    #                 #m = 2, maxit = 2,
    #                 remove.collinear=T)
    #final.mice.data <- complete(mice_set, 1)   
  }
  # adding other necessary components back in.
  create.if.not.exists("data/mice_US")
  save_raw_data_in(final.mice.data, "data/mice_US/")
}#

main()
