# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 13:33:49 2014

@author: lucadelu
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from stem_functions import temporaryFilesGRASS
from stem_base_dialogs import BaseDialog


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.iface = iface
        self.name = "Feature di tessitura"
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)

        BaseDialog.__init__(self, self.iface.mainWindow(), self.iface,
                            self.name)
        self._insertSingleInput()
        methods = ['asm', 'contrast', 'corr', 'var', 'idm', 'sa', 'se', 'sv',
                   'entr', 'dv', 'de', 'moc1', 'moc2']
        label = "Metodo per calcolare la tessitura"
        self._insertMethod(methods, label, 0)
        label = "Dimensione della finestra mobile"
        self._insertFirstLineEdit(label, 1)

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
        if self.BaseInputCombo.currentText() == 'filter':
            pass
        else:
            com = ['r.texture', 'input={name}'.format(name=tempin),
                   'output={name}'.format(name=tempout),
                   'size={val}'.format(val=self.Linedit.text()),
                   'method={met}'.format(met=self.MethodInput.currentText())]
        self.saveCommand(com)
        gs.run_grass(com, source, tempin, tempout, self.TextOut.text(), typ)
        if self.AddLayerToCanvas.isChecked():
            self.addLayerIntoCanvas(self.TextOut.text(), 'raster')
