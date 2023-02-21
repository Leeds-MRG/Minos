
source("minos/transitions/utils.R")
#source("minos/transitions/plotting_utils.R")

# load data for 2018/2019
# fit binary logistic glm.
# plot goodness of fit. 

years <- c(2018, 2019)
files <- get.two.files("data/final_US/", 2018, 2019)
data <- files$data1
data2 <- files$data2

columns <- c("pidp", 
             "education_state", 
             "sex", 
             "age",
             "SF_12",
             "ethnicity",
             "labour_state",
             "job_sec",
             "net_hh_income",
             "ncigs",
             'hh_comp',
             'marital_status',
             'heating',
             'weight',
             'nbedrooms',
             #'household_size',
             'tenure',
             'hhsize',
             'urban',
             #'central_heating',
             'yearly_energy',
             'financial_situation')

data <- data[, columns]
data2 <- data2[, c("pidp", "heating")]
# Force missing values to NA.
data <- replace.missing(data)
data2 <- replace.missing(data2)

# only look at individuals with data in both waves.
common <- intersect(data$pidp, data2$pidp)
data <- data[which(data$pidp %in% common), ]
data2 <- data2[which(data2$pidp %in% common), ]

# merge data frames and remove missing. 
data2 <- data2[, c("pidp", "heating")]
colnames(data2) <- c("pidp", "heating_next")
data <- merge(data, data2,"pidp")
data <- data[complete.cases(data),]

data$weight <- scale(data$weight)
data$weight <- data$weight - min(data$weight)

formula <- "heating_next ~ factor(heating) +
            scale(SF_12)+ 
            relevel(factor(ethnicity), ref='WBI') +
            net_hh_income+ 
            factor(marital_status)+ 
            ncigs+ 
            hhsize +
            factor(urban) +
            factor(tenure) + 
            factor(financial_situation)"
heating_logit <- glm(formula, family=binomial(link="logit"), data=data)

create.if.not.exists("data/transitions/heating")
finsit.clm.path <- "data/transitions/heating/logit/"
create.if.not.exists(finsit.clm.path)
finsit.clm.file <- "heating_logit_2018_2019.rds"
finsit.clm.filename <- paste0(finsit.clm.path, finsit.clm.file)
saveRDS(finnow_clm, file=finsit.clm.filename)


print(summary(heating_logit))

preds <- predict(heating_logit, type='response')
preds <- runif(length(preds)) <= preds
print(table(data$heating_next, preds))

#preds <- predict(heating_logit)
#preds <-sapply(preds, invlogit)
#preds[which(preds>=0.5)] <- 1
#preds[which(preds<0.5)] <- 0
#glm_barplot(data$heating_next, preds)
#glm_output(heating_logit)

#obs <- data$heating_next
#colours <- obs
#colours[which(obs==0)] <- orange
#colours[which(obs==1)] <- blue
#plot(predict(heating_logit), col=colours)
#plot(sapply(predict(heating_logit), invlogit), col=colours)
#print(1-deviance(heating_logit)/heating_logit$null.deviance)

#plot(predict(heating_logit, data), col=colours)
#plot(sapply(predict(heating_logit), invlogit), col=colours)