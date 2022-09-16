# script for application of cumulative link model (clm) to neighbourhood transitions in MINOS.
require(ordinal)
source("minos/transitions/utils.R")
#TODO weight me.

get.neighbourhood.clm.filename <- function(destination, year1, year2){
  # generate file name for neighbourhood clm transition outputs for year1.
  file_name <- paste0(destination, "neighbourhood_clm_")
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
    colnames(data2) <- c("pidp", "y")
    data <- merge(data, data2,"pidp")
    data <- data[complete.cases(data),]
    #data$age<- scale(data$age)
    #data$SF_12<- scale(data$SF_12)
    #data$hh_income<- scale(data$hh_income)
    data$y <- factor(data$y, levels=c(1, 2, 3))

    #print(str(data))
    
    formula <- "y ~ factor(sex) +
                        age +
                        SF_12 +
                        labour_state +
                        factor(job_sec) +
                        ethnicity +
                        hh_income +
                        factor(housing_quality) +
                        region +
                        factor(education_state)
                        "
    clm.neighbourhood <- clm(formula,
        data = data,
        link = "logit",
        threshold = "flexible",
        Hess=T)
    print(summary(clm.neighbourhood))
    prs<- 1 - logLik(clm.neighbourhood)/logLik(clm(y ~ 1, data=data))
    print(prs)
    
    out.path <- "data/transitions/neighbourhood/clm/"
    create.if.not.exists("data/transitions/neighbourhood/")
    create.if.not.exists(out.path)
    
    clm.file.name <- get.neighbourhood.clm.filename(out.path, year, year+3)
    saveRDS(clm.neighbourhood, file=clm.file.name)
    print("Saved to: ")
    print(clm.file.name)
  }
}

years <- seq(2011, 2014, 3)
clm.neighbourhood.main(years)