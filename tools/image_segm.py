# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 12:14:33 2014

@author: lucadelu
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from base import _translate
from stem_base_dialogs import BaseDialog
from stem_functions import temporaryFilesGRASS


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.iface = iface
        self.name = "Segmentazione"
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)

        BaseDialog.__init__(self, self.iface.mainWindow(), self.iface,
                            self.name)
        self._insertSingleInput()
        self.addLayerToComboBox(self.BaseInput, 1)
        self._insertSecondOutput("Goodness of fit", 1)
        self.connect(self.BrowseButton2, SIGNAL("clicked()"), self.BrowseDir)
        self.BrowseButton2.setText(_translate("Dialog", "Sfoglia", None))
        self._insertThresholdDouble(0.000, 1.000, 0.001, 1, 3)

        methods = ['euclidean', 'manhattan']
        label = "Seleziona il metodo di calcolo della similarità"
        self._insertMethod(methods, label, 2)
        self._insertThresholdInteger(1, 100000, 1, 3)

        ln = "Selezionare il numero minimo di celle in un segmento"
        self._insertFirstLineEdit(ln, 3)

        lm = "Inserire il valore di memoria da utilizzare in MB"
        self._insertSecondLineEdit(lm, 4)
        #self.BaseInputPan.currentIndexChanged.connect(self.operatorChanged)

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onClosing(self):
        BaseDialog.onClosing(self)

    def onRunLocal(self):
        name = str(self.BaseInput.currentText())
        tempin, tempout, gs = temporaryFilesGRASS(name)
        layer = self.inlayers[name]
        typ = self.checkMultiRaster()