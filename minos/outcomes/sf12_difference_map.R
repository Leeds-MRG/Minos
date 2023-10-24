library(argparse)
source("minos/outcomes/minos_SF12_maps.R")

main <- function(){
  
  parser <- ArgumentParser(description="Plot a map of some MINOS geojson.")
  parser$add_argument('-m', '--mode', help='Which experiment are we mapping? 
                      This mainly relates to the output subdirectory we will use 
                      to find files for aggregation and mapping.')
  parser$add_argument('-b', '--baseline', help='Which run are we mapping? 
                      For single maps this will most likely be the baseline run 
                      i.e. no intervention')
  parser$add_argument('-i', '--intervention', help='Which intervention to compare 
                      with baseline?')
  parser$add_argument('-r', '--region', help='Which region are we mapping? 
                      Currently available are Glasgow, Sheffield, Manchester, 
                      and Scotland.')
  parser$add_argument('-y', '--year', help='What year to map data for.')
  #parser$add_argument("-d", "--plot_destination", dest='destination', help="Where to save a plot.")
  parser$add_argument("-v", "--v", dest='var', help="What variable to map.")
  
  args <- parser$parse_args()
  output_subdir <- args$mode
  run <- args$baseline
  intervention <- args$intervention
  region <- args$region
  year <- args$year
  #plot_destination <- args$destination
  v <- args$var
  
  ## handle runtime subdirectory
  # first construct geojson file path and name from arguments
  # baseline
  geojson_file_path_base <- paste0('output/', output_subdir, '/', run, '/')
  geojson_file_name_base <- paste0(region, '_nanmean_', v, '_', year, '.geojson')
  # intervention
  geojson_file_path_int <- paste0('output/', output_subdir, '/', intervention, '/')
  geojson_file_name_int <- paste0(region, '_nanmean_', v, '_', year, '.geojson')
  
  print(geojson_file_path_base)
  print(geojson_file_name_base)
  print(geojson_file_path_int)
  print(geojson_file_name_int)
  
  # first select only the path (not filename)
  out.files1 <- list.files(geojson_file_path_base)
  out.files2 <- list.files(geojson_file_path_int)

  ## Check how many subdirectories, if more than 1 then pick most recent
  # First output dir
  if(length(out.files1) == 1) {
    geojson_file_name1 = paste0(geojson_file_path_base, '/', out.files1[1], '/', geojson_file_name_base)
  }
  else if(length(out.files1) > 1) {
    out.files1.date <- as.POSIXlt(out.files1, format='%Y_%m_%d_%H_%M_%S')

    max.date <- max(out.files1.date)

    # Collecting these objects here as they have to be formatted
    yr <- max.date$year + 1900 # year is years since 1900
    month <- formatC(max.date$mon + 1, width=2, flag='0') # months are zero indexed (WHY??)
    day <- formatC(max.date$mday, width=2, flag='0')
    hour <- formatC(max.date$hour, width=2, flag='0')
    min <- formatC(max.date$min, width=2, flag='0')
    sec <- formatC(max.date$sec, width=2, flag='0')

    str.date1 <- paste0(yr, '_',
                       month, '_',
                       day, '_',
                       hour, '_',
                       min, '_',
                       sec)
    geojson_file_name1 <- paste0(geojson_file_path_base, '/', str.date1, '/', geojson_file_name_base)
  }
  # Second output dir
  if(length(out.files2) == 1) {
    geojson_file_name2 = paste0(geojson_file_path_int, '/', out.files2[1], '/', geojson_file_name_int)
  }
  else if(length(out.files2) > 1) {
    out.files2.date <- as.POSIXlt(out.files2, format='%Y_%m_%d_%H_%M_%S')

    max.date <- max(out.files2.date)

    # Collecting these objects here as they have to be formatted
    yr <- max.date$year + 1900 # year is years since 1900
    month <- formatC(max.date$mon + 1, width=2, flag='0') # months are zero indexed (WHY??)
    day <- formatC(max.date$mday, width=2, flag='0')
    hour <- formatC(max.date$hour, width=2, flag='0')
    min <- formatC(max.date$min, width=2, flag='0')
    sec <- formatC(max.date$sec, width=2, flag='0')

    str.date2 <- paste0(yr, '_',
                        month, '_',
                        day, '_',
                        hour, '_',
                        min, '_',
                        sec)
    geojson_file_name2 <- paste0(geojson_file_path_int, '/', str.date2, '/', geojson_file_name_int)
  }

  # Generate output filename
  plot_destination <- paste(v, region, run, intervention, year, 'diffmap.pdf', sep='_')
  plot_destination <- paste('plots', plot_destination, sep='/')

  main.diff(geojson_file_name1, geojson_file_name2, plot_destination, v)
}

main()
#main.diff("output/baseline/nanmean_SF_12_2018.geojson", 
#          "output/povertyUplift/nanmean_SF_12_2018.geojson",
#          "output/baseline/sf12_baseline_povertyUplift_diff_map.pdf", 
#          "sheffield", 
#          "SF_12")