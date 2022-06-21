#STEM: estrazione chm da file LAS e dtm multipli 
#
#
#copyright: Thomas Maffei 

##Pre-elaborazione Lidar=group
##folder_las=folder
##folder_dtm=folder  
##folder_output=folder  
##single_or_multi=output number

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

#instal the required packages 
install.packages("sp")
install.packages("raster")
install.packages("lidR")

#load libraries
library(sp)
library(raster)
library(lidR)

#define input folders path
#folder_las <- "C:/Users/thoma/Documents/STEM/dati_input/lidar/laz"
#folder_dtm <- "C:/Users/thoma/Documents/STEM/dati_input/lidar/dtm_test"

#create a list of all dtm imported as a raster
list_file_dtm <- list.files(path = folder_dtm, pattern = ".*\\.(asc|tif)$$", full.names = TRUE)
alldtm <- lapply(list_file_dtm, raster)

#read the lascatalog
fileLas <- readLAScatalog(folder_las)

#create function to chech which dtm has the same extent of the las
dtm_list_overlap <- function(las, dtm_list){
   for(i in 1:length(dtm_list)){
    if(is.null(intersect(extent(dtm_list[[i]]), extent(las))) == FALSE) {
        dtm <- dtm_list[[i]]
        return(dtm)
        dtm_list[[i]] <- NA
    } else {
        dtm <- NULL
        next
        }
   }
}

#define user function  to extract CHM from a lascatalog respect a list of dtm
#if a dtm is missing it will skip the normalization of the las file
#if you have more dtm respect to the las files does not matter
chm_chunk_dtm_list <- function(chunk, dtm_list){
    las <- readLAS(chunk)
    if (is.empty(las)) return(NULL)
    dtm <- dtm_list_overlap(las, dtm_list)
    if (is.null(dtm) == FALSE){
        chm <- normalize_height(las, dtm, na.rm = T)
        return(chm)
    } else {
        return(NULL)
    }
}

#define output for each las
opt_output_files(fileLas) <- paste0(folder_output, "/{*}_CHM")
options <- list(automerge = TRUE)
opt_chunk_buffer(fileLas) <- 0

#apply user function over all the las catalog
output <- catalog_apply(fileLas, chm_chunk_dtm_list, dtm_list = alldtm, .options = options)
single_or_multi = 1

