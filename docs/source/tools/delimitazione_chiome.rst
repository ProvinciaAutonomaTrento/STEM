Delimitazione chiome
================================

Il modulo permette di delineare le chiome degli alberi a partire da un file .las del Canopy Height Model (ottenuto in uscita dal modulo "Estrazione CHM"). L'algoritmo esegue le seguenti operazioni: 1) viene creato un raster del CHM alla risoluzione impostata dall'utente; 2) il raster viene filtrato con un filtro di media usando una finestra mobile impostata dall'utente; 3) i massimi locali vengono identificati usando una finestra mobile impostata dall'utente; 4) partendo dai massimi locali le chiome vengono definite usando un metodo di tipo *decision tree*. Durante questa fase viene considerata la differenza di altezza tra il massimo locale considerato e i pixel adiacenti, e la loro distanza (la distanza massima è fissata dall'utente); 5) partendo dalle chiome delineate al punto 4 vengono estratti i punti LIDAR di ogni chioma e vengono sogliati usando il metodo di sogliatura Otsu; 6) ai punti LIDAR contenuti in ogni chioma con valore di altezza al di sopra della soglia Otsu (di valore diverso per ogni chioma) viene applicato un *convex hull* sul piano x,y; 7) le forme cosi' ottenute sono convertite in shapefile e date in output.

NB: l'algoritmo e' molto lento se il file di input è grande. I tempi di elaborazione sono di circa 5 minuti su file di dimensione 100x100 m.

.. only:: latex

  .. image:: ../_static/tool_images/delimitazione_chiome.png


Input
------------

**File .las del CHM**: selezionare il file .las del CHM di partenza.

Parametri
------------

**Risoluzione del raster**: risoluzione del raster di partenza. Default: 0.5 m.

**Dimensione finestra mobile filtro di media**: dimensione della finestra mobile del fitro di media. Il valore deve essere dispari e maggiore o uguale a 3. Default: 3.

**Dimensione finestra mobile massimi locali**: dimensione della finestra mobile usata per identificare i massimi locali. Il valore deve essere dispari e maggiore o uguale a 3. Default: 5.

**Distanza massima tra massimo locale e pixel**: distanza massima (in numero di pixels) tra il massimo locale e i pixel appartenerti alla sua chioma. Questo valore si può interpretare come il raggio massimo delle chiome delineate. Default: 20.


Output
------------

**Risultato**: inserire il percorso e il nome dello shapefile di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
