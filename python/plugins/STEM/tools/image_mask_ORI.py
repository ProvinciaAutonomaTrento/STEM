# -*- coding: utf-8 -*-

"""
Tool to set up a mask. It save a variable with the name source of the
choosen vector map.

Date: December 2020

Copyright: (C) 2020 Trilogis

Authors: Trilogis

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import str
__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from libs.stem_utils_server import STEMSettings


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface
        
        self.LocalCheck.hide()
        
        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)

        self.LabelOut.setText(self.tr(name, "Impostando la maschera "
                                            "tutte le successive operazioni "
                                            "verranno effettuate all'interno "
                                            "della mappa selezionata"))
        self.TextOut.hide()
        self.BrowseButton.hide()
        self.AddLayerToCanvas.setText(self.tr(name, "Rimuovi la maschera"))
        self.AddLayerToCanvas.setChecked(False)
        self.LocalCheck.setText(self.tr(name, "Maschera inversa"))
        self.LocalCheck.setChecked(False)
        self.QGISextent.hide()

        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        if self.AddLayerToCanvas.isChecked():
            STEMSettings.setValue("mask", "")
            STEMSettings.setValue("mask_inverse", "")
            STEMMessageHandler.success("Maschera rimossa correttamente")
        else:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            STEMSettings.setValue("mask", source)
            if self.LocalCheck.isChecked():
                STEMSettings.setValue("mask_inverse", "true")
            else:
                STEMSettings.setValue("mask_inverse", "false")
            STEMMessageHandler.success("Maschera impostata correttamente")
