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
from stem_utils import STEMUtils, STEMSettings, STEMMessageHandler
from stem_base_dialogs import BaseDialog
import traceback
import numpy


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

        self._insertThresholdDouble(0.1, 1.00, 0.1, 1, 1,
                                    "Selezionare il threshold minimo")
        self._insertSecondThresholdDouble(0.1, 1.00, 0.1, 2, 1,
                                          "Selezionare il threshold massimo")

        self.thresholdd2.setValue(0.7)

        ln = "Selezionare il valore incrementale del threshold"
        self._insertFirstLineEdit(ln, 3)
        self.Linedit.setText('0.1')

        lm = "Inserire il valore di memoria da utilizzare in MB"
        self._insertSecondLineEdit(lm, 4)
        self.Linedit2.setText('500')

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
            coms = []

            cut, cutsource, mask = self.cutInput(name, source, typ)

            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = STEMUtils.temporaryFilesGRASS(name)

            gs.import_grass(source, tempin, typ, nlayers)

            if mask:
                gs.check_mask(mask)

            minthre = self.thresholdd.value()
            step = float(self.Linedit.text())
            maxthre = self.thresholdd.value() + step
            memory = str(self.Linedit2.text())

            outputs = []
            for i in numpy.arange(minthre, maxthre, step):
                output = '{outname}_{thre}'.format(outname=tempout, thre=i)
                outputs.append(output)
                com = ['i.segment', '-d', 'group={name}'.format(name=tempin),
                       'output={out}'.format(out=output),
                       'thres={val}'.format(val=i),
                       'similarity=euclidean', 'minsize=1', 'iter=20',
                       'memory={val}'.format(val=memory)]
                coms.append(com)
                self.saveCommand(com)

            gs.run_grass(coms)

            gs.create_group(outputs, tempout)
            STEMUtils.exportGRASS(gs, self.overwrite, self.TextOut.text(),
                                  tempout, typ)
            gs.removeMapset()
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)

        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
