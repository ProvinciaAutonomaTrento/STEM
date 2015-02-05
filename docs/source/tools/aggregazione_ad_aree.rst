Aggregazione ad aree
================================

Il modulo prende in input un primo vettoriale relativo a parametri di interesse (ad es. shape file delle chiome) e un secondo vettoriale che delimita le aree di interesse (ad es. shapefile del catasto sull'area di competenza).
Per ogni area del secondo vettoriale vengono calcolate le statistiche di uno o più parametri di interesse (ad es. altezze medie, volume totale, ecc.) memorizzati nel primo file.

.. only:: latex

  .. image:: ../_static/tool_images/aggregazione_ad_aree.png


Input
------------

**Dati di input (vettoriale di punti o aree)**: nella finestra compaiono i file vettoriali attualmente aperti in QGIS.
Selezionare il vettoriale relativo ai parametri di interesse.

**Dati di input (vettoriale di aree)**: nella finestra compaiono i file vettoriali attualmente aperti in QGIS. Selezionare il vettoriale relativo alla suddivisione in aree di interesse.

Parametri
------------

**Seleziona la colonna da considerare per le statistiche**: seleziona uno o più parametri di interesse memorizzati sul vettoriale di punti o aree e su cui si vogliono calcolare le statistiche.

**Metodo statistico di aggregazione**: Seleziona il parametro statistico da considerare sull'area di applicazione. I parametri statistici implementati sono:

 * *sum*: calcola la somma del parametro di interesse sull'area di interesse.
 * *average*: calcola la media del parametro di interesse sull'area di interesse.
 * *median*: calcola la mediana del parametro di interesse sull'area di interesse.
 * *mode*: calcola la moda del parametro di interesse sull'area di interesse.
 * *minimum*: calcola il minimo del parametro di interesse sull'area di interesse.
 * *maximum*: calcola il massimo del parametro di interesse sull'area di interesse.
 * *range*: calcola l'intervallo di valori del parametro di interesse sull'area di interesse.
 * *stddev*: calcola la deviazione standard del parametro di interesse sull'area di interesse.
 * *variance*: calcola la varianza del parametro di interesse sull'area di interesse.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
