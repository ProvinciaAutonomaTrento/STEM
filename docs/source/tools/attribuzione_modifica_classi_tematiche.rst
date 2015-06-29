Attribuzione/modifica classi tematiche
=========================================

Il modulo permette di modificare un mappa di classificazione aggregando le classi per area o modificandole manualmente.
Questo modulo va usato nella fase di post-classificazione, per esempio per passare da una mappa di dettaglio delle specie forestali ad una meno dettagliata contenente solo le classi "conifere" e "latifoglie". Può essere inoltre usato per aggregare mappe di classificazione a pixel in aree di interesse.


.. only:: latex

  .. image:: ../_static/tool_images/attribuzione_modifica_classi_tematiche.png


Input
------------

**Dati di input**: selezionare la mappa classificata da modificare.

Parametri
------------

**Selezionare il metodo da utilizzare**:

 * *Automatico*: utilizzando questa modalità ad ogni gruppo di pixels aventi la stessa etichetta viene assegnata una nuova classe. Questo fa aumentare il numeri di classi che diventa pari al numero di cluster di pixels aventi la stessa etichetta nella mappa iniziale. Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `r.clump <http://grass.osgeo.org/grass70/manuals/r.clump.html>`_

 * *Area*:  Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `r.reclass.area <http://grass.osgeo.org/grass70/manuals/r.reclass.area.html>`_

 * *Manuale*: nella finestra vanno inserite le regole da utilizzare per la riclassificazione dell'immagine. Ogni riga deve essere strutturata in questo modo:

     *input_categories=output_category [label]*

     *input_categories* é una lista numerica di una o più classi;  *output_category* deve essere una classe; *[label]* é la nuova etichetta della nuova classe.

     Esempio:

        .. image:: ../_static/tool_images/attribuzione_modifica_classi_tematiche_esempio_input_1.png

        In questo caso le classi 1, 2 e 3 sono trasformate nella classe 1 che viene rinominata "conifere", le classi 4 e 5 sono trasformate
        nella classe 2 rinominata "latifoglie", e tutte le altre classi vengono lasciate inalterate " * = * ".

   Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `r.reclass <http://grass.osgeo.org/grass70/manuals/r.reclass.html>`_

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
