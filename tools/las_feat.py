# -*- coding: utf-8 -*-

"""
Create a raster map starting from LAS file using univariate statistics

It use the **grass_stem** library and it run several times *r.in.lidar* GRASS
command.

Date: August 2014

Copyright: (C) 2014 Luca Delucchi

Authors: Luca Delucchi

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import os
import traceback
import sys
from las_stem import stemLAS
from pyro_stem import PYROSERVER
from pyro_stem import LASPYROOBJNAME
from pyro_stem import LAS_PORT
from PyQt4.QtCore import Qt


STATS = {'max': "Valore massimo della dimensione selezionata",
         'mean': "Media della dimensione selezionata", 
         'mode': "Moda della dimensione selezionata",
         'hcv': "Coefficiente di variazione della dimensione selezionata",
         'p10': "10mo percentile della dimensione selezionata",
         'p20': "20mo percentile della dimensione selezionata",
         'p30': "30mo percentile della dimensione selezionata",
         'p40': "40mo percentile della dimensione selezionata",
         'p50': "50mo percentile della dimensione selezionata",
         'p60': "60mo percentile della dimensione selezionata",
         'p70': "70mo percentile della dimensione selezionata",
         'p80': "80mo percentile della dimensione selezionata",
         'p90': "90mo percentile della dimensione selezionata",
         'c2m': "Numero ritorni sopra 2 metri diviso il totale dei ritorni",
         'cmean': "Numero ritorni sopra la media della dimensione selezionata diviso il totale dei ritorni"}

DIMENSIONS = ["Z","X","Y","Intensity","ReturnNumber","NumberOfReturns","ScanDirectionFlag","EdgeOfFlightLine","Classification","ScanAngleRank","UserData","PointSourceId","GpsTime","Red","Green","Blue"]

class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.shp')
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self._insertFileInput(pos=1)
        self.QGISextent.hide()
        self._insertFirstCombobox(label="Seleziona le statistiche da calcolare",
                                  posnum=0, combo=True)
        self.BaseInputCombo.addItems(STATS.values())
        self._insertSecondCombobox(label="Seleziona la dimensione",
                                   posnum=1)
        self.BaseInputCombo2.addItems(DIMENSIONS)
        self.helpui.fillfromUrl(self.SphinxUrl())

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def _keysStats(self, val):
        return [key for key, value in STATS.items() if value == val]

    def _selectedStats(self):
        itemlist = []
        for i in range(self.BaseInputCombo.count()):
            item = self.BaseInputCombo.model().item(i)
            if item.checkState() == Qt.Checked:
                val = str(item.text())
                key = self._keysStats(val)
                itemlist.append(key[0])
        if not itemlist:
            for i in range(self.BaseInputCombo.count()):
                item = self.BaseInputCombo.model().item(i)
                val = str(item.text())
                key = self._keysStats(val)
                itemlist.append(key[0])
        return itemlist

    def onRunLocal(self):
        # Estrazione feature LiDAR da poligoni
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source = str(self.TextIn.text())
            #name = os.path.basename(source).replace('.las', '')
            local = self.LocalCheck.isChecked()
            invect = str(self.BaseInput.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            out = str(self.TextOut.text())
            dimension = self.BaseInputCombo2.currentText()
            if local:
                las = stemLAS()
            else:
                if sys.platform == 'win32':
                    source = STEMUtils.pathClientWinToServerLinux(source)
                    invectsource = STEMUtils.pathClientWinToServerLinux(invectsource)
                    out = STEMUtils.pathClientWinToServerLinux(out)
                import Pyro4
                las = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                   port=LAS_PORT,
                                                                   name=LASPYROOBJNAME))
            stats = self._selectedStats()
            las.zonal_statistics(source, invectsource, out, stats, self.overwrite, dimension=dimension)
            STEMMessageHandler.success("{ou} file created".format(ou=self.TextOut.text()))
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'vector')
            
            if not local:
                las._pyroRelease()
        except:
            if not local:
                las._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
