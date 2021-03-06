# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 11:50:05 2015

@author: lucadelu
"""

"""
Tool to patch plus LAS file in one

It use the **las_stem** library

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
from gdal_stem import TreesTools
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import traceback
import Pyro4
from pyro_stem import PYROSERVER
from pyro_stem import TREESTOOLSNAME
from pyro_stem import GDAL_PORT

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.shp')
        self.toolName = name
        self.iface = iface

        self._insertSingleInput(label="CHM di input")
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        min_label = "Valore minimo della finestra mobile per trovare gli alberi (pixel)"
        self._insertFirstLineEdit(min_label, 0)

        max_label = "Valore massimo della finestra mobile per trovare gli alberi (pixel)"
        self._insertSecondLineEdit(max_label, 1)

        min_height = "Valore minimo dell'altezza degli alberi (metri)"
        self._insertThirdLineEdit(min_height, 2)
        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            rasttyp = STEMUtils.checkMultiRaster(source)
            cut, cutsource, mask = self.cutInput(name, source, rasttyp, local=self.LocalCheck.isChecked())
            
            if cut:
                name = cut
                source = cutsource
            
            out = str(self.TextOut.text())
            
            if self.LocalCheck.isChecked():
                trees_tools = TreesTools()
                trees_tools.position_alberi(source, out,
                                            float(self.Linedit.text()),
                                            float(self.Linedit2.text()),
                                            float(self.Linedit3.text()),
                                            overwrite=self.overwrite)
            else:
                trees_tools = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                           port=GDAL_PORT,
                                                                           name=TREESTOOLSNAME))
                remote_source = STEMUtils.pathClientWinToServerLinux(source)
                remote_out = STEMUtils.pathClientWinToServerLinux(out)
                trees_tools.position_alberi(remote_source, remote_out,
                                            float(self.Linedit.text()),
                                            float(self.Linedit2.text()),
                                            float(self.Linedit3.text()),
                                            overwrite=self.overwrite)
            
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(out, 'vector')
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
