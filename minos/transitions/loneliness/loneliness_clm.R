source("minos/transitions/utils.R")
library(ordinal)

#eth_loneliness_plot<- ggplot(data, aes(x=ethnicity, y=loneliness_spending)) + 
#  geom_boxplot(outlier.colour="red", outlier.shape=8,
#               outlier.size=4)
#eth_loneliness_plot

# ndrinks vs expenditure. very strong positive correlation predictably..
#plot(data$ndrinks, data$loneliness_spending)

get.loneliness.clm.filename <- function(destination, year1, year2){
  # generate file name for loneliness zero inflated poisson transition outputs for year1.
  file_name <- paste0(destination, "loneliness_clm_")
  file_name <- paste0(file_name, str(year1))
  file_name <- paste0(file_name, "_")
  file_name <- paste0(file_name, str(year2))
  file_name <- paste0(file_name, ".rds")
  return(file_name)
}


main <- function(years){
  for (year in years){
    print("Writing loneliness logistic model for years ")
    print(year)
    print(" to ")
    print(year+1)
    data_source<- "data/final_US/"
    data_files <- get.two.files(data_source, year, year+1)
    data <- data_files$data1
    data2 <- data_files$data2
    
    columns <- c("pidp", 
                 "education_state", 
                 "sex", 
                 "age",
                 "SF_12",
                 "ethnicity",
                 "labour_state",
                 "job_sec",
                 "hh_income",
                 "alcohol_spending",
                 "ncigs",
                 'loneliness')
    
    data <- data[, columns]
    data2 <- data2[, c("pidp", "loneliness")]
    # Force missing values to NA.
    data <- replace.missing(data)
    data2 <- replace.missing(data2)
    
    # only look at individuals with data in both waves.
    common <- intersect(data$pidp, data2$pidp)
    data <- data[which(data$pidp %in% common), ]
    data2 <- data2[which(data2$pidp %in% common), ]
    
    
    # TODO no MICE imputation here yet..
    # not 100% sure how to impute across years.
    # simplest may be to impute years seperately and edit mids objects for final
    # pool of clms. see also longitudinal mice (looks slow and painful).
    # Huque 2014 - A comparison of multiple imputation methods for missing data in longitudinal studies
    
    data2 <- data2[, c("pidp", "loneliness")]
    colnames(data2) <- c("pidp", "loneliness_next")
    data <- merge(data, data2,"pidp")
    data <- data[complete.cases(data),]
    
    #data$age<- scale(data$age)
    #data$SF_12<- scale(data$SF_12)
    #data$hh_income<- scale(data$hh_income)
    
    data$loneliness_next <-factor(data$loneliness_next, levels=c(1, 2, 3))
    loneliness.clm <- clm(loneliness_next ~ sex +
                              age +
                              SF_12 +
                              labour_state +
                              ethnicity +
                              hh_income +
                              alcohol_spending +
                              ncigs
                          , data = data, link='logit')
    
    print(summary(loneliness.clm))
    prs<- 1 - logLik(loneliness.clm)/logLik(clm(loneliness_next ~ 1, data=data))
    print(prs)
    
    out.path <- "data/transitions/loneliness/clm/"
    create.if.not.exists("data/transitions/loneliness/")
    create.if.not.exists(out.path)
    
    loneliness.file.name <- get.loneliness.clm.filename(out.path, year, year+1)
    saveRDS(loneliness.clm, file=loneliness.file.name)
    print("Saved to: ")
    print(loneliness.file.name)
    
  }
}

years <- seq(2017, 2018, 1)

main(years)