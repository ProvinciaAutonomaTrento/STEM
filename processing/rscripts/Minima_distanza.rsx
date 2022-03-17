##Classificazione Supervisionata=group
##File_raster=raster
##Training_aree=vector polygon
##Seleziona_colonna_codice_classe=Field Training_aree
##Elenco_features=optional string
##File_features=optional file
##Creazione_mappa=selection Si;No
##Numero_di_neighbors=optional number
##Aree_validazione=optional vector 
##Numero_fold_cross_validation=optional number
##Output_mappa=output file
##Output_Info_modello=output file
##Output_Metriche_accuratezza=optional string
##load_vector_using_rgdal

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("sp")
install.packages("raster")
install.packages("rgdal")
install.packages("RStoolbox")

library(sp)
library(raster)
library(rgdal)
library(RStoolbox)

print("Versione Packages:")
paste("sp:", packageVersion("sp"))
paste("raster:", packageVersion("raster"))
paste("rgdal:", packageVersion("rgdal"))
paste("RStoolbox",packageVersion("RStoolbox"))

if(Elenco_features == ""){
   Elenco_features = FALSE
} 

if(File_features == ""){
   File_features = FALSE
} 

if(Elenco_features == FALSE & File_features == FALSE){
  immagine <- File_raster
} else if (Elenco_features == FALSE){
  features <- read.table(File_features)
  features = as.numeric(features)
  immagine <- File_raster[[features]]
} else if (File_features == FALSE){
  feature<- strsplit(Elenco_features, " ")[[1]]
  feature = as.numeric(feature)
  immagine <- File_raster[[feature]]
} 

Training_aree <- spTransform(Training_aree, crs(immagine))
if(is.null(Aree_validazione)==FALSE){
Aree_validazione <- spTransform(Aree_validazione, crs(immagine))
}

if(Creazione_mappa == 0){
  Creazione_mappa = TRUE
} else {
  Creazione_mappa = FALSE
}

if(is.null(Numero_fold_cross_validation) == TRUE){
   Numero_fold_cross_validation = 3
}


if(is.null(Numero_di_neighbors) == FALSE){
  supClass_knn <- superClass(immagine, trainData = Training_aree, responseCol = Seleziona_colonna_codice_classe, filename = Output_mappa, 
                             valData = Aree_validazione, model = "knn", overwrite = TRUE, mode = "classification", predict = Creazione_mappa, predType = "raw",
                             tuneGrid = expand.grid(k = Numero_di_neighbors), kfold = Numero_fold_cross_validation, verbose = TRUE, polygonBasedCV = TRUE)
  model <- supClass_knn$model
  if(is.null(Aree_validazione)==FALSE){
  accuracy <- supClass_knn$validation$performance
  }
} else {
  supClass_knn <- superClass(immagine, trainData = Training_aree, responseCol = Seleziona_colonna_codice_classe, filename = Output_mappa, 
                             valData = Aree_validazione, model = "knn", overwrite = TRUE, mode = "classification", predict = Creazione_mappa,
                              predType = "raw", verbose = TRUE, polygonBasedCV = TRUE, kfold = Numero_fold_cross_validation)
  model <- supClass_knn$model
  if(is.null(Aree_validazione)==FALSE){
  accuracy <- supClass_knn$validation$performance
  }
}
capture.output(model, file = Output_Info_modello)

 if(is.null(Aree_validazione)==FALSE){
capture.output(accuracy, file = Output_Metriche_accuratezza)
}