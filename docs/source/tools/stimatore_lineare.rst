Stimatore lineare
=================

Il modulo esegue la stima di parametri utilizzando uno stimatore lineare.
Gli input allo stimatore sono un file vettoriale contente una colonna con l'indicazione del target da stimare in formato numerico, e (opzionale) l'indicazione delle variabili (attributi del vettore) da usare nella stima. Se le variabili non sono già contenute nel file vettoriale dovrà essere data in input un'immagine raster da cui estrarle.
L'utente potrà anche inserire un vettoriale da usare nella fase di validazione.


.. only:: latex

  .. image:: ../_static/tool_images/stimatore_lineare.png


Input
------------

**Dati di input vettoriale**: file vettoriale contente le aree di training e l'indicazione dei target.

**Seleziona la colonna con indicazione del target**: selezionare tra le colonne del file vettoriale quella che indica il target da stimare.

**Dati di input raster** (opzionale): immagine da cui estrarre le variabili e da stimare (opzionale).

**Seleziona le bande da utilizzare cliccandoci sopra** (opzionale): selezionare le bande da utilizzare. Se non si seleziona nulla vengono usate tutte le bande.

Parametri
------------

**Selezione variabili**:

	* *no*: nessuna selezione delle variabili.
	* *manuale*: le variabili vengono selezionate manualmente.
	* *file*: le variabili sono scelte in base al file di output del modulo "Selezione variabili per la stima".

**File di selezione** (opzionale): inserire il file ottenuto in output dal modulo "Selezione variabili per la stima". Attivato solo se l'opzione "file" viene scelta nel menu "selezione variabili".

**Vettoriale di validazione** (opzionale): file vettoriale contenente le aree di validazione e l'indicazione del target.

**Seleziona la colonna per la validazione** (opzionale): selezionare tra le colonne del file vettoriale quella che indica il target.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
