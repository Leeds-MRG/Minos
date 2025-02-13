.. code:: r

   library(dplyr)

::

   ## 
   ## Attaching package: 'dplyr'

::

   ## The following objects are masked from 'package:stats':
   ## 
   ##     filter, lag

::

   ## The following objects are masked from 'package:base':
   ## 
   ##     intersect, setdiff, setequal, union

.. code:: r

   library(here)

::

   ## here() starts at /home/luke/Documents/WORK/MINOS/Minos

.. code:: r

   source(here::here("docsrc", "documentation", "notebooks", "sphinx_notebook_utils.R"))
   source(here::here('minos', 'utils_datain.R'))
   source(here::here('minos', 'utils_validation_vis.R'))

::

   ## Loading required package: ggridges

::

   ## Loading required package: viridis

::

   ## Warning in library(package, lib.loc = lib.loc, character.only = TRUE,
   ## logical.return = TRUE, : there is no package called 'viridis'

::

   ## Loading required package: ggExtra

::

   ## Loading required package: scales

::

   ## 
   ## Attaching package: 'scales'

::

   ## The following object is masked from 'package:purrr':
   ## 
   ##     discard

::

   ## The following object is masked from 'package:readr':
   ## 
   ##     col_factor

::

   ## Loading required package: gghighlight

::

   ## Loading required package: viridis

::

   ## Warning in library(package, lib.loc = lib.loc, character.only = TRUE,
   ## logical.return = TRUE, : there is no package called 'viridis'

Validation
==========

For validation MINOS uses 2 methods; ‘handover’ plots and 5-fold
cross-validation.

Handovers
---------

Handovers are not a method of statistical validation, but more of a
sanity check giving a quick visual indication that the transition models
are behaving as we would expect. In these plots, we show the ‘handover’
from the unsimulated survey data to the simulated model output. This
shows us whether the trends seen in the survey data are carried on into
the simulation, and therefore whether the simulation continues trends
from the underlying data.

As an example, see below the handover plots for household income.

.. code:: r

   ### Read data in for handovers plots
   # Read raw datafiles in
   raw.files <- list.files(here::here('data', 'final_US'), pattern='[0-9]{4}_US_cohort.csv', full.names = TRUE)
   raw.dat <- do.call(rbind, lapply(raw.files, read.csv))
   raw.dat <- raw.dat %>%
     filter(weight > 0)

   out.path <- here::here('output', 'default_config/')
   base.dat <- read_singular_local_out(out.path, 'baseline', 
                                       drop.dead = TRUE, 
                                       drop.zero.weight = TRUE)

   # cut off any years of raw data AFTER start year of simulation
   if (min(base.dat$time) <= max(raw.dat$time)) {
     raw.dat <- raw.dat %>%
       filter(time <= min(base.dat$time))
   }

   # cut missing data for key variable
   raw.dat <- raw.dat %>%
     filter(!.data[['hh_income']] %in% miss.values)

   handover_boxplots(raw.dat, base.dat, 'hh_income')

.. figure:: ./figure/hh_income_handovers-1.png
   :alt: plot of chunk hh_income_handovers

   plot of chunk hh_income_handovers

.. code:: r

   handover_lineplots(raw.dat, base.dat, 'hh_income')

.. figure:: ./figure/hh_income_handovers-2.png
   :alt: plot of chunk hh_income_handovers

   plot of chunk hh_income_handovers

Cross-Validation
----------------

The other form of validation is 5-fold cross-validation (CV), which is a
valid form of statistical validation. For CV, we split the survey data
into 5 pieces by splitting the list of personal identifiers into 5 equal
chunks (this ensures that each chunk of data will have roughly similar
numbers of individuals covering the full range of the survey).

With the data split into 5 chunks we can simulate a single each chunk of
the data independently, fitting transition models to the other 4/5ths of
data before starting. We run each chunk once, starting in 2015 and
running to 2021. This allows us to compare our simulated values to the
true raw data over this time period, and assessing how our model is
performing when trying to recreate real data.

.. code:: r

   # out.path <- here::here('output', 'cv')
   # cv1 <- read_singular_local_out(here::here(out.path, 'default1/'), 'baseline', drop.dead = TRUE)
   # cv2 <- read_singular_local_out(here::here(out.path, 'default2/'), 'baseline', drop.dead = TRUE)
   # cv3 <- read_singular_local_out(here::here(out.path, 'default3/'), 'baseline', drop.dead = TRUE)
   # cv4 <- read_singular_local_out(here::here(out.path, 'default4/'), 'baseline', drop.dead = TRUE)
   # cv5 <- read_singular_local_out(here::here(out.path, 'default5/'), 'baseline', drop.dead = TRUE)

   # cvlist <- list(cv1, cv2, cv3, cv4, cv5)
   # cv <- do.call(rbind, cvlist)

   # cv simulation batches
   cv.simul.files1 <- list.files(here::here('data', 'final_US', 'cross_validation', 'batch1'),
                                pattern = '[0-9]{4}_US_cohort.csv',
                                full.names = TRUE)
   raw1 <- do.call(rbind, lapply(cv.simul.files1, read.csv))
   cv.simul.files2 <- list.files(here::here('data', 'final_US', 'cross_validation', 'batch2'),
                                pattern = '[0-9]{4}_US_cohort.csv',
                                full.names = TRUE)
   raw2 <- do.call(rbind, lapply(cv.simul.files2, read.csv))
   cv.simul.files3 <- list.files(here::here('data', 'final_US', 'cross_validation', 'batch3'),
                                pattern = '[0-9]{4}_US_cohort.csv',
                                full.names = TRUE)
   raw3 <- do.call(rbind, lapply(cv.simul.files3, read.csv))
   cv.simul.files4 <- list.files(here::here('data', 'final_US', 'cross_validation', 'batch4'),
                                pattern = '[0-9]{4}_US_cohort.csv',
                                full.names = TRUE)
   raw4 <- do.call(rbind, lapply(cv.simul.files4, read.csv))
   cv.simul.files5 <- list.files(here::here('data', 'final_US', 'cross_validation', 'batch5'),
                                pattern = '[0-9]{4}_US_cohort.csv',
                                full.names = TRUE)
   raw5 <- do.call(rbind, lapply(cv.simul.files5, read.csv))

   rawlist <- list(raw1, raw2, raw3, raw4, raw5)
   raw.dat <- do.call(rbind, rawlist)

   # year filter
   # cv.years <- cv %>% select(time) %>% unique()
   # cv.years <- cv.years[['time']]

   #cv <- cv.dat %>% filter(pidp %in% both.pidps$pidp)
   # raw <- raw.dat %>% filter(time %in% cv.years)

   #rm(cv.pidps, raw.pidps, both.pidps, cv.years)
   # rm(cv.years)

.. code:: r

   cv.mean.plots(cv1, cv2, cv3, cv4, cv5, raw, 'hh_income')

::

   ## Error in filter(., .data[[var]] != -9): object 'cv1' not found

.. code:: r

   multi_year_boxplots(raw, cv, 'hh_income')

::

   ## Error in UseMethod("select"): no applicable method for 'select' applied to an object of class "function"

.. code:: r

   snapshot_OP_plots(raw, cv, 'hh_income', target.years = c(2015, 2017, 2019, 2021))

::

   ## Error in select(., pidp, time, all_of(var)): object 'cv' not found

.. code:: r

   q_q_comparison(raw, cv, 'hh_income')

::

   ## Error in UseMethod("select"): no applicable method for 'select' applied to an object of class "function"

.. code:: r

   inc.14 <- marg_dist_densigram_plot_oneyear(observed = raw, 
                                    predicted = cv, 
                                    var = 'hh_income', 
                                    target.year = 2015)

::

   ## Error in UseMethod("filter"): no applicable method for 'filter' applied to an object of class "function"

.. code:: r

   print(inc.14)

::

   ## Error in print(inc.14): object 'inc.14' not found

.. code:: r

   inc.16 <- marg_dist_densigram_plot_oneyear(observed = raw, 
                                    predicted = cv, 
                                    var = 'hh_income', 
                                    target.year = 2017)

::

   ## Error in UseMethod("filter"): no applicable method for 'filter' applied to an object of class "function"

.. code:: r

   print(inc.16)

::

   ## Error in print(inc.16): object 'inc.16' not found

.. code:: r

   inc.18 <- marg_dist_densigram_plot_oneyear(observed = raw, 
                                    predicted = cv, 
                                    var = 'hh_income', 
                                    target.year = 2019)

::

   ## Error in UseMethod("filter"): no applicable method for 'filter' applied to an object of class "function"

.. code:: r

   print(inc.18)

::

   ## Error in print(inc.18): object 'inc.18' not found

.. code:: r

   inc.20 <- marg_dist_densigram_plot_oneyear(observed = raw, 
                                    predicted = cv, 
                                    var = 'hh_income', 
                                    target.year = 2021)

::

   ## Error in UseMethod("filter"): no applicable method for 'filter' applied to an object of class "function"

.. code:: r

   print(inc.20)

::

   ## Error in print(inc.20): object 'inc.20' not found

.. code:: r

   rm(inc.14, inc.16, inc.18, inc.20)

::

   ## Warning in rm(inc.14, inc.16, inc.18, inc.20): object 'inc.14' not found

::

   ## Warning in rm(inc.14, inc.16, inc.18, inc.20): object 'inc.16' not found

::

   ## Warning in rm(inc.14, inc.16, inc.18, inc.20): object 'inc.18' not found

::

   ## Warning in rm(inc.14, inc.16, inc.18, inc.20): object 'inc.20' not found

References
----------
