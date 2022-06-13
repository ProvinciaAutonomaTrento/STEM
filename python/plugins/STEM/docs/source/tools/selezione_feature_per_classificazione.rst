Selezione feature per classificazione
=========================================

Il modulo esegue la selezione delle feature (bande di un raster) con un maggior contributo informativo ai fini della successiva classificazione. La ricerca viene effettuata sulla base di una serie di aree di training (input vettoriale) con l'indicazione, per ciascun'area, della classe di appartenenza. La selezione viene effettuata utilizzando l'algoritmo Sequential Forward Floating Selection (SFFS) e la distanza di Jeffries-Matusita. In output vengono generati 2 file di testo: il primo con un riassunto generale della selezione, il secondo con l'indicazione delle feature da selezionare (per i moduli di classificazione supervisionata).
La distanza di Jeffries-Matusita satura ad un valore pari a radice di 2, quindi, il numero ottimale di feature si avrà quando la distanza è uguale a radice di 2. La selezione si ferma automaticamente quando questo accade. Per maggiori informazioni vedi la funzione 'varSelSFFS' in https://cran.r-project.org/web/packages/varSel/varSel.pdf


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

**Dati di input vettoriale**: selezionare il file di input vettoriale contente le aree di training con un campo numerico della classe di appartenenza.

**Seleziona la colonna con l'indicazione della classe**: selezionare la colonna con l'indicazione dei codici delle classi. 

**Dati di input raster**: selezionare il file raster da cui estrarre i valori dei pixel.

Parametri
------------

**Selezionare la strategia da utilizzare**:

	* *minimum*: distanza di Jeffries-Matusita minima tra le classi;
	* *mean*: distanza di Jeffries-Matusita media tra le classi;

**Selezionare numero variabili**: numero di features da selezionare (deve essere maggiore di 2). 

Output
------------

**Report Selezione**: inserire il percorso e il nome del file di output. Il file di output è un file .txt contenete una lista con le distanze JM delle singole bande, una matrice con set delle features selezionate e un vettore contenente le distanze delle feature.

**Lista feature selezionate**: inserire il percorso e il nome del file di output. Il file di output è un file .txt contenete la lista delle features selezionate (utilizzabile per i moduli di classificazione) 

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
