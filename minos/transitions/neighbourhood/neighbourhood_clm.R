# script for application of cumulative link model (clm) to neighbourhood transitions in MINOS.
require(ordinal)
source("minos/transitions/utils.R")
#TODO weight me.

get.neighbourhood.clm.filename <- function(destination, year1, year2){
  # generate file name for neighbourhood clm transition outputs for year1.
  file_name <- paste0(destination, "neighbourhood_safety_")
  file_name <- paste0(file_name, str(year1))
  file_name <- paste0(file_name, "_")
  file_name <- paste0(file_name, str(year2))
  file_name <- paste0(file_name, ".rds")
  return(file_name)
}

clm.neighbourhood.main <- function(years){
  # loop over specified years and fit clm models.
  for (year in years){
    print("Writing neighbourhood CLM model for years ")
    print(year)
    print(" to ")
    print(year+3)
    data_source<- "data/final_US/"
    data_files <- get.two.files(data_source, year, year+3)
    data <- data_files$data1
    data2 <- data_files$data2
    
    # only look at individuals with data in both waves.
    common <- intersect(data$pidp, data2$pidp)
    data <- data[which(data$pidp %in% common), ]
    data2 <- data2[which(data2$pidp %in% common), ]
    

    # TODO no MICE imputation here yet..
    # not 100% sure how to impute across years.
    # simplest may be to impute years seperately and edit mids objects for final
    # pool of clms. see also longitudinal mice (looks slow and painful).
    # Huque 2014 - A comparison of multiple imputation methods for missing data in longitudinal studies
  
    data2 <- data2[, c("pidp", "neighbourhood_safety")]
    colnames(data2) <- c("pidp", "neighbourhood_safety_next")
    data <- merge(data, data2,"pidp")
    data <- data[complete.cases(data),]
    #data$age<- scale(data$age)
    #data$SF_12<- scale(data$SF_12)
    #data$hh_income<- scale(data$hh_income)
    data$neighbourhood_safety_next <- factor(data$neighbourhood_safety_next, levels=c(1, 2, 3))
    data$sex <- factor(data$sex)
    #data$housing_quality <- factor(data$housing_quality)
    #data$education_state <- factor(data$education_state)
    #print(str(data))
    
    #formula <- "y ~ factor(sex) +
    #                    age +
    #                    SF_12 +
    #                    labour_state +
    #                    factor(job_sec) +
    #                    ethnicity +
    #                    hh_income +
    #                    factor(housing_quality) +
    #                    region +
    #                    factor(education_state)"

    data$neighbourhood_safety_next <- factor(data$neighbourhood_safety_next, levels=c(1,2,3))    
    formula <- "y ~ scale(age) + factor(sex) + factor(job_sec) + relevel(factor(ethnicity), ref = 'WBI') + scale(hh_income) + factor(housing_quality) + relevel(factor(region), ref = 'South East')"
    neighbourhood.clm <- clm(neighbourhood_safety_next  ~ 
                               scale(age) + 
                               factor(sex) + 
                               factor(job_sec) + 
                               relevel(factor(ethnicity), ref = 'WBI') + 
                               scale(hh_income) + factor(housing_quality) + 
                               relevel(factor(region), ref = 'South East'),
                                data = data,
                                link = "logit",
                                threshold = "flexible",
                                Hess=T)
                                
    print(summary(neighbourhood.clm))
    prs<- 1 - logLik(neighbourhood.clm)/logLik(clm(neighbourhood_safety_next ~ 1, data=data))
    print(prs)
    
    out.path <- "data/transitions/neighbourhood/clm/"
    create.if.not.exists("data/transitions/neighbourhood/")
    create.if.not.exists(out.path)
    
    neighbourhood.clm$model_data <- data 
    clm.file.name <- get.neighbourhood.clm.filename(out.path, year, year+3)
    saveRDS(neighbourhood.clm, file=clm.file.name)
    print("Saved to: ")
    print(clm.file.name)
  }
  test_path <- "data/transitions/test/"
  create.if.not.exists(test_path)
  neighbourhood.testfile.name <- get.neighbourhood.clm.filename(test_path, year, year+3)
  saveRDS(neighbourhood.clm, file=neighbourhood.testfile.name)
  print("Saved to: ")
  print(neighbourhood.testfile.name)
}

years <- seq(2011, 2014, 3)
clm.neighbourhood.main(years)