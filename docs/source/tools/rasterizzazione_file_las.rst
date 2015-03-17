Rasterizzazione file LAS
================================

Il modulo converte una nuvola di punti in formato LAS in una nuova immagine raster. L'utente può scegliere tra una varietà di metodi statistici nella creazione del nuova raster. L'output sarà un'mmagine raster.

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `r.in.lidar <http://grass.osgeo.org/grass70/manuals/r.in.lidar.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/rasterizzazione_file_las.png

Input
------------

**File LAS di input**: selezionare il file LAS da rasterizzare.

Parametri
------------

**Selezionare il ritorno desiderato**:

	* *all*: tutti i ritorni;
	* *first*: solo il primo ritorno;
	* *last*: solo l'ultimo ritorno;
	* *mid*: solo i ritorni intermedi.

**Selezionare il metodo statistico da utilizzare**:

	* *n*: numero di punti nel pixel;
	* *min*: valore minimo dei punti nel pixel;
	* *max*: valore massimo dei punti nel pixel;
	* *range*: intervallo dei valori dei punti nel pixel;
	* *sum*: somma dei valori dei punti nel pixel;
	* *mean*: media dei punti nel pixel;
	* *stddev*:	deviazione standard dei punti nel pixel;
	* *variance*: varianza dei punti nel pixel
	* *coeff_var*: coefficiente di variazione dei punti nel pixel in percentuale [(deviazione_standard/media)*100];
	* *median*: mediana dei punti nel pixel
	* *percentile*: n-esimo percentile dei punti nel pixel
	* *skewness*: skewness dei punti nel pixel
	* *trimmean*: media dei punti nel pixel al di sopra e al di sotto di una soglia.

**Percentile**: valore del percentile (attivo solo se si estrae il percentile).

**Trim**: valore della soglia da usare in trimmean (attivo solo se si estrae il trimmean).

**Risoluzione finale del raster**: risoluzione geometrica del file di output in metri.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
