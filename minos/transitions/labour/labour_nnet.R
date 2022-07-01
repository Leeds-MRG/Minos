source("minos/transitions/utils.R")
require(nnet)

get.labour.files <- function(source, year1, year2){
  # get files for year 1 and year 2 respectively.
  file_name <- get_US_file_names(source, year1)[3]
  data <- get_US_data(file_name)
  file_name2 <- get_US_file_names(source, year2)[3]
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
    data_files <- get.housing.files(data_source, year, year+1)
    data <- data_files$data1
    data2 <- data_files$data2
    
    # only look at individuals with data in both waves.
    common <- intersect(data$pidp, data2$pidp)
    data <- data[which(data$pidp %in% common), ]
    data2 <- data2[which(data2$pidp %in% common), ]
    
    data2 <- data2[, c("pidp", "labour_state")]
    colnames(data2) <- c("pidp", "y")
    data <- merge(data, data2,"pidp")
    data <- data[complete.cases(data),]
    m1 <- multinom(factor(y) ~ 
                     (factor(sex) +
                      factor(ethnicity) + 
                      age + 
                      factor(education_state) + 
                      SF_12 +
                      factor(housing_quality) +
                      factor(labour_state) +
                      factor(job_sec) + 
                      hh_income + 
                        alcohol_spending)#**2 # higher order terms. better accuracy but takes 20x as long to calibrate.
                   ,data = data, MaxNWts = 10000, maxit=10000)
    m1
    nnet.file.name <- get.nnet.file.name("data/transitions/labour/nnet/", year, year+1)
    saveRDS(m1, file=nnet.file.name)
    print("Saved to:")
    print(nnet.file.name)
    }
}

years <- seq(2009, 2018)
labour.nnet.main(years)
