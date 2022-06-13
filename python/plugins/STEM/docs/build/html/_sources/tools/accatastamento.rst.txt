Accatastamento
================================

Il modulo accatastamento (o layer stacking) crea un nuovo raster multibanda a partire da più file raster mono o multibanda. L'output è un nuovo file multibanda in cui ogni banda (o gruppo di bande) deriva da uno dei file selezionati come input. L'estensione spaziale del nuovo file raster dipendera' dall'utilizzo o meno della funzione 'forza ritaglio su overlap'. Se questa funzione non viene selezionata l'estensione sara' pari alla massima estensione dei raster che si sono selezionati per l'accatastamento. Se invece si utilizza 'forza ritaglio su overlap' l'estensione dell'output sara' pari all'estensione di sovrapposizione dei raster selezionati rispetto al primo raster.

Per maggiori informazioni si veda la documentazione R del metodo  `align_rasters <https://www.rdocumentation.org/packages/gdalUtils/versions/2.0.3.2/topics/align_rasters>`_.


.. only:: latex

  .. image:: ../_static/tool_images/accatastamento.png


Input
------------

**Dati di input**: nella finestra compaiono i raster attualmente aperti in QGIS. Selezionare i raster da accatastare. E' possibile eliminare dalla lista uno o piu' raster selezionarli e premere 'canc' o variare l'ordine trascinando il raster selezionato lungo la lista. Si puo' indicare quali bande accatastare per ciascun raster selezionato inserendo il numero delle bande separate da uno spazio. Per esempio se un raster ha 4 bande e si desidera accatastare solo la prima e la seconda banda si dovra' inserire "1 2". Se non si seleziona nulla verranno utilizzate tutte le bande.  

.. warning:: 

  L'ordine dei raster è importante soprattutto per definire l'estensione
  dell'output. Il primo raster selezionato, dall'alto verso il basso, 
  sarà quello sul quale si effettuera' l'accatastamento e l'eventuale ritaglio se si utilizza la funzione 'forza ritaglio su overlap'. 

Parametri
------------

**Formato di output**: selezionare il formato per l'output del comando

  * *ENVI*: formato ENVI (file binario + header).
  * *GTIFF*: formato GeoTiff.

**Forza ritaglio su overlap**: definisce l'estensione finale del raster

**Metodo di interpolazione**: definisce con che metodo i diversi raster sono allineati tra di loro

**Risoluzione immagine accatastata**: mostra le possibili risoluzioni spaziali che il raster di destinazione può assumere. Tali risoluzioni sono basate sulle risoluzioni dei raster di input

  
Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
