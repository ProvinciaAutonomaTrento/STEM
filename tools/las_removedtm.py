# -*- coding: utf-8 -*-

"""
Tool to perform CHM from LAS file

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
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import traceback
from las_stem import stemLAS
import os
from pyro_stem import PYROSERVER
from pyro_stem import LASPYROOBJNAME
from pyro_stem import LAS_PORT


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.las')
        self.toolName = name
        self.iface = iface

        self.QGISextent.hide()
        self.AddLayerToCanvas.hide()
        self._insertFileInput()
        self._insertSecondSingleInput(label="Input DTM")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1)
        label = "Comprimere il file di output"
        self._insertCheckbox(label, 1, output=True)
        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)
        
    def get_output_path_fields(self):
        """Fornisce al padre una lista di path di output da verificare
        prima di invocare onRunLocal().
        """
        return []
    
    def get_input_sources(self):
        """Fornisce al padre una lista di path di input da verificare
        prima di invocare onRunLocal()"""
        return []
    
    def check_form_fields(self):
        """Fornisce al padre una lista di errori che riguardano i campi della form.
        Non include gli errori che possono esser verificati con le funzioni precedenti"""
        
        dtm_name = str(self.BaseInput2.currentText())
        dtm_source = STEMUtils.getLayersSource(dtm_name)
        
        if not dtm_source:
            return [u'Input DTM non è un layer di QGIS valido']
        
        return []
    
    def onRunLocal(self):
        # Estrazione CHM
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source = str(self.TextIn.text())
            dtm_name = str(self.BaseInput2.currentText())
            dtm_source = STEMUtils.getLayersSource(dtm_name)
            out = str(self.TextOut.text())
            if self.LocalCheck.isChecked():
                las = stemLAS()
                source_task = source
                out_task = out
                dtm_source_task = dtm_source
            else:
                import Pyro4
                las = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                   port=LAS_PORT,
                                                                   name=LASPYROOBJNAME))
                source_task = STEMUtils.pathClientWinToServerLinux(source)
                out_task = STEMUtils.pathClientWinToServerLinux(out)
                dtm_source_task = STEMUtils.pathClientWinToServerLinux(dtm_source)
            las.initialize()
            if self.checkbox.isChecked():
                compres = True
            else:
                compres = False
            com = las.chm(source_task, out_task, dtm_source_task, compressed=compres)
            STEMUtils.saveCommand(com)
            STEMMessageHandler.success("{ou} LAS file created".format(ou=out))
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
