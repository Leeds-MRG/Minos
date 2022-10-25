source('minos/transitions/utils.R')
library(jtools) # for forest plots
library(sjPlot) # forest plots

get.extrapolated_weight.files <- function(source, year1, year2){
  # get files for year 1 and year 2 respectively.
  file_name <- get_US_file_names(source, year1, ".csv")
  data <- get_US_data(file_name)
  file_name2 <- get_US_file_names(source, year2, ".csv")
  data2 <- get_US_data(file_name2)
  data_files <- list("data1" = data, "data2" = data2)
  return(data_files)
}


main <- function(years){
  
  data <- data.frame()
  source <- 'data/extrapolated_weights_data_'
  for (year in years){
    data_files <- get.extrapolated_weight.files(source, year, year+1)
    new_data <- data_files$data1
    new_data2 <- data_files$data2
    
    # only look at individuals with data in both waves.
    common <- intersect(new_data$pidp, new_data2$pidp)
    new_data <- new_data[which(new_data$pidp %in% common), ]
    new_data2 <- new_data2[which(new_data2$pidp %in% common), ]
    new_data2 <- new_data2[, c("pidp", "SF_12")]
    colnames(new_data2) <- c("pidp", "y")
    new_data <- merge(new_data, new_data2,"pidp")
    new_data <- new_data[complete.cases(new_data),]
    
    year0_weight <- paste0(paste0("X", year), "_weight")
    year5_weight <- paste0(paste0("X", year+5), "_weight")
    year10_weight <-  paste0(paste0("X", year+10), "_weight")
    colnames(new_data)[which(colnames(new_data)==year0_weight)] <- 'year0_weight'
    colnames(new_data)[which(colnames(new_data)==year5_weight)] <- 'year5_weight'
    colnames(new_data)[which(colnames(new_data)==year10_weight)] <- 'year10_weight'
    
    data <- rbind(data, new_data)
  }

  data$ethnicity <- relevel(factor(data$ethnicity), ref="WBI")
  #data$education_state <- relevel(factor(data$education_state), ref=0)
  data$region <- relevel(factor(data$region), ref="London")
  data$sex <- factor(data$sex)
  data$labour_state <- factor(data$labour_state)
  data$job_sec <- relevel(factor(data$job_sec), ref=1)
  data$gross_hh_income <- data$gross_hh_income
  data$age <- data$age
  data$job_sec <- factor(data$job_sec)
  
  formula <- "y ~ sex + 
                  ethnicity + 
                  age + 
                  education_state + 
                  labour_state + 
                  job_sec +
                  region +
                  scale(hh_income)"
  
  sf12.lm <- lm(formula, weights = year0_weight, data = data)
  print(summary(sf12.lm))

  
  
  png('papers/phd1/extrapolated_SF12_forest_2013.png')
  plot_models(sf12.lm, p.shape=T, legend.title = NULL, m.labels=NULL)
  dev.off()
}

years <- c(2011, 2012, 2013)
main(years)