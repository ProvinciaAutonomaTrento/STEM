##Stima dei parametri=group
##Dati_di_input=vector point
##Seleziona_colonna_indicazione_specie=Field Dati_di_input
##Seleziona_colonna_indicazione_diametro=Field Dati_di_input
##Seleziona_colonna_indicazione_altezza=Field Dati_di_input
##load_vector_using_rgdal
##Output=output vector

print("Versione 2.0.0 - TESTED WITH R.4.1.2 QGIS 3.22")

install.packages("rgdal")

library(rgdal)

print("Versione Packages:")
paste("rgdal:", packageVersion("rgdal"))

volume <- c(NA)
Dati_di_input@data = cbind(Dati_di_input@data, volume)

specie = c("ar", "ab", "la", "fa", "ps", "pc", "pn")
a = c(0.000177, 0.000163, 0.000108, 0.000055, 0.000102, 0.000188, 0.000129)
b = c(1.564254, 1.706560, 1.407756, 1.942089, 1.918184, 1.613713, 1.763086)
c = c(1.051565, 0.941905, 1.341377, 1.006420, 0.830164, 0.985266, 0.938445)
d0 = c(3.694650, 3.694650, 3.694650, 4.009100, 3.694650, 3.694650, 3.694650)
df <- data.frame(specie, a, b, c, d0)

tree1 <- data.frame(Dati_di_input)

al <- which(tree1[[Seleziona_colonna_indicazione_specie]] == "al")
tree1[[Seleziona_colonna_indicazione_specie]][al] <- "fa"

volume_ar = function(tree1){
  df$a[1]*((tree1[[Seleziona_colonna_indicazione_diametro]][i] - df$d0[1])^df$b[1]) * (tree1[[Seleziona_colonna_indicazione_altezza]][i]^df$c[1])
}
volume_ab = function(tree1){
  df$a[2]*((tree1[[Seleziona_colonna_indicazione_diametro]][i] - df$d0[2])^df$b[2]) * (tree1[[Seleziona_colonna_indicazione_altezza]][i]^df$c[2])
}
volume_la = function(tree1){
  df$a[3]*((tree1[[Seleziona_colonna_indicazione_diametro]][i] - df$d0[3])^df$b[3]) * (tree1[[Seleziona_colonna_indicazione_altezza]][i]^df$c[3])
}
volume_fa = function(tree1){
  df$a[4]*((tree1[[Seleziona_colonna_indicazione_diametro]][i] - df$d0[4])^df$b[4]) * (tree1[[Seleziona_colonna_indicazione_altezza]][i]^df$c[4])
}
volume_ps = function(tree1){
  df$a[5]*((tree1[[Seleziona_colonna_indicazione_diametro]][i] - df$d0[5])^df$b[5]) * (tree1[[Seleziona_colonna_indicazione_altezza]][i]^df$c[5])
}
volume_pc = function(tree1){
  df$a[6]*((tree1[[Seleziona_colonna_indicazione_diametro]][i] - df$d0[6])^df$b[6]) * (tree1[[Seleziona_colonna_indicazione_altezza]][i]^df$c[6])
}
volume_pn = function(tree1){
  df$a[7]*((tree1[[Seleziona_colonna_indicazione_diametro]][i] - df$d0[7])^df$b[7]) * (tree1[[Seleziona_colonna_indicazione_altezza]][i]^df$c[7])
}

#apply to the data frame the several functions
for(i in 1:length(tree1[[Seleziona_colonna_indicazione_specie]])){
  if(tree1[[Seleziona_colonna_indicazione_specie]][i]=="ar"){
    tree1$volume[i] = volume_ar(tree1)
  } else if (tree1[[Seleziona_colonna_indicazione_specie]][i]=="ab"){
    tree1$volume[i] = volume_ab(tree1)
  } else if (tree1[[Seleziona_colonna_indicazione_specie]][i]=="la"){
    tree1$volume[i] = volume_la(tree1)
  } else if (tree1[[Seleziona_colonna_indicazione_specie]][i]=="fa"){
    tree1$volume[i] = volume_fa(tree1)
  } else if (tree1[[Seleziona_colonna_indicazione_specie]][i]=="ps"){
    tree1$volume[i] = volume_ps(tree1)
  } else if (tree1[[Seleziona_colonna_indicazione_specie]][i]=="pc"){
    tree1$volume[i] = volume_pc(tree1)
  } else if (tree1[[Seleziona_colonna_indicazione_specie]][i]=="pn"){
    tree1$volume[i] = volume_pn(tree1)
  }
}

new_SPDF <- SpatialPointsDataFrame(coords = Dati_di_input@coords, data = tree1, proj4string = Dati_di_input@proj4string)

Output = new_SPDF
