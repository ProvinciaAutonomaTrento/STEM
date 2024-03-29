# -*- coding: utf-8 -*-

"""
Tool to extract geometry feature

It use the **grass_stem** library and it run several times *i.segment* GRASS
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
import numpy
import sys


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface
        
        self.LocalCheck.hide()
        self.QGISextent.hide()
                
        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox()
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

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

        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        self.EPSGlineEdit.hide()
        self.EPSGLabel.hide()

        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

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
            nlayers = STEMUtils.checkLayers(source, self.layer_list)
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
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
            gs.import_grass(source, tempin, typ, nlayers)

            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())

            minthre = self.thresholdd.value()
            step = float(self.Linedit.text())
            maxthre = self.thresholdd2.value()
            memory = str(self.Linedit2.text())

            outputs = []
            for i in numpy.arange(minthre, maxthre + step, step):
                out = '{outname}_{thre}'.format(outname=tempout, thre=i)
                outputs.append(out)
                com = ['i.segment', '-d', 'group={name}'.format(name=tempin),
                       'output={out}'.format(out=out),
                       'thres={val}'.format(val=i),
                       'similarity=euclidean', 'minsize=1', 'iter=20',
                       'memory={val}'.format(val=memory)]
                coms.append(com)
                STEMUtils.saveCommand(com)

            gs.run_grass(coms)

            gs.create_group(outputs, tempout)
            STEMUtils.exportGRASS(gs, self.overwrite, output, tempout, typ,
                                  False, local = local)
            gs.removeMapset()
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
