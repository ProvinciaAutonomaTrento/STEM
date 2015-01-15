# -*- coding: utf-8 -*-

"""
***************************************************************************
    post_aggraree.py
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
import traceback
from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput("Dati di input (vettoriale di punti)")
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)

        self._insertSecondSingleInput(label="Dati di input (vettoriale di aree)")
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0)

        label = "Seleziona la colonna da considerare per le statistiche"
        self._insertFirstCombobox(label, 0)
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addColumnsName(self.BaseInput, self.BaseInputCombo)

        methods = ['sum', 'average', 'median', 'mode', 'minimum', 'min_cat',
                   'maximum', 'max_cat', 'range', 'stddev', 'variance',
                   'diversity']
        lmet = "Method for aggregate statistics"
        self._insertMethod(methods, lmet, 1)

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addColumnsName(self.BaseInput, self.BaseInputCombo)

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
            typ = 'vector'
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            name2 = str(self.BaseInput.currentText())
            source2 = STEMUtils.getLayersSource(name2)
            cut, cutsource, mask = self.cutInput(name, source, typ)
            cut2, cutsource2, mask = self.cutInput(name2, source2, typ)
            if cut:
                name = cut
                source = cutsource
            if cut2:
                name2 = cut2
                source2 = cutsource2

            tempin, tempout, gs = STEMUtils.temporaryFilesGRASS(name)
            pid = tempin.split('_')[2]
            gs.import_grass(source, tempin, typ)
            tempin2 = 'stem_{name}_{pid}'.format(name=name, pid=pid)
            gs.import_grass(source2, tempin2, typ)
            if mask:
                gs.check_mask(mask)
            com = ['v.vect.stats', 'points={m}'.format(m=tempin),
                   'areas={n}'.format(n=tempin2),
                   'count_column=count_{p}'.format(p=pid),
                   'stats_column=stats_{p}'.format(p=pid),
                   'points_column={pc}'.format(pc=self.BaseInputCombo.currentText())]
            self.saveCommand(com)
            gs.run_grass([com])
            STEMUtils.exportGRASS(gs, self.overwrite, self.TextOut.text(),
                                  tempout, typ)

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
