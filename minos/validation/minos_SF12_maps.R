# This file aims to transpose minos outputs onto Chris' spatially weighted GB data
library(geojsonio)
library(ggplot2)
library(broom)
library(sp)
library(readxl)
library(sf)
library(tibble)


# grab data 
poly_data_minos <- geojson_read("/Users/robertclay/data/minos_LSOA_with_SF12_2016.geojson"
                           ,what='sp')
poly_data_real <- geojson_read("/Users/robertclay/data/real_LSOA_with_SF12_2016.geojson"
                              ,what='sp')
# TODO take subset of LSOAs as necessary. E.g. group by those in sheffield or by latlong

# grab lsoas in sheffield metro area for gb.
yorkshire_lsoas <- read_excel("/Users/robertclay/data/yorkshire_lsoas.xlsx",
                              skip=11)
yorkshire_lsoas <- data.frame(yorkshire_lsoas)[-c(1:11),c(5,4)]
colnames(yorkshire_lsoas) <- c("ONS", "metro_area")
unique_lsoas <- unique(yorkshire_lsoas$ONS)
yorkshire_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$ONS%in%unique_lsoas),]
sheffield_lsoas <- yorkshire_lsoas[which(yorkshire_lsoas$metro_area=="Sheffield"),]


sheff_polys_minos <- subset(poly_data_minos, LSOA11CD %in% sheffield_lsoas$ONS)
sheff_polys_minos_sf<- st_as_sf(sheff_polys_minos)
sheff_polys_real <- subset(poly_data_real, LSOA11CD %in% sheffield_lsoas$ONS)
sheff_polys_real_sf<- st_as_sf(sheff_polys_real)


sheff_polys_minos_tb <- as_tibble(sheff_polys_minos_sf)
sheff_polys_real_tb <- as_tibble(sheff_polys_real_sf)

sheff_polys_minos_tb$SF12_diff <- sheff_polys_minos_tb$SF_12 - sheff_polys_real$SF_12
# positive diff implies minos SF12 overestimates sf12.
print("data cleaned. plotting..")

c.min <- min(sheff_polys_minos_tb$SF12_diff)
c.max <- max(sheff_polys_minos_tb$SF12_diff)
  
SF12.map <- ggplot(data = sheff_polys_minos_tb, aes(geometry = geometry, fill=SF12_diff)) + 
  geom_sf() +
  #scale_fill_viridis_c(alpha = .8) + 
  scale_fill_distiller(palette = "PuOr", limits=c(-c.max,c.max)) + 
  #scale_fill_stepsn(colors=c('#0000FF','#FFFFFF','#ff0000'), 
  #                  n.breaks=20, limits=c(-c.max, c.max),) + 
  theme(aspect.ratio=9/16) +
  ggtitle("Difference in SF12 spatial distribution for real US data and minos in Sheffield.") +
  xlab("Longitude") +
  ylab("Latitude")
SF12.map


five_largest <- tail(sort(sheff_polys_minos_tb$SF12_diff), 5)
five_largest_lsoas <- sheff_polys_minos_tb[which(sheff_polys_minos_tb$SF12_diff%in%five_largest),]
# most over estimated areas.
# broomhill student area, greystones posh, northern general hospital ,woodhouse badger estate rough, direct city centre. 
                                           
