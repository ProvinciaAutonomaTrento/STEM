Come installare il plugin
==============================

Il plugin richiede `GRASS GIS 7`_, `GDAL`_ e le librerie di Python
`numpy`_, `scikit-learn`_ (versione maggiore o uguale alla 0.15.2) e
`psutil`_ (versione maggiore alla 2.1.1)

Installazione su Linux
------------------------------

In base alla distribuzione installare i pacchetti sopra indicati
con il software manager preferito.

Se le librerie Python non sono disponibili per la distribuzione in uso
si possono installare tramite `pip`_

Installazione su Windows
----------------------------------------

Installare tramite `OSGeo4W`_ i pacchetti di `GRASS GIS 7`_, `GDAL`_,
`numpy`_, `scikit-learn`_, `pip`_.

Tramite `pip`_ installare `psutil`_ e aggiornare `scikit-learn`_.

Risoluzione dei problemi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Potrebbe mancare Visual Studio 2010 c++: in mancanza di questo non
possibile installare il pacchetto di `numpy`_ corretto. Tipico errore:
"Unable to find vcvarsall.bat".

 * soluzione: installare Visual Studio 2010 c++ 2010 Express dal sito
   https://www.visualstudio.com/downloads/download-visual-studio-vs#DownloadFamilies_4;

 * installare "Microsoft Visual C++ Compiler for Python 2.7" tramite il sito
   http://www.microsoft.com/en-us/download/details.aspx?id=44266.

Errata versione `numpy`_: versioni precedenti alla 1.9.2 di `numpy`_ non sono
compatibili con `scikit-learn`_ versione maggiore della 0.15.0.

 * soluzione: aggiornare `numpy`_ tramite il comando
   `easy_install.exe --upgrade numpy`
   oppure disinstallarlo con `pip uninstall numpy` e poi reinstallarlo
   con `pip install numpy` per evitare residui di versioni.

Errore "ImportError: cannot import name inplace_column_scale": possibili
residui di precedenti installazioni di `scikit-learn`_.

 * Soluzione: cancellare il file
   $Home_OSGeo4W\python27\Lib\site-packages\sklearn\utils\sparsefuncs.py.

.. _`GRASS GIS 7`: http://grass.osgeo.org
.. _`GDAL`: http://gdal.osgeo.org
.. _`numpy`: http://www.numpy.org/
.. _`scikit-learn`: http://scikit-learn.org/
.. _`pip`: http://www.pip-installer.org/
.. _`OSGeo4W`: http://trac.osgeo.ogr/osgeo4w
.. _`psutil`: https://github.com/giampaolo/psutil
