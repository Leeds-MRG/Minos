source("minos/transitions/utils.R")
require(nnet)

get.labour.files <- function(source, year1, year2){
  # get files for year 1 and year 2 respectively.
  file_name <- get_US_file_names(source, year1, "_US_cohort.csv")
  data <- get_US_data(file_name)
  file_name2 <- get_US_file_names(source, year2, "_US_cohort.csv")
  data2 <- get_US_data(file_name2)
  data_files <- list("data1" = data, "data2" = data2)
  return(data_files)
}

get.nnet.file.name <- function(destination, year1, year2){
  file_name <- paste0(destination, "labour_nnet_")
  file_name <- paste0(file_name, str(year1))
  file_name <- paste0(file_name, "_")
  file_name <- paste0(file_name, str(year2))
  file_name <- paste0(file_name, ".rds")
  return(file_name)
}

labour.nnet.main <- function(years){
  for (year in years){
    print("Writing NNET model for years")
    print(year)
    print(year+1)
    data_source<- "data/final_US/"
    data_files <- get.labour.files(data_source, year, year+1)
    data <- data_files$data1
    data2 <- data_files$data2
    
    # only look at individuals with data in both waves.
    common <- intersect(data$pidp, data2$pidp)
    data <- data[which(data$pidp %in% common), ]
    data2 <- data2[which(data2$pidp %in% common), ]
    
    data2 <- data2[, c("pidp", "labour_state")]
    colnames(data2) <- c("pidp", "labour_state_next")
    data <- merge(data, data2,"pidp")
    data <- data[complete.cases(data),]

    if(year == 2009) {
        # no weight data in 2009
        labour.nnet <- multinom(factor(labour_state_next) ~
                 (factor(sex) +
                  relevel(factor(ethnicity), ref = "WBI") +
                  age +
                  relevel(factor(education_state), ref = '3') +
                  scale(SF_12) +
                  factor(housing_quality) +
                  relevel(factor(labour_state), ref = "Employed") +
                  #factor(job_sec) +
                  scale(hh_income) +
                  scale(alcohol_spending))#**2 # higher order terms. better accuracy but takes 20x as long to calibrate.
               ,data = data, MaxNWts = 10000, maxit=10000)
    } else {
        # weight data available 2010 onwards
        labour.nnet <- multinom(factor(labour_state_next) ~
                 (factor(sex) +
                  relevel(factor(ethnicity), ref = "WBI") +
                  age +
                  relevel(factor(education_state), ref = '3') +
                  scale(SF_12) +
                  factor(housing_quality) +
                  relevel(factor(labour_state), ref = "Employed") +
                  #factor(job_sec) +
                  scale(hh_income) +
                  scale(alcohol_spending))#**2 # higher order terms. better accuracy but takes 20x as long to calibrate.
               ,data = data, MaxNWts = 10000, maxit=10000, weights = weight)
    }

    out.path <- "data/transitions/labour/nnet/"
    create.if.not.exists("data/transitions/labour/")
    create.if.not.exists(out.path)

    nnet.file.name <- get.nnet.file.name(out.path, year, year+1)
    saveRDS(labour.nnet, file=nnet.file.name)
    print("Saved to:")
    print(nnet.file.name)
  }
  test_path <- "data/transitions/test/"
  create.if.not.exists(test_path)
  labour.testfile.name <- get.nnet.file.name(test_path, year, year+1)
  saveRDS(labour.nnet, file=labour.testfile.name)
  print("Saved to: ")
  print(labour.testfile.name)
}

#years <- seq(2009, 2018)
years <- seq(2017, 2018)
labour.nnet.main(years)
