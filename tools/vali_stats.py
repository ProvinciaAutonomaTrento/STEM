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


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.name = "Statistiche"
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)

        BaseDialog.__init__(self, self.iface.mainWindow(), self.iface,
                            self.name)
        self._insertSingleInput()

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onClosing(self):
        BaseDialog.onClosing(self)
