##Struttura bosco=group
##File_CHM_raster=raster
##Risoluzione=number
##Ampiezza_minima_finestra=number
##Ampiezza_massima_finestra=number
##Soglia_crescita_chioma=number
##Soglia_crescita_albero=number 
##Soglia_minima_diametro_chioma=number
##Soglia_massima_diametro_chioma=number
##Altezza_minima_albero=number
##Definisci_EPSG=string
##Output_chiome=output vector
##Output_cime_chiome=output vector

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("sp")
install.packages("rgdal")
install.packages("raster")
install.packages("lidR")
install.packages("itcSegment")

library(sp)
library(rgdal)
library(raster)
library(lidR)
library(itcSegment)


print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("rgdal:", packageVersion("rgdal"))
paste("raster:", packageVersion("raster"))
paste("lidR:", packageVersion("lidR"))
paste("itcSegment:", packageVersion("itcSegment"))

coords <- xyFromCell(File_CHM_raster,1:ncell(File_CHM_raster))
valori <-getValues(File_CHM_raster)
xyzlist <- list(X=coords[,'x'], Y=coords[,'y'], Z=valori)
df <- data.frame(xyzlist)
df <- na.omit(df)

crown <- itcLiDAR(df[1], df[2], df[3], epsg = 25832, resolution = Risoluzione, MinSearchFilSize = Ampiezza_minima_finestra, MaxSearchFilSize = Ampiezza_massima_finestra, 
                  TRESHSeed = Soglia_crescita_albero, TRESHCrown = Soglia_crescita_chioma, minDIST = Soglia_minima_diametro_chioma, maxDIST = Soglia_massima_diametro_chioma, 
                  HeightThreshold = Altezza_minima_albero)

tt <- SpatialPoints(cbind(crown$X, crown$Y))

df <- data.frame(crown@data)
treetops <- SpatialPointsDataFrame(coords = tt, data = df, proj4string =crown@proj4string)

proj <- "+init=epsg:"
proj_EPSG <- paste(proj, Definisci_EPSG, sep="")
crs(treetops) <- proj_EPSG

Output_chiome= st_as_sf(crown)
Output_cime_chiome=st_as_sf(treetops)