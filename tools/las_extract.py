# -*- coding: utf-8 -*-

"""
***************************************************************************
    las_extract.py
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
from grass_stem import stats

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        methods = ['all', 'first', 'last', 'mid']
        label = "Selezionare il ritorno desiderato"
        self._insertMethod(methods, label, 0)
        label = "Selezionare il metodo statistico da utilizzare"
        self._insertFirstCombobox(stats, label, 1)
        label = "Risoluzione finale del raster"
        self._insertFirstLineEdit(label, 2)
        label = "Percentile"
        self._insertSecondLineEdit(label, 3)
        self.BaseInputCombo.currentIndexChanged.connect(self.checkPercentile)
        self.LabelLinedit2.setEnabled(False)
        self.Linedit2.setEnabled(False)
        self.helpui.fillfromUrl(helpUrl('r.in.lidar'))

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def checkPercentile(self):
        if self.BaseInputCombo.currentText() == 'percentile':
            self.LabelLinedit2.setEnabled(True)
            self.Linedit2.setEnabled(True)
        else:
            self.LabelLinedit2.setEnabled(False)
            self.Linedit2.setEnabled(False)

    def onRunLocal(self):
        name = str(self.BaseInput.currentText())
        tempin, tempout, gs = temporaryFilesGRASS(name)
        method = str(self.methodInput.currentText())
        reso = self.Linedit.currentText()
        perc = self.Linedit2.currentText()
        layer = self.inlayers[name]
        com = ['r.in.lidar', 'flags=eo',
               'input={name}'.format(name=tempin),
               'output={name}'.format(name=tempout),
               'method={met}'.format(met=method)]
        if reso:
            com.append('resolution={res}'.format(res=reso))
        if perc:
            com.append('percentile={per}'.format(per=perc))
        gs.run_grass(layer.source(), tempin, tempout, self.TextOut.text(),
                     'raster', com)