library(xtable)
library(dplyr)

# one of them:
#is_discrete   <- function(vec) all(is.numeric(x)) && all(x %% 1 == 0)
is_discrete   <- function(vec, tolerance=0.000001) all(is.numeric(x)) && all(min(abs(c(x %% 1, x %% 1 - 1))) < tolerance)


is_continuous <- function(vec) all(is.numeric(vec)) && !is_discrete(vec)


main <- function() {
  
  # get data.
  data <- read.csv("data/scaled_manchester_aligned_US/2020.csv")
  # get continuous variables.
  # summarise.
  # latex table. 
   cont_data <- data %>%
          select(where(is_continuous))
   print(xtable(t(summary(cont_data))), type="tex", file="cont_data_summary.tex", include.rownames=FALSE)
   
  # get discrete vars.
  # summarise.
  # tex table.
   disc_data <- data %>%
     select(where(is_discrete))
   print(xtable(t(summary(disc_data))), type="tex", file="disc_data_summary.tex", include.rownames=FALSE)
}



main()