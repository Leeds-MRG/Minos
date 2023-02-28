library(argparse)
source("minos/validation/minos_SF12_maps.R")

main <- function(){

  parser <- ArgumentParser(description="Plot a map of some MINOS geojson.")
  parser$add_argument("-f", "--geojson_file_name1", dest='file1', help="What geojson to use.")
  parser$add_argument("-g", "--geojson_file_name2", dest='file2', help="What second geojson to use.")
  parser$add_argument("-d", "--plot_destination", dest='destination', help="Where to save a plot.")
  parser$add_argument("-m", "--mode", dest='mode', help="What spatial region to use. sheffield, manchester, scotland(not yet)")
  parser$add_argument("-v", "--v", dest='var', help="What variable to map.")
  
  args <- parser$parse_args()
  geojson_file_name1 <- args$file1
  geojson_file_name2 <- args$file2
  plot_destination <- args$destination
  mode <- args$mode
  v <- args$var

  ## handle runtime subdirectory
  # first select only the path (not filename)
  out.files1 <- list.files(dirname(geojson_file_name1))
  out.files2 <- list.files(dirname(geojson_file_name2))

  ## Check how many subdirectories, if more than 1 then pick most recent
  # First output dir
  if(length(out.files1) == 1) {
    geojson_file_name1 = paste0(dirname(geojson_file_name1), '/', out.files1[1], '/', basename(geojson_file_name1))
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
    geojson_file_name1 <- paste0(dirname(geojson_file_name1), '/', str.date1, '/', basename(geojson_file_name1))
  }
  # Second output dir
  if(length(out.files2) == 1) {
    geojson_file_name2 = paste0(dirname(geojson_file_name2), '/', out.files2[1], '/', basename(geojson_file_name2))
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
    geojson_file_name2 <- paste0(dirname(geojson_file_name2), '/', str.date2, '/', basename(geojson_file_name2))
  }

  main.diff(geojson_file_name1, geojson_file_name2, plot_destination, mode, v)
}

main()
#main.diff("output/baseline/nanmean_SF_12_2018.geojson", 
#          "output/povertyUplift/nanmean_SF_12_2018.geojson",
#          "output/baseline/sf12_baseline_povertyUplift_diff_map.pdf", 
#          "sheffield", 
#          "SF_12")