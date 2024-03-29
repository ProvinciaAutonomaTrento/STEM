Risoluzione dei problemi noti
===================================

Le finestre dei moduli non si aprono
----------------------------------------

Se la finestre del plugin non si aprono e non viene stampato a video
alcun errore, procedere con l’apertura della console Python su QGIS per
indagare più a fondo sul problema.

Percorsi a GRASS GIS non corretti
-------------------------------------

Se ottenete un errore simile a quello che segue molto probabilmente
non avrete settato correttamente i percorsi alle variabili di GRASS GIS
nelle impostazioni, in particolare:

* Percorso all'eseguibile di GRASS GIS 7.8
* Percorso alla GRASSDATA directory
* Nome della LOCATION da utilizzare

::

    Traceback (most recent call last):
        File "/home/lucadelu/.qgis2/python/plugins/STEM/tools/error_reduction.py", line 89, in onRunLocal
        tempin, tempout, gs = STEMUtils.temporaryFilesGRASS(name, self.LocalCheck.isChecked)
        File "/home/lucadelu/.qgis2/python/plugins/STEM/stem_utils.py", line 407, in temporaryFilesGRASS
        gs.initialize(pid, grassdatabase, location, grassbin, epsg)
        File "/home/lucadelu/.qgis2/python/plugins/STEM/libs/grass_stem.py", line 84, in initialize
        stdout=PIPE, stderr=PIPE)
        File "/usr/lib/python2.7/subprocess.py", line 710, in __init__
        errread, errwrite)
        File "/usr/lib/python2.7/subprocess.py", line 1335, in _execute_child
        raise child_exception
    OSError: [Errno 2] No such file or directory

Questo può capitare quando si passa da lanciare i comandi in locale a
lanciarli sul server e viceversa.

Classificazione
---------------------

Se con i moduli di classificazione ottenete degli errori provate a rimuovere
il contenuto della cartella `$HOME/.qgis2/stem/`. Questa contiene i risultati
delle analisi di classificazione precedenti, che servono per velocizzare
analisi identiche, e potrebbero essere la causa di qualche malfunzionamento.

Caricamento output
------------------------

Alcune volte, in modo casuale, succede che i layer di output, anche se creati
correttamente non vengano caricati su QGIS. Questa situazione capita più
frequentemente quando il processo è lanciato su un server. Se non si ottengono
errori controllate la cartella selezionata per l'output e controllare se
il file è presente.