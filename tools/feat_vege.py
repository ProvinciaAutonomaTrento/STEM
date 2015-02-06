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
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
from grass_stem import helpUrl
from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox(label="Selezionare la banda per il canale rosso",
                                        combo=False)
        self.BaseInput.currentIndexChanged.connect(STEMUtils.addLayersNumber)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        self._insertLayerChooseCheckBox2(label="Selezionare la banda per il canale infrarosso",
                                         combo=False)
        self.BaseInput.currentIndexChanged.connect(STEMUtils.addLayersNumber)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list2)

        self.helpui.fillfromUrl(helpUrl('i.vi'))

        STEMSettings.restoreWidgetsValue(self, self.toolName)

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
            nir = str(self.layer_list2.currentIndex() + 1)
            nlayers = [red, nir]

            typ = STEMUtils.checkMultiRaster(source, self.layer_list)

            cut, cutsource, mask = self.cutInput(name, source, typ)

            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = STEMUtils.temporaryFilesGRASS(name)
            if mask:
                gs.check_mask(mask)
            gs.import_grass(source, tempin, typ, nlayers)
            com = ['i.vi', 'red={name}.{l}'.format(name=tempin, l=red),
                   'nir={name}.{l}'.format(name=tempin, l=nir),
                   'output={name}'.format(name=tempout), 'viname=ndvi']
            self.saveCommand(com)
            gs.run_grass([com])

            gs.export_grass(tempout, self.TextOut.text(), typ, False)
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
