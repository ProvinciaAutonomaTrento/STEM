# -*- coding: utf-8 -*-

"""
Tool to patch plus LAS file in one

It use the **las_stem** library

Date: December 2020

Copyright: (C) 2020 Trilogis

Authors: Trilogis

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import range
__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from las_stem import stemLAS
from stem_utils import STEMMessageHandler, STEMUtils
from stem_utils_server import STEMSettings
import traceback
import time
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
        self._insertMultipleInput(multi=True)

        label_compr = "Comprimere il file di output"
        self._insertCheckbox(label_compr, 1, output=True)
        self.checkbox.stateChanged.connect(self.compressStateChanged)
        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        
    def compressStateChanged(self):
        checked = self.checkbox.isChecked()
        self.TextOut.setText(STEMUtils.check_las_compress(self.TextOut.text(), checked))

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            items = []
            if len(self.BaseInput.selectedItems()) != 0:
                items = self.BaseInput.selectedItems()
            else:
                for index in range(self.BaseInput.count()):
                    items.append(self.BaseInput.item(index).text())
            out = self.TextOut.text()
            if self.checkbox.isChecked():
                compres = True
            else:
                compres = False
            out = STEMUtils.check_las_compress(out, compres)
            out_locale = out
            if self.LocalCheck.isChecked():
                las = stemLAS()
            else:
                for i in range(len(items)):
                    items[i] = STEMUtils.pathClientWinToServerLinux(items[i])
                out = STEMUtils.pathClientWinToServerLinux(out)

            las.initialize()
            com = las.union(items, out, compres, local=self.LocalCheck.isChecked())
            STEMUtils.saveCommand(com)

            if not self.LocalCheck.isChecked():
                las._pyroRelease()
            
            t = time.time()
            while not os.path.isfile(out_locale):
                if time.time()-t > 5:
                    STEMMessageHandler.error("{ou} LAS file not created".format(ou=out_locale))
                    return
                time.sleep(.1)
            STEMMessageHandler.success("{ou} LAS file created".format(ou=out_locale))
        except:
            if not self.LocalCheck.isChecked():
                las._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
