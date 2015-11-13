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
from gdal_stem import position_alberi
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import traceback


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.shp')
        self.toolName = name
        self.iface = iface

        self._insertSingleInput(label="CHM di input")
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        min_label = "Valore minimo della finestra mobile per trovare gli alberi"
        self._insertFirstLineEdit(min_label, 0)

        max_label = "Valore massimo della finestra mobile per trovare gli alberi"
        self._insertSecondLineEdit(max_label, 1)

        min_height = "Valore minimo dell'altezza degli alberi"
        self._insertThirdLineEdit(min_height, 2)
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            position_alberi(source, self.TextOut.text(),
                            float(self.Linedit.text()),
                            float(self.Linedit2.text()),
                            float(self.Linedit3.text()),
                            overwrite=self.overwrite)
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), 'vector')
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
