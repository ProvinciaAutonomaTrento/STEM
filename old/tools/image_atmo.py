# -*- coding: utf-8 -*-

"""
Tool to performs atmospheric correction using the 6S algorithm

It use the **grass_stem** library and it run *i.atcorr* GRASS command.

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
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertFileInput(pos=1, filterr="Text file (*.txt)")
        self.lf = "Selezionare file con i parametri 6s"
        self.labelF.setText(self.tr("", self.lf))

        self._insertLayerChoose()
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list, is_checkable=False)

        items = ['6s']
        label = "Seleziona l'algortimo da utilizzare"
        self._insertFirstCombobox(label, 2, items)
        self.BaseInputCombo.currentIndexChanged.connect(self.operatorChanged)

        self._insertCheckbox('Convertire la mappa di input in riflettanza '
                             '(default è radianza)', 3)
        self._insertSecondCheckbox('ETM+ precedente al 1 Luglio 2000', 4)
        self._insertThirdCheckbox('ETM+ successivo al 1 Luglio 2000', 4)

        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def operatorChanged(self):
        if self.BaseInputCombo.currentText() == '6s':
            self.LabelLinedit.setText(self.tr(self.toolName, self.lf))
            self.BrowseButtonIn.setEnabled(True)

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onRunLocal(self):
        # Correzione atmosferica
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            gs = None
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            nlayerchoose = STEMUtils.checkLayers(source, self.layer_list)
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            coms = []
            outnames = []
            output = self.TextOut.text()
            local = self.LocalCheck.isChecked()
            cut, cutsource, mask = self.cutInput(name, source, typ,
                                                 local=local)
            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = temporaryFilesGRASS(name, local)
            if not local and sys.platform == 'win32':
                source = STEMUtils.pathClientWinToServerLinux(source)
                output = STEMUtils.pathClientWinToServerLinux(output)
            gs.import_grass(source, tempin, typ, [nlayerchoose])
            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())

            outnames.append(tempout)
            para = self.TextIn.text().strip()
            
            if not local and sys.platform == 'win32':
                para = STEMUtils.pathClientWinToServerLinux(para)
            
            if not para:
                STEMMessageHandler.error("Selezionare il file con i parametri s6")
                return
            com = ['i.atcorr', 'input={name}'.format(name=tempin),
                   'output={outname}'.format(outname=tempout),
                   'parameters={para}'.format(para=para)]
            if self.checkbox.isChecked():
                com.append('-r')
            if self.checkbox2.isChecked():
                com.append('-b')
            if self.checkbox3.isChecked():
                com.append('-a')
            coms.append(com)
            STEMUtils.saveCommand(com)
            gs.run_grass(coms)

            STEMUtils.exportGRASS(gs, self.overwrite, output, tempout, typ, local = local)

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
