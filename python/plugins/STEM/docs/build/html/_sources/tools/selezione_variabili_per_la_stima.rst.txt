Selezione variabili per la stima
=========================================

Il modulo esegue la selezione delle variabili per la stima. La selezione viene effettuata costruendo un modello di regressione da un set di variabili predittori candidati inserendo e rimuovendo i predittori in base al p-value, con approccio stepwise fino a che non ci sono più variabili da inserire o rimuovere. Il valore di p-value per l'inserimento nel modello  di regressione è 0,05. Per altre informazioni vedere in https://www.rdocumentation.org/packages/olsrr/versions/0.5.3/topics/ols_step_both_p

.. warning::

  Questo modulo non prende in considerazione l'estensione di QGIS e/o una maschera

.. only:: latex

  .. image:: ../_static/tool_images/selezione_variabili_per_la_stima.png

Input
------------

**Dati di input vettoriale di training**: selezionare il file di input vettoriale contente le aree di training.

**Seleziona la colonna con l'indicazione del parametro da stimare**: selezionare la colonna con l'indicazione del target.

**Colonna da non considerare nella selezione**: selezionare quale colonna non si vuole considerare nella selezione delle variabili.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output. Il file di output è un file .txt contenete le informazioni statistiche delle variabili selezionate.

**Variabili significative**: inserire il percorso e il nome del file di output. Il file di output è un file .txt contenete i nomi delle variabili significative selezionate. Questo file .txt potrà essere utilizzato nei moduli 'Stimatore lineare' o 'Support Vector Regression'.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
