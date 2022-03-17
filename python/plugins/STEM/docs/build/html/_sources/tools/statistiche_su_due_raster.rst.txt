Statistiche su due raster
================================

Il modulo calcola una serie di statistiche sul raster fornito in input dall'utente aggregando i risultati in base ad aree fornite in input con un secondo raster. Fornisce in uscita un file di testo con le statistiche. Per ogni area le statistiche calcolate sono:

	* *n*: numero totale di pixels;
	* *min*: valore minimo dei pixels dell'immagine;
	* *max*: valore massimo dei pixels dell'immagine;
	* *range*: range dei valori dei pixels dell'immagine;
	* *mean*: valore medio dei pixels dell'immagine;
	* *stddev*: deviazione standard dei valori dei pixels dell'immagine;
	* *variance*: varianza dei valori dei pixels dell'immagine;
	* *coeff_var*: coefficiente di variazione dei valori dei pixels dell'immagine;
	* *sum*: somma dei valori dei pixels dell'immagine;
	* *first_quartile*: primo quartile dei valori dei pixels dell'immagine;
	* *median*: mediana dei valori dei pixels dell'immagine;
	* *third_quartile*: terzo quartile dei valori dei pixels dell'immagine;
	* *percentile_n*: n-esimo percentile dei valori dei pixels dell'immagine.

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `r.univar <http://grass.osgeo.org/grass70/manuals/r.univar.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/statistiche_su_due_raster.png


Input
------------

**Dati di input**: selezionare il raster di input.

**Selezionare la banda su cui calcolare le statistiche**: selezionare la banda del raster di input su cui calcolare le statistiche.

**Raster delle aree su cui calcolare le statistiche**: raster delle aree su cui calcolare le statistiche. Deve essere un raster con valori interi (es. mappa di classificazione). Controllare in *Proprietà -> Metadati*.

**Selezionare la banda delle aree da analizzare**: selezionare la banda del raster con le aree su cui calcolare le statistiche.

Parametri
------------

**Percentile da calcolare**: percentile da calcolare (da 1 a 99).

Output
------------

**Risultato**: file di testo in cui salvare il risultato. L'estensione .txt va specificata.


.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
