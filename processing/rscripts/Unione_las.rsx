##Pre-elaborazione Lidar=group
##FileLas=file
##FileLas_2=file
##Output=output file

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("lidR")
install.packages("sp")
install.packages("raster")

library(sp)
library(raster)
library(lidR)

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("raster:", packageVersion("raster"))
paste("lidR:", packageVersion("lidR"))

path_1 <- file.path(FileLas)
path_2 <- file.path(FileLas_2)

path_output <- file.path(Output)

las1 <- readLAS(path_1)
las2 <- readLAS(path_2)

las_mesh <- rbind(las1, las2)

writeLAS(las_mesh, path_output)