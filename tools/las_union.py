# -*- coding: utf-8 -*-

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
from las_stem import stemLAS
from stem_utils import STEMMessageHandler, STEMUtils
from stem_utils_server import STEMSettings
import traceback


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.las')
        self.toolName = name
        self.iface = iface

        self.QGISextent.hide()
        self.AddLayerToCanvas.hide()
        self._insertMultipleInput(multi=True)

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
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            items = []
            if len(self.BaseInput.selectedItems()) != 0:
                items = self.BaseInput.selectedItems()
            else:
                for index in xrange(self.BaseInput.count()):
                    items.append(self.BaseInput.item(index))
            out = self.TextOut.text()
            if self.LocalCheck.isChecked():
                las = stemLAS()
            else:
                import Pyro4
                las = Pyro4.Proxy("PYRONAME:stem.las")
            las.initialize()
            if self.checkbox.isChecked():
                compres = True
            else:
                compres = False
            com = las.union(items, out, compres)
            STEMUtils.saveCommand(com)
            STEMMessageHandler.success("{ou} LAS file created".format(ou=out))
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
