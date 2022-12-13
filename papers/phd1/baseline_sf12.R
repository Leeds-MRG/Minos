# Get baseline OLS model.
# output coefficient table, rsquared and save to rda.

source("papers/phd1/paper1Utils.R")
source("papers/phd1/utils.R")
library(texreg)
library(sjPlot)
library(VIM)


format_transition_data <- function(source, years, v){
  main_data <- c()
  for (year in years){
    print(year)
    print(year+1)
    data_source<- source
    data_files <- get_US_files(data_source, year, year+1)
    data <- data_files$data1
    data2 <- data_files$data2
    columns <- c( "pidp",
                  "time",
                  "sex",
                  "ethnicity", 
                  "age",
                  "education_state",
                  "labour_state",
                  "job_sec",
                  "region",
                  "hh_netinc",
                  "SF_12")
    
    data <- data[, columns]
    data2 <- data2[, columns]
    
    data <- replace.missing(data)
    data2 <- replace.missing(data2)
    
    
    # only look at individuals with data in both waves.
    common <- intersect(data$pidp, data2$pidp)
    data <- data[which(data$pidp %in% common), ]
    data2 <- data2[which(data2$pidp %in% common), ]
    
    data2 <- data2[, c("pidp", v)]
    colnames(data2) <- c("pidp", "y")
    data <- merge(data, data2,"pidp")
    main_data <- rbind(main_data, data)
  }
  return(main_data)
}

data <- format_transition_data("data/raw_US/", c(2011,2012, 2013), "SF_12")

pdf("papers/phd1/plots/total_missingness_structure.pdf")
aggr(subset(data, select=-c(y)), sortVars=T,  oma=c(8,4,4,4), numbers=T, cex.axis=1.0, col = c(blue, orange), prop=F, combined=T, cex.numbers=0.5)
dev.off()

pidp <- data$pidp
time <- data$time

data <- data[complete.cases(data),]
data$ethnicity <- relevel(factor(data$ethnicity), ref="WBI")
data$education_state <- factor(data$education_state)
data$region <- relevel(factor(data$region), ref="London")
data$sex <- factor(data$sex)
data$labour_state <- factor(data$labour_state)
data$job_sec <- relevel(factor(data$job_sec), ref=1)
data$hh_netinc <- scale(data$hh_netinc)
data$age <- scale(data$age)

sf12.lm <- lm(y ~ sex + 
                ethnicity + 
                scale(age) + 
                education_state + 
                labour_state + 
                job_sec +
                region +
                scale(hh_netinc),
              data= data)
a<- summary(sf12.lm)
print(a)
print(a$adj.r.squared)
texreg(sf12.lm, dcolumn=T, booktabs=T, file='papers/phd1/plots/ols_coefficients.txt', custom.model.names=c("OLS"), single.row=T)
save(sf12.lm, file = "papers/phd1/data/baseline_OLS.RData")
save(data, file = "papers/phd1/data/baseline_OLS_data.RData")