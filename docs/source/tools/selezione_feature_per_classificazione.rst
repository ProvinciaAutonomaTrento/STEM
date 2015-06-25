Selezione feature per la classificazione
=========================================

Il modulo esegue la selezione delle feature per la classificazione. La selezione verrà effettuata utilizzando l'algoritmo Sequential Forward Floating Selection (SFFS) e la distanza di Jeffries-Matusita. In output vi sarà un file di testo con l'indicazione delle feature da utilizzare.

.. only:: latex

  .. image:: ../_static/tool_images/selezione_feature_per_la_classificazione.png


Input
------------

**Dati di input vettoriale**: selezionare il file di input vettoriale contente le aree di training.

**Seleziona la colonna con l'indicazione della classe**: selezionare la colonna con l'indicazione delle classi.

**Dati di input raster**: selezionare il file raster da cui estrarre i valori dei pixel.

Parametri
------------

**Selezionare la strategia da utilizzare**:

	* *min*: distanza minima;
	* *mean*: distanza media;
	* *median*: distanza mediana.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
