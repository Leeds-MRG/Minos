# script for application of cumulative link model (clm) housing transitions in MINOS. 
# This file fits clm models to mice imputed datasets. 
########################
# todolist
# get data in. two waves with desired household prediction and imputation variables. 
# may be easier to just impute household datasets seperately.. 

# fit clm on estimation of next household state. 
########################

require(ordinal)
source("transitions/utils.R")

get.housing.files <- function(source, year1, year2){
  # get files for year 1 and year 2 respectively.
  file_name <- get_US_file_names(source, year1)[3]
  data <- get_US_data(file_name)
  data_source<- "data/corrected_US/"
  columns <- c("pidp", 
               "hidp", 
               "education_state", 
               "sex", 
               "age",
               "SF_12",
               "ethnicity",
               "depression_change",
               "labour_state",
               "job_sec",
               "fridge_freezer", 
               "washing_machine", 
               "tumble_dryer", 
               "dishwasher", 
               "microwave", 
               "heating",
               "hh_netinc")
  data<- data[, columns]
  file_name2 <- get_US_file_names(source, year2)[3]
  data2 <- get_US_data(file_name2)
  data2<- data2[, columns]
  data_files <- list("data1" = data, "data2" = data2)
  return(data_files)
}

format.housing.composite <- function(data){
  data$five_household <- rowSums(data[, c("fridge_freezer",
                                          "washing_machine",
                                          "tumble_dryer",
                                          "dishwasher",
                                          "microwave")])
  # TODO some investigation here into whether these threshholds are useful.
  # overwhelming majority (>90%) have at least 4 of the 6 housing values.
  # things like dishwasher and heating are more scarce.
  data$housing_quality <- rowSums(data[, c("five_household", "heating")])
  data[which(data$housing_quality <= 1), "housing_quality"] <- 1
  data[which(data$housing_quality <= 5 & data$housing_quality > 2), "housing_quality"] <- 2
  data[which(data$housing_quality >= 5), "housing_quality"] <- 3
  data$housing_quality <- factor(data$housing_quality, levels=c(1,2,3))
  return(data)
}

get.clm.file.name <- function(destination, year1, year2){
  # Rda file names for clm outputs. annoying string concatenation.
  file_name <- paste0(destination, str(year1))
  file_name <- paste0(file_name, "_")
  file_name <- paste0(file_name, year2)
  file_name <- paste0(file_name, "_housing_clm.rds")
  return(file_name)
}

clm.housing.main <- function(years){
  # loop over specified years and fit clm models. 
  for (year in years){
    print("Writing CLM model for years")
    print(year)
    print(year+1)
    data_source<- "data/corrected_US/"
    data_files <- get.housing.files(data_source, year, year+1)
    data <- data_files$data1
    data2 <- data_files$data2
    data <- replace.missing(data)
    data2 <- replace.missing(data2)
    
    # only look at individuals with data in both waves.
    common <- intersect(data$pidp, data2$pidp)
    data <- data[which(data$pidp %in% common), ]
    data2 <- data2[which(data2$pidp %in% common), ]
    
    # TODO no MICE imputation here yet.. 
    # not 100% sure how to impute accross years.
    # simplest may be to impute years seperately and edit mids objects for final
    # pool of clms. see also longitudinal mice (looks slow and painful).
    # Huque 2014 - A comparison of multiple imputation methods for missing data in longitudinal studies
    data <- format.housing.composite(data)
    data2 <- format.housing.composite(data2)
    
    data2 <- data2[, c("pidp", "housing_quality")]
    colnames(data2) <- c("pidp", "y")
    data <- merge(data, data2,"pidp")
    data <- data[complete.cases(data),]
    #data[, c("SF.12")] <- scale(data[, c("SF.12")])
    
    formula <- "y ~ factor(sex) + 
                    age + 
                    scale(SF_12) + 
                    factor(labour_state) +
                    factor(job_sec) +
                    factor(ethnicity) +
                    factor(housing_quality)"
    names(data)[names(data)=="SF.12"] = "SF_12"
    clm.housing <- clm(formula, 
                       data = data, 
                       link = "logit", 
                       threshold = "flexible", nAGQ = 10)
    prs<- 1 - logLik(clm.housing)/logLik(clm(y ~ 1, data=data))
    print(prs)
    clm.file.name <- get.clm.file.name("transitions/housing/clm_output/", year, year+1)
    saveRDS(clm.housing, file=clm.file.name)
    print("Saved to:")
    print(clm.file.name)
  }
}
# apply clm model


years <- seq(2009, 2018)
clm.housing.main(years)