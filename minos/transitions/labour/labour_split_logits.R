source("transitions/utils.R")
require(ggplot2)  # ggplot2 functions
require(stringr)
library(shadowtext)

data_source<- "data/corrected_US/"
data <-  read.csv(get_US_file_names(data_source, c("2011"))[3])
data2 <- read.csv(get_US_file_names(data_source, c("2012"))[3])

columns <- c("pidp", "sex", "ethnicity", "age", "education_state", "depression_change", 
             "labour_state", "job_sec", "hh_netinc", "alcohol_spending")
data <- data[, columns]
data2 <- data2[, columns]

data[which(data$labour_state%in%c("Other", "Government Training")),"labour_state"] <- NA
data2[which(data2$labour_state%in%c("Other", "Government Training")),"labour_state"] <- NA

for(co in colnames(data)){
  i <- which(data[,co]%in%missing) # missing values in utils.R
  data[,co] <- replace(data[,co], i, NA)
}
for(co in colnames(data2)){
  i <- which(data2[,co]%in%missing) # missing values in utils.R
  data2[,co] <- replace(data2[,co], i, NA)
}


data <- data[complete.cases(data), ]
data2 <- data2[complete.cases(data2), ]

common <- intersect(data$pidp, data2$pidp)

# regressors and response variables for the final multinom fit.
X<- data[which(data$pidp %in% common), ]
y<- data2[which(data2$pidp %in% common), ]$labour_state

X$y <- y

# Just looking at employed to retired logit here..
X2 <- X[which(X$labour_state=="Employed"), ]
X2 <- X2[which(X2$y %in% c("Retired", "Employed")), ]

X2$y2 <- X2$y == "Employed" & X2$labour_state == "Employed"

m1.logit <- glm("factor(y2) ~ 
                 (factor(sex) +
                 factor(ethnicity) + 
                 age + 
                 factor(education_state) + 
                 factor(depression_change) +
                 factor(job_sec) +
                 hh_netinc + 
                 alcohol_spending)",
                data=X2,
                family="binomial")
print(summary(m1.logit))

cols <- X2$y2
cols[which(cols=="TRUE")] <- "orange"
cols[which(cols=="FALSE")] <- "blue"

markers <- X2$y2
markers[which(markers==1)] <- 1
markers[which(markers==0)] <- 15

preds <- sapply(predict(m1.logit, X2), invlogit)
pdf("../../../plots/employment_retirement.pdf")
plot(preds, col = cols, pch = markers)
dev.off()

# Now do studet vs employed.

X2 <- X[which(X$labour_state=="Student"), ]
X2 <- X2[which(X2$y %in% c("Student", "Employed")), ]

X2$y2 <- X2$y == "Student" & X2$labour_state == "Student"

m2.logit <- glm("factor(y2) ~ 
                 (factor(sex) +
                 factor(ethnicity) + 
                 age + 
                 factor(education_state) + 
                 factor(depression_change) +
                 factor(job_sec) +
                 hh_netinc + 
                 alcohol_spending)",
                data=X2,
                family="binomial")
print(summary(m2.logit))

cols <- X2$y2
cols[which(cols=="TRUE")] <- "orange"
cols[which(cols=="FALSE")] <- "blue"

markers <- X2$y2
markers[which(markers==1)] <- 1
markers[which(markers==0)] <- 15

preds <- sapply(predict(m2.logit, X2), invlogit)
pdf("../../../plots/student_employed_separation.pdf")
plot(preds, col = cols, pch = markers)
dev.off()