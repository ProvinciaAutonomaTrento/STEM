# -*- coding: utf-8 -*-

"""
Tool to calculate statistics of raster maps with a zonal map

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
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings, inverse_mask
from grass_stem import temporaryFilesGRASS
import traceback
import sys


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.txt')
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox(label="Selezionare la banda su cui "
                                        "calcolare le statistice", combo=False)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)

        self._insertSecondSingleInput(pos=2, label="Raster delle aree su cui "
                                                   "calcolare le statistiche")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1)
        self._insertLayerChooseCheckBox2(label="Selezionare la banda delle "
                                               "aree da utilizzare",
                                         combo=False)
        self.BaseInput2.currentIndexChanged.connect(self.indexChanged2)
        STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list2)
        self.AddLayerToCanvas.hide()

#        self._insertLayerChooseCheckBox()
#        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
#        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        label = "Percentile da calcolare"
        self._insertFirstLineEdit(label, 0)
        self.Linedit.setText('90')
#        self.connect(self.BrowseButton, SIGNAL("clicked()"),
#                     partial(self.browseDir, self.TextOut, None))
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def indexChanged2(self):
        STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list2)

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

            zonename = name = str(self.BaseInput2.currentText())
            zonesource = STEMUtils.getLayersSource(zonename)
            zonenlayerchoose = [str(STEMUtils.checkLayers(zonesource,
                                                          self.layer_list2))]
            zonetyp = STEMUtils.checkMultiRaster(zonesource, self.layer_list2)
            zonecut, zonecutsource, zonemask = self.cutInput(zonename,
                                                             zonesource,
                                                             zonetyp, local=self.LocalCheck.isChecked())
            if cut:
                zonename = zonecut
                zonesource = zonecutsource

            pid = tempin.split('_')[2]
            zonetempin = 'stem_{name}_{pid}'.format(name=zonename, pid=pid)
            gs.import_grass(zonesource, zonetempin, typ, zonenlayerchoose)

            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())

            com = ['r.univar', '-e', '-g', 'map={name}'.format(name=tempin),
                   'percentile={p}'.format(p=perc),
                   'zones={zon}'.format(zon=zonetempin)]
            if output:
                com.append('output={name}'.format(name=self.TextOut.text()))
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
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
