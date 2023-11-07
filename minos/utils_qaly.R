### QALY calculation plots and utility functions


# AUC Plots:
# This function will plot the total AUC (which equals the total QALYs in the
# system) for 2 interventions, and the change in AUC between the 2.
auc.plots <- function(base, base.name, intervention, int.name) {
  base.auc <- base %>%
    group_by(run_id) %>%
    summarise(AUC = auc(x=year, y = QALYs, type = 'spline')) %>%
    mutate(intervention = base.name)
  
  int.auc <- intervention %>%
    group_by(run_id) %>%
    summarise(AUC = auc(x=year, y = QALYs, type = 'spline')) %>%
    mutate(intervention = int.name)
  
  combined.auc <- rbind(base.auc, int.auc)
  
  print(combined.auc)
  
  combined.auc.plot <- combined.auc %>%
    group_by(intervention) %>%
    summarise(sd = sd(AUC),
              margin = (qt(0.975, df = n() - 1) * sd) / sqrt(n()),
              AUC = mean(AUC))
  
  p1 <- ggplot(data = combined.auc.plot, aes(x = intervention, y = AUC, group = intervention, fill = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = AUC - margin, ymax = AUC + margin, width = 0.4, group = intervention)) +
    labs(title = 'Total AUC comparison', subtitle = paste0(int.name, ' vs ', base.name)) +
    xlab('Intervention')
  print(p1)
  
  # Another version showing difference from baseline for easier comparison
  combined.auc2 <- combined.auc %>%
    pivot_wider(names_from = 'intervention',
                values_from = c('AUC')) %>%
    mutate(change_baseline = .data[[base.name]] - .data[[base.name]],
           change_intervention = .data[[int.name]] - .data[[base.name]]) %>%
    pivot_longer(cols = change_baseline:change_intervention,
                 names_to = 'intervention',
                 names_prefix = 'change_',
                 values_to = 'AUC_difference') %>%
    filter(intervention != 'baseline')
  
  print(combined.auc2)
  
  combined.auc2.plot <- combined.auc2 %>%
    group_by(intervention) %>%
    summarise(margin = (qt(0.975, df = n() - 1) * sd(AUC_difference)) / sqrt(n()),
              AUC_difference = mean(AUC_difference))
  
  p2 <- ggplot(combined.auc2.plot, aes(x = intervention, y = AUC_difference, group = intervention, fill = intervention)) +
    geom_col() +
    geom_errorbar(aes(ymin = AUC_difference - margin, ymax = AUC_difference + margin, width = 0.4, group = intervention)) +
    labs(title = 'Change in AUC', subtitle = paste0(int.name, ' vs ', base.name)) +
    xlab('Intervention')
  
  print(p2)
  
  print(paste0('Change in AUC == ', combined.auc2.plot$AUC_difference, ' +- ', combined.auc2.plot$margin))
}



## COST PER QALY
# This function will calculate and plot the cost per QALY over time, as well 
# as the total cost change over the length of the simulation.
cost.per.qaly <- function(base, base.name, int, int.name, QALY_value) {
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
    filter(intervention != 'baseline')
  
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
}


ICER <- function(base, base.name, int, int.name, QALY_value) {
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
    pivot_longer(cols = -c(run_id, year),
                 names_prefix = 'ICER_',
                 names_to = 'intervention',
                 values_to = 'ICER')
  
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
  
  print(paste0('ICER == ', ICER.final$ICER, ' +- ', ICER.final$margin))
}

