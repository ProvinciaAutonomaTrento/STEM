# -*- coding: utf-8 -*-

"""
Tool to calculate kappa parameter for accuracy assessment of classification
result

It use the **grass_stem** library and it run several times *r.kappa* GRASS
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
from stem_utils_server import STEMSettings
from grass_stem import temporaryFilesGRASS
import traceback
import sys


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), '.txt')
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertSecondSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1)
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0, False)

        label = "Seleziona la colonna da considerare per le statistiche"
        self._insertFirstCombobox(label, 0)
        self.BaseInput2.currentIndexChanged.connect(self.indexChanged)
        self.indexChanged()
        self.label2.setText(self.tr(name, "Input mappa training area (sia raster che vettoriale)"))
        self.label.setText(self.tr(name, "Input mappa classificata"))
        self.helpui.fillfromUrl(self.SphinxUrl())
        self.AddLayerToCanvas.hide()
        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        type2 = STEMUtils.getLayersType(self.BaseInput2.currentText())
        if type2 == 0:
            STEMUtils.addColumnsName(self.BaseInput2, self.BaseInputCombo)
        else:
            self.BaseInputCombo.clear()

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
            name2 = str(self.BaseInput2.currentText())
            source2 = STEMUtils.getLayersSource(name2)
            type2 = STEMUtils.getLayersType(name2)
            nlayerchoose = [1]
            if type2 == 1:
                nlayerchoose2 = [1]
                type2 = 'raster'
            else:
                type2 = 'vector'
                nlayerchoose2 = None
            typ = 'raster'
            coms = []
            local = self.LocalCheck.isChecked()
            cut, cutsource, mask = self.cutInput(name, source, typ,
                                                 local=local)
            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = temporaryFilesGRASS(name, local)
            pid = tempin.split('_')[2]
            tempin2 = 'stem_{name}_{pid}'.format(name=name, pid=pid)
            cut2, cutsource2, mask = self.cutInput(name2, source2, type2, local=self.LocalCheck.isChecked())
            if cut2:
                name2 = cut2
                source2 = cutsource2
            output = self.TextOut.text()
            if not local and sys.platform == 'win32':
                source = STEMUtils.pathClientWinToServerLinux(source)
                source2 = STEMUtils.pathClientWinToServerLinux(source2)
                output = STEMUtils.pathClientWinToServerLinux(output, False)
            gs.import_grass(source, tempin, typ, nlayerchoose)
            gs.import_grass(source2, tempin2, type2, nlayerchoose2)

            if type2 == 'vector':
                gs.vtorast(tempin2, self.BaseInputCombo.currentText())

            com = ['r.kappa', '-w',
                   'classification={name}'.format(name=tempin),
                   'reference={name}'.format(name=tempin2),
                   'output={outname}'.format(outname=output)]
            coms.append(com)
            STEMUtils.saveCommand(com)
            gs.run_grass(coms)

            self.finished(self.TextOut.text())

            if not local:
                gs._pyroRelease()
        except:
            if not local and gs is not None:
                gs._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
