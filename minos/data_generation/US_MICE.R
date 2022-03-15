require(mice)
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

data$depression <- as.factor(data$depression)
data$depression_change <- as.factor(data$depression_change)

print(summary(data[,c("SF.12", "depression_change", "depression")]))
mice_set <- mice(data = data[,c("SF.12", "depression_change", "depression")],
                 m = 5, method = "norm.predict", maxit = 50, seed = 500,
                 remove.collinear=T)
print(summary(mice_set[,c("SF.12", "depression_change", "depression")]))

# 50: In `[<-.factor`(`*tmp*`, cc, value = structure(c(1.93295160253826,  ... :
# invalid factor level, NA generated