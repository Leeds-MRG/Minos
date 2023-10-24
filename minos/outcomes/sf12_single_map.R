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
  parser$add_argument("-d", "--plot_destination", dest='destination', help="Where to save a plot.")
  parser$add_argument("-v", "--v", dest='var', help="What variable to map.")
  
  args <- parser$parse_args()
  output_subdir <- args$mode
  run <- args$baseline
  region <- args$region
  year <- args$year
  plot_destination <- args$destination
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

  main.single(geojson_file_name, plot_destination, v)
}

main()
#main.single("output/baseline/2016.geojson", "output/baseline/scotland_sf12_map.pdf", "scotland", "SF_12")
