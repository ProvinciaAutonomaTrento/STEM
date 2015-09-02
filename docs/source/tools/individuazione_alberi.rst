Individuazione alberi
================================

Il modulo permette di individuare le posizioni degli alberi a partire da un file raster del Canopy Height Model (ottenuto in uscita dal modulo *Rasterizzazione file LAS*). L'algoritmo individua i massimi locali usando una finestra mobile la cui dimensione è impostata dall'utente. La finestra mobile può avere dimensione variabile, con valori più piccoli per altezze basse e più alti per altezze maggiori. L'utente imposta anche una soglia minima di altezza per gli alberi da individuare.
Se il raster del CHM di partenza ha una risoluzione spaziale molto alta (es. 0.25 m) si consiglia di applicare un filtro di media 3x3 prima di usare questo modulo.

.. only:: latex

  .. image:: ../_static/tool_images/delimitazione_chiome.png


Input
------------

**CHM di input**: selezionare il file raster del CHM di partenza.

Parametri
------------

**Valore minimo della finestra mobile per trovare gli alberi**: dimensione minima della finestra mobile usata per identificare i massimi locali. Il valore deve essere dispari e maggiore o uguale a 3.

**Valore massimo della finestra mobile per trovare gli alberi**: dimensione massima della finestra mobile usata per identificare i massimi locali. Il valore deve essere dispari e maggiore o uguale al parametro precedente (*Valore minimo della finestra mobile per trovare gli alberi*).

**Valore minimo dell'altezza degli alberi**: soglia minima di altezza per gli alberi da individuare (es. 2 m).

Output
------------

**Risultato**: inserire il percorso e il nome dello shapefile di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
