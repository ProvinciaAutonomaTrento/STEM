##Pre-elaborazione Lidar=group
##FileLas=file
##Maschera=vector polygon
##Output=output file
##load_vector_using_rgdal

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("lidR")
install.packages("sp")
install.packages("raster")
install.packages("rgdal")

library(sp)
library(rgdal)
library(raster)
library(lidR)

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("raster:", packageVersion("raster"))
paste("rgdal:", packageVersion("rgdal"))
paste("lidR:", packageVersion("lidR"))

las_path <-file.path(FileLas)

fileLas <- readLAS(las_path)

clipped_las <- clip_roi(fileLas, Maschera)

if(is.list(clipped_las) == TRUE){
  clipped_las = do.call("rbind", clipped_las)
}

writeLAS(clipped_las, file = Output)