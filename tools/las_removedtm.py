# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 10:04:54 2014

@author: lucadelu
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from stem_base_dialogs import BaseDialog
from base import _fromUtf8, _translate


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.iface = iface
        self.name = "Estrazione CHM"
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)

        BaseDialog.__init__(self, self.iface.mainWindow(), self.iface,
                            self.name)
        self._insertSingleInput()
        self._insertSecondSingleInput()
        self.label2.setText(_translate("Dialog", "Input DTM", None))
        self.label.setText(_translate("Dialog", "Input LAS file", None))

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onClosing(self):
        BaseDialog.onClosing(self)
