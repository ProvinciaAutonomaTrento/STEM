Estrazione feature LIDAR da poligoni
====================================

Il modulo permette di estrarre feature LIDAR a partire da un file .las e uno shapefile poligonale. L'output è uno shapefile contente come attributi i parametri estratti dal file .las.

.. only:: latex

  .. image:: ../_static/tool_images/estrazione_feature_lidar_da_poligoni.png


Input
------------

**Dati di input**: selezionare lo shapefile da usare per ritagliare il file .las. Lo shapefile deve essere stato precedentemente aperto in Qgis.

**File LAS di input**: selezionare il file .las da ritagliare.

Parametri
------------

**Seleziona le statistiche da calcolare**: selezionare dal menù a tendina le statistiche da calcolare. E' possibile scegliere più statistiche.
	* *Valore massimo altezza punti*: valore massimo di altezza dei punti.
	* *Altezza media punti*: valore medio di altezza dei punti.
	* *N-esimo percentile altezze punti*: percentile sulle altezze dal 10mo al 90mo.
	* *Coefficiente di variazione*: rapporto tra la deviazione standard delle altezze dei punti e la media delle altezze.
	* *Numero ritorni sopra l'altezza media diviso il totale dei ritorni*
	* *Numero ritorni sopra 2 metri diviso il totale dei ritorni*

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
