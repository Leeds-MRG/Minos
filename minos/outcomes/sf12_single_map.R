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
  parser$add_argument('-r', '--region', help='Which region are we mapping? 
                      Currently available are Glasgow, Sheffield, Manchester, 
                      and Scotland.')
  parser$add_argument('-y', '--year', help='What year to map data for.')
  parser$add_argument('-s', '--synthetic', help='Is this a synthetic population run being mapped?')
  parser$add_argument("-v", "--v", dest='var', help="What variable to map.")
  
  args <- parser$parse_args()
  output_subdir <- args$mode
  run <- args$baseline
  region <- args$region
  year <- args$year
  synth <- args$synth
  v <- args$var

  ## handle runtime subdirectory
  # first construct geojson file path and name from arguments
  geojson_file_path <- paste0('output/', output_subdir, '/', run, '/')
  geojson_file_name <- paste0(region, '_nanmean_', v, '_', year, '.geojson')
  
  # first select only the path (not filename)
  out.files <- list.files(geojson_file_path)
  
  # if length of out.files is 1, we know that is the directory to look in
  if(length(out.files) == 1) {
    geojson_file_name = paste0(geojson_file_path, '/', out.files[1], '/', geojson_file_name)
  } # if out.files length is more than 1, we have multiple directories in the folder. Pick the latest one
  else if(length(out.files) > 1) {
    out.files.date <- as.POSIXlt(out.files, format='%Y_%m_%d_%H_%M_%S')
    max.date <- max(out.files.date)
    
    # Collecting these objects here as they have to be formatted
    yr <- max.date$year + 1900 # year is years since 1900
    month <- formatC(max.date$mon + 1, width=2, flag='0') # months are zero indexed (WHY??)
    day <- formatC(max.date$mday, width=2, flag='0')
    hour <- formatC(max.date$hour, width=2, flag='0')
    min <- formatC(max.date$min, width=2, flag='0')
    sec <- formatC(max.date$sec, width=2, flag='0')
    # generate the string runtime directory so we can add to the path
    str.date <- paste0(yr, '_',
                       month, '_',
                       day, '_',
                       hour, '_',
                       min, '_',
                       sec)

    geojson_file_name <- paste0(geojson_file_path, '/', str.date, '/', geojson_file_name)
  }

  # Generate output filename
  #plot_destination <- paste(v, region, run, year, 'map.pdf', sep='_')
  
  if (tolower(synth) == 'true'){
    plot_destination <- paste(v, region, 'synthetic', run, year, 'map.pdf', sep='_')
  }
  else {
    plot_destination <- paste(v, region, run, year, 'map.pdf', sep='_')
  }

  plot_destination <- paste('plots', plot_destination, sep='/')

  main.single(geojson_file_name, plot_destination, v)
}


main <- function(){
  
  parser <- ArgumentParser(description="Plot a map of some MINOS geojson.")
  parser$add_argument("-m", "--mode", dest='mode', help="What source to use. e.g. defualt_config")
  parser$add_argument("-i", "--intervention", dest='intervention', help="What inteverntion to map. e.g. livingWageIntervention")
  parser$add_argument("-r", "--region", dest='region', help="What spatial region to use. sheffield, manchester, scotland(not yet)")
  parser$add_argument("-y", "--year", dest='yearr', help="What year of MINOS data to map.")
  parser$add_argument("-d", "--destination", dest='destination', help="Where to save to.")
  
  args <- parser$parse_args()
  
  mode <- args$mode
  intervention <- args$intervention
  region <- args$region
  year <- args$year 
  destination_file_name <- args$destination

  #mode <- "default_config"
  #intervention <- "baseline"
  #region <- "manchester"
  #year <- 2025
  #v <- "SF_12"
  
  ## handle runtime subdirectory
  # first select only the path (not filename)
  geojson_file_name <- get_geojson_file_name(mode, intervention, region, year)
  print(geojson_file_name)
  main.single(geojson_file_name, destination_file_name)
}

main()