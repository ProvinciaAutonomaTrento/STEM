Filtro riduzione del rumore
================================

Il modulo riduce il rumore di un'immagine raster applicando filtri spaziali al raster selezionato. Il valore di ogni pixel viene sostituito dal valore della funzione scelta applicata ad un intorno di pixel scelto dall'utente. Il file di output sarà una nuova immagine raster.

.. only:: latex

  .. image:: ../_static/tool_images/filtro_riduzione_del_rumore.png

Input
------------

**Dati di input**: selezionare il raster da utilizzare tra quelli attualmente aperti in QGIS.

**Selezione bande**: selezionare le bande che si vogliono utilizzate; se non si seleziona nulla vengono utilizzate tutte le bande.

Parametri
------------

**Selezione l'algoritmo**: selezionare uno degli algoritmi possibili, attualmente solo neighbors.

**Selezione il metodo per il neighbors**: si possono scegliere diversi metodi per effettuare la riduzione del rumore

  * *average*: media dei pixel dell'intorno (neighbors);
  * *median*: mediana dei pixel dell'intorno (neighbors);
  * *mode*: moda dei pixel dell'intorno (neighbors);
  * *minimum*: minimo dei pixel dell'intorno (neighbors);
  * *maximum*: massimo dei pixel dell'intorno (neighbors);
  * *range*: intervallo dei pixel dell'intorno (neighbors);
  * *stddev*: deviazione standard dei pixel dell'intorno (neighbors);
  * *sum*: somma dei pixel dell'intorno (neighbors);
  * *count*: numero dei pixel dell'intorno (neighbors);
  * *variance*: varianza dei pixel dell'intorno (neighbors);
  * *diversity*: diversità dei pixel dell'intorno (neighbors);
  * *interspersion*: interspersion dei pixel dell'intorno (neighbors);
  * *quart1*: primo quartile dei pixel dell'intorno (neighbors);
  * *quart3*: terzo quartile dei pixel dell'intorno (neighbors);
  * *perc90*: 90esimo percentile dei pixel dell'intorno (neighbors);
  * *quantile*: n-esimo quartile dei pixel dell'intorno (neighbors).

**Valore del quantile**: valore tra 0 e 1 indicante in quantile da calcolare. Opzione attiva solos e si selezione "quantile" come metodo per il neighbor.
  
**Dimensione del neighborhood**: valore numerico dispari indicativo della dimensione della finestra mobile del filtro. Il valore deve essere dispari.

**Usa Neighborhood circolare**: se selzionato veine usata uan finestra mobile circolare anzichè quadrata.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
