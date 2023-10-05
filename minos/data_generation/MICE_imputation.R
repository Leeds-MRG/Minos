library(mice)

source("minos/utils_datain.R")
source("minos/transitions/utils.R")
main <- function(){
  
  # load in all post LOCFcorrected data? maybe composite?
  # MICE impuation from notebook
  # save to individual waves.
  # get composite/complete case this data instead. I.E. slot into current pipeline and makes. 
  data <- read_raw_data_out("data/", "composite_US") 
  
  
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
  
  other.data <- data[, !names(data) %in% imp_columns]
  mice.data <- data[, c(imp_columns)]
  mice.data <- replace.missing(mice.data)
  data <- cbind(mice.data, other.data)
  

  mice_set <- mice(data = data[,imp_columns], method=method,
                   m = 1, maxit = 1,
                   #m = 2, maxit = 2,
                   remove.collinear=T)
  final.mice.data <- complete(mice_set) 
  # add weights, time and pidps back in. 
  mice.data <- cbind(final.mice.data, other.data)
  create.if.not.exists("data/mice_US")
  save_raw_data_in(mice.data, "data/mice_US/")
}#


main()