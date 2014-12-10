# -*- coding: utf-8 -*-

"""
***************************************************************************
    feat_texture.py
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
from stem_functions import temporaryFilesGRASS
from stem_base_dialogs import BaseDialog


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        methods = ['asm', 'contrast', 'corr', 'var', 'idm', 'sa', 'se', 'sv',
                   'entr', 'dv', 'de', 'moc1', 'moc2']
        label = "Metodo per calcolare la tessitura"
        self._insertMethod(methods, label, 0)
        label = "Dimensione della finestra mobile"
        self._insertFirstLineEdit(label, 1)

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
