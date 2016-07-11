# -*- coding: utf-8 -*-

"""
Tool to return statistics of classification maps

It use the **grass_stem** library and it run several times *v.vect.stats* GRASS
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
from gdal_stem import infoOGR
from grass_stem import temporaryFilesGRASS
import traceback
import sys


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='.shp')
        self.toolName = name
        self.iface = iface

        self._insertSingleInput("Vettoriale di punti")
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)

        self._insertSecondSingleInput(label="Vettoriale di aree su cui aggregare")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0)

        label = "Seleziona la colonna da considerare per le statistiche"
        self._insertFirstCombobox(label, 0)
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addColumnsName(self.BaseInput, self.BaseInputCombo)

        methods = ['sum', 'average', 'median', 'mode', 'minimum',
                   'maximum', 'range', 'stddev', 'variance']
        lmet = "Metodo statistico di aggregazione"
        self._insertMethod(methods, lmet, 1)
        labelcount = "Nome della nuova colonna con il numero di elementi " \
                     "all'interno di ogni area. Massimo 10 caratteri"
        self._insertFirstLineEdit(label=labelcount, posnum=2)
        self.Linedit.setMaxLength(10)
        labelstats = "Nome della nuova colonna con la statistica sugli " \
                     "elementi all'interno di ogni area. Massimo 10 caratteri"
        self._insertSecondLineEdit(label=labelstats, posnum=3)
        self.Linedit2.setMaxLength(10)
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

    def indexChanged(self):
        STEMUtils.addColumnsName(self.BaseInput, self.BaseInputCombo)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            gs = None
            typ = 'vector'
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            infoname = infoOGR()
            infoname.initialize(source)
            if infoname.getType() in [1, 4, -2147483647, -2147483644]:
                geotype = 'point'
            elif infoname.getType() in [3, 6, -2147483645, -2147483642]:
                self.error = "Geometria non supportata, creare i centroidi con " \
                        "lo strumento dedicato di QGIS"
                STEMMessageHandler.error(self.error)
            else:
                self.error = "Geometria non supportata"
                STEMMessageHandler.error(self.error)
                return
            name2 = str(self.BaseInput2.currentText())
            source2 = STEMUtils.getLayersSource(name2)
            local = self.LocalCheck.isChecked()
            cut, cutsource, mask = self.cutInput(name, source, typ,
                                                 local=local)
            cut2, cutsource2, mask = self.cutInput(name2, source2, typ,
                                                   local=local)
            if cut:
                name = cut
                source = cutsource
            if cut2:
                name2 = cut2
                source2 = cutsource2

            tempin, tempout, gs = temporaryFilesGRASS(name, local)
            pid = tempin.split('_')[2]
            output = self.TextOut.text()
            if not local and sys.platform == 'win32':
                source = STEMUtils.pathClientWinToServerLinux(source)
                source2 = STEMUtils.pathClientWinToServerLinux(source2)
                output = STEMUtils.pathClientWinToServerLinux(output, False)
            gs.import_grass(source, tempin, typ)
            tempin2 = 'stem_{name}_{pid}'.format(name=name2, pid=pid)
            gs.import_grass(source2, tempin2, typ)
            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())
            com = ['v.vect.stats', 'points={m}'.format(m=tempin),
                   'areas={n}'.format(n=tempin2), 'type={t}'.format(t=geotype),
                   'count_column={p}'.format(p=str(self.Linedit.text())),
                   'stats_column={p}'.format(p=str(self.Linedit2.text())),
                   'method={m}'.format(m=self.MethodInput.currentText()),
                   'points_column={pc}'.format(pc=self.BaseInputCombo.currentText())]
            STEMUtils.saveCommand(com)
            gs.run_grass([com])
            STEMUtils.exportGRASS(gs, self.overwrite, output, tempin2, typ)

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
                
            if not local:
                gs._pyroRelease()
        except:
            if not local and gs is not None:
                gs._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
