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
            else:
                import Pyro4
                las = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                                   port=LAS_PORT,
                                                                   name=LASPYROOBJNAME))
            las.initialize()
            if self.checkbox.isChecked():
                compres = True
            else:
                compres = False
            com = las.chm(source, out, dtm_source, compressed=compres)
            STEMUtils.saveCommand(com)
            if os.path.exists(out):
                STEMMessageHandler.success("{ou} LAS file created".format(ou=out))
            else:
                STEMMessageHandler.error("{ou} LAS file not created".format(ou=out))
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
