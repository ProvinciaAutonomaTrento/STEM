# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 10:04:54 2014

@author: lucadelu
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import pdb
from stem_base_dialogs import BaseDialog
import os


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.iface = iface
        self.name = "Mosaico Immagini"
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)

        BaseDialog.__init__(self, self.iface.mainWindow(), self.iface,
                            self.name)
        self._insertMultipleInput()
        self.addLayerToComboBox(self.BaseInput, 1)
        self._insertLayerChoose()

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onClosing(self):
        BaseDialog.onClosing(self)

    def onRunLocal(self):
        pid = os.getpid()
        innames = self.BaseInput.selectedItems()
        out = self.TextOut.text()
        nlayers = self.checkLayers()
        pyqtRemoveInputHook()
        pdb.set_trace()