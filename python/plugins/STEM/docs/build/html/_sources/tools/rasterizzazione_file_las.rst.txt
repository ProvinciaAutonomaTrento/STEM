Rasterizzazione file LAS
================================

Il modulo serve per creare immagini raster partendo da file in formato .las (o .laz). Una volta scelto il file da elaborare, cliccando sul tasto 'Cariche Statistiche' viene lanciata una preelaborazione per determinare i ritorni e le classi presenti nel dataset i quali verranno usati per valorizzare i parametri del modulo. I principali passaggi effettuati dall'algoritmo sono: 1) creazione di una griglia uniforme di risoluzione spaziale pari alla risoluzione scelta dall'utente; 2) per ogni cella vengono estratte le altezze (Z) dei punti LIDAR contenuti in essa; 3) ai valori di altezza (Z) estratti precedentemente viene applicato il metodo statistico scelto dall'utente (es. media); 4) partendo dai valori ottenuti al punto 3 viene creata un'immagine raster.
L'utente può scegliere tra una varietà di metodi statistici nella creazione dell'immagine raster. L'output sarà un'immagine raster.

Per maggiori informazioni si veda la documentazione della funzione grid_terrain del pacchetto lidR di R https://www.rdocumentation.org/packages/lidR/versions/3.0.3/topics/grid_terrain 

.. only:: latex

  .. image:: ../_static/tool_images/rasterizzazione_file_las.png

Input
------------

**File LAS di input**: selezionare il file .las (o .laz) da rasterizzare.

Parametri
------------

**Selezionare il ritorno da mantenere**: valore del ritorno da mantenere. Se non si seleziona nulla vengono matenuti tutti i ritorni.
	
**Selezionare il valore della classe da mantenere**: valore della classe da mantenere. Se non si seleziona nulla vengono matenute tutte le classi.

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
	* *trimmean*: media dei punti nel pixel al di sopra (del valore minimo) e al di sotto (del valore massimo) rispetto al valore di trim definita come soglia (percentuale).

**Percentile valori supportati 1 100** (opzionale): valore del percentile (attivo solo se si estrae il percentile).

**Soglia trim**: valore della soglia da usare in trimmean (attivo solo se si estrae il trimmean).

**Risoluzione finale del raster**: risoluzione geometrica del file di output in metri.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
