Minima distanza
================================

Il modulo effettua la classificazione di immagini o vettori usando l'algoritmo di classificazione supervisionata non-parametrico Minima Distanza. L'algoritmo partendo dai dati di training definisce il centroide delle classi nello spazio delle feature ed assegna ad ogni pixel dell'immagine la classe corrispondente al centroide più vicino nello spazio delle feature.
Gli input al classificatore sono un file vettoriale contente una colonna con l'indicazione della classe in formato numerico (1,2,...,N), e (opzionale) l'indicazione delle feature (attributi del vettoriale) da usare nella classificazione. Se le feature non sono già contenute nel file vettoriale dovrà essere data in input un'immagine raster da cui estrarle.
L'utente potrà anche inserire un vettoraile da usare nella fase di validazione.

.. only:: latex

  .. image:: ../_static/tool_images/minima_distanza.png


Input
------------

**Dati di input vettoriale**: file vettoriale contente le aree di training e l'indicazione delle classi.

**Seleziona la colonna con indicazione della classe**: selezionare tra le colonne del file vettoriale quella che indica le classi.

**Dati di input raster** (opzionale): immagine da cui estrarre le feature e da classificare (opzionale).

**Seleziona le bande da utilizzare cliccandoci sopra** (opzionale): selezionare le bande da utilizzare. Se non si seleziona nulla vengono usate tutte le bande.

Parametri
------------

**Selezione feature**:

	* *no*: nessuna selezione delle feature.
	* *manuale*: le feature vengono selezionate manualemnte.
	* *file*: le feature sono scelte in base al file di output del modulo "Selezione feature per la classificazione".

**File di selezione** (opzionale): inserire il file ottenuto in output dal modulo "Selezione feature per la classificazione". Attivato solo se l'opzione "file" viene scelta nel menu "selezione feature".

**Vettoriale di validazione** (opzionale): file vettoriale contenente le aree di validazione e l'indicazione delle classi.

**Seleziona la colonna per la validazione** (opzionale): selezionare tra le colonne del file vettoriale quella che indica le classi.

Output
------------

**Risultato**: inserire il percorso e il nome del file di output.

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
