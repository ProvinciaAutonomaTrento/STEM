Avvio applicativi lato server
===============================

Per la comunicazione client-server viene utilizzato Pyro4,

Dopo aver installato Pyro4 sul server, bisogna scaricare il
codice sorgente di STEM sul server (basta anche solo la cartella `libs`).

A questo punto ci si sposta dentro la cartella `libs` e si modifica il file
`pyro_stem.py` settando i parametri corretti alle variabili presenti.

Pyro4 sarà raggiungibile dai client all'IP e alle porte che sono state
impostate.

Salvare il file e avviare il server di Pyro4 con ::

    python -m Pyro4.naming -h IP

.. warning::

    Se non viene utilizzata l'opzione `-h` il server viene avviato
    localmente e non sarà visibile ai client

A questo punto bisognerà lanciare gli script delle librerie (`grass_stem.py`,
`gdal_stem.py`, `machine_learning.py`, `las_stem.py`).

Per lanciare tutti i vari processi in contemporanea si può utilizzare
l'utility `screen` oppure `python grass_stem.py &`.

.. warning::

    Se il client non comunica con il vostro server controllate che
    i client possano raggiungere l'IP alle porte impostate. Se questo
    è stato appurato controllate che le versioni di Pyro4 siano
    compatibili.