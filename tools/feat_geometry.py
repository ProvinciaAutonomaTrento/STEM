# -*- coding: utf-8 -*-

"""
***************************************************************************
    feat_geometry.py
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


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox(label="Selezionare la banda per il canale rosso",
                                        combo=False)
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        self._insertLayerChooseCheckBox2(label="Selezionare la banda per il canale verde",
                                         combo=False)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list2)

        self._insertLayerChooseCheckBox3(label="Selezionare la banda per il canale blu",
                                         combo=False)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list3)

        self._insertLayerChooseCheckBox4(label="Selezionare la banda per il canale infrarosso",
                                         combo=False)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list4)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list2)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list3)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list4)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        if not self.overwrite:
            self.overwrite = STEMUtils.fileExists(self.TextOut.text())
        try:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)

            red = str(self.layer_list.currentIndex() + 1)
            green = str(self.layer_list2.currentIndex() + 1)
            blu = str(self.layer_list3.currentIndex() + 1)
            pan = str(self.layer_list4.currentIndex() + 1)
            nlayers = [red, green, blu, pan]

            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            method = str(self.MethodInput.currentText())
            coms = []

            cut, cutsource, mask = self.cutInput(name, source, typ)

            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = STEMUtils.temporaryFilesGRASS(name)

            gs.import_grass(source, tempin, typ, nlayers)

            if mask:
                gs.check_mask(mask)
