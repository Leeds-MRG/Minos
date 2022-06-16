# file for imputing US datasets for use in housing module transitions. 
require("VIM") # for visualisation
require("mice") # for imputation.
require("dplyr")
require("ordinal")

# load data and format.
source("transitions/utils.R")
data_source<- "data/corrected_US/"
years <- c("2016")
file_names <- get_US_file_names(data_source, years)
data <- get_US_data(file_names)


# replace missing value codes with NAs so R can read them. 
#for(co in colnames(data)){
#  i <- which(data[,co]%in%missing)
#  data[,co] <- replace(data[,co], i, NA)
#}
data <- replace_missing(data)

# create partial household composite that are imputed together due to 100%
# mutual missingness.
data$five_household <- rowSums(data[, c("fridge_freezer",
                                                  "washing_machine",
                                                  "tumble_dryer",
                                                  "dishwasher",
                                                  "microwave")])

# implementing MICE. which colums to impute

imp_columns <- c("five_household", "heating", "labour_state", "education_state",
                 "sex", "job_sec", "ethnicity", "age", "SF.12")
# initialise MICE object but don't run anything yet. 

# TODO define imputation methods vector rather than letting mice decide.
# initiate with 0 iterations and changes $meth attribute. 
house.mice <- mice(data = data[,imp_columns],
                   m = 5, maxit = 5, seed = 500,
                   remove.collinear=T)

# convert housing variables into one composite.
# TODO interesting work here on playing around with these levels.
# what is important in a "low quality" house.
long.data <- complete(house.mice, action='long', include=TRUE)

long.data$housing <- rowSums(long.data[, c("five_household", "heating")])
long.data[which(long.data$housing <= 0), "housing"] <- 0
long.data[which(long.data$housing <= 5 & long.data$housing > 0), "housing"] <- 1
long.data[which(long.data$housing >= 5), "housing"] <- 2
long.data$housing <- as.factor(long.data$housing)
house.mice <- as.mids(long.data)

clm.housing <- with(house.mice, clm(factor(housing) ~ factor(sex) + 
                       age + 
                       SF.12 + 
                       factor(labour_state) +
                       factor(job_sec) +
                       factor(ethnicity),
                       link = "logit",
                       threshold = "flexible",
                       Hess=T))

out <- pool(clm.housing)
out$coefficients <- summary(out)$estimate
formula <- clm.housing[[1]]

save(out, file = "housing_clm_2016.Rda")