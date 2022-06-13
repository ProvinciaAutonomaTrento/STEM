Delimitazione chiome
================================

Il modulo permette di delineare le chiome e la posizione degli apici delle singole piante a partire da un file raster del Canopy Height Model (ottenuto in uscita dal modulo *Rasterizzazione file LAS*). L'algoritmo si basa sulla funzione itcLiDAR consultabile in https://rdrr.io/cran/itcSegment/man/itcLiDAR.html.

NB: l'algoritmo può essere lento se il file di input è grande.

.. only:: latex

  .. image:: ../_static/tool_images/delimitazione_chiome.png


Input
------------

**File CHM raster**: selezionare il file raster del CHM.

Parametri
------------

**Risoluzione**: risoluzione del raster sul quale viene effettuata la prima segmentazione.

**Ampiezza minima finestra**: ampiezza minima (in pixels) della finestra mobile.

**Ampiezza massima finestra**: ampiezza massima (in pixels) della finestra mobile. Deve essere maggiore o uguale a 'Ampiezza minima finestra'.

**Soglia crescita chioma**: valore di soglia 'TRESHCrown'. Deve essere tra 0 e 1.

**Soglia crescita albero**: valore di soglia 'TRESHSeed'. Deve essere tra 0 e 1. 

**Soglia minima diametro chioma**: soglia minima di diametro dell'abero individuato.

**Soglia massima diametro chioma**: soglia massima di diametro dell'abero individuato. Deve essere maggiore di 'Soglia minima diametro chioma'. 

**Altezza minima albero**: altezza minima dell'albero.

Output
------------

**Output chiome**: inserire il percorso e il nome dello shapefile di output contenete le chiome delineate.

**Output cime chiome**: inserire il percorso e il nome dello shapefile di output delle cime delle chiome.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
