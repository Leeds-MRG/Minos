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
  file_name <- paste0(destination, "loneliness_")
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
                 'loneliness',
                 'hh_comp',
                 'marital_status')
    
    data <- data[, columns]
    data2 <- data2[, c("pidp", "loneliness")]
    # Force missing values to NA.
    
    data[which(data$ncigs==-8), 'ncigs'] <- 0
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
    colnames(data2) <- c("pidp", "y")
    data <- merge(data, data2,"pidp")
    data <- data[complete.cases(data),]
    #data$age<- scale(data$age)
    #data$SF_12<- scale(data$SF_12)
    #data$hh_income<- scale(data$hh_income)
    
    # baseline model just zeroing based on ethnicity
    #    m1 <- zeroinfl(y ~ factor(sex) +
    #                    age +
    #                    scale(SF_12) +
    #                    factor(labour_state) +
    #                    factor(job_sec) +
    #                    factor(ethnicity) +
    #                    scale(hh_income) | factor(ethnicity),
    #                   data = data, dist='pois')
    
    data$y <-factor(data$y, levels=c(1, 2, 3))
    #loneliness.clm <- clm(y ~ factor(sex) +
    #                          age +
    #                          scale(SF_12) +
    #                          factor(labour_state) +
    #                          factor(job_sec) +
    #                          relevel(factor(ethnicity), ref='WBI') +
    #                          scale(hh_income) +
    #                          scale(alcohol_spending) +
    #                          scale(ncigs)# + factor
    #                      , data = data, link='logit')
    loneliness.clm <- clm(y ~ scale(age) + 
                            factor(sex) + 
                            scale(SF_12) + 
                            relevel(factor(education_state), ref = '3') + 
                            relevel(factor(job_sec), ref = '3') + 
                            scale(hh_income) + 
                            relevel(factor(hh_comp), ref = '3') + 
                            relevel(factor(marital_status), ref = 'Partnered')
                          , data = data, link='logit')
    
    print(summary(loneliness.clm))
    prs<- 1 - logLik(loneliness.clm)/logLik(clm(y ~ 1, data=data))
    print(prs)
    
    #preds <- predict(loneliness.clm, type='zero')
    #preds <- (runif(length(preds)) < preds) * predict(m1, type='count')
    
    #plot(density(preds, from=0), xlim=c(0, 20), lty=1)
    #lines(density(data$y, from=0), col='red', xlim=c(0, 20), lty=2)
    #legend('topright', legend=c("Predicted", "Real"), col=c("black", "red"), lty=1:2)
    
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