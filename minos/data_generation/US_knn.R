require(VIM)
library(laeken) # for weighedMean.

file_name <-"/Users/robertclay/Minos/data/corrected_US/2010_US_Cohort.csv"
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


knn_set <- kNN(head(data[, c("SF.12", "depression", "depression_change")], 1000), numFun = weightedMean)
knn_set <- kNN(head(data[, c("SF.12", "depression", "depression_change")], 1000), numFun = weightedMean)