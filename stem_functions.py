# -*- coding: utf-8 -*-
"""
Created on Wed Oct  8 11:19:36 2014

@author: lucadelu
"""
from PyQt4.QtCore import QSettings
import os
from grass_stem import stemGRASS


def QGISettingsGRASS(grassdatabase=None, location=None, grassbin=None,
                     epsg=None):
    """Read the QGIS's settings and obtain information for GRASS GIS"""
    s = QSettings()
    # query GRASS 7 itself for its GISBASE
    # we assume that GRASS GIS' start script is available and in the PATH
    if not grassbin:
        grassbin = str(s.value("stem/grasspath", ""))
    if not grassdatabase:
        grassdatabase = str(s.value("stem/grassdata", ""))
    if not location:
        location = str(s.value("stem/grasslocation", ""))
    if not epsg:
        epsg = str(s.value("stem/epsgcode", ""))
    return grassdatabase, location, grassbin, epsg


def temporaryFilesGRASS(name):
    pid = os.getpid()
    tempin = 'stem_{name}_{pid}'.format(name=name, pid=pid)
    tempout = 'stem_output_{pid}'.format(pid=pid)
    grassdatabase, location, grassbin, epsg = QGISettingsGRASS()
    gs = stemGRASS(pid, grassdatabase, location, grassbin, epsg)
    return tempin, tempout, gs
