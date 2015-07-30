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
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
import traceback
from las_stem import stemLAS


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

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source = str(self.TextIn.text())
            dtm_name = str(self.BaseInput2.text())
            dtm_source = STEMUtils.getLayersSource(dtm_name)
            out = str(self.TextOut.text())
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
            las.chm(source, out, dtm_source, compressed=compres)
            STEMMessageHandler.success("{ou} LAS file created".format(ou=out))
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
