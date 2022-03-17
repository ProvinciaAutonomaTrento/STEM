##Stima dei parametri=group
##Dati_di_input_vettoriale_di_training=vector
##Seleziona_la_colonna_del_parametro_da_stimare=Field Dati_di_input_vettoriale_di_training
##Vettoriale_di_mappa=vector
##Inserire_numero_di_fold_della_cross_validation=optional number
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
install.packages("caret")

library(rgdal)
library(caret)

print("Versione Packages:")
paste("rgdal:", packageVersion("rgdal"))
paste("caret:", packageVersion("caret"))

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

if(is.null(Inserire_numero_di_fold_della_cross_validation) == TRUE){
  fit_mod <- lm(predict ~ ., data = new_verita)
} else {
  new_verita = cbind(new_verita@data, predict)
  ctrl <- trainControl(method = "cv", number = Inserire_numero_di_fold_della_cross_validation)
  fit_mod <- train(predict ~ ., data = new_verita, method = "lm", trControl = ctrl)
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
  colonna <- which(colnames(Vettoriale_di_validazione@data) == Seleziona_la_colonna_del_parametro_da_stimare)
  new_validazione <- Vettoriale_di_validazione[-colonna]
} else {
  new_validazione <- Vettoriale_di_validazione[ , my_variable]
}
  predictions <- predict(fit_mod, new_validazione)
  test <- Vettoriale_di_validazione[[Seleziona_la_colonna_del_parametro_da_stimare]]
  statistics_validation <- data.frame(
  R2 = R2(predictions, test),
  RMSE = RMSE(predictions, test),
  MAE = MAE(predictions, test)
)

capture.output(statistics_validation, file = Accuratezza)
}

