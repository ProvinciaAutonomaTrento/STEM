##Struttura bosco=group
##File_cime_o_chiome=vector
##Altezza_albero=Field File_cime_o_chiome
##Area_chioma=Field File_cime_o_chiome
##Bioma=number 19 
##Definisci_EPSG=string
##load_vector_using_rgdal
##Output=output vector

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("sp")
install.packages("raster")
install.packages("rgdal")
install.packages("itcSegment")

library(sp)
library(rgdal)
library(raster)
library(itcSegment)

File_cime_o_chiome$CD_m <- 2*sqrt(File_cime_o_chiome@data[Area_chioma]/pi)
File_cime_o_chiome$CD_m <- as.numeric(unlist(File_cime_o_chiome$CD_m))
File_cime_o_chiome$dbh <- NA
File_cime_o_chiome$dbh <- dbh(File_cime_o_chiome@data[Altezza_albero],File_cime_o_chiome$CD_m,biome=Bioma)
File_cime_o_chiome$dbh <- as.numeric(unlist(File_cime_o_chiome$dbh))

crs_wgs84 <- CRS(SRS_string = paste0("EPSG:", Definisci_EPSG))
proj4string(File_cime_o_chiome) <- crs_wgs84

Output= File_cime_o_chiome
