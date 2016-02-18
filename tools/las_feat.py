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


STATS = {'max': "Valore massimo altezza punti", 'mean': "Altezza media punti",
         'hcv': "Coefficiente di variazione altezza punti",
         'p10': "10mo percentile altezze punti",
         'p20': "20mo percentile altezze punti",
         'p30': "30mo percentile altezze punti",
         'p40': "40mo percentile altezze punti",
         'p50': "50mo percentile altezze punti",
         'p60': "60mo percentile altezze punti",
         'p70': "70mo percentile altezze punti",
         'p80': "80mo percentile altezze punti",
         'p90': "90mo percentile altezze punti",
         'c2m': "Numero ritorni sopra 2 metri diviso il totale dei ritorni",
         'cmean': "Numero ritorni sopra l'altezza media diviso il totale dei ritorni"}


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.shp')
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self._insertFileInput(pos=1)

        self._insertFirstCombobox(label="Seleziona le statistiche da calcolare",
                                  posnum=0, combo=True)
        self.BaseInputCombo.addItems(STATS.values())

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
        return itemlist

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source = str(self.TextIn.text())
            #name = os.path.basename(source).replace('.las', '')
            local = self.LocalCheck.isChecked()
            invect = str(self.BaseInput.currentText())
            invectsource = STEMUtils.getLayersSource(invect)
            out = str(self.TextOut.text())
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
            las.zonal_statistics(source, invectsource, out, stats, self.overwrite)
            if os.path.exists(self.TextOut.text()):
                STEMMessageHandler.success("{ou} file created".format(ou=self.TextOut.text()))
                if self.AddLayerToCanvas.isChecked():
                    STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'vector')
            else:
                STEMMessageHandler.error("{ou} file not created".format(ou=self.TextOut.text()))
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
