library(argparse)
source("minos/validation/minos_SF12_maps.R")

main <- function(){
  
  parser <- ArgumentParser(description="Plot a map of some MINOS geojson.")
  parser$add_argument("-f", "--geojson_file_name", dest='file', help="What geojson to use.")
  parser$add_argument("-d", "--plot_destination", dest='destination', help="Where to save a plot.")
  parser$add_argument("-m", "--mode", dest='mode', help="What spatial region to use. sheffield, manchester, scotland(not yet)")
  parser$add_argument("-v", "--v", dest='var', help="What variable to map.")
  
  args <- parser$parse_args()
  geojson_file_name <- args$file
  plot_destination <- args$destination
  mode <- args$mode
  v <- args$var

  ## handle runtime subdirectory
  # first select only the path (not filename)
  out.files <- list.files(dirname(geojson_file_name))

  if(length(out.files) == 1) {
    geojson_file_name = paste0(dirname(geojson_file_name), '/', out.files[1], '/', basename(geojson_file_name))
  }
  else if(length(out.files) > 1) {
    out.folders.date <- as.POSIXlt(out.folders, format='%Y_%m_%d_%H_%M_%S')
    max.date <- max(out.folders.date)
    
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
    
    geojson_file_name <- paste0(dirname(geojson_file_name), '/', str.date, '/', basename(geojson_file_name))
  }
  
  main.single(geojson_file_name, plot_destination, mode, v)
}

main()
#main.single("output/baseline/2016.geojson", "output/baseline/scotland_sf12_map.pdf", "scotland", "SF_12")
