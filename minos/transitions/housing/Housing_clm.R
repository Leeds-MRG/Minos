# script for application of cumulative link model (clm) housing transitions in MINOS.
# This file fits clm models to mice imputed datasets.
########################
# todolist
# get data in. two waves with desired household prediction and imputation variables.
# may be easier to just impute household datasets seperately..

# fit clm on estimation of next household state.
########################

require(ordinal)
source("minos/transitions/utils.R")

get.housing.files <- function(source, year1, year2){
  # get files for year 1 and year 2 respectively.
  file_name <- get_US_file_names(source, year1, "_US_cohort.csv")
  data <- get_US_data(file_name)
  file_name2 <- get_US_file_names(source, year2, "_US_cohort.csv")
  data2 <- get_US_data(file_name2)
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
  data$housing <- rowSums(data[, c("five_household", "heating")])
  data[which(data$housing <= 1), "housing"] <- 1
  data[which(data$housing <= 5 & data$housing > 1), "housing"] <- 2
  data[which(data$housing >= 5), "housing"] <- 3
  data$housing <- factor(data$housing, levels = c(1, 2, 3))
  return(data)
}

get.clm.file.name <- function(destination, year1, year2){
  file_name <- paste0(destination, "housing_clm_")
  file_name <- paste0(file_name, str(year1))
  file_name <- paste0(file_name, "_")
  file_name <- paste0(file_name, str(year2))
  file_name <- paste0(file_name, ".rds")
  return(file_name)
}

clm.housing.main <- function(years){
  # loop over specified years and fit clm models.
  for (year in years){
    print("Writing CLM model for years")
    print(year)
    print(year+1)
    data_source<- "data/final_US/"
    data_files <- get.housing.files(data_source, year, year+1)
    data <- data_files$data1
    data2 <- data_files$data2

    # only look at individuals with data in both waves.
    common <- intersect(data$pidp, data2$pidp)
    data <- data[which(data$pidp %in% common), ]
    data2 <- data2[which(data2$pidp %in% common), ]

    # TODO no MICE imputation here yet..
    # not 100% sure how to impute accross years.
    # simplest may be to impute years seperately and edit mids objects for final
    # pool of clms. see also longitudinal mice (looks slow and painful).
    # Huque 2014 - A comparison of multiple imputation methods for missing data in longitudinal studies
    #data <- format.housing.composite(data)
    #data2 <- format.housing.composite(data2)

    data2 <- data2[, c("pidp", "housing_quality")]
    colnames(data2) <- c("pidp", "y")
    data <- merge(data, data2,"pidp")
    data <- data[complete.cases(data),]

    data$y <- factor(data$y, levels=c(1, 2, 3))
    formula <- "y ~ factor(sex) +
                    age +
                    scale(SF_12) +
                    factor(labour_state) +
                    factor(job_sec) +
                    factor(ethnicity) +
                    scale(hh_income)"
    clm.housing <- clm(formula,
                       data = data,
                       link = "logit",
                       threshold = "flexible",
                       Hess=T)
    prs<- 1 - logLik(clm.housing)/logLik(clm(y ~ 1, data=data))
    print(prs)
    clm.file.name <- get.clm.file.name("data/transitions/housing/clm/", year, year+1)
    saveRDS(clm.housing, file=clm.file.name)
    print("Saved to:")
    print(clm.file.name)
  }
}
# apply clm model


years <- seq(2009, 2018)
clm.housing.main(years)
