### QALY calculation plots and utility functions


##############################################################################
# QALY Comparisons
##############################################################################

## QALY comparisons
# QALY_comparison <- function(base, base.name, int, int.name) {
#   
#   combined <- rbind(base, int)
#   
#   p1 <- ggplot(data = combined, aes(x = year, y = QALYs, group = intervention, colour = intervention)) +
#     geom_smooth() +
#     labs(title = 'QALYs per year')
#   print(p1)
#   
#   # Now change from baseline
#   combined.QALY.change <- combined %>%
#     select(run_id, year, intervention, QALYs) %>%
#     pivot_wider(names_from = 'intervention',
#                 values_from = 'QALYs') %>%
#     mutate(QALYs = .data[[int.name]] - .data[[base.name]]) %>%
#     select(run_id, year, QALYs)
#   
#   p2 <- ggplot(data = combined.QALY.change, aes(x = year, y = QALYs)) +
#     geom_hline(yintercept = 0, linetype = 'dashed') +
#     geom_smooth() +
#     labs(title = 'QALY change', subtitle = paste0(int.name, ' vs ', base.name))
#   print(p2)
#   
#   combined.QALY.change.confint <- combined.QALY.change %>%
#     group_by(year) %>%
#     summarise(n = n(),
#               mean_QALY_change = mean(QALYs),
#               margin = qt(0.975, df = n - 1) * (sd(QALYs) / sqrt(n)),
#               lower = mean_QALY_change - margin,
#               upper = mean_QALY_change + margin)
#   
#   p3 <- ggplot(combined.QALY.change.confint, aes(x = year, y = mean_QALY_change)) +
#     geom_ribbon(aes(ymin = lower, ymax = upper), fill = 'grey70') +
#     geom_line(color = "blue") +
#     geom_hline(yintercept = 0, linetype = 'dashed') +
#     labs(title = 'QALY Change', subtitle = paste0(int.name, ' vs ', base.name))
#   print(p3)
# }

## QALY comparisons
QALY_comparison <- function(combined, ints) {
  
  p1 <- ggplot(data = combined, aes(x = year, y = QALYs, group = intervention, colour = intervention)) +
    geom_smooth() +
    labs(title = 'QALYs per year')
  print(p1)
  
  # Now change from baseline
  combined.QALY.change <- combined %>%
    select(run_id, year, intervention, QALYs) %>%
    pivot_wider(names_from = 'intervention',
                values_from = 'QALYs') %>%
    #mutate(QALYs = .data[[int.name]] - .data[[base.name]]) %>%
    mutate(across(all_of(ints), ~.x - .data[[baseline]], .names = "QALYs_{.col}")) %>%
    select(run_id, year, contains('QALYs')) %>%
    pivot_longer(cols = contains('QALYs'),
                 names_prefix = 'QALYs_',
                 names_to = 'scenario',
                 values_to = 'QALYs')
  
  p2 <- ggplot(data = combined.QALY.change, aes(x = year, y = QALYs, group = scenario, color = scenario, fill = scenario)) +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    geom_smooth() +
    labs(title = 'QALY change')
  print(p2)
  
  combined.QALY.change.confint <- combined.QALY.change %>%
    group_by(year, scenario) %>%
    summarise(n = n(),
              mean_QALY_change = mean(QALYs),
              margin = qt(0.975, df = n - 1) * (sd(QALYs) / sqrt(n)),
              lower = mean_QALY_change - margin,
              upper = mean_QALY_change + margin)
  
  p3 <- ggplot(combined.QALY.change.confint, aes(x = year, y = mean_QALY_change, group = scenario, color = scenario)) +  # fill = scenario
    geom_ribbon(aes(ymin = lower, ymax = upper)) +
    geom_line(color = 'black') +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    labs(title = 'QALY Change') +
    xlab('Year') +
    ylab('QALYs')
  print(p3)
}


## QALY comparisons
QALY_comparison.smooth <- function(base, base.name, int, int.name) {
  
  combined <- rbind(base, int)
  
  p1 <- ggplot(data = combined, aes(x = year, y = QALYs, group = intervention, colour = intervention)) +
    geom_smooth() +
    labs(title = 'QALYs per year')
  print(p1)
  
  # Now change from baseline
  combined.QALY.change <- combined %>%
    select(run_id, year, intervention, QALYs) %>%
    pivot_wider(names_from = 'intervention',
                values_from = 'QALYs') %>%
    mutate(QALYs = .data[[int.name]] - .data[[base.name]]) %>%
    select(run_id, year, QALYs)
  
  p2 <- ggplot(data = combined.QALY.change, aes(x = year, y = QALYs)) +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    geom_smooth() +
    labs(title = 'QALY change', subtitle = paste0(int.name, ' vs ', base.name))
  print(p2)
}

##############################################################################
# SF12 Comparison Plots
##############################################################################

# Plot mean comparison and change from baseline for both MCS and PCS.
# This version plots lineplots with 95% confidence intervals instead of 
# smoothed below
sf12.plots <- function(combined, ints) {
  ## now SF12 plots for comparison
  p1 <- ggplot(combined, aes(x = year, y = SF_12_MCS, group = intervention, colour = intervention, fill = intervention)) +
    geom_smooth()
  p2 <- ggplot(combined, aes(x = year, y = SF_12_PCS, group = intervention, colour = intervention, fill = intervention)) +
    geom_smooth()
  
  print(p1)
  print(p2)
  
  combined.SF12 <- combined %>%
    select(run_id, year, intervention, SF_12_MCS, SF_12_PCS) %>%
    pivot_wider(names_from = 'intervention',
                values_from = c('SF_12_MCS', 'SF_12_PCS')) %>%
    mutate(across(all_of(paste0('SF_12_MCS_', ints)), ~.x - .data[[paste0('SF_12_MCS_', baseline)]], .names = "diff_MCS_{.col}"),
           across(all_of(paste0('SF_12_PCS_', ints)), ~.x - .data[[paste0('SF_12_PCS_', baseline)]], .names = "diff_PCS_{.col}")) %>%
    select(run_id, year, starts_with('diff_')) %>%
    rename_with(~sub("diff_MCS_SF_12_MCS_", "MCS_", .x), starts_with("diff_MCS_SF_12_MCS_")) %>%
    rename_with(~sub("diff_PCS_SF_12_PCS_", "PCS_", .x), starts_with("diff_PCS_SF_12_PCS_")) %>%
    pivot_longer(cols = contains(ints),
                 names_sep = '_',
                 names_to = c('SF12', 'scenario'),
                 values_to = 'difference')
  
  
  p3 <- ggplot(filter(combined.SF12, SF12 == 'MCS'), aes(x = year, y = difference, group = scenario, color = scenario, fill = scenario)) +
    geom_point() +
    geom_smooth() +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    labs(title = 'Change in SF_12_MCS') +
    xlab('Year') +
    ylab('Change in MCS')
  
  p4 <- ggplot(filter(combined.SF12, SF12 == 'PCS'), aes(x = year, y = difference, group = scenario, color = scenario, fill = scenario)) +
    geom_point() +
    geom_smooth() +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    labs(title = 'Change in SF_12_PCS') +
    xlab('Year') +
    ylab('Change in PCS')
  
  print(p3)
  print(p4)
  
  
  combined.small <- combined.SF12 %>%
    group_by(year, SF12, scenario) %>%
    summarise(n = n(),
              mean_diff = mean(difference),
              margin = qt(0.975, df = n - 1) * (sd(difference) / sqrt(n))) # 95% confidence intervals
  
  p5 <- ggplot(filter(combined.small, SF12 == 'MCS'), aes(x = year, y = mean_diff, group = scenario, color = scenario, fill = scenario)) +
    geom_ribbon(aes(ymin = mean_diff - margin, ymax = mean_diff + margin), fill = 'grey70') +
    geom_line() +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    labs(title = 'Change in SF_12_MCS') +
    xlab('Year') +
    ylab('Change in MCS')
  
  p6 <- ggplot(filter(combined.small, SF12 == 'PCS'), aes(x = year, y = mean_diff, group = scenario, color = scenario, fill = scenario)) +
    geom_ribbon(aes(ymin = mean_diff - margin, ymax = mean_diff + margin), fill = 'grey70') +
    geom_line() +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    labs(title = 'Change in SF_12_PCS') +
    xlab('Year') +
    ylab('Change in PCS')
  
  print(p5)
  print(p6)
}

# # Plot mean comparison and change from baseline for both MCS and PCS.
# # This version plots lineplots with 95% confidence intervals instead of 
# # smoothed below
# sf12.plots <- function(base, base.name, int, int.name) {
#   ## SF12 Comparison Plots
#   combined <- rbind(base, int)
#   
#   ## now SF12 plots for comparison
#   p1 <- ggplot(combined, aes(x = year, y = SF_12_MCS, group = intervention, colour = intervention, fill = intervention)) +
#     geom_smooth()
#   p2 <- ggplot(combined, aes(x = year, y = SF_12_PCS, group = intervention, colour = intervention, fill = intervention)) +
#     geom_smooth()
#   
#   print(p1)
#   print(p2)
#   
#   combined.SF12 <- combined %>%
#     select(run_id, year, intervention, SF_12_MCS, SF_12_PCS) %>%
#     pivot_wider(names_from = 'intervention',
#                 values_from = c('SF_12_MCS', 'SF_12_PCS')) %>%
#     mutate(MCS_diff = .data[[paste0('SF_12_MCS_', int.name)]] - .data[[paste0('SF_12_MCS_', base.name)]],
#            PCS_diff = .data[[paste0('SF_12_PCS_', int.name)]] - .data[[paste0('SF_12_PCS_', base.name)]]) %>%
#     select(run_id, year, MCS_diff, PCS_diff)
#   
#   
#   p3 <- ggplot(combined.SF12, aes(x = year, y = MCS_diff)) +
#     geom_point() +
#     geom_smooth() +
#     geom_hline(yintercept = 0, linetype = 'dashed') +
#     labs(title = 'Change in SF_12_MCS', subtitle = paste0(int.name, ' vs ', base.name)) +
#     xlab('Year') +
#     ylab('Change in MCS')
#   
#   p4 <- ggplot(combined.SF12, aes(x = year, y = PCS_diff)) +
#     geom_point() +
#     geom_smooth() +
#     geom_hline(yintercept = 0, linetype = 'dashed') +
#     labs(title = 'Change in SF_12_PCS', subtitle = paste0(int.name, ' vs ', base.name)) +
#     xlab('Year') +
#     ylab('Change in PCS')
#   
#   print(p3)
#   print(p4)
#   
#   
#   combined.small <- combined.SF12 %>%
#     group_by(year) %>%
#     summarise(n = n(),
#               mean_MCS_diff = mean(MCS_diff),
#               mean_PCS_diff = mean(PCS_diff),
#               MCS_margin = qt(0.975, df = n - 1) * (sd(MCS_diff) / sqrt(n)),  # 95% confidence intervals
#               PCS_margin = qt(0.975, df = n - 1) * (sd(PCS_diff) / sqrt(n)))
#   
#   p5 <- ggplot(combined.small, aes(x = year, y = mean_MCS_diff)) +
#     geom_ribbon(aes(ymin = mean_MCS_diff - MCS_margin, ymax = mean_MCS_diff + MCS_margin), fill = 'grey70') +
#     geom_line() +
#     geom_hline(yintercept = 0, linetype = 'dashed') +
#     labs(title = 'Change in SF_12_MCS', subtitle = paste0(int.name, ' vs ', base.name)) +
#     xlab('Year') +
#     ylab('Change in MCS')
#   
#   p6 <- ggplot(combined.small, aes(x = year, y = mean_PCS_diff)) +
#     geom_ribbon(aes(ymin = mean_PCS_diff - PCS_margin, ymax = mean_PCS_diff + PCS_margin), fill = 'grey70') +
#     geom_line() +
#     geom_hline(yintercept = 0, linetype = 'dashed') +
#     labs(title = 'Change in SF_12_PCS', subtitle = paste0(int.name, ' vs ', base.name)) +
#     xlab('Year') +
#     ylab('Change in PCS')
#   
#   print(p5)
#   print(p6)
# }


## SF12 Comparison Plots
# Plot mean comparison and change from baseline for both MCS and PCS.
# This version plots geom_smooth instead of lineplots with confidence
# intervals as above
sf12.plots.smooth <- function(base, base.name, int, int.name) {
  
  combined <- rbind(base, int)
  
  ## now SF12 plots for comparison
  p1 <- ggplot(combined, aes(x = year, y = SF_12_MCS, group = intervention, colour = intervention, fill = intervention)) +
    geom_smooth()
  p2 <- ggplot(combined, aes(x = year, y = SF_12_PCS, group = intervention, colour = intervention, fill = intervention)) +
    geom_smooth()
  
  print(p1)
  print(p2)
  
  combined.SF12 <- combined %>%
    select(run_id, year, intervention, SF_12_MCS, SF_12_PCS) %>%
    pivot_wider(names_from = 'intervention',
                values_from = c('SF_12_MCS', 'SF_12_PCS')) %>%
    mutate(MCS_diff = .data[[paste0('SF_12_MCS_', int.name)]] - .data[[paste0('SF_12_MCS_', base.name)]],
           PCS_diff = .data[[paste0('SF_12_PCS_', int.name)]] - .data[[paste0('SF_12_PCS_', base.name)]]) %>%
    select(run_id, year, MCS_diff, PCS_diff)
  
  p3 <- ggplot(combined.SF12, aes(x = year, y = MCS_diff)) +
    geom_smooth() +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    labs(title = 'Change in SF_12_MCS', subtitle = paste0(int.name, ' vs ', base.name)) +
    xlab('Year') +
    ylab('Change in MCS')
  
  p4 <- ggplot(combined.SF12, aes(x = year, y = PCS_diff)) +
    geom_smooth() +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    labs(title = 'Change in SF_12_PCS', subtitle = paste0(int.name, ' vs ', base.name)) +
    xlab('Year') +
    ylab('Change in PCS')
  
  print(p3)
  print(p4)
}


##############################################################################
# AUC Plots
##############################################################################

# This function will plot the total AUC (which equals the total QALYs in the
# system) for 2 interventions, and the change in AUC between the 2.
auc.plots <- function(combined, ints) {
  
  combined.auc <- combined %>%
    group_by(intervention, run_id) %>%
    summarise(AUC = auc(x=year, y = QALYs, type = 'spline'))
  
  combined.auc.plot <- combined.auc %>%
    group_by(intervention) %>%
    summarise(sd = sd(AUC),
              margin = (qt(0.975, df = n() - 1) * sd) / sqrt(n()),
              AUC = mean(AUC))
  
  p1 <- ggplot(data = combined.auc.plot, aes(x = intervention, y = AUC, group = intervention, fill = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = AUC - margin, ymax = AUC + margin, width = 0.4, group = intervention)) +
    coord_cartesian(ylim = c(min(combined.auc.plot$AUC) - max(combined.auc.plot$margin), max(combined.auc.plot$AUC) + max(combined.auc.plot$margin))) +
    labs(title = 'Total AUC comparison') +
    xlab('Intervention')
  print(p1)
  
  # auc.base <- combined.auc %>% filter(intervention == 'baseline')
  # auc.int <- combined.auc %>% filter(intervention == int.name)
  # 
  # tt <- t.test(x = auc.base$AUC,
  #              y = auc.int$AUC)
  # 
  # print(tt)
  
  #mutate(across(all_of(ints), ~.x - .data[[baseline]], .names = "diff_{.col}")) %>%
  
  # Another version showing difference from baseline for easier comparison
  combined.auc2 <- combined.auc %>%
    pivot_wider(names_from = 'intervention',
                values_from = c('AUC')) %>%
    mutate(across(all_of(ints), ~.x - .data[[baseline]], .names = "change_{.col}")) %>%
    select(run_id, contains('change_')) %>%
    pivot_longer(cols = contains('change_'),
                 names_to = 'intervention',
                 names_prefix = 'change_',
                 values_to = 'AUC_difference')
  
  combined.auc2.plot <- combined.auc2 %>%
    group_by(intervention) %>%
    summarise(margin = (qt(0.975, df = n() - 1) * sd(AUC_difference)) / sqrt(n()),
              AUC_difference = mean(AUC_difference))
  
  p2 <- ggplot(combined.auc2.plot, aes(x = intervention, y = AUC_difference, group = intervention, fill = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = AUC_difference - margin, ymax = AUC_difference + margin, width = 0.4, group = intervention)) +
    labs(title = 'Change in AUC') +
    xlab('Intervention')
  
  print(p2)
  
  #print(paste0('Change in AUC == ', combined.auc2.plot$AUC_difference, ' +- ', combined.auc2.plot$margin))
  
  print("Table of change in AUC:")
  print(combined.auc2.plot)
  
}

# This function will plot the total AUC (which equals the total QALYs in the
# system) for 2 interventions, and the change in AUC between the 2.
# auc.plots <- function(base, base.name, intervention, int.name) {
#   base.auc <- base %>%
#     group_by(run_id) %>%
#     summarise(AUC = auc(x=year, y = QALYs, type = 'spline')) %>%
#     mutate(intervention = base.name)
#   
#   int.auc <- intervention %>%
#     group_by(run_id) %>%
#     summarise(AUC = auc(x=year, y = QALYs, type = 'spline')) %>%
#     mutate(intervention = int.name)
#   
#   combined.auc <- rbind(base.auc, int.auc)
#   
#   combined.auc.plot <- combined.auc %>%
#     group_by(intervention) %>%
#     summarise(sd = sd(AUC),
#               margin = (qt(0.975, df = n() - 1) * sd) / sqrt(n()),
#               AUC = mean(AUC))
#   
#   p1 <- ggplot(data = combined.auc.plot, aes(x = intervention, y = AUC, group = intervention, fill = intervention)) +
#     geom_col() +
#     geom_errorbar(aes(ymin = AUC - margin, ymax = AUC + margin, width = 0.4, group = intervention)) +
#     coord_cartesian(ylim = c(min(combined.auc.plot$AUC) - max(combined.auc.plot$margin), max(combined.auc.plot$AUC) + max(combined.auc.plot$margin))) +
#     labs(title = 'Total AUC comparison', subtitle = paste0(int.name, ' vs ', base.name)) +
#     xlab('Intervention')
#   print(p1)
#   
#   auc.base <- combined.auc %>% filter(intervention == 'baseline')
#   auc.int <- combined.auc %>% filter(intervention == int.name)
#   
#   tt <- t.test(x = auc.base$AUC,
#                y = auc.int$AUC)
#   
#   print(tt)
#   
#   # Another version showing difference from baseline for easier comparison
#   combined.auc2 <- combined.auc %>%
#     pivot_wider(names_from = 'intervention',
#                 values_from = c('AUC')) %>%
#     mutate(change_baseline = .data[[base.name]] - .data[[base.name]],
#            change_intervention = .data[[int.name]] - .data[[base.name]]) %>%
#     pivot_longer(cols = change_baseline:change_intervention,
#                  names_to = 'intervention',
#                  names_prefix = 'change_',
#                  values_to = 'AUC_difference') %>%
#     filter(intervention != 'baseline')
#   
#   combined.auc2.plot <- combined.auc2 %>%
#     group_by(intervention) %>%
#     summarise(margin = (qt(0.975, df = n() - 1) * sd(AUC_difference)) / sqrt(n()),
#               AUC_difference = mean(AUC_difference))
#   
#   p2 <- ggplot(combined.auc2.plot, aes(x = intervention, y = AUC_difference, group = intervention, fill = intervention)) +
#     geom_col() +
#     geom_errorbar(aes(ymin = AUC_difference - margin, ymax = AUC_difference + margin, width = 0.4, group = intervention)) +
#     labs(title = 'Change in AUC', subtitle = paste0(int.name, ' vs ', base.name)) +
#     xlab('Intervention')
#   
#   print(p2)
#   
#   print(paste0('Change in AUC == ', combined.auc2.plot$AUC_difference, ' +- ', combined.auc2.plot$margin))
# }

##############################################################################
# COST PER QALY
##############################################################################

# This function will calculate and plot the cost per QALY over time, as well 
# as the total cost change over the length of the simulation.

cost.per.qaly <- function(base, base.name, int, int.name, QALY_value, int.label) {
  combined <- rbind(base, int)
  
  combined.cost <- combined %>%
    #select(-alive_pop, -SF_12_MCS, -SF_12_PCS, -utility) %>%
    select(run_id, year, alive_pop, total_boost, intervention, QALYs) %>%
    mutate(QALY_value = QALYs * QALY_value)
  
  p1 <-ggplot(combined.cost, aes(x = year, y = QALY_value, group = intervention, colour = intervention)) +
    geom_smooth() +
    scale_y_continuous(label = comma) +
    labs(title = 'QALY value comparison', subtitle = paste0(int.name, ' vs ', base.name))
  print(p1)
  
  combined.cost.change <- combined.cost %>%
    select(run_id, year, intervention, QALY_value) %>%
    pivot_wider(names_from = 'intervention',
                values_from = 'QALY_value') %>%
    mutate(change_baseline = .data[[base.name]] - .data[[base.name]],
           change_intervention = .data[[int.name]] - .data[[base.name]]) %>%
    select(run_id, year, change_baseline, change_intervention) %>%
    pivot_longer(cols = change_baseline:change_intervention,
                 names_to = 'intervention',
                 names_prefix = 'change_',
                 values_to = 'QALY_value_change') %>%
    filter(intervention != 'baseline') %>%
    mutate(intervention = int.label)
  
  combined.cost.change.plot <- combined.cost.change %>%
    group_by(year, intervention) %>%
    summarise(n = n(),
              mean_QALY_value_change = mean(QALY_value_change),
              margin = qt(0.975, df = n - 1) * (sd(QALY_value_change) / sqrt(n)))
  
  p2 <- ggplot(combined.cost.change.plot, aes(x = year, y = mean_QALY_value_change, group = intervention, colour = intervention, fill = intervention)) +
    geom_ribbon(aes(ymin = mean_QALY_value_change - margin, ymax = mean_QALY_value_change + margin)) +
    geom_line(color = 'black') +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    scale_y_continuous(label = comma) +
    labs(title = 'QALY value change', subtitle = paste0(int.name, ' vs ', base.name)) +
    xlab('Year') +
    ylab('QALY Value Difference')
  print(p2)
  
  total.combined.cost <- combined.cost.change %>%
    group_by(run_id, intervention) %>%
    summarise(TotalChange = sum(QALY_value_change)) %>%
    group_by(intervention) %>%
    summarise(margin = (qt(0.975, df = n() - 1) * sd(TotalChange)) / sqrt(n()),
              TotalChange = mean(TotalChange))
  
  p3 <- ggplot(total.combined.cost, aes(x = intervention, y = TotalChange, group = intervention, fill = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = TotalChange - margin, ymax = TotalChange + margin, width = 0.4, group = intervention)) +
    scale_y_continuous(label = comma) +
    labs(title = 'Total Change in QALY Value', subtitle = paste0(int.name, ' vs ', base.name)) +
    xlab('Intervention')
  print(p3)
  
  print(paste("QALY value change across full simulation: ", format(total.combined.cost$TotalChange[1], big.mark = ',', trim = TRUE), sep = ' '))
}

cost.per.qaly.smooth <- function(base, base.name, int, int.name, QALY_value, int.label) {
  combined <- rbind(base, int)
  
  combined.cost <- combined %>%
    #select(-alive_pop, -SF_12_MCS, -SF_12_PCS, -utility) %>%
    select(run_id, year, alive_pop, total_boost, intervention, QALYs) %>%
    mutate(QALY_value = QALYs * QALY_value)
  
  p1 <-ggplot(combined.cost, aes(x = year, y = QALY_value, group = intervention, colour = intervention)) +
    geom_smooth() +
    scale_y_continuous(label = comma) +
    labs(title = 'QALY value comparison', subtitle = paste0(int.name, ' vs ', base.name))
  print(p1)
  
  combined.cost.change <- combined.cost %>%
    select(run_id, year, intervention, QALY_value) %>%
    pivot_wider(names_from = 'intervention',
                values_from = 'QALY_value') %>%
    mutate(change_baseline = .data[[base.name]] - .data[[base.name]],
           change_intervention = .data[[int.name]] - .data[[base.name]]) %>%
    select(run_id, year, change_baseline, change_intervention) %>%
    pivot_longer(cols = change_baseline:change_intervention,
                 names_to = 'intervention',
                 names_prefix = 'change_',
                 values_to = 'QALY_value_change') %>%
    filter(intervention != 'baseline') %>%
    mutate(intervention = int.label)
  
  p2 <- ggplot(combined.cost.change, aes(x = year, y = QALY_value_change, group = intervention, colour = intervention, fill = intervention)) +
    geom_smooth() +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    scale_y_continuous(label = comma) +
    labs(title = 'QALY value change', subtitle = paste0(int.name, ' vs ', base.name))
  print(p2)
  
  total.combined.cost <- combined.cost.change %>%
    group_by(run_id, intervention) %>%
    summarise(TotalChange = sum(QALY_value_change)) %>%
    group_by(intervention) %>%
    summarise(margin = (qt(0.975, df = n() - 1) * sd(TotalChange)) / sqrt(n()),
              TotalChange = mean(TotalChange))
  
  p3 <- ggplot(total.combined.cost, aes(x = intervention, y = TotalChange, group = intervention, fill = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = TotalChange - margin, ymax = TotalChange + margin, width = 0.4, group = intervention)) +
    scale_y_continuous(label = comma) +
    labs(title = 'Total Change in QALY Value', subtitle = paste0(int.name, ' vs ', base.name)) +
    xlab('Intervention')
  print(p3)
  
  print(paste("QALY value change across full simulation: ", format(total.combined.cost$TotalChange[1], big.mark = ',', trim = TRUE), sep = ' '))
}

##############################################################################
# Incremental Cost Effective Ratio (ICER)
##############################################################################

# ICER <- function(base, base.name, int, int.name, QALY_value, int.label, start.year = 2021) {
#   combined <- rbind(base, int)
#   
#   combined.cost.mean <- combined %>%
#     #select(-alive_pop, -SF_12_MCS, -SF_12_PCS, -utility) %>%
#     select(run_id, year, total_boost, intervention, QALYs) %>%
#     mutate(QALY_value = QALYs * QALY_value) %>%
#     group_by(run_id, year, intervention) %>%
#     summarise(across(everything(), mean))
#   
#   # ICER = (C1 - C0) / (E1 - E0)
#   # where
#   # C1 = cost of intervention
#   # E1 = effect of intervention
#   # C0 = cost of control group
#   # E0 = effect of control group
#   
#   # prepare var names
#   c1 <- paste('total_boost', int.name, sep='_')
#   c0 <- paste('total_boost', base.name, sep='_')
#   e1 <- paste('QALYs', int.name, sep='_')
#   e0 <- paste('QALYs', base.name, sep='_')
#   
#   ICER <- combined.cost.mean %>%
#     pivot_wider(names_from = 'intervention',
#                 values_from = c('total_boost', 'QALYs', 'QALY_value')) %>%
#     mutate(ICER = (.data[[c1]] - .data[[c0]]) / (.data[[e1]] - .data[[e0]])) %>%
#     select(run_id, year, ICER) %>%
#     mutate(intervention = int.label)
#   
#   # No intervention in first year so can't calculate ICER
#   #TODO: Find start year automatically
#   ICER <- ICER %>%
#     filter(year != start.year)
#   
#   ICER.plot <- ICER %>%
#     group_by(year, intervention) %>%
#     summarise(n  = n(),
#               mean_ICER = mean(ICER),
#               margin = qt(0.975, df = n - 1) * (sd(ICER) / sqrt(n)))
#   
#   p1 <- ggplot(ICER.plot, aes(x = year, y = mean_ICER, group = intervention, fill = intervention, colour = intervention)) +
#     geom_ribbon(aes(ymin = mean_ICER - margin, ymax = mean_ICER + margin)) +
#     geom_line(color = 'black') +
#     geom_hline(yintercept = 0, linetype = 'dashed') +
#     scale_y_continuous(label = comma) +
#     labs(title = 'ICER - Full', subtitle = paste0(int.name, ' vs ', base.name))
#   print(p1)
#   
#   pc1 <- quantile(ICER$ICER, .01)
#   # print(pc1)
#   # print(min(ICER$ICER))
#   pc99 <- quantile(ICER$ICER, .99)
#   # print(pc99)
#   # print(max(ICER$ICER))
#   
#   ICER <- filter(ICER, ICER < pc99, ICER > pc1)
#   # print(min(ICER$ICER))
#   # print(max(ICER$ICER))
#   
#   ICER.plot2 <- ICER %>%
#     group_by(year, intervention) %>%
#     summarise(n  = n(),
#               mean_ICER = mean(ICER),
#               margin = qt(0.975, df = n - 1) * (sd(ICER) / sqrt(n)))
#   
#   p2 <- ggplot(ICER.plot2, aes(x = year, y = mean_ICER, group = intervention, fill = intervention, colour = intervention)) +
#     geom_ribbon(aes(ymin = mean_ICER - margin, ymax = mean_ICER + margin)) +
#     geom_line(color = 'black') +
#     geom_hline(yintercept = 0, linetype = 'dashed') +
#     scale_y_continuous(label = comma) +
#     labs(title = 'ICER - Outliers Removed', subtitle = paste0(int.name, ' vs ', base.name))
#   print(p2)
#   
#   ICER.final <- ICER %>%
#     group_by(run_id, intervention) %>%
#     summarise(ICER = mean(ICER)) %>%
#     group_by(intervention) %>%
#     summarise(margin = (qt(0.975, df=n() - 1) * sd(ICER)) / sqrt(n()),
#               ICER = mean(ICER))
#   
#   p3 <- ggplot(ICER.final, aes(x = intervention, y = ICER, group = intervention, fill = intervention)) +
#     geom_col() +
#     geom_errorbar(aes(ymin = ICER - margin, ymax = ICER + margin, width = 0.4, group = intervention)) +
#     scale_y_continuous(label = comma) +
#     labs(title = 'ICER', subtitle = paste0(int.name, ' vs ', base.name)) +
#     xlab('Intervention')
#   print(p3)
#   
#   print(paste0('ICER == ', format(ICER.final$ICER, big.mark = ',', trim = TRUE), ' +- ', format(ICER.final$margin, big.mark = ',', trim = TRUE)))
# }

ICER <- function(combined, ints, QALY_value, start.year = 2020) {
  
  # Calculate the monetary value of QALYs
  combined <- combined %>%
    mutate(QALY_value_monetary = QALYs * QALY_value)
  
  # Calculate mean costs and effects (QALYs) per intervention and year
  combined_summary <- combined %>%
    group_by(run_id, year, intervention) %>%
    summarise(mean_total_boost = mean(total_boost),
              mean_QALYs = mean(QALYs),
              mean_QALY_value = mean(QALY_value_monetary),
              .groups = 'drop')
  
  # Identify baseline intervention
  baseline_intervention <- "baseline" # Adjust this to match the exact name of your baseline in the 'intervention' column
  
  # For each intervention, calculate ICER relative to the baseline
  ICER <- combined_summary %>%
    # Joining the table with itself on run_id and year to compare each intervention against the baseline
    inner_join(combined_summary, by = c("run_id", "year"), suffix = c(".int", ".base")) %>%
    # Filtering to compare each intervention to the baseline
    filter(intervention.int != intervention.base, intervention.base == baseline_intervention) %>%
    # Calculating ICER
    mutate(ICER = (mean_total_boost.int - mean_total_boost.base) / (mean_QALYs.int - mean_QALYs.base)) %>%
    # Selecting relevant columns for the final output
    select(run_id, year, intervention = intervention.int, ICER)
  
  # No intervention in first year so can't calculate ICER
  #TODO: Find start year automatically
  ICER <- ICER %>%
    filter(year != start.year)
  
  ICER.plot <- ICER %>%
    group_by(year, intervention) %>%
    summarise(n  = n(),
              mean_ICER = mean(ICER),
              margin = qt(0.975, df = n - 1) * (sd(ICER) / sqrt(n)))
  
  p1 <- ggplot(ICER.plot, aes(x = year, y = mean_ICER, group = intervention, fill = intervention, colour = intervention)) +
    geom_ribbon(aes(ymin = mean_ICER - margin, ymax = mean_ICER + margin)) +
    geom_line(color = 'black') +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    scale_y_continuous(label = comma) +
    labs(title = 'ICER - Full')
  print(p1)
  
  pc1 <- quantile(ICER$ICER, .01)
  # print(pc1)
  # print(min(ICER$ICER))
  pc99 <- quantile(ICER$ICER, .99)
  # print(pc99)
  # print(max(ICER$ICER))
  # 
  ICER <- filter(ICER, ICER < pc99, ICER > pc1)
  # print(min(ICER$ICER))
  # print(max(ICER$ICER))
  
  ICER.plot2 <- ICER %>%
    group_by(year, intervention) %>%
    summarise(n  = n(),
              mean_ICER = mean(ICER),
              margin = qt(0.975, df = n - 1) * (sd(ICER) / sqrt(n)))
  
  p2 <- ggplot(ICER.plot2, aes(x = year, y = mean_ICER, group = intervention, fill = intervention, colour = intervention)) +
    geom_ribbon(aes(ymin = mean_ICER - margin, ymax = mean_ICER + margin)) +
    geom_line(color = 'black') +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    scale_y_continuous(label = comma) +
    labs(title = 'ICER - Outliers Removed')
  print(p2)
  
  ICER.final <- ICER %>%
    group_by(run_id, intervention) %>%
    summarise(ICER = mean(ICER)) %>%
    group_by(intervention) %>%
    summarise(margin = (qt(0.975, df=n() - 1) * sd(ICER)) / sqrt(n()),
              ICER = mean(ICER))
  
  p3 <- ggplot(ICER.final, aes(x = intervention, y = ICER, group = intervention, fill = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = ICER - margin, ymax = ICER + margin, width = 0.4, group = intervention)) +
    scale_y_continuous(label = comma) +
    labs(title = 'ICER') +
    xlab('Intervention')
  print(p3)
  
  print(paste0('ICER == ', format(ICER.final$ICER, big.mark = ',', trim = TRUE), ' +- ', format(ICER.final$margin, big.mark = ',', trim = TRUE)))
  
}

ICER.smooth <- function(base, base.name, int, int.name, QALY_value, int.label) {
  combined <- rbind(base, int)
  
  combined.cost.mean <- combined %>%
    #select(-alive_pop, -SF_12_MCS, -SF_12_PCS, -utility) %>%
    select(run_id, year, total_boost, intervention, QALYs) %>%
    mutate(QALY_value = QALYs * QALY_value) %>%
    group_by(run_id, year, intervention) %>%
    summarise(across(everything(), mean))
  
  # ICER = (C1 - C0) / (E1 - E0)
  # where
  # C1 = cost of intervention
  # E1 = effect of intervention
  # C0 = cost of control group
  # E0 = effect of control group
  
  # prepare var names
  c1 <- paste('total_boost', int.name, sep='_')
  c0 <- paste('total_boost', base.name, sep='_')
  e1 <- paste('QALYs', int.name, sep='_')
  e0 <- paste('QALYs', base.name, sep='_')
  
  ICER <- combined.cost.mean %>%
    pivot_wider(names_from = 'intervention',
                values_from = c('total_boost', 'QALYs', 'QALY_value')) %>%
    mutate(ICER = (.data[[c1]] - .data[[c0]]) / (.data[[e1]] - .data[[e0]])) %>%
    select(run_id, year, ICER) %>%
    mutate(intervention = int.label)
  
  pc1 <- quantile(ICER$ICER, .01)
  print(pc1)
  print(min(ICER$ICER))
  pc99 <- quantile(ICER$ICER, .99)
  print(pc99)
  print(max(ICER$ICER))
  
  ICER <- filter(ICER, ICER < pc99, ICER > pc1)
  print(min(ICER$ICER))
  print(max(ICER$ICER))
  
  p1 <- ggplot(ICER, aes(x = year, y = ICER, group = intervention, fill = intervention, colour = intervention)) +
    geom_smooth() +
    scale_y_continuous(label = comma) +
    labs(title = 'ICER', subtitle = paste0(int.name, ' vs ', base.name))
  print(p1)
  
  ICER.final <- ICER %>%
    group_by(run_id, intervention) %>%
    summarise(ICER = mean(ICER)) %>%
    group_by(intervention) %>%
    summarise(margin = (qt(0.975, df=n() - 1) * sd(ICER)) / sqrt(n()),
              ICER = mean(ICER))
  
  p2 <- ggplot(ICER.final, aes(x = intervention, y = ICER, group = intervention, fill = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = ICER - margin, ymax = ICER + margin, width = 0.4, group = intervention)) +
    scale_y_continuous(label = comma) +
    labs(title = 'ICER', subtitle = paste0(int.name, ' vs ', base.name)) +
    xlab('Intervention')
  print(p2)
  
  print(paste0('ICER == ', format(ICER.final$ICER, big.mark = ',', trim = TRUE), ' +- ', format(ICER.final$margin, big.mark = ',', trim = TRUE)))
}

##############################################################################
# Intervention Cost
##############################################################################

intervention.cost <- function(base, base.name, int, int.name, int.label) {
  combined <- rbind(base, int)
  
  total.cost.byYear <- combined %>%
    select(run_id, year, intervention, total_boost) %>%
    group_by(run_id, year, intervention) %>%
    summarise(total_yearly_cost = sum(total_boost)) %>%
    pivot_wider(names_from = 'intervention',
                values_from = 'total_yearly_cost') %>%
    mutate(cost_difference = .data[[int.name]] - .data[[base.name]]) %>%
    select(run_id, year, cost_difference) %>%
    mutate(intervention = int.name)
  
  total.cost.byYear.plot <- total.cost.byYear %>%
    group_by(year, intervention) %>%
    summarise(n = n(),
              mean_cost_difference = mean(cost_difference),
              margin = qt(0.975, df = n - 1) * (sd(cost_difference) / sqrt(n)))
  
  p2 <- ggplot(total.cost.byYear.plot, aes(x = year, y = mean_cost_difference, group = intervention, fill = intervention, colour = intervention)) +
    geom_ribbon(aes(ymin = mean_cost_difference - margin, ymax = mean_cost_difference + margin)) +
    geom_line() +
    labs(title = 'Intervention Cost by Year', subtitle = paste0(int.name, ' vs ', base.name))
  print(p2)
  
  total.cost.firstYr <- total.cost.byYear %>%
    filter(year == 2022)
  
  print(paste("Cost of intervention in the first year (2022) ==", format(total.cost.firstYr$cost_difference[1],
                                                                         big.mark = ',',
                                                                         trim = TRUE), 
              sep = ' '))
  
  total.cost <- total.cost.byYear %>%
    group_by(intervention, run_id) %>%
    summarise(cost_difference = sum(cost_difference)) %>%
    group_by(intervention) %>%
    summarise(margin = (qt(0.975, df=n() - 1) * sd(cost_difference)) / sqrt(n()),
              cost_difference = mean(cost_difference))
  
  p1 <- ggplot(total.cost, aes(x = intervention, y = cost_difference, group = intervention, fill = intervention, colour = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = cost_difference - margin, ymax = cost_difference + margin, width = 0.4, group = intervention)) +
    labs(title = 'Total cost of intervention', subtitle = paste0(int.name, ' vs ', base.name)) +
    scale_y_continuous(label = comma)
  print(p1)
  
  print(paste("Total cost of the intervention over the full simulation (2020-2035) ==", format(total.cost$cost_difference,
                                                                                               big.mark = ',',
                                                                                               trim = TRUE), 
              sep = ' '))
}

intervention.cost.smooth <- function(base, base.name, int, int.name, int.label) {
  combined <- rbind(base, int)
  
  total.cost.byYear <- combined %>%
    select(run_id, year, intervention, total_boost) %>%
    group_by(run_id, year, intervention) %>%
    summarise(total_yearly_cost = sum(total_boost)) %>%
    pivot_wider(names_from = 'intervention',
                values_from = 'total_yearly_cost') %>%
    mutate(cost_difference = .data[[int.name]] - .data[[base.name]]) %>%
    select(run_id, year, cost_difference) %>%
    mutate(intervention = int.name)
  
  p2 <- ggplot(total.cost.byYear, aes(x = year, y = cost_difference)) +
    geom_smooth() +
    labs(title = 'Intervention Cost by Year', subtitle = paste0(int.name, ' vs ', base.name))
  print(p2)
  
  total.cost.firstYr <- total.cost.byYear %>%
    filter(year == 2022)
  
  print(paste("Cost of intervention in the first year (2022) ==", format(total.cost.firstYr$cost_difference[1], 
                                                                         big.mark = ',', 
                                                                         trim = TRUE), 
              sep = ' '))
  
  total.cost <- total.cost.byYear %>%
    group_by(intervention, run_id) %>%
    summarise(cost_difference = sum(cost_difference)) %>%
    group_by(intervention) %>%
    summarise(margin = (qt(0.975, df=n() - 1) * sd(cost_difference)) / sqrt(n()),
              cost_difference = mean(cost_difference))
  
  p1 <- ggplot(total.cost, aes(x = intervention, y = cost_difference, group = intervention, fill = intervention, colour = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = cost_difference - margin, ymax = cost_difference + margin, width = 0.4)) +
    labs(title = 'Total cost of intervention', subtitle = paste0(int.name, ' vs ', base.name)) +
    scale_y_continuous(label = comma)
  print(p1)
  
  print(paste("Total cost of the intervention over the full simulation (2020-2035) ==", format(total.cost$cost_difference[1],
                                                                                               big.mark = ',',
                                                                                               trim = TRUE), 
              sep = ' '))
}
