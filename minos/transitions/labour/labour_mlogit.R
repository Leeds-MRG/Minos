require(mlogit)

source("transitions/utils.R")
data_source<- "data/corrected_US/"
data <-  read.csv(get_US_file_names(data_source, c("2012"))[3])
data2 <- read.csv(get_US_file_names(data_source, c("2013"))[3])

common <- which(data$pidp%in%data2$pidp)

data <- data[common,]
data2<-data2[common,]

y1 <- data$labour_state
pidp<- data$pidp
y2 <- data2$labour_state
data3<- cbind(y2, y1, pidp, data$age, data$sex, data$ethnicity)
data3<- as.data.frame(data3)
colnames(data3) <- c("y2", "y1", "pidp", "age", "sex", "ethnicity")

for(co in columns){
  i <- which(data[,co]%in%missing) # missing values in utils.R
  data[,co] <- replace(data[,co], i, NA)
}
data3<- data3[complete.cases(data3),]

data3<- head(data3, 5000)
alt_levels = unique(data$labour_state)

data4 <- mlogit.data(data3, 
                     shape="wide", 
                     choice="y2"
)

#data4 <- mlogit.data(data4, 
#                     shape="long", 
#                     choice="y2", 
#                     alt.var="alt",
#                     chid.var="chid",
#                     alt.levels=alt_levels
#                     )

m<- mlogit(y2 ~ 0 | age + sex + ethnicity, data4)

