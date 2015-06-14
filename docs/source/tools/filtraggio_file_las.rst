Filtraggio file LAS
================================

Il modulo esegue il filtraggio dei file .las (o .laz) in modo da selezionare solo i punti LIDAR che rispettano determinate regole.

.. only:: latex

  .. image:: ../_static/tool_images/filtraggio_file_las.png


Input
------------

**File LAS di input**: selezionare il file .las (o .laz) da filtrare.

Parametri
------------

Tutti i parametri sono opzionali. Se non viene impostato nessun parametro il modulo darà in output lo stesso file .las (o .laz) di input.

**Selezionare il ritorno da mantenere**: se non si seleziona nulla vengono matenuti tutti i ritorni.

	* *primo*: primi ritorni;

	* *ultimo*: ultimi ritorni;

	* *altri*: ritorni intermedi;

**Inserire i valori minimo e massimo per le X**: valori minimo e massimo della X da mantenere. I valori vanno seprati da uno spazio.

**Inserire i valori minimo e massimo per le Y**: valori minimo e massimo della Y da mantenere. I valori vanno seprati da uno spazio.

**Inserire i valori minimo e massimo per le Z**: valori minimo e massimo della Z da mantenere. I valori vanno seprati da uno spazio.

**Inserire i valori minimo e massimo per l'intensita'**: valori minimo e massimo dell'intensita' da mantenere. I valori vanno seprati da uno spazio.

**Inserire i valori minimo e massimo per l'angolo di scansione**: valori minimo e massimo per l'angolo di scansione da mantenere. I valori vanno seprati da uno spazio.

**Inserire il valore della classe da tenere**: valore della classe da mantenere.

**Scegliere la libreria da utilizzare**:

	* *liblas*

	* *pdal*

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

**Comprimere il file di output**: se selzionato l'output sara' in formato .laz.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
