##Struttura bosco=group
##CHM_las=file
##Algoritmo_segmentazione=selection dalponte2016;li2012
##Altezza_minima_albero=number
##Ampiezza_minima_finestra_Dalponte=optional number
##Forma_finestra_Dalponte=selection square;circular;nulla
##CHM_raster_Dalponte=optional file
##Zu_Li=optional number
##Distanza_1_Li=optional number
##Distanza_2_Li=optional number
##Massimo_raggio_chioma_Li=optional number
##Definisci_EPSG=string
##Output_cima=output vector
##Output_las=output file 

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("sp")
install.packages("raster")
install.packages("rgdal")
install.packages("lidR")

library(sp)
library(raster)
library(rgdal)
library(lidR)

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("raster:", packageVersion("raster"))
paste("rgdal:", packageVersion("rgdal"))
paste("lidR",packageVersion("lidR"))



if(Forma_finestra_Dalponte==0){
Forma_finestra_Dalponte <- "square"
} else if(Forma_finestra_Dalponte==1){
Forma_finestra_Dalponte <- "circular"
} else{
Forma_finestra_Dalponte <- NULL
}

chm_las_path <-file.path(CHM_las)
chm_raster_path <- file.path(CHM_raster_Dalponte)

chm <- readLAS(chm_las_path, select = "xyziarc")

if(Algoritmo_segmentazione == 1){
  seg_tree <- segment_trees(chm, algorithm = li2012(hmin = Altezza_minima_albero, speed_up = Massimo_raggio_chioma_Li,
                                                    dt1 = Distanza_1_Li, dt2 = Distanza_2_Li, Zu = Zu_Li))
  tree_tops <- tree_metrics(seg_tree, func = .stdtreemetrics, attribute = "treeID")
  proj <- "+init=epsg:"
  proj_EPSG <- paste(proj, Definisci_EPSG, sep="")
  crs(tree_tops) <- proj_EPSG
  tree_tops <- st_as_sf(tree_tops)
  tree_tops <- st_zm(tree_tops, drop = TRUE, what = "ZM")
  Output_cima = tree_tops
  writeLAS(seg_tree, file = Output_las)
} else {
  chm_raster <- raster(chm_raster_path)
  ttops <- find_trees(chm, lmf(Ampiezza_minima_finestra_Dalponte, hmin = Altezza_minima_albero, shape = Forma_finestra_Dalponte))
  seg_tree2 <- segment_trees(chm, dalponte2016(chm_raster, ttops))
  tree_tops2 <- tree_metrics(seg_tree2, func = .stdtreemetrics, attribute = "treeID")
  proj <- "+init=epsg:"
  proj_EPSG <- paste(proj, Definisci_EPSG, sep="")
  crs(tree_tops2) <- proj_EPSG
  tree_tops2 <- st_as_sf(tree_tops2)
  tree_tops2 <- st_zm(tree_tops2, drop = TRUE, what = "ZM")
  Output_cima = st_as_sf(tree_tops2)
  writeLAS(seg_tree2, file = Output_las)
}
