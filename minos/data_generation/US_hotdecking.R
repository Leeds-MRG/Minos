require(VIM)
file_name <-"/Users/robertclay/Minos/data/corrected_US/2011_US_Cohort.csv"
data <- read.csv(file_name)
 
missing <- c("-1", "-2", "-7", "-8", "-9", 
                -1, -2, -7, -8,- 9,
                -1., -2., -7., -8., -9.)
columns <- c("SF.12", "job_sec","education_state", "sex",
             "depression_change", "depression", "labour_state", "job_sec", 
             "tumble_dryer", "dishwasher", "microwave", "region",#"heating", 
             "job_duration_m", "job_duration_y", "job_industry", "ethnicity",        
              "job_occupation", "birth_month", "academic_year" )
for(co in columns){
  i <- which(data[,co]%in%missing)
  data[,co] <- replace(data[,co], i, NA)
}

# PLOTS ############################################
aggr(data[, columns], numbers=T)
aggr(data[, c("SF.12", "depression", "depression_change")], labels = c("SF.12", "depression", "depression_change"), cex.axis = 0.7, oma=c(8,8,4,4), combined=F, sortVars=T, varheight=F, numbers=T, prop=T)

spineMiss(data[, c("ethnicity", "SF.12")])
spineMiss(data[, c("age", "SF.12")])
spineMiss(data[, c("labour_state", "SF.12")])
matrixplot(data, sortby=c("SF.12"), cex.axis=0.7)
matrixplot(data, sortby=c("depression"))
matrixplot(data, sortby=c("depression_change"))
                      
# IMPUTATION METHODS ################################
# Usage of sequential hotdecking in a simple example.
# has variables for
# variable - which variables to impute
# ord_var - which variables to sort pop by. 
# domain_var - which groups to divide into before sorting. 
# algorithm divides data by domain group, sorts by ord_var, and sequentially 
# runs through data taking value of last ocuring individual with same observed
# ord_vars complete value.
# https://ec.europa.eu/eurostat/cros/system/files/Imputation-04-T-Donor%20Imputation%20v1.0_2.pdf

print(summary(data[,c("SF.12", "depression_change", "depression")]))
hotdeck_set <- hotdeck(
  data,
  variable = c(columns), 
  ord_var = c("age")
)
print(summary(hotdeck_set[,c("SF.12", "depression_change", "depression")]))

# appears to be mostly MCAR.
