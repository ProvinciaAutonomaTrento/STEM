Filtro maggioranza
================================

Il modulo effettua un filtraggio a maggioranza delle mappe di classificazione. Il modulo va utilizzato per rimuovere i pixel di una classe isolati tra pixel di un'altra classe, o piccole aree classificate in una classe ma circondate da altre classi.

.. only:: latex

  .. image:: ../_static/tool_images/filtro_maggioranza.png

Input
------------

**Dati di input**: selezionare il raster da utilizzare tra quelli attualmente aperti in QGIS.

**Selezione bande**: selezionare le bande che si vogliono utilizzate; se non si seleziona nulla vengono utilizzate tutte le bande.

Parametri
------------

**Selezione il metodo da utilizzare**: si possono scegliere diversi metodi per effettuare il filtro di maggioranza

  * *vicinanza*: il valore del pixel centrale della finestra di dimensioni impostata dall'utente viene sostituito con il valore più frequente dei pixel di quell'intorno;
  * *area*: in questo modo tutti i gruppi di pixel di area inferiore ad una certa soglia impostata dall'utente vengono uniti al gruppo di pixel più vicino di dimensioni superiori alla soglia.

**Dimensione del neighborhood** (opzionale): valore numerico dispari indicativo della dimensione della finestra mobile del filtro. Il valore deve essere dispari. Attivo solo se il metodo selezionato è "vicinanza".

**Inserire la dimensione minima da tenere in considerazione** (opzionale): valore numerico indicativo della dimensione minima da tenere in considerazione nel filtraggio. Attivo solo se il metodo selezionato è "area".

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
