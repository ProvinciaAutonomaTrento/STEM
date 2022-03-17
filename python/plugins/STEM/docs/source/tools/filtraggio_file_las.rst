Filtraggio file LAS
================================

Il modulo esegue il filtraggio dei file .las (o .laz) in modo da selezionare solo i punti LIDAR che rispettano determinate regole. Una volta scelto il file da elaborare, cliccando sul tasto 'Cariche Statistiche' viene lanciata una preelaborazione per determinare i ritorni e le classi presenti nel dataset i quali verranno usati per valorizzare i parametri del modulo.  

Per maggiori informazioni si veda la documentazione R del metodo  `filter_poi <https://www.rdocumentation.org/packages/lidR/versions/4.0.0/topics/filters>`_.

.. only:: latex

  .. image:: ../_static/tool_images/filtraggio_file_las.png


Input
------------

**File LAS di input**: selezionare il file .las (o .laz) da filtrare.

Parametri
------------

Tutti i parametri sono opzionali. Se non viene impostato nessun parametro il modulo darà in output lo stesso file .las (o .laz) di input.

**Selezionare il ritorno da mantenere**: valore del ritorno da mantenere. Se non si seleziona nulla vengono matenuti tutti i ritorni.
	
**Selezionare il valore della classe da mantenere**: valore della classe da mantenere. Se non si seleziona nulla vengono matenute tutte le classi.

**Inserire il valore minimo per la X**: valore minimo della X da mantenere. Se non si inserisce non ci sarà una soglia minima per la X.

**Inserire il valore massimo per la X**: valore massimo della X da mantenere. Se non si inserisce non ci sarà una soglia massima per la X.

**Inserire il valore minimo per la Y**: valore minimo della Y da mantenere. Se non si inserisce non ci sarà una soglia minima per la Y.

**Inserire il valore massimo per la Y**: valore massimo della Y da mantenere. Se non si inserisce non ci sarà una soglia massima per la Y.

**Inserire il valore minimo per la Z**: valore minimo della Z da mantenere. Se non si inserisce non ci sarà una soglia minima per la Z.

**Inserire il valore massimo per la Z**: valore massimo della Z da mantenere. Se non si inserisce non ci sarà una soglia massima per la Z.

**Inserire il valore minimo per l'intensita'**: valore minimo dell'intensita' da mantenere. Se non si inserisce non ci sarà una soglia minima per l'intensita'.

**Inserire il valore massimo per l'intensita'**: valore massimo dell'intensita' da mantenere. Se non si inserisce non ci sarà una soglia massima per l'intensita'.

**Inserire il valore minimo per l'angolo di scansione**: valore minimo dell'angolo di scansione da mantenere. Se non si inserisce non ci sarà una soglia minima per l'angolo di scansione.

**Inserire il valore massimo per l'angolo di scansione**: valore massimo dell'angolo di scansione da mantenere. Se non si inserisce non ci sarà una soglia massima per l'angolo di scansione.

**Inserire i valori minimo e massimo per l'angolo di scansione**: valori minimo e massimo per l'angolo di scansione da mantenere. I valori vanno seprati da uno spazio.



Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

**Comprimere il file di output**: se selzionato l'output sara' in formato .laz.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
