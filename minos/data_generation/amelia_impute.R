### LA 3/1/24
## This script will run Amelia on composite_US data to produce a single imputed dataset.

###################### LIBRARIES ######################

require(tidyverse)
require(knitr)
require(here)
require(Amelia)
require(caret)
require(randomForest)


###################### FUNCTIONS ######################

# Function to identify columns with fully missing data within each wave
identify_missing_columns_by_wave <- function(data, time_column) {
  unique_waves <- unique(data[[time_column]])
  missing_data_info <- list()
  
  for(wave in unique_waves) {
    # putting a stop in here to only care about waves for cross-validation (2015)
    # and sim start years (say 2019-2021). We only need full data from here (for
    # now). However REMEMBER TO CHANGE THIS IF WE NEED A DIFFERENT YEAR
    if (!wave %in% c(2015, 2016, 2017, 2018, 2019, 2020, 2021)) next
    
    # Now get only the data for each wave and check for full NA columns
    wave_data <- data[data[[time_column]] == wave, ]
    missing_columns <- sapply(wave_data, function(x) all(is.na(x)))
    missing_column_names <- names(missing_columns[missing_columns])
    
    if(length(missing_column_names) > 0) {
      message(paste("In wave", wave, "the following columns have fully missing data:"))
      print(missing_column_names)
      missing_data_info[[as.character(wave)]] <- missing_column_names
    } else {
      message(paste("In wave", wave, "there are no columns with fully missing data."))
    }
  }
  
  return(missing_data_info)
}


# Function to impute missing columns within specific waves using predictive modeling
impute_missing_columns_by_wave <- function(data, time_column, missing_data_by_wave, features) {
  for(wave in names(missing_data_by_wave)) {
    # putting a stop in here to only care about waves for cross-validation (2015)
    # to sim start years (say 2019-2021). We only need full data from here (for
    # now). However REMEMBER TO CHANGE THIS IF WE NEED A DIFFERENT YEAR
    if (!wave %in% c(2015, 2016, 2017, 2018, 2019, 2020, 2021)) next
    for(column_to_impute in missing_data_by_wave[[wave]]) {
      # Equivalent income is calculated deterministically (and separately)
      if(column_to_impute == 'equivalent_income') next
      
      print(paste0("Imputing '", column_to_impute, "' for year ", wave, "..."))
      
      # Splitting the dataset into the wave with missing data and other waves
      data_wave_missing <- data %>% filter(time == as.numeric(wave))
      data_other_waves <- data %>% filter(time != as.numeric(wave))
      
      # Selecting rows from other waves where column_to_impute is not NA
      data_for_model <- data_other_waves[!is.na(data_other_waves[[column_to_impute]]), c(column_to_impute, features)]
      
      # Filtering for complete cases in data_for_model for the selected features and the target column
      data_for_model_complete <- data_for_model[complete.cases(data_for_model), ]
      
      # Check if there's sufficient data to train the model
      if(nrow(data_for_model_complete) == 0) {
        print(paste0("Insufficient data to train the RandomForest model for '", column_to_impute, "' in year ", wave))
        next
      }
      
      # Determine if the response variable is numeric or categorical
      if(is.numeric(data_for_model_complete[[column_to_impute]]) && length(unique(na.omit(data_for_model_complete[[column_to_impute]]))) >= 15) {
        model_type <- "regression"
      } else {
        model_type <- "classification"
        data_for_model_complete[[column_to_impute]] <- as.factor(data_for_model_complete[[column_to_impute]])
      }
      
      print(paste0('Var is ', column_to_impute, ' and year is ', wave, ' and var type is ', model_type))
      
      if (model_type == 'classification') {
        # Check distribution before imputation
        print(paste("Distribution of", column_to_impute, "before imputation:"))
        print(table(data_for_model_complete[[column_to_impute]]))
      }
      
      # Building a Random Forest model
      model_formula <- as.formula(paste(column_to_impute, "~", paste(features, collapse = "+")))
      model <- randomForest(model_formula, data = data_for_model_complete)
      
      # Predicting the missing values for the wave with missing data
      predicted_values <- predict(model, data_wave_missing[, c(column_to_impute, features)])
      
      # Replacing the missing values with predictions
      data_wave_missing[[column_to_impute]] <- predicted_values
      
      # Combining the datasets back
      data <- rbind(data_other_waves, data_wave_missing)
      
      if (model_type == 'classification') {
        # Check distribution before imputation
        print(paste("Distribution of", column_to_impute, "before imputation:"))
        print(table(data[[column_to_impute]]))
      }
      
      print(paste0("Imputation of '", column_to_impute, "' for year ", wave, " is complete."))
    }
  }
  return(data)
}


# Function to calculate equivalent income using SIPHER calculation
# For this I asked chatGPT to port the Python function into R, so it's maybe
# not the best way to do this in R (I needed speed...)
calculate_equivalent_income <- function(data) {
  message('Calculating equivalent income...')
  
  # Setting up dictionaries for each variable to hold its factor weights
  phys_health_dict <- c('5' = 0, 
                        '4' = -0.116/1.282, 
                        '3' = -0.135/1.282, 
                        '2' = -0.479/1.282, 
                        '1' = -0.837/1.282, 
                        '-9' = -1, '-8' = -1, '-7' = -1, '-1' = -1, '-2' = -1, '-10' = -1)
  men_health_dict <- c('5' = 0, 
                       '4' = -0.14/1.282, 
                       '3' = -0.215/1.282, 
                       '2' = -0.656/1.282, 
                       '1' = -0.877/1.282, 
                       '-9' = -1, '-8' = -1, '-7' = -1, '-1' = -1, '-2' = -1, '-10' = -1)
  loneliness_dict <- c('1' = 0, 
                       '2' = -0.186/1.282, 
                       '3' = -0.591/1.282, 
                       '-9' = -1, '-8' = -1, '-7' = -1, '-1' = -1, '-2' = -1, '-10' = -1)
  employment_dict <- c('FT Employed' = 0, 
                       'PT Employed' = 0.033/1.282, 
                       'Job Seeking' = -0.283/1.282, 
                       'FT Education' = -0.184/1.282, 
                       'Family Care' = -0.755/1.282, 
                       'Not Working' = -0.221/1.282, 
                       '-8' = -1, '-7' = -1, '-1' = -1, '-2' = -1, '-10' = -1)
  housing_dict <- c('Yes to all' = 0, 
                    'Yes to some' = -0.235/1.282, 
                    'No to all' = -0.696/1.282, 
                    '-9' = -1, '-8' = -1, '-7' = -1, '-1' = -1, '-2' = -1, '-10' = -1)
  nh_safety_dict <- c('Hardly ever' = 0, 
                      'Some of the time' = -0.291/1.282,
                      'Often' = -0.599/1.282, 
                      '-9' = -1, '-8' = -1, '-7' = -1, '-1' = -1, '-2' = -1, '-10' = -1)
  
  # Function to safely get value from dictionary
  get_dict_value <- function(x, dict) {
    if(is.na(x) || !as.character(x) %in% names(dict)) {
      return(NA)
    }
    return(dict[as.character(x)])
  }
  
  print(typeof(data$S7_physical_health))
  print(typeof(data$S7_mental_health))
  print(typeof(data$loneliness))
  print(typeof(data$S7_labour_state))
  print(typeof(data$S7_housing_quality))
  print(typeof(data$S7_neighbourhood_safety))
  
  # Creating the exponent term for modifying income to equivalent income
  data$EI_exp_term <- as.numeric(0)
  data$EI_exp_term <- data$EI_exp_term + sapply(data$S7_physical_health, function(x) get_dict_value(x, phys_health_dict))
  data$EI_exp_term <- data$EI_exp_term + sapply(data$S7_mental_health, function(x) get_dict_value(x, men_health_dict))
  data$EI_exp_term <- data$EI_exp_term + sapply(data$loneliness, function(x) get_dict_value(x, loneliness_dict))
  data$EI_exp_term <- data$EI_exp_term + sapply(data$S7_labour_state, function(x) get_dict_value(x, employment_dict))
  data$EI_exp_term <- data$EI_exp_term + sapply(data$S7_housing_quality, function(x) get_dict_value(x, housing_dict))
  data$EI_exp_term <- data$EI_exp_term + sapply(data$S7_neighbourhood_safety, function(x) get_dict_value(x, nh_safety_dict))
  
  # Calculate equivalent income
  data$hh_income_abs <- abs(data$hh_income)
  data$equivalent_income <- data$hh_income_abs * exp(data$EI_exp_term)
  
  # Adjusting the sign of the equivalent income based on the original income sign
  data$equivalent_income[data$hh_income < 0] <- -data$equivalent_income[data$hh_income < 0]
  
  
  # Handling missing values
  var_list_num <- c('S7_physical_health', 'S7_mental_health', 'loneliness')
  var_list_str <- c('S7_labour_state', 'S7_housing_quality', 'S7_neighbourhood_safety')
  data$equivalent_income[rowSums(data[var_list_num] < 0, na.rm = TRUE) > 0] <- -9
  data$equivalent_income[apply(data[var_list_str], 1, function(x) any(x %in% c('-1', '-2', '-7', '-8', '-9', '-10')))] <- '-9'
  
  # Dropping the EI_exp_term column
  data$EI_exp_term <- NULL
  data$hh_income_abs <- NULL
  
  return(data)
}


# Function to guess variable types
guess_var_type <- function(data) {
  var_types <- sapply(data, function(x) {
    if(all(is.na(x))) {
      return("remove")
    }
    if(is.numeric(x)) {
      if(all(x == round(x), na.rm = TRUE) && length(unique(na.omit(x))) < 15) {
        return("ordinal")
      } else {
        return("continuous")
      }
    } else {
      "nominal"
    }
  })
  return(var_types)
}

# Function to cast columns with numbers to numeric. At some point in this script
# numeric columns are converted to character, I think in impute_missing_columns_by_wave
is_all_numeric <- function(x) {
  !any(is.na(suppressWarnings(as.numeric(na.omit(x))))) & is.character(x)
}

###################### DATA PREPARATION ######################

# # Read 2021 composite datafile in
# comp.2021.file <- here::here('data', 'composite_US', '2021_US_cohort.csv')
# comp.dat <- read.csv(comp.2021.file)

# Read raw datafiles in
raw.files <- list.files(here::here('data', 'composite_US'), pattern='[0-9]{4}_US_cohort.csv', full.names = TRUE)
raw.dat <- do.call(rbind, lapply(raw.files, read.csv))


# Some variables are not required in the model, but cause problems for Amelia to impute. Remove these variables here
data <- raw.dat %>%
  select(-child_ages, -ndrinks, -gross_pay_se, -newest_education_state, -smoker, 
         -job_hours_se, -job_inc, -jb_inc_per, -clinical_depression, -depression,
         -hourly_rate, -gross_paypm, -future_financial_situation, -likely_move,
         -job_duration_m, -job_duration_y, -nobs, -job_hours, -job_hours_diff,
         -job_occupation, -job_industry)


# Replace missing values with NA
miss.values <- c(-10, -9, -8, -7, -3, -2, -1,
                 -10., -9., -8., -7., -3., -2., -1.,
                 '-10', '-9', '-8', '-7', '-3', '-2', '-1')

data <- data.frame(sapply(data, function(x) replace(x, x %in% miss.values, NA)))


###################### PREPARATION FOR AMELIA ######################

# Identify columns with fully missing data in a wave
missing_data_by_wave <- identify_missing_columns_by_wave(data, "time")

# Impute completely null columns before Amelia imputation
selected_features <- c('age', 'sex', 'ethnicity', 'hh_income', 'SF_12', 'region', 'nkids_ind', 'yearly_energy')
data <- impute_missing_columns_by_wave(data, "year", missing_data_by_wave, selected_features)

data <- data %>% 
  mutate_if(is_all_numeric,as.numeric)

# Specifying var types
# Classify variables
var_types <- guess_var_type(data)

# Creating vectors for each variable type
ordinal_vars <- names(var_types[var_types == "ordinal"])
nominal_vars <- names(var_types[var_types == "nominal"])
continuous_vars <- names(var_types[var_types == "continuous"])

###################### AMELIA ######################

print('Beginning Amelia imputation...')
print('Imputing data for years 2015-2021')
data <- data %>% filter(time == 2015)

# Calculate equivalent income before imputing
data <- calculate_equivalent_income(data)

data <- data %>% 
  mutate_if(is_all_numeric,as.numeric)

# Perform multiple imputation
# Key variables: pidp and hidp
amelia_output <- amelia(x = data, 
                        m = 5,
                        idvars = c("pidp", "hidp"),
                        ords = ordinal_vars,
                        noms = nominal_vars)

imp1 <- amelia_output$imp1

# Final step is to calculate equivalent income again with the newly imputed data
imp1 <- calculate_equivalent_income(imp1)

data <- data %>% 
  mutate_if(is_all_numeric,as.numeric)

###################### WRITING DATA ######################

# Set up out path and make if needed
out.path <- 'data/amelia_imputed/'
if(!file.exists(out.path)) {
  dir.create(path = out.path)
}

# Loop through each year so we save yearly data files
for (year in imp1$time) {
  # putting a stop in here to only care about waves for cross-validation (2015)
  # and sim start years (say 2019-2021). We only need full data from here (for
  # now). However REMEMBER TO CHANGE THIS IF WE NEED A DIFFERENT YEAR
  # also see chunk at top of script in identify_missing_columns_by_wave() ^
  if (!year %in% c(2015, 2019, 2020, 2021)) next
  
  new.dat <- imp1 %>% filter(time == year)
  write.csv(x = new.dat,
            file = paste0(out.path, year, '_US_cohort.csv'))
}

print(paste0('Imputation complete, datafiles saved to ', out.path))

# write.csv(x = amelia_output$imp1, 
#           file = paste0(out.path, '2021_US_cohort.csv'))













# Assuming 'data' is your dataframe
na_counts_data <- data %>% 
  summarise_all(~sum(is.na(.)))

print(na_counts_data)


na_counts_imp1 <- data %>% 
  summarise_all(~sum(is.na(.)))
print(na_counts_imp1)


# Checking for complete cases in the data for the year 2015
complete_cases_2015 <- data %>% filter(time == 2015) %>% complete.cases()
print(sum(complete_cases_2015))



# Checking missing values in key variables for the year 2015
missing_values_key_vars <- data %>% 
  filter(time == 2015) %>% 
  summarise(across(everything(), ~sum(is.na(.))))

print(missing_values_key_vars)
