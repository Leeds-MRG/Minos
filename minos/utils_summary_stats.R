#####################################################################
# Summary Statistic Utils                                           #
# This script will be used for generating summary statistics on any #
# US sample population.                                             #
#                                                                   #
# Author: Luke Archer                                               #
# Date: 19/11/24                                                    #
#####################################################################



########### Summary Functions ###########

# Function to summarize continuous variables
summarize_continuous <- function(data, vars, weight_col) {
  data %>%
    summarise(across(all_of(vars), list(
      n = ~ n(),
      mean = ~ weighted.mean(.x, w = .data[[weight_col]], na.rm = TRUE),
      sd = ~ sqrt(weighted.mean((.x - weighted.mean(.x, w = .data[[weight_col]], na.rm = TRUE))^2, w = .data[[weight_col]], na.rm = TRUE)),
      min = ~ min(.x, na.rm = TRUE),
      max = ~ max(.x, na.rm = TRUE)
    )))
}

# Function to summarize nominal/ordinal variables
summarize_categorical <- function(data, vars, weight_col) {
  map(vars, function(var) {
    data %>%
      filter(!is.na(.data[[var]])) %>%  # Remove rows with NA in the current variable
      group_by(.data[[var]]) %>%
      summarise(count = sum(.data[[weight_col]], na.rm = TRUE)) %>%
      mutate(prop = count / sum(count)) %>%
      select(-count) %>%
      pivot_wider(names_from = .data[[var]], values_from = prop, values_fill = 0) %>%
      rename_with(~ paste0(var, "_", .))
  }) %>%
    reduce(left_join, by = character(0))  # Combine all summaries
}

# Main function to generate stratified summary statistics
generate_summary <- function(data, strat_var, continuous_vars, categorical_vars, weight_col) {
  
  # Function to generate stratified summaries
  stratified_summaries <- function(subset_data) {
    continuous_summary <- summarize_continuous(subset_data, continuous_vars, weight_col)
    categorical_summary <- summarize_categorical(subset_data, categorical_vars, weight_col)
    bind_cols(continuous_summary, categorical_summary)
  }
  
  # Split the data by stratification variable
  stratified_data <- split(data, data[[strat_var]])
  
  # Apply the summary function to each stratum
  stratified_results <- map(stratified_data, stratified_summaries)
  
  # Bind the results together into a single data frame
  result <- bind_rows(stratified_results, .id = strat_var)
  
  return(result)
}

# Function to print the summary table in HTML and LaTeX formats
print_summary <- function(summary_df, file_prefix) {
  # For R Notebook
  summary_df %>%
    kable(format = "html") %>%
    kable_styling(bootstrap_options = c("striped", "hover", "condensed")) %>%
    print()
  
  # For LaTeX
  summary_df %>%
    kable(format = "latex", booktabs = TRUE) %>%
    kable_styling(latex_options = "hold_position") %>%
    save_kable(paste0(file_prefix, "_summary.tex"))
}

########### Writing to File ###########

write_summary_to_file <- function(summary_df, path, filename) {
  
  fname <- paste0(filename, "_summary.csv")
  full_path <- paste0(path, fname)
  
  # Write to CSV
  write_csv(summary_df, full_path)
  
  
  message("Summary table saved as: ", fname)
  message("Path: ", path)
}


########### Example Usage ###########

# Example usage:
# data <- data  # Replace with your actual data frame
# continuous_vars <- c("age", "hh_income", "SF_12", "nutrition_quality")
# categorical_vars <- c("sex", "education_state", "region", "ethnicity", "marital_status", "housing_quality", "neighbourhood_safety", "universal_credit", "S7_labour_state")

# Generate stratified summary statistics by gender (sex)
# summary_by_gender <- generate_summary(data, strat_var = "sex", continuous_vars, categorical_vars, weight_col = "weight")

# Print the summary tables
# print_summary(summary_by_gender, file_prefix = "gender")

# Write to file
# write_summary_to_file(summary_by_gender, 
#                       path = "/home/luke/Documents/WORK/MINOS/DELIVERABLES/MHF_SCP_NoScottish/",
#                       filename = "Gender")