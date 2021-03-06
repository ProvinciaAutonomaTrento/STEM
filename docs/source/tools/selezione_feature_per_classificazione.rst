Selezione feature per classificazione
=========================================

Il modulo esegue la selezione delle feature per la classificazione. La selezione verrà effettuata utilizzando l'algoritmo Sequential Forward Floating Selection (SFFS) e la distanza di Jeffries-Matusita. In output vi sarà un file di testo con l'indicazione delle feature da utilizzare.
La distanza di Jeffries-Matusita satura ad un valore pari a radice di 2, quindi il numero ottimale di feature si avrà quando la distanza è uguale a radice di 2. La selezione si ferma automaticamente quando questo accade.

.. warning::

  Ogni classe deve avere un numero di pixel superiore al numero totale di bande. Se questo vincolo non è soddisfatto la selezione si blocca in anticipo rispetto al valore ottimale a causa della non invertibilità della matrice di covarianza della classe il cui numero di campioni è limitato. Il modulo da comunque in output la selezione con un numero di bande non ottimale.


.. warning::

  Se una banda del file di input contiene valori dei pixel tutti uguali è probabile che la selezione si blocchi alla prima iterazione. Si consiglia di verificare quindi i valori delle bande, e semmai rimuovere le bande corrotte, per evitare questo problema.

.. warning::

  Questo modulo non prende in considerazione l'estensione di QGIS e/o una maschera

.. only:: latex

  .. image:: ../_static/tool_images/selezione_feature_per_classificazione.png


Input
------------

**Dati di input vettoriale**: selezionare il file di input vettoriale contente le aree di training.

**Seleziona la colonna con l'indicazione della classe**: selezionare la colonna con l'indicazione delle classi.

**Dati di input raster**: selezionare il file raster da cui estrarre i valori dei pixel.

Parametri
------------

**Selezionare la strategia da utilizzare**:

	* *min*: distanza di Jeffries-Matusita minima tra le classi;
	* *mean*: distanza di Jeffries-Matusita media tra le classi;
	* *median*: distanza di Jeffries-Matusita mediana tra le classi.

**Numero massimo di feature da selezionare**: numero massimo di feature da selezionare. Se il campo rimane vuoto viene usato il numero totale di bande meno 1.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output. Il file di output è un file .txt contenete l'indicazione della selezione (1) o non selezione (0) delle feature del file di input.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
