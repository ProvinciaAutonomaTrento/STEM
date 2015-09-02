Delimitazione chiome
================================

Il modulo permette di delineare le chiome degli alberi a partire da un file raster del Canopy Height Model (ottenuto in uscita dal modulo *Rasterizzazione file LAS*) e dallo shapefile delle posizioni degli alberi ottenuto col modulo *Individuazione alberi*. L'algoritmo partendo dalle posizioni degli alberi delinea le chiome usando un metodo di tipo *decision tree*. Durante questa fase viene considerata la differenza di altezza tra il massimo locale considerato e i pixel adiacenti, e la loro distanza (la distanza massima è fissata dall'utente). Una volta delineate le chiome sul file raster viene applicato un *convex hull* sul piano x,y ad ogni chioma in modo da renderle più smussate. Le forme così ottenute sono convertite in shapefile e date in output.

NB: l'algoritmo può essere lento se il file di input è grande.

.. only:: latex

  .. image:: ../_static/tool_images/delimitazione_chiome.png


Input
------------

**CHM utilizzato per calcolare le posizioni degli alberi**: selezionare il file raster del CHM usato per calcolare le posizioni degli alberi.

**Vettoriale contenente le posizioni degli alberi**: selezionare il vettoriale con le posizioni degli alberi ottenuto in uscita dal modulo *Individuazione alberi*.

Parametri
------------

**Valore minimo del raggio massimo della chioma**: valore minimo del raggio massimo della chioma in pixel.

**Valore massimo del raggio massimo della chioma**: valore massimo del raggio massimo della chioma in pixel. Deve essere maggiore o uguale a *Valore minimo del raggio massimo della chioma*.

**Soglia di crescita della chioma**: valore di soglia percentuale tra il valore di altezza dell'albero e i valori di altezza più bassi della chioma. Deve essere tra 0 e 1. Default: 0.65.

**Valore minimo dell'altezza della chioma**: soglia minima di altezza per i pixel appartenenti alla chioma (es. 2 m).

Output
------------

**Risultato**: inserire il percorso e il nome dello shapefile di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
