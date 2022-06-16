# script for application of cumulative link model (clm) housing transitions in MINOS. 
# This file fits clm models to mice imputed datasets. 
########################
# todolist
# get data in. two waves with desired household prediction and imputation variables. 
# may be easier to just impute household datasets seperately.. 

# fit clm on estimation of next household state. 
########################

require(ordinal)

# import US data and format.

data_source<- "data/corrected_US/"
data <-  read.csv(get_US_file_names(data_source, c("2011"))[3])
data2 <- read.csv(get_US_file_names(data_source, c("2012"))[3])

columns <- c("pidp", "sex", "ethnicity", "age", "education_state", "depression_change", 
             "labour_state", "job_sec", "hh_netinc", "alcohol_spending")
data <- data[, columns]
data2 <- data2[, columns]

data[which(data$labour_state%in%c("Other", "Government Training")),"labour_state"] <- NA
data2[which(data2$labour_state%in%c("Other", "Government Training")),"labour_state"] <- NA

for(co in colnames(data)){
  i <- which(data[,co]%in%missing) # missing values in utils.R
  data[,co] <- replace(data[,co], i, NA)
}
for(co in colnames(data2)){
  i <- which(data2[,co]%in%missing) # missing values in utils.R
  data2[,co] <- replace(data2[,co], i, NA)
}


data <- data[complete.cases(data), ]
data2 <- data2[complete.cases(data2), ]

common <- intersect(data$pidp, data2$pidp)

# regressors and response variables for the final multinom fit.
X<- data[which(data$pidp %in% common), ]
y<- data2[which(data2$pidp %in% common), ]$labour_state


# apply clm model


# diagnostics
# bubble plots, residuals, metrics of fit.



# main function generates a series of clm models over UKHLS range (2009-2020).