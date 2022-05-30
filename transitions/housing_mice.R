require("VIM")
require("mice")

# load data and format
source("transitions/utils.R")
data_source<- "data/corrected_US/"
years <- c("2011")
file_names <- get_US_file_names(data_source, years)
data <- get_US_data(file_names)
data <- format_US_housing_data(data)

household_vars = c("fridge_freezer",
                   "washing_machine",
                   "tumble_dryer",
                   "dishwasher",
                   "microwave",
                   "heating")

# replace missing value codes with NAs so R can read them. 
for(co in columns){
  i <- which(data[,co]%in%missing)
  data[,co] <- replace(data[,co], i, NA)
}

# diagnostic plots for missingness structure of six variables
# simple missinginess struture plots from VIM. 
# results indicate that.. 
a <- aggr(data, plot = FALSE)
plot(a, numbers = TRUE, prop = FALSE)

b <- aggr(data[, household_vars], plot = FALSE)
plot(b, numbers = TRUE, prop = FALSE)

# implementing MICE

# 