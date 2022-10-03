# script for application of cumulative link model (clm) nutrition transitions in MINOS.
# This file fits clm models to mice imputed datasets.
########################
# todolist
# get data in. two waves with desired household prediction and imputation variables.
# may be easier to just impute household datasets seperately..

# fit clm on estimation of next nutrition state.
########################

source("minos/transitions/utils.R")


get.nutrition.files <- function(source, year1, year2){
  # get files for year 1 and year 2 respectively.
  file_name <- get_US_file_names(source, year1, "_US_cohort.csv")
  data <- get_US_data(file_name)
  file_name2 <- get_US_file_names(source, year2, "_US_cohort.csv")
  data2 <- get_US_data(file_name2)
  data_files <- list("data1" = data, "data2" = data2)
  return(data_files)
}


get.nutrition.file.name <- function(destination, year1, year2){
  # Rda file names for clm outputs. annoying string concatenation.
  file_name <- paste0(destination, "nutrition_ols_")
  file_name <- paste0(file_name, str(year1))
  file_name <- paste0(file_name, "_")
  file_name <- paste0(file_name, str(year2))
  file_name <- paste0(file_name, ".rds")
  return(file_name)
}


nutrition.main <- function(year){
  data_source<- "data/final_US/"
  data_files <- get.nutrition.files(data_source, year, year+1)
  data <- data_files$data1
  data2 <- data_files$data2

  # only look at individuals with data in both waves.
  common <- intersect(data$pidp, data2$pidp)
  data <- data[which(data$pidp %in% common), ]
  data2 <- data2[which(data2$pidp %in% common), ]
  data2 <- data2[, c("pidp", "nutrition_quality")]
  colnames(data2) <- c("pidp", "y")
  data <- merge(data, data2,"pidp")
  data <- data[complete.cases(data),]
  formula <- "y ~ factor(sex) +
                age +
                scale(SF_12) +
                factor(education_state) +
                factor(labour_state) +
                factor(ethnicity) +
                scale(hh_income) +
                scale(ncigs) +
                scale(alcohol_spending)"

  if(year == 2009) {
      # no weight data in 2009
      nutrition.lm <- lm(formula,
                    data = data)
  } else {
      # weight data available 2010 onwards
      nutrition.lm <- lm(formula,
                    data = data,
                    weights = weight)
  }

  out.path <- "data/transitions/nutrition/ols/"
  create.if.not.exists("data/transitions/nutrition/")
  create.if.not.exists(out.path)

  nutrition.file.name <- get.nutrition.file.name(out.path, year, year+1)
  saveRDS(nutrition.lm, file=nutrition.file.name)
  print("Saved to:")
  print(nutrition.file.name)
}


year <- 2018
nutrition.main(year)