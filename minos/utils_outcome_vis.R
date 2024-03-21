### This utils file will contain functions purely for outcome visualisation.

require(ggplot2)
require(ggExtra)
require(here)

# Function to generate scatterplots with marginal distributions included.
# It compares two scenarios (intervention vs baseline most common) in a given
# end year, attempting to highlight the difference in SF12 change in the two
# scenarios.
# Args:
#       base - baseline output dataframe. Needs all years (output from datain
#               util function)
#       int - intervention output dataframe (output from datain func)
#       int.name - string name of intervention for legend
#       target.year - 'end' year to plot
#       save - Binary, save or not
#       save.path - path to directory in which to save the plots
SF12_marg_dist_densigram_plot <- function(base, 
                                         int, 
                                         int.name, 
                                         target.year = 2035,
                                         save = FALSE,
                                         save.path = here::here('plots')) {
  # get just one year
  b.start <- base %>% filter(time == 2020, SF_12_MCS != -8.0)
  b.end <- base %>% filter(time == target.year, SF_12_MCS != -8.0)
  i.end <- int %>% filter(time == target.year, SF_12_MCS != -8.0)
  # get just the SF12 columns and rename for later
  b.start <- b.start %>% select(pidp, SF_12_MCS) %>% rename(initial = SF_12_MCS)
  b.end <- b.end %>% select(pidp, SF_12_MCS) %>% rename(end = SF_12_MCS)
  i.end <- i.end %>% select(pidp, SF_12_MCS) %>% rename(end = SF_12_MCS)
  
  # combine before we plot
  b.end$scen <- 'baseline'
  i.end$scen <- int.name
  combined <- rbind(b.end, i.end)
  
  # now merge with initial
  merged <- merge(b.start, combined, by = 'pidp')
  
  p <- ggplot(data = merged, aes(x = initial, y = end, group = scen, color = scen)) +
    geom_point(alpha = 0.6, size=0.1) +
    geom_smooth() +
    theme(legend.position = c(0.15, 0.9))
  
  p1 <- ggMarginal(p, type='densigram', groupColour = TRUE, xparams = list(position = 'dodge'), yparams=list(position = 'dodge'))
  p1
  
  plot.name <- paste0('scatter_marg_densigram_', int.name, '.png')
  
  if(save) {
    ggsave(filename = plot.name,
           plot = p1,
           path = save.path)
  }
  
  print(p1)
  
  return(p1)
}


# DOCSTRING HERE
SF12_marg_dist_densigram_plot_oneyear <- function(base, 
                                                  int,
                                                  int.name,
                                                  target.year = 2035,
                                                  save = FALSE,
                                                  save.path = here::here('plots')) {
  # get just one year
  b.end <- base %>% filter(time == target.year, SF_12_MCS != -8.0)
  i.end <- int %>% filter(time == target.year, SF_12_MCS != -8.0)
  # get just the SF12 columns and rename for later
  b.end <- b.end %>% select(pidp, SF_12_MCS) %>% rename(baseline = SF_12_MCS)
  i.end <- i.end %>% select(pidp, SF_12_MCS) %>% rename(intervention = SF_12_MCS)
  
  # combine before we plot
  combined <- merge(b.end, i.end, by = 'pidp')
  
  p <- ggplot(data = combined, aes(x = baseline, y = intervention)) +
    geom_point(alpha = 0.6, size=0.1) +
    geom_smooth() +
    geom_abline(intercept = 0, scale=1) +
    stat_ellipse(color = 'red') +
    theme(legend.position = c(0.15, 0.9)) +
    labs(title = paste0(int.name, ' - ', target.year))
  
  p1 <- ggMarginal(p, type='densigram', xparams = list(position = 'dodge'), yparams=list(position = 'dodge'))
  p1
  
  plot.name <- paste0('scatter_marg_densigram_', int.name, '_ONEYEAR.png')
  
  if(save) {
    ggsave(filename = plot.name,
           plot = p1,
           path = save.path)
  }
  
  print(p1)
  
  return(p1)
}
