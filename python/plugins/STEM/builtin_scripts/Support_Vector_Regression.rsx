##Stima dei parametri=group
##Dati_di_input_vettoriale_di_training=vector
##Seleziona_la_colonna_del_parametro_da_stimare=Field Dati_di_input_vettoriale_di_training
##Vettoriale_di_mappa=vector
##Inserire_numero_di_fold_della_cross_validation=optional number
##Seleziona_il_kernel_da_utilizzare=selection lineare;polinomiale;radiale
##Inserire_il_parametro_C=optional number
##Inserire_il_valore_di_epsilon=optional number
##Inserire_il_valore_di_gamma=optional number
##Inserire_il_valore_del_polinomio=optional number
##Selezionare_la_trasformazione=selection nessuna;radice_quadra;logaritmica
##Seleziona_variabili=selection no;manuale;file
##Colonne_delle_feature_da_utilizzare=optional string
##File_di_selezione=optional file
##Vettoriale_di_validazione=optional vector
##Seleziona_colonna_per_la_validazione=optional Field Vettoriale_di_validazione
##Risultato=output vector
##Nome_colonna_per_i_valori_della_stima=string
##Accuratezza=output file
##load_vector_using_rgdal is specified

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("rgdal")
install.packages("kernlab")
install.packages("e1071")
install.packages("caret")

library(rgdal)
library(kernlab)
library(e1071)
library(caret)

print("Versione Packages:")
paste("kernlab:", packageVersion("kernlab"))
paste("e1071:", packageVersion("e1071"))
paste("rgdal:", packageVersion("rgdal"))
paste("caret:", packageVersion("caret"))


if(Seleziona_il_kernel_da_utilizzare== 0){
  Seleziona_il_kernel_da_utilizzare="lineare"
} else if (Seleziona_il_kernel_da_utilizzare== 1){
  Seleziona_il_kernel_da_utilizzare="polinomiale"
} else if (Seleziona_il_kernel_da_utilizzare== 2){
  Seleziona_il_kernel_da_utilizzare="radiale"
}

if(Seleziona_variabili== 0){
  Seleziona_variabili="no"
} else if (Seleziona_variabili== 1){
  Seleziona_variabili="manuale"
} else if (Seleziona_variabili== 2){
  Seleziona_variabili="file"
}

if(Seleziona_variabili=="file"){
  predictor <- read.table(File_di_selezione)
  predictor = as.character(predictor)
  my_variable<- c(predictor)
  new_verita <- Dati_di_input_vettoriale_di_training[ , my_variable]
  new_vettoriale <- Vettoriale_di_mappa[ , my_variable]
  predict <- Dati_di_input_vettoriale_di_training[[Seleziona_la_colonna_del_parametro_da_stimare]]
} else if(Seleziona_variabili=="manuale"){
  predictor<- strsplit(Colonne_delle_feature_da_utilizzare, " ")[[1]]
  predictor = as.character(predictor)
  my_variable<- c(predictor)
  new_verita <- Dati_di_input_vettoriale_di_training[ , my_variable]
  new_vettoriale <- Vettoriale_di_mappa[ , my_variable]
  predict <- Dati_di_input_vettoriale_di_training[[Seleziona_la_colonna_del_parametro_da_stimare]]
} else if(Seleziona_variabili=="no"){ 
  colonna <- which(colnames(Dati_di_input_vettoriale_di_training@data) == Seleziona_la_colonna_del_parametro_da_stimare)
  new_verita <- Dati_di_input_vettoriale_di_training[-colonna]
  new_vettoriale <- Vettoriale_di_mappa
  predict <- Dati_di_input_vettoriale_di_training[[colonna]]
}

predict <- as.numeric(predict)

if(Selezionare_la_trasformazione== 0){
  Selezionare_la_trasformazione="nessuna"
} else if (Selezionare_la_trasformazione== 1){
  Selezionare_la_trasformazione="radice_quadra"
} else if (Selezionare_la_trasformazione== 2){
  Selezionare_la_trasformazione="logaritmica"
}

if(Selezionare_la_trasformazione=="radice_quadra"){
  predict = sqrt(predict)
} else if (Selezionare_la_trasformazione=="logaritmica"){
  predict = log(predict)
} 

new_vettoriale <- data.frame(new_vettoriale)

if(Seleziona_variabili=="no"){
  Dimension <- length(new_verita)
} else {
  Dimension <- length(my_variable)
}

if(is.null(Inserire_il_parametro_C) == TRUE){
  Inserire_il_parametro_C = 1
}
if(is.null(Inserire_il_valore_del_polinomio) == TRUE){
  Inserire_il_valore_del_polinomio = 3
}
if(is.null(Inserire_il_valore_di_gamma) == TRUE){
  Inserire_il_valore_di_gamma = (1/Dimension)
}
if(is.null(Inserire_il_valore_di_epsilon) == TRUE){
  Inserire_il_valore_di_epsilon = 0.1
}

if(is.null(Inserire_numero_di_fold_della_cross_validation) == TRUE){
  if(Seleziona_il_kernel_da_utilizzare == "lineare"){
    fit_mod<- svm(predict ~ ., data = new_verita, type = "eps-regression", kernel = "linear", 
                  epsilon = Inserire_il_valore_di_epsilon, cost = Inserire_il_parametro_C)
  } else if(Seleziona_il_kernel_da_utilizzare == "polinomiale"){
    fit_mod<- svm(predict ~ ., data = new_verita, type = "eps-regression", kernel = "polynomial", 
                  epsilon = Inserire_il_valore_di_epsilon, cost = Inserire_il_parametro_C, degree = Inserire_il_valore_del_polinomio)
  } else if(Seleziona_il_kernel_da_utilizzare == "radiale"){
    fit_mod<- svm(predict ~ ., data = new_verita, type = "eps-regression", kernel = "radial", 
                  epsilon = Inserire_il_valore_di_epsilon, cost = Inserire_il_parametro_C, gamma = Inserire_il_valore_di_gamma)
  }
} else {
  if(Seleziona_il_kernel_da_utilizzare == "lineare"){
    fit_mod<- svm(predict ~ ., data = new_verita, type = "eps-regression", kernel = "linear", 
                  epsilon = Inserire_il_valore_di_epsilon, cost = Inserire_il_parametro_C, cross = Inserire_numero_di_fold_della_cross_validation)
  } else if(Seleziona_il_kernel_da_utilizzare == "polinomiale"){
    fit_mod<- svm(predict ~ ., data = new_verita, type = "eps-regression", kernel = "polynomial", 
                  epsilon = Inserire_il_valore_di_epsilon, cost = Inserire_il_parametro_C, degree = Inserire_il_valore_del_polinomio, cross = Inserire_numero_di_fold_della_cross_validation)
  } else if(Seleziona_il_kernel_da_utilizzare == "radiale"){
    fit_mod<- svm(predict ~ ., data = new_verita, type = "eps-regression", kernel = "radial", 
                  epsilon = Inserire_il_valore_di_epsilon, cost = Inserire_il_parametro_C, gamma = Inserire_il_valore_di_gamma, cross = Inserire_numero_di_fold_della_cross_validation)
  }
}  

risultato_sl <- c(NA)
risultato_sl = predict(fit_mod, new_vettoriale)

if(Selezionare_la_trasformazione == "radice_quadra"){
  risultato_sl = risultato_sl*risultato_sl
} else if(Selezionare_la_trasformazione == "logaritmica"){
  risultato_sl = exp(risultato_sl)
} else {
  risultato_sl = predict(fit_mod, new_vettoriale)
}
Vettoriale_di_mappa@data = cbind(Vettoriale_di_mappa@data, risultato_sl)
colnames(Vettoriale_di_mappa@data)[colnames(Vettoriale_di_mappa@data) == "risultato_sl"] <- Nome_colonna_per_i_valori_della_stima

Risultato <- Vettoriale_di_mappa


if(is.null(Vettoriale_di_validazione) == FALSE){
if(Seleziona_variabili=="no"){
  colonna <- which(colnames(Vettoriale_di_validazione@data) == Seleziona_colonna_per_la_validazione)
  new_validazione <- Vettoriale_di_validazione[-colonna]
} else {
  new_validazione <- Vettoriale_di_validazione[ , my_variable]
}
  #predictions <- predict(fit_mod, new_validazione)
  predictions <- predict(fit_mod, new_validazione@data)
  test <- as.numeric(Vettoriale_di_validazione[[Seleziona_colonna_per_la_validazione]])
  statistics_validation <- data.frame(
  R2 = R2(predictions, test),
  RMSE = RMSE(predictions, test),
  MAE = MAE(predictions, test)
)
capture.output(statistics_validation, file = Accuratezza)
}