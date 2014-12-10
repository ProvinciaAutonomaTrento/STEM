# -*- coding: utf-8 -*-

"""
***************************************************************************
    feat_vege.py
    ---------------------
    Date                 : August 2014
    Copyright            : (C) 2014 Luca Delucchi
    Email                : luca.delucchi@fmach.it
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from stem_base_dialogs import BaseDialog
from base import _translate

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        self._insertLayerChoose()
        self.label_layer.setText(self.tr(name, "Inserire i numeri dei "
                                        "layer da utilizzare, separati da"
                                        " una virgola e partendo da 1."
                                        " Il primo valore dev'essere la "
                                        "banda dell'infrarosso mentre la "
                                        "seconda dev'essere quella del "
                                        "rosso"))

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

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

