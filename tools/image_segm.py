# -*- coding: utf-8 -*-

"""
***************************************************************************
    image_segm.py
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
from stem_utils import STEMUtils
from stem_functions import temporaryFilesGRASS

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)
        self._insertSecondOutput("Goodness of fit", 0)
        self.connect(self.BrowseButton2, SIGNAL("clicked()"), self.BrowseDir)
        self.BrowseButton2.setText(self.tr(name, "Sfoglia"))
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
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        name = str(self.BaseInput.currentText())
        tempin, tempout, gs = temporaryFilesGRASS(name)
        layer = self.inlayers[name]
        typ = self.checkMultiRaster()