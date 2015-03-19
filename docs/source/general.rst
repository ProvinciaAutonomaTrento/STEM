Informazioni di base
========================

Dati di input
------------------

Tutti i moduli, tranne quelli che hanno come input un file
`LAS <http://www.asprs.org/Committee-General/LASer-LAS-File-Format-Exchange-Activities.html>`_,
utilizzano i dati caricati nell'albero dei layer di QGIS.
Per i file LAS è possibile direttamente impostare il percorso al file
direttamente all'interno del modulo selezionato.

.. warning::

  I dati devono avere tutti lo stesso sistema di coordinate, non è possibile
  eseguire alcuna analisi con dati con proiezioni diverse e non viene
  effettuata nessuna riproiezione. Se necessario utilizzare lo strumento
  di riproiezione prima di eseguire le analisi.


Dati di output
--------------------

I dati di output vengono salvati nella directory e con il nome specificato
nel campo apposito.

Opzioni comuni dei moduli
---------------------------

* *Esegui localmente*: selezionare per eseguire in locale.
* *Aggiungi risultato alla mappa*: selezionare se il risultato va aggiunto alla mappa
* *Utilizza estensione QGIS*: taglia i dati sulla estensione attuale della
  finestra di visualizzazione dei dati di QGIS


.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
