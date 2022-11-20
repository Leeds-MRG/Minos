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
    
  main.diff(geojson_file_name1, geojson_file_name2, plot_destination, mode, v)
}

main()
#main.diff("output/baseline/nanmean_SF_12_2018.geojson", 
#          "output/povertyUplift/nanmean_SF_12_2018.geojson",
#          "output/baseline/sf12_baseline_povertyUplift_diff_map.pdf", 
#          "sheffield", 
#          "SF_12")