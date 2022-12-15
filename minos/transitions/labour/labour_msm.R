source("transitions/utils.R")
require(msm)
require(tidyr)

data_source<- "data/corrected_US/"
data <-  read.csv(get_US_file_names(data_source, c("2011"))[3])
data2 <- read.csv(get_US_file_names(data_source, c("2012"))[3])

common <- intersect(data$pidp, data2$pidp)

data <- data[which(data$pidp)%in%common,]
data2<-data2[which(data2$pidp)%in%common,]

data[which(data$labour_state%in%c("Other", "Government Training")),"labour_state"] <- NA
data2[which(data2$labour_state%in%c("Other", "Government Training")),"labour_state"] <- NA

data <- data[, c("labour_state", "pidp", "time")]
data2 <- data2[, c("labour_state", "pidp", "time")]

data3 <- rbind(data, data2)

for(co in colnames(data3)){
  i <- which(data3[,co]%in%missing) # missing values in utils.R
  data3[,co] <- replace(data3[,co], i, NA)
}
data3<- data3[complete.cases(data3),]

who_twice <- as.integer(names(which(table(data3$pidp)==2)))
data3 <- data3[which(data3$pidp%in%who_twice), ]
data3 <- data3[order(data3$pidp, data3$time),]

data3$labour_state <- as.integer(factor(data3$labour_state))

y1 <- data3[which(data3$time==2011), "labour_state"]
y2 <- data3[which(data3$time==2012), "labour_state"]
empirical <- table(y1, y2)/ sum(table(y1, y2))

t <- statetable.msm(labour_state, pidp, data3)
lab.msm <- msm(labour_state ~ time, data=data3, qmatrix=empirical)
print(summary(lab.msm))