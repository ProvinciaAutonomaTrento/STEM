##Pre-elaborazione Lidar=group
##FileLas=file
##DTM=raster
##Output_las=output file
##single_or_multi=output number

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("sp")
install.packages("raster")
install.packages("lidR")

library(sp)
library(raster)
library(lidR)

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("raster:", packageVersion("raster"))
paste("lidR:", packageVersion("lidR"))

las_path <-file.path(FileLas)

dtm <- DTM[[1]]

fileLas <- readLAS(las_path)

chm <- normalize_height(fileLas, dtm, na.rm = TRUE)

writeLAS(chm, file = Output_las)
single_or_multi = 0
