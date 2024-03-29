# -*- coding: utf-8 -*-

"""
Tool to calculate statistics of raster maps

It use the **grass_stem** library and it run several times *r.univar* GRASS
command.

Date: December 2020

Copyright: (C) 2020 Trilogis

Authors: Trilogis

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import str
__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings, inverse_mask
from grass_stem import temporaryFilesGRASS
import traceback
import sys


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='*.txt')
        self.toolName = name
        self.iface = iface

        self.LocalCheck.hide()
        self.QGISextent.hide()
        self.groupBox.hide()

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
        
        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        self.EPSGlineEdit.hide()
        self.EPSGLabel.hide()

        
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
            gs = None
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            nlayerchoose = [str(STEMUtils.checkLayers(source,
                                                      self.layer_list))]
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            perc = str(self.Linedit.text())
            coms = []
            local = self.LocalCheck.isChecked()
            cut, cutsource, mask = self.cutInput(name, source, typ,
                                                 local=local)
            if cut:
                name = cut
                source = cutsource

            tempin, tempout, gs = temporaryFilesGRASS(name, local)
            output = self.TextOut.text()
            if not local and sys.platform == 'win32':
                source = STEMUtils.pathClientWinToServerLinux(source)
                output = STEMUtils.pathClientWinToServerLinux(output, False)
            gs.import_grass(source, tempin, typ, nlayerchoose)
            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())

            com = ['r.univar', '-e', '-g', 'map={name}'.format(name=tempin),
                   'percentile={p}'.format(p=perc)]
            if output:
                com.append('output={name}'.format(name=output))
            else:
                STEMMessageHandler.error("Si prega di inserire il nome del "
                                         "file di output")
            coms.append(com)
            STEMUtils.saveCommand(com)

            gs.run_grass(coms)
            STEMMessageHandler.success("Il file {name} è stato scritto "
                                       "correttamente".format(name=self.TextOut.text()))

            if not local:
                gs._pyroRelease()
        except:
            if not local and gs is not None:
                gs._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
