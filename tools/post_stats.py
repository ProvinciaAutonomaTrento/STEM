# -*- coding: utf-8 -*-

"""
Tool to calculate statistics of raster maps

It use the **grass_stem** library and it run several times *r.univar* GRASS
command.

Date: August 2014

Copyright: (C) 2014 Luca Delucchi

Authors: Luca Delucchi

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
from grass_stem import temporaryFilesGRASS
import traceback


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox(label="Selezionare la banda su cui "
                                        "calcolare le statistice", combo=False)
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)
        self.AddLayerToCanvas.hide()

#        self._insertLayerChooseCheckBox()
#        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
#        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        label = "Percentile da calcolare"
        self._insertFirstLineEdit(label, 0)
        self.Linedit.setText('90')

        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            nlayerchoose = [str(STEMUtils.checkLayers(source, self.layer_list))]
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            perc = str(self.Linedit.text())
            coms = []
            cut, cutsource, mask = self.cutInput(name, source, typ)
            if cut:
                name = cut
                source = cutsource

            tempin, tempout, gs = temporaryFilesGRASS(name, self.LocalCheck.isChecked())
            gs.import_grass(source, tempin, typ, nlayerchoose)
            if mask:
                gs.check_mask(mask)

            com = ['r.univar', '-e', '-g', 'map={name}'.format(name=tempin),
                   'percentile={p}'.format(p=perc)]
            out = self.TextOut.text()
            if out:
                com.append('output={name}'.format(name=out))
            else:
                STEMMessageHandler.error("Si prega di inserire il nome del "
                                         "file di output")
            coms.append(com)
            self.saveCommand(com)

            gs.run_grass(coms)
            STEMMessageHandler.success("Il file {name} è stato scritto "
                                       "correttamente".format(name=out))

        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
