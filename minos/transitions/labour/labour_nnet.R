source("transitions/utils.R")
require(nnet)
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

X2<- X[which(X$labour_state != X$y), ]
m1 <- multinom(factor(y) ~ 
                 (factor(sex) +
                 factor(ethnicity) + 
                 age + 
                 factor(education_state) + 
                 factor(depression_change) +
                 factor(labour_state) +
               + factor(job_sec) + hh_netinc + alcohol_spending)**2
                 ,data = X2, MaxNWts = 10000, maxit=10000)
m1

#s <- summary(m1)
#z <- s$coefficients/s$standard.errors
#p <- (1 - pnorm(abs(z), 0, 1)) * 2
#z
#p
  #confusion.matrix<- table(X2$y, predict(m1, X2))
  confusion.matrix<- table(X2$y, predict(m1, X2))
  group_pops<-rowSums(confusion.matrix)
  confusion.frame <- as.data.frame(confusion.matrix/group_pops) # convert to data frame
  confusion.frame$Freq <-round(confusion.frame$Freq, 3) # round to 2dp
  row_names <- paste0(rownames(confusion.matrix), " [")
  row_names <- paste0(row_names,  as.character(group_pops))
  row_names <- paste0(row_names, "]")
  row_names <- str_wrap(row_names, width = 12)
  col_names <- str_wrap(colnames(confusion.matrix), 10)
colnames(confusion.frame) <- c("x", "y", "Freq")
  # each column is people actually in a state.
  # each row is people predicted a state.
  # E.g. row 3 column 2 is the percentage of people actually in family care
  # predicted as sick/disabled (~7%).
confusion.plot<- ggplot(confusion.frame, aes(y, rev(x), fill= Freq)) +
  scale_fill_viridis_c("% of state")+
  geom_tile() + 
  geom_shadowtext(aes(label=Freq)) +
  #scale_fill_gradient(high="#87ceeb", low="#e34234") +
  labs(y = "True State [population in state]",x = "Predicted State (no units)") + 
  scale_y_discrete(labels=rev(row_names)) + # label axes
  scale_x_discrete(labels=col_names)
pdf("plots/labour_multinom_confusion_plot.pdf")
confusion.plot
dev.off()
print(confusion.plot) 