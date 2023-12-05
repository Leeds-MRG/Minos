source("minos/transitions/utils.R")
library(mice)
library(progressr)
save.path <- "minos/outcomes/paper1_plots/"
mice.data.dir <- "data/composite_US/"



# load in all 2009-2020 datasets
mice.filelist <- list.files(mice.data.dir,
                            include.dirs = FALSE,
                            full.names = TRUE,
                            pattern = '[0-9]{4}_US_cohort.csv')
mice.data <- do.call(rbind, lapply(mice.filelist, read.csv))

# missingness MICE model formula

mice_formula_string <- "SF_12 ~ 
                        factor(sex) + 
                        relevel(factor(ethnicity), ref='WBI') + 
                        scale(age) + 
                        factor(education_state) + 
                        factor(S7_labour_state) + 
                        relevel(factor(job_sec), ref=1) +
                        relevel(factor(region), ref='London') +
                        scale(hh_income) + 
                        scale(I(hh_income**2)) +
                        factor(housing_quality) +
                        factor(neighbourhood_safety) + 
                        factor(loneliness) +
                        ncigs +
                        nutrition_quality"

mice_model_formula <- as.formula(mice_formula_string)
variables <- all.vars(mice_model_formula)

# get required variables and replace missing value codes.
mice.data <- replace.missing(mice.data)



imp_columns <- c("SF_12",
                 'sex',
                 "job_sec",
                 "education_state",
                 "S7_labour_state", 
                 "region", 
                 "ethnicity", 
                 "age", 
                 "time", 
                 "hh_income",
                 "housing_quality",
                 "neighbourhood_safety",
                 "loneliness",
                 "ncigs",
                 'nutrition_quality'
)

method <- c("pmm",
            'pmm',
            'pmm',
            'pmm',#'polr',
            'pmm',
            'pmm', #'polr',
            'pmm',
            'pmm', #'polr', #'pmm',
            'pmm',
            'pmm',
            'pmm',
            'pmm',
            'pmm',
            'pmm',
            "pmm",
            "pmm")

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


mice.data$ethnicity <- factor(mice.data$ethnicity)
mice.data$S7_labour_state <- factor(mice.data$S7_labour_state)
mice.data$region <- factor(mice.data$region)
mice.data$heating <- factor(mice.data$heating)
mice.data$job_sec <- factor(mice.data$job_sec)
mice.data$education_state <- factor(mice.data$education_state)
mice.data$sex <- factor(mice.data$sex)
#mice.data$smoker <- factor(mice.data$smoker)
mice.data$behind_on_bills <- factor(mice.data$behind_on_bills)
mice.data$ghq_depression <- factor(mice.data$ghq_depression)
mice.data$ghq_happiness <- factor(mice.data$ghq_happiness)
mice.data$clinical_depression <- factor(mice.data$clinical_depression)
mice.data$scsf1 <- factor(mice.data$scsf1)
mice.data$health_limits_social <- factor(mice.data$ghq_depression)
mice.data$housing_tenure <- factor(mice.data$housing_tenure)
mice.data$urban <- factor(mice.data$urban)
mice.data$marital_status <- factor(mice.data$marital_status)


n_iter <- 30
max_iter <- 10
# future mice is parallelised version of MICE.
#mice_set <- mice(data = mice.data[, imp_columns], #method=method,
#                 m = n_iter, maxit = max_iter,
#                 remove.collinear=T)

start.time <- Sys.time()
print("starting mice")
# tried to get progress bar working to no avail. think it needs an interactive session. 
mice_set <- progressr::with_progress(futuremice(data = mice.data[, mice_columns], #method=method,
                                     m = n_iter, maxit = max_iter,
                                     quiet=F,
                                     progressor = progressr::handlers("progress")))
end.time <- Sys.time()
saveRDS(mice_set, "data/transitions/MICE_set.rds")
print("Time Elapsed: ")
print(end.time-start.time)

