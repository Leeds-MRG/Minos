library(pscl)
source("minos/transitions/utils.R")


eth_tobacco_plot<- function(data){
  ggplot(data, aes(x=ethnicity, y=ncigs)) + 
  geom_boxplot(outlier.colour="red", outlier.shape=8,
               outlier.size=4)
  eth_tobacco_plot
}

get.tobacco.zip.filename <- function(destination, year1, year2){
  # generate file name for tobacco zero inflated poisson transition outputs for year1.
  file_name <- paste0(destination, "tobacco_zip_")
  file_name <- paste0(file_name, str(year1))
  file_name <- paste0(file_name, "_")
  file_name <- paste0(file_name, str(year2))
  file_name <- paste0(file_name, ".rds")
  return(file_name)
}


main <- function(years){
  for (year in years){
    print("Writing tobacco ZIP model for years ")
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
                 "ncigs")
    
    data <- data[, columns]
    data2 <- data2[, c("pidp", "ncigs")]
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
    
    data2 <- data2[, c("pidp", "ncigs")]
    data2$ncigs[is.na(data2$ncigs)] <- 0 # set NAs to 0. 
    if (min(data2$ncigs)==-10){
      data2[which(data2$ncigs==-10), "ncigs"] <- 0 # set NAs to 0. 
    }
    data2[which(data2$ncigs!=0),]$ncigs <- (data2[which(data2$ncigs!=0),]$ncigs%/%5) + 1 # round up to nearest 5. 
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
    tobacco.zip <- zeroinfl(y ~ factor(sex) +
                             scale(age) +
                             scale(SF_12) +
                             factor(labour_state)|
                             relevel(factor(ethnicity), ref='WBI') +
                             #factor(labour_state) + 
                             scale(age),
                           data = data, dist='pois')  
    
    print(summary(tobacco.zip))
    prs<- 1 - logLik(tobacco.zip)/logLik(zeroinfl(y ~ 1, data=data, dist='pois'))
    print(prs)
    
    #preds <- predict(tobacco.zip, type='zero')
    #preds <- (runif(length(preds)) < preds) * predict(tobacco.zip, type='count')
    
    #plot(density(preds, from=0), xlim=c(0, 20), lty=1)
    #lines(density(data$y, from=0), col='red', xlim=c(0, 20), lty=2)
    #legend('topright', legend=c("Predicted", "Real"), col=c("black", "red"), lty=1:2)
    
    out.path <- "data/transitions/tobacco/zip/"
    create.if.not.exists("data/transitions/tobacco/")
    create.if.not.exists(out.path)
    
    tobacco.file.name <- get.tobacco.zip.filename(out.path, year, year+1)
    saveRDS(tobacco.zip, file=tobacco.file.name)
    print("Saved to: ")
    print(tobacco.file.name)
    
  }
}
# no data until wave 5 because ????????????????. Changes to a likert scale for waves 3,4. no data at all for wave 1.
# I'n just going to do 5 years of transitions..
years <- seq(2013, 2018, 1)

main(years)