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
                 "ncigs",
                 "weight")
    
    data <- data[, columns]
    data2 <- data2[, c("pidp", "ncigs")]
    # Force missing values to NA.
    data <- replace.missing(data)
    data2 <- replace.missing(data2)
    

    
    #data2 <- data2[, c("pidp", "ncigs")]
    data2$ncigs[is.na(data2$ncigs)] <- 0 # set NAs to 0.
    #data2$ncigs[data2$ncigs < 0] <- 0 # set negative values to 0 (missings)
    #data2[which(data2$ncigs!=0),]$ncigs <- (data2[which(data2$ncigs!=0),]$ncigs%/%5) + 1 # round up to nearest 5. 
    colnames(data2) <- c("pidp", "ncigs_next")
    data <- merge(data, data2,"pidp")
    data <- data[complete.cases(data),]
    #data$age<- scale(data$age)
    #data$SF_12<- scale(data$SF_12)
    #data$hh_income<- scale(data$hh_income)
    
    # no weight var in 2009 (wave 1)
    if(year == 2009) {
      data$weight <- 1
    }
    
    tobacco.zip <- zeroinfl(ncigs_next ~ 
                              factor(sex) +
                              age +
                              SF_12 +
                              factor(labour_state) +
                              relevel(factor(ethnicity), ref='WBI') +
                              factor(education_state) +
                              factor(job_sec) +
                              scale(hh_income) +
                              ncigs |
                              relevel(factor(ethnicity), ref='WBI') +
                              #factor(labour_state) +
                              age +
                              SF_12 + ncigs, 
                            #weights = weight, 
                            model=T,
                            data = data, 
                            dist='pois', link='logit')
    
    print(summary(tobacco.zip))
    prs<- 1 - (logLik(tobacco.zip)/logLik(zeroinfl(ncigs_next ~ 1, data=data, dist='negbin', link='logit')))
    print(prs)
    
    # deprecated density plot.
    #preds <- predict(tobacco.zip, type='zero')
    #preds <- (runif(length(preds)) > preds) * predict(tobacco.zip, type='count')
    #d1 <- density(data$ncigs_next, from=-0.0001)
    #d2 <- density(preds, from=-0.0001)
    #plot(d1, ylim=c(0, max(max(d1$y), max(d2$y))), lty=1, col='red')
    #lines(d2, col='blue', xlim=c(0, 20), lty=2)
    #legend('topright', legend=c("Predicted", "Real"), col=c("blue", "red"), lty=1:2)
    
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
# I'm just going to do 5 years of transitions..
years <- seq(2014, 2018, 1)

test <- main(years)
