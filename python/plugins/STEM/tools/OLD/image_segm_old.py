# -*- coding: utf-8 -*-

"""
Tool to perform segmentation

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
from functools import partial

import sys


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox()
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        self._insertSecondOutput("Goodness of fit", 1)
        #self.BrowseButton2.clicked.connect(self.browseDir)
        self.BrowseButton2.setText(self.tr(name, "Sfoglia"))
        self.BrowseButton2.clicked.connect(partial(self.browseDir, self.TextOut2))

        self._insertThresholdDouble(0.001, 1.000, 0.001, 1, 3)

        methods = ['euclidean', 'manhattan']
        label = "Seleziona il metodo di calcolo della similarità"
        self._insertMethod(methods, label, 2)

        li = "Numero massimo di iterazioni"
        self._insertThresholdInteger(1, 100000, 1, 3, li)
        self.thresholdi.setValue(20)

        ln = "Selezionare il numero minimo di pixel in un segmento"
        self._insertFirstLineEdit(ln, 3)
        self.Linedit.setText('1')

        lm = "Inserire il valore di memoria da utilizzare in MB"
        self._insertSecondLineEdit(lm, 4)
        self.Linedit2.setText('500')

        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def get_output_path_fields(self):
        """Fornisce al padre una lista di path di output da verificare
        prima di invocare onRunLocal().
        """
        return [self.TextOut2.text()]
    
    def get_input_sources(self):
        """Fornisce al padre una lista di path di input da verificare
        prima di invocare onRunLocal()"""
        return []    

    def onRunLocal(self):
        # Segmentazione
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            gs = None
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            nlayerchoose = STEMUtils.checkLayers(source, self.layer_list)
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            thre = str(self.thresholdd.value())
            itera = str(self.thresholdi.value())
            size = str(self.Linedit.text())
            memory = str(self.Linedit2.text())
            coms = []
            local = self.LocalCheck.isChecked()
            cut, cutsource, mask = self.cutInput(name, source, typ,
                                                 local=local)

            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = temporaryFilesGRASS(name, local)
            output = self.TextOut.text()
            output2 = self.TextOut2.text()
            if not local and sys.platform == 'win32':
                source = STEMUtils.pathClientWinToServerLinux(source)
                output = STEMUtils.pathClientWinToServerLinux(output)
                output2 = STEMUtils.pathClientWinToServerLinux(output2)

            gs.import_grass(source, tempin, typ, nlayerchoose)
            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())

            com = ['i.segment', 'group={name}'.format(name=tempin),
                   'output={outname}'.format(outname=tempout),
                   'thres={val}'.format(val=thre),
                   'similarity={met}'.format(met=self.MethodInput.currentText()),
                   'minsize={val}'.format(val=size),
                   'memory={val}'.format(val=memory),
                   'iter={val}'.format(val=itera)]
            if self.TextOut2.text():
                good = 'goodness_{name}'.format(name=tempout)
                com.append('goodness={val}'.format(val=good))
            coms.append(com)
            STEMUtils.saveCommand(com)

            gs.run_grass(coms)

            STEMUtils.exportGRASS(gs, self.overwrite, output,
                                  tempout, typ, False, local = local)

            if self.TextOut2.text():
                STEMUtils.exportGRASS(gs, self.overwrite, output2,
                                      'goodness_{name}'.format(name=tempout),
                                      typ, local = local)
            else:
                gs.removeMapset()
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
                if self.TextOut2.text():
                    STEMUtils.addLayerIntoCanvas(self.TextOut2.text(), typ)
                
            if not local:
                gs._pyroRelease()
        except:
            if not local and gs is not None:
                gs._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
