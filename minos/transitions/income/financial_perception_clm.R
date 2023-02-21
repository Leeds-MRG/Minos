
source("minos/transitions/utils.R")
source("minos/transitions/plotting_utils.R")

# load data for 2018/2019
# fit binary logistic glm.
# plot goodness of fit. 

years <- c(2018, 2019)
files <- get.two.files("data/composite_US/", 2018, 2019)
data <- files$data1
data2 <- files$data2

columns <- c("pidp", 
             "region",
             #"education_state", 
             #"sex", 
             "age",
             "SF_12",
             #"ethnicity",
             "labour_state",
             "job_sec",
             "hh_income",
             #"alcohol_spending",
             #"ncigs",
             #"nkids",
             #'hh_comp',
             'marital_status',
             #'heating',
             'weight',
             #'urban',
             #'nbedrooms',
             'hhsize',
             'tenure',
             #'central_heating',
             #'yearly_energy',
             'financial_situation')
             #'neighbourhood_safety',
             #'housing_quality')

data <- data[, columns]
data2 <- data2[, c("pidp", "financial_situation")]
# Force missing values to NA.
data <- replace.missing(data)
data2 <- replace.missing(data2)

# only look at individuals with data in both waves.
common <- intersect(data$pidp, data2$pidp)
data <- data[which(data$pidp %in% common), ]
data2 <- data2[which(data2$pidp %in% common), ]

# merge data frames and remove missing. 
data2 <- data2[, c("pidp", "financial_situation")]
colnames(data2) <- c("pidp", "financial_situation_next")
data <- merge(data, data2,"pidp")
data <- data[complete.cases(data),]

data$weight <- scale(data$weight)
data$weight <- data$weight - min(data$weight)

data$financial_situation_next <- factor(data$financial_situation_next)

#finnow_clm <- clm(financial_situation_next ~ (factor(financial_situation) +
#                    factor(labour_state)+ 
#                    scale(SF_12)+ 
#                    factor(job_sec)+ 
#                    scale(hh_income)+ 
#                    + I(scale(hh_income)**2) +
#                    factor(marital_status)+ 
#                    ncigs+ 
#                    scale(age) +
#                    I(scale(age)**2) +
#                    nbedrooms +
#                    hhsize +
#                    factor(tenure) +
#                    factor(heating) +
#                    factor(education_state)+
#                    factor(neighbourhood_safety)+
#                    factor(housing_quality)),
#                   data = data,
#                   link = "logit",
#                   threshold = "flexible",
#                   Hess=T,
#                  weights = weight)

finnow_clm <- clm(financial_situation_next ~ 
                  factor(financial_situation) +
                  factor(labour_state) + 
                  #factor(ethnicity) +
                  scale(SF_12) + 
                  factor(job_sec)+ 
                  scale(hh_income)+ 
                  I(scale(hh_income)**2) +
                  #factor(region) +
                  factor(marital_status) +
                  #ncigs+ 
                  #I(scale(age)) +
                  #nbedrooms +
                  hhsize +
                  factor(tenure)
                  ,
                  data = data,
                  #weights=weight,
                  link = "logit",
                  threshold = "flexible",
                  Hess=T)

#finsit_poisson <- glm(financial_situation_next ~ 1 +
#      (#factor(financial_situation) +
#      factor(labour_state)+ 
#      scale(SF_12) + 
#      factor(job_sec)+ 
#      hh_income+ 
#      + I(hh_income**2) +
#      factor(marital_status)+ 
#      ncigs + 
#      nkids +
#      I(age**2) +
#      nbedrooms +
#      hhsize),
#      data, family = poisson(link = "log"))
#print(summary(finsit_poisson))
#data$hh_income <- data$hh_income - 1000
#round(predict(finsit_poisson, type='response'))

finsit.clm.path <- "data/transitions/hh_income/clm"
finsit.clm.file <- "/perception_clm.rds"
finsit.clm.filename <- paste0(finsit.clm.path, finsit.clm.file)
create.if.not.exists(finsit.clm.path)
saveRDS(finnow_clm, file=finsit.clm.filename)

obs <- data$financial_situation_next
data$financial_situation_next <- NULL
prob_mat <-  predict(finnow_clm, newdata = data, type='prob')$fit

preds <- predict(finnow_clm, newdata = data, type='class')$fit
preds <- apply(prob_mat, 1, function(x) sample(5, 1, prob=x))
print(table(obs, preds))
clm_barplot(obs, preds, "financial_situation")
clm_output(finnow_clm)
#fdasf