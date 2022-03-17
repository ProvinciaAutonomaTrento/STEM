Segmentazione
================================

Il modulo effettua la segmentazione di immagini. La segmentazione di immagini è il processo di raggruppamento dei pixel simili in segmenti distinti. In letteratura esistono molti algoritmi di segmentazione; in questo tool è implementato un algoritmo di region growing: l'algoritmo parte da punti "seme" da cui il segmento si espande ai pixel contigui che soddisfano alcuni criteri definiti dall'utente.
Più nel dettaglio, l'algoritmo di region growing esamina iterativamente tutti i segmenti nella mappa raster, calcolando la somiglianza fra il segmento analizzato (secondo una formula di distanza) e ciascuno dei segmenti ad esso vicini.
Due segmenti saranno uniti se, e solo se, soddisfano una serie di criteri, tra cui:

 * i due segmenti sono reciprocamente simili tra loro (la distanza di somiglianza è inferiore rispetto alla soglia di ingresso), e
 * la somiglianza fra di essi è maggiore rispetto agli altri segmenti adiacenti. Il processo viene ripetuto fino a quando non è possibile eseguire ulteriori fusioni delle regioni.

Ad ogni oggetto trovato durante il processo di segmentazione viene assegnato un ID univoco.
Nota che la segmentazione differesce dalla classificazione dove tutti i pixel simili tra loro sono assegnati alla stessa classe e non devono essere contigui (nella segmentazione devono essere contigui!).
Il risultati di una segmentazione di un'immagine può essere utile per conto proprio o essere utilizzato come un passo di preprocessing per la classificazione delle immagini.
La segmentazione è una fase di pre-elaborazione in grado di ridurre il rumore e velocizzare la classificazione.

Per maggiori informazioni si veda la documentazione del comando di GRASS GIS utilizzato `i.segment <http://grass.osgeo.org/grass70/manuals/i.segment.html>`_

.. only:: latex

  .. image:: ../_static/tool_images/segmentazione.png


Input
------------

**Dati di input**: nella finestra compaiono i raster attualmente aperti in QGIS. Selezionare il raster su cui eseguire la segmentazione.


Parametri
------------

**Seleziona il threshold da utilizzare**: seleziona il threshold di "somiglianza" con il quale suddividere in segmenti l'immagine. La somiglianza tra i segmenti e gli oggetti non uniti è utilizzata per determinare quali pixel possono essere fusi fra loro in unico oggetto. Valori di distanza piccoli indicano una corrispondenza più stretta, con un punteggio di somiglianza pari a zero per i pixel identici. Durante la normale elaborazione, le fusioni sono consentite soltanto quando la somiglianza tra due segmenti è inferiore al valore di soglia. La soglia deve essere maggiore di 0 e minore di 1. Una soglia 0 consentirebbe di unire solo pixels con valori identici, mentre una soglia 1 consentirebbe di unire tutti i pixel in un'unica regione. Test empirici iniziali indicano che valori di soglia nell'intervallo 0.2-0.01 sono valori ragionevoli: ad ogni modo tale valore dipende dalla tipologia di immagine e di oggetti presi in considerazione. Si raccomanda di iniziare con un valore basso, ad esempio 0.01, e quindi eseguire la segmentazione gerarchica utilizzando l'uscita dell'ultima esecuzione come "seme" per la corsa successiva.

**Seleziona il metodo di calcolo della similarità**: seleziona il metodo per calcolare la similarità fra pixel adiacienti.

  * *euclidean*: calcola la distanza euclidea fra i valori dei due pixel adiacenti.
  * *manhattan*: calcola la distanza Manhattan fra i valori dei due pixel adiacenti.

**Numero massimo di iterazioni**: rappresenta il numero massimo di iterazioni eseguite dall'algoritmo durante il processo di aggregazione dei segmenti. Più il numero è elevato, più il processo è completo, richiedendo tuttavia un maggior tempo di elaborazione. Il numero impostato di default rappresenta un valore inferiore al di sotto del quale è consigliabile non andare.

**Selezionare il numero minimo di pixel in un segmento**: rappresenta il numero minimo di pixel di cui deve essere composto ogni singolo segmento. Durante l'iterazione finale del processo, qualora un segmento abbia dimensione minima inferiore, verrà aggregato on il segmento adiacente più simile anche se la somiglianza è superiore alla soglia (vedi spiegazione threshold di similarità).

**Inserire il valore di memoria da utilizzare in MB**: esprime il valore in MB di RAM da utilizzare per il processo in corso.


Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

**Goodness of fit**: La bontà di adattamento per ciascun pixel viene calcolato come 1 - distanza del pixel dal segmento a cui appartiene. La distanza è calcolata con il metodo di somiglianza selezionato. Il valore 1 significa valori identici, mentre il valore 0 significa massima distanza possibile.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
