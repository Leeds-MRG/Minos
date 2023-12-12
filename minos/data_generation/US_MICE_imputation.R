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
                  #"yearly_energy",
                  "nutrition_quality"
                  #"hh_comp", 
                  #"marital_status"
)
  
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
  
  other.data <- start.data[, !names(start.data) %in% mice_columns]
  mice.data <- start.data[, c(mice_columns)]
  mice.data <- replace.missing(mice.data)
  data <- cbind(mice.data, other.data)
  
  

  cached <- TRUE
  if (cached == TRUE) {
    print("Loading Cached MICE data.")
    mice.set <- readRDS("data/transitions/MICE_set.rds")
    final.mice.data <- complete(mice.set, 1)
    final.mice.data <- cbind(final.mice.data, other.data)
  }
  else {
    #mice_set <- mice(data = data[,imp_columns], method=method,
    #                 m = 1, maxit = 1,
    #                 #m = 2, maxit = 2,
    #                 remove.collinear=T)
    #final.mice.data <- complete(mice_set, 1)
    #final.mice.data <- cbind(final.mice.data, other.data)   
  }
  # adding other necessary components back in.
  save.path <- here::here("data", "mice_US/")
  print(save.path)
  print(colnames(final.mice.data))
  create.if.not.exists(save.path)
  save_raw_data_in(final.mice.data, save.path)
  print("MICE data save to data/mice_US")
}#

main()
