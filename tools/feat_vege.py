# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 13:51:58 2014

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
        self.iface = iface
        self.name = "Indici di vegetazione"
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)

        BaseDialog.__init__(self, self.iface.mainWindow(), self.iface,
                            self.name)
        self._insertSingleInput()
        self._insertLayerChoose()
        self.label_layer.setText(_translate("Dialog", "Inserire i numeri dei "
                                            "layer da utilizzare, separati da"
                                            " una virgola e partendo da 1.",
                                            " Il primo valore dev'essere la "
                                            "banda dell'infrarosso mentre la "
                                            "seconda dev'essere quella del "
                                            "rosso", None))

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onClosing(self):
        BaseDialog.onClosing(self)

    def onRunLocal(self):
        name = str(self.BaseInput.currentText())
        source = self.getLayersSource(name)
        tempin, tempout, gs = temporaryFilesGRASS(name)
        typ = self.checkMultiRaster()
        cut = self.cutInput(name, source, 'raster')
        if cut:
            name = cut
        if self.BaseInputCombo.currentText() == 'filter':
            pass
        else:
            com = ['i.vi', 'input={name}'.format(name=tempin),
                   'output={name}'.format(name=tempout), 'viname=ndvi',
                   'nir={val}'.format(val=self.Linedit.text())]
        self.saveCommand(com)
        gs.run_grass(com, source, tempin, tempout, self.TextOut.text())
        if self.AddLayerToCanvas.isChecked():
            self.addLayerIntoCanvas(self.TextOut.text(), 'raster')

