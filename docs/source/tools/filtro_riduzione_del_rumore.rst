Filtro riduzione del rumore
================================

Il modulo riduce il rumore di un'immagine raster applicando filtri spaziali al raster selezionato. Il filtraggio è solitamente utilizzato come fase preliminare del processamento delle immagini telerilevate. In particolare, l'algoritmo sostituisce il valore di ogni pixel nell'immagine con il valore della funzione scelta applicata ad un intorno di pixel scelto dall'utente. Il file di output sarà una nuova immagine raster.

A seconda del tipo di metodo scelto l'utput potrà essere usato per diverse applicazioni: ad esempio il metodo *average* é solitamente utilizzato per uniformare i valori dei pixel in un'immagine ed evitare di avere in fase di classificazione pixel classificati in modo erroneo sparsi per l'immagine (errore *salt and pepper*).

**Esempio di funzionamento del metodo average**:

* Valori dei pixel dell'immagine di input:

	1	1	1	1	1

	1	1	1	1	1

	1	1	10	1	1

	1	1	1	1	1

	1	1	1	1	1


* Scegliendo  un neighborhood 3, e una finestra circolare si avrà in output:

	1	1	1	1	1

	1	1	2	1	1

	1	2	2	2	1

	1	1	2	1	1

	1	1	1	1	1

Come si può vedere l'immagine é stata smussata e il valore 10 (molto superiore agli altri valori dell'immagine) é sparito.

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `r.neighbors <http://grass.osgeo.org/grass70/manuals/r.neighbors.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/filtro_riduzione_del_rumore.png

Input
------------

**Dati di input**: selezionare l'immagine raster da utilizzare tra i raster attualmente aperti in QGIS.

**Selezione bande**: selezionare le bande che si vogliono utilizzare; se non si seleziona nulla vengono utilizzate tutte le bande.

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

**Valore del quantile**: valore tra 0 e 1 indicante il quantile da calcolare. Opzione attiva solo se si selezione *quantile* come metodo per il neighbor.

**Dimensione del neighborhood**: valore numerico dispari indicativo della dimensione della finestra mobile del filtro. Il valore deve essere dispari.

**Usa neighborhood circolare**: se selezionato viene usata una finestra mobile circolare anzichè quadrata.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
