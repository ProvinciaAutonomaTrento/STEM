Pansharpening
================================

Il modulo utilizza la banda pancromatica di un'immagine multispettrale per incrementare la risoluzione di altre tre bande a più bassa risoluzione geometrica. Le tre bande possono poi essere combinate in un'immagine RGB a più alta risoluzione geometrica. Per esempio, un'immagine Landsat ETM ha alcune bande a 30 m di risoluzione spaziale [banda 1 (blu), 2 (verde), 3 (rosso), 4 (NIR), 5 (mid-IR), and 7 (mid-IR)], e una banda pancromatica a più alta risoluzione(banda 8 a 15m di risoluzione geometrica). Il modulo pansharpening permette alle bande 3-2-1 (o ad altre combinazioni di bande a 30 m di risoluzione, come ad esempio 4-3-2 or 5-4-2) di essere combinate in un'immagine a 15 metri di risoluzione.

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `i.pansharpen <http://grass.osgeo.org/grass70/manuals/i.pansharpen.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/pansharpening.png

Input
------------

**Dati di input**: selezionare il raster a risoluzione più bassa contenente le tre bande per cui la risoluzione va incrementata. Il raster deve essere precedentemente aperto in QGIS.

  * *Selezionare la banda per il canale rosso*: selezionare tra le bande dell'immagine caricata sopra la banda corrispondente al canale del rosso;
  * *Selezionare la banda per il canale verde*: selezionare tra le bande dell'immagine caricata sopra la banda corrispondente al canale del verde;
  * *Selezionare la banda per il canale blu*: selezionare tra le bande dell'immagine caricata sopra la banda corrispondente al canale del blu;

**Dati di input**: selezionare il raster contente la banda a risoluzione migliore da utilizzare per il pansharpening. Il raster deve essere precedentemente aperto in QGIS.

  * *Selezionare la banda a risoluzione migliore*: selezionare tra le bande dell'immagine caricata sopra la banda a maggiore risoluzione.


**Selezione bande**: selezionare le bande che si vogliono utilizzare; se non si seleziona nulla vengono utilizzate tutte le bande.

Parametri
------------

**Seleziona il tipo di Pansharpening**: si possono scegliere diversi metodi per effettuare la riduzione del rumore

  * *brovey*: nel pansharpening Brovey, ognuna delle 3 bande a bassa risoluzione e la banda pancromatica sono combinati utilizzando il seguente algoritmo per calcolare 3 nuove band alla risoluzione più elevata (ad esempio, per la banda 1):
	nuova_banda1 = [banda1/(banda1+banda2+banda3)]*pancromatica
  * *ihs*: nel pansharpening IHS le 3 bande a bassa risoluzione originali, selezionate come canali rosso, verde e blu per creare un'immagine composita RGB, vengono trasformate in IHS (intensità, tonalità e saturazione). La banda pancromatica viene quindi sostituita al canale intensità (I), in combinazione con la tonalità (H) e saturazione (S) originali. L'immagine IHS viene poi ritrasformata verso lo spazio colore RGB alla risoluzione spaziale della banda pancromatica. L'algoritmo può essere rappresentato come: RGB - > IHS - > [pan]HS - > RGB.
  * *pca*: nel pansharpening PCA un'analisi delle componenti principali viene eseguita sulle 3 bande a bassa risoluzione originali per creare 3 immagini delle componenti principali (PC1, PC2 e PC3) e i  loro autovettori associati (EV), in modo tale che:
	+-------+----------+-----------+-----------+
	|       | banda1   | banda2    | banda3    |
	+-------+----------+-----------+-----------+
	| PC1   | EV1-1    | EV1-2     | EV1-3     |
	+-------+----------+-----------+-----------+
	| PC2   | EV2-1    | EV2-2     | EV2-3     |
	+-------+----------+-----------+-----------+
	| PC3   | EV3-1    | EV3-2     | EV3-3     |
	+-------+----------+-----------+-----------+
	e
	PC1 = EV1-1 * banda1 + EV1-2 * banda2 + EV1-3 * banda3 - media(bande 1,2,3)


Output
------------

**Prefisso del risultato**: inserire il percorso e il prefisso dei nomi dei file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
