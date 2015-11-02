Selezione variabili per la stima
=========================================

Il modulo esegue la selezione delle variabili per la stima. La selezione viene effettuata in base all'*F-test*. Il modulo effettua dei test lineari univariati sul modello di regressione. In particolare vengono fatti vari modelli che vengono testati via via in modo da massimizzare l'*F-score*. Nel dettaglio i passi sono tre: (i) il modello di regressione in esame e i dati sono ortogonalizzati rispetto a regressori costanti; (ii) viene calcolata la cross-correlazione tra i dati e i regressori; e (iii) la cross-correlazione è convertita in un *F-score* e un *p-value*.

.. only:: latex

  .. image:: ../_static/tool_images/selezione_variabili_per_la_stima.png

.. warning::

  Questo modulo non prende in considerazione l'estensione di QGIS e/o una maschera

Input
------------

**Dati di input vettoriale**: selezionare il file di input vettoriale contente le aree di training.

**Seleziona la colonna con l'indicazione del parametro da stimare**: selezionare la colonna con l'indicazione del target.


Parametri
------------

**Numero variabili da selezionare**: numero intero inferiore al numero di varaibili disponibili.


Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
