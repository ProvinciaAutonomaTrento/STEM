Individuazione alberi
================================

Il modulo permette di individuare le posizioni degli alberi a partire da un file .las del Canopy Height Model (ottenuto in uscita dal modulo *Estrazione CHM*). Vi sono due algoritmi di segmentazione selezionabili: Li (https://www.rdocumentation.org/packages/lidR/versions/3.0.4/topics/li2012) e Dalponte (https://www.rdocumentation.org/packages/lidR/versions/3.0.2/topics/dalponte2016). 
Si otterrà una nuvola di punti con un nuovo attributo "treeID" indipendentemente dall'algoritmo scelto e la posizione delle cime come file vettoriale.

.. only:: latex

  .. image:: ../_static/tool_images/individuazione_alberi.png


Input
------------

**File Las di input**: selezionare il file .las (o .laz).

**CHM raster Dalponte** (opzionale): selezionare il file raster del CHM necessario per l'agoritmo di Dalponte.

Parametri
------------

**Algoritmo segmentazione**: selezionare l'agoritmo di segmentazione.

**Inserire altezza minima albero**: inserire l'altezza in metri. Questo è un parametro necessario per entrambi gli algoritmi.

**Ampiezza minima finestra Dalponte**: dimensione minima in piexels della finestra mobile usata per identificare i massimi locali. Questo è un parametro necessario per l'algoritmo Dalponte.

**Forma finestra Dalponte**: definire la forma della finestra mobile. Questo è un parametro necessario per l'algoritmo Dalponte.

**Zu Li**: parametro necessario per l'algoritmo di Li. Si consiglia un valore di 15,0.

**Distanza 1 Li**: parametro necessario per l'algoritmo di Li. Si consiglia un valore di 1,5.

**Distanza 2 Li**: parametro necessario per l'algoritmo di Li. Si consiglia un valore di 2,0.

**Massimo raggio chioma Li**: parametro necessario per l'algoritmo di Li. Si consiglia un valore di 10,0.

Output
------------

**Risultato**: inserire il percorso e il nome dello shapefile di output.

**Output Las**: inserire percorso file .las (o .laz) contenente il nuovo attributo "treeID".

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
