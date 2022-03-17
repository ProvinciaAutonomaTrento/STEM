Rasterizzazione file LAS
================================

Il modulo serve per creare immagini raster partendo da file in formato .las. I principali passaggi effettuati dall'algoritmo sono: 1) creazione di una griglia uniforme di risoluzione spaziale pari alla risoluzione scelta dall'utente; 2) per ogni cella vengono estratte le altezze (Z) dei punti LIDAR contenuti in essa; 3) ai valori di altezza (Z) estratti precedentemente viene applicato il metodo statistico scelto dall'utente (es. media); 4) partendo dai valori ottenuti al punto 3 viene creata un'immagine raster.
L'utente può scegliere tra una varietà di metodi statistici nella creazione dell'immagine raster. L'output sarà un'immagine raster.

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `r.in.lidar <http://grass.osgeo.org/grass70/manuals/r.in.lidar.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/rasterizzazione_file_las.png

Input
------------

**File LAS di input**: selezionare il file .las da rasterizzare.

Parametri
------------

**Selezionare il ritorno desiderato**: con questo parametro si sceglie quali ritorni utilizzare nella fase di rasterizzazione.

	* *all*: tutti i ritorni;
	* *first*: solo il primo ritorno;
	* *last*: solo l'ultimo ritorno;
	* *mid*: solo i ritorni intermedi.

**Selezionare il metodo statistico da utilizzare**: con questo parametro si sceglie il metodo statistico da utilizzare nella fase di rasterizzazione

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
