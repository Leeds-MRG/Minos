source("minos/transitions/utils.R")
require(nnet)
require(tidyverse)


get.educ.file <- function(source, year1, year2){
  # get files for year 1 and year 2 respectively.
  file_name <- get_US_file_names(source, year1, "_US_cohort.csv")
  data <- get_US_data(file_name)
  file_name2 <- get_US_file_names(source, year2, "_US_cohort.csv")
  data2 <- get_US_data(file_name2)
  data_files <- list("data1" = data, "data2" = data2)
  return(data_files)
}


get.nnet.file.name <- function(destination, year1, year2){
  file_name <- paste0(destination, "educ_nnet_")
  file_name <- paste0(file_name, str(year1))
  file_name <- paste0(file_name, "_")
  file_name <- paste0(file_name, str(year2))
  file_name <- paste0(file_name, ".rds")
  return(file_name)
}


educ.nnet.main <- function(year){
  print("Writing NNET model for years")
  print(year)
  print(year+1)
  data_source<- "data/final_US/"
  data_files <- get.educ.file(data_source, year, year+1)
  data <- data_files$data1
  data2 <- data_files$data2
  
  # limit to over 30
  data <- filter(data, age >= 30)
  data2 <- filter(data2, age >= 30)
  
  # only look at individuals with data in both waves.
  common <- intersect(data$pidp, data2$pidp)
  data <- data[which(data$pidp %in% common), ]
  data2 <- data2[which(data2$pidp %in% common), ]

  data2 <- data2[, c("pidp", "education_state")]
  colnames(data2) <- c("pidp", "y")
  data <- merge(data, data2,"pidp")
  data <- data[complete.cases(data),]

  # weight data available 2010 onwards
  m1 <- multinom(factor(y) ~
                 (factor(sex) +
                  relevel(factor(ethnicity), ref = "WBI") +
                  relevel(factor(region), ref = 'South East'))
        ,data = data, MaxNWts = 10000, maxit=10000, weights = weight)
  m1

  out.path <- "data/transitions/education/"
  create.if.not.exists(out.path)
  create.if.not.exists(paste0(out.path, 'nnet/'))

  nnet.file.name <- get.nnet.file.name(paste0(out.path, 'nnet/'), year, year+1)
  saveRDS(m1, file=nnet.file.name)
  print("Saved to:")
  print(nnet.file.name)
}

year <- 2018
educ.nnet.main(year)
