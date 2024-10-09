library(xtable)
library(dplyr)
library(gtsummary)

# one of them:
is_discrete   <- function(x) all(is.numeric(x)) && all(x %% 1 == 0)
#is_discrete   <- function(x, tolerance=0.001) all(is.numeric(x)) && all(min(abs(c(x %% 1, x %% 1 - 1))) < tolerance)


is_continuous <- function(vec) all(is.numeric(vec)) && !is_discrete(vec)


# get data.
data <- read.csv("data/scaled_manchester_aligned_US/2020_US_cohort.csv")
# get continuous variables.
# summarise.
# latex table. 
cont_variables <- c("SF_12_MCS", "hh_income", "SF_12_PCS",
                    "council_tax", "oecd_equiv", "hh_rent", "hh_mortgage", "net_hh_income", "yearly_gas", 
                    "yearly_electric", "yearly_gas_electric", "yearly_oil", "yearly_other_fuel")
# cont_variables <- c("SF_12_MCS", "hh_income", "job_hours", "hourly_wage", "SF_12_PCS", 
#                     "council_tax", "oecd_equiv", "hh_rent", "hh_mortgage", "gross_paypm", 
#                     "job_hours_se", "yearly_council_tax_change", "net_hh_income", "outgoings", "phealth", 
#                     "equivalent_income", "hh_income_diff", "net_hh_income_diff", "SF_12_MCS_diff", 
#                     "job_hours_diff", "hourly_wage_diff")
cont_data <- data[, cont_variables]
 #cont_data <- data %>%
#        select(where(is_continuous))
 # drop variables not used. 
 print(xtable(t(summary(cont_data))), type="latex", file="plots/cont_data_summary.tex", include.rownames=TRUE)
 
# get discrete vars.
# summarise.
# tex table.
 # disc_variables <-  c("hidp", "age", "job_sec", "ncigs", "education_state", "loneliness", 
 #                      "nkids", "behind_on_bills", "financial_situation", "heating", "neighbourhood_safety", "yearly_energy", 
 #                      "nutrition_quality", "nkids_ind",  "housing_tenure", "job_sector", "active",  "yearly_gas", 
 #                      "yearly_electric", "yearly_gas_electric", "yearly_oil", "yearly_other_fuel", "smoker",  
 #                      "number_of_bedrooms", "number_of_rooms", "birth_year", "hh_int_m", "hh_int_y", "job_duration_m", "job_duration_y", 
 #                      "job_industry", "job_occupation", "pidp", "alcohol_spending", "ndrinks", "gas_electric_combined",
 #                      "electric_payment", "gas_payment", "duel_payment", "gross_pay_se", "job_inc", "jb_inc_per", "S7_physical_health", 
 #                      "S7_mental_health", "hhsize",  "urban", "ncars", "universal_credit", "floors",  "entrance_floor", "n_pensioners", 
 #                      "matdepa", "matdepd", "matdepe", "matdepf", "matdepg", "matdeph", "matdepi", "matdepj", "depression", "birth_month", 
 #                      "academic_year", "time",    "weight",  "nobs", "dwelling_type", "council_tax_band", "Date", 
 #                      "hh_comp", "chron_disease", "max_educ", "nutrition_quality_diff", "simd_decile","ZoneID","region", "ethnicity", 
 #                      "sex" , "housing_quality", "S7_labour_state", "marital_status", "auditc", "child_ages", 
 #                      "S7_housing_quality", "is_overcrowded", "FP10")
 disc_variables <-  c("age", "job_sec", "ncigs", "education_state", "loneliness", 
                      "nkids", "behind_on_bills", "financial_situation", "heating", "neighbourhood_safety", "yearly_energy", 
                      "nutrition_quality", "housing_tenure", "job_sector", "active",  
                       "number_of_rooms", "birth_year", "ncars", "dwelling_type", "council_tax_band","region", "ethnicity", 
                      "sex" , "housing_quality", "S7_labour_state", "marital_status", "auditc",
                      "S7_housing_quality")
 disc_data <- data[, disc_variables]
 #disc_data <- data %>%
#   select(where(is_discrete))
 # drop variables not used. 
 
# print(xtable(t(summary(disc_data))), type="latex", file="plots/disc_data_summary.tex", include.rownames=FALSE)
#print(xtable(tbl_summary(disc_data)), type="latex", file="plots/disc_data_summary.tex", include.rownames=FALSE)
#disc_table <- gt::as_latex(as_gt(tbl_summary(disc_data)))[[1]]
print(xtable(as.data.frame(tbl_summary(disc_data))), type='latex', file="plots/disc_data_summary.tex", include.rownames=FALSE)
