# -*- coding: utf-8 -*-

"""
Tool to change attribute of classification map

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
from grass_stem import helpUrl
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
import traceback
from gdal_stem import file_info


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

        items = ['automatico', 'area', 'manuale']
        label = "Seleziona il metodo da utilizzare"
        self._insertFirstCombobox(label, 1, items)
        self.BaseInputCombo.currentIndexChanged.connect(self.operatorChanged)
        label2 = "Inserire la dimensione minima da tenere in considerazione"
        self._insertFirstLineEdit(label2, 2)
        labelText = "Regole per la classificazione manuale"
        self._insertTextArea(labelText, 3)
        tooltip = self.tr(name, "Inserire le regole per la riclassificazione "
                                "secondo lo stile richiesto dal comando di "
                                "GRASS GIS r.reclass. Per maggiori "
                                "informazioni consultare l'help")
        self.TextArea.setToolTip(tooltip)
        self.LabelTextarea.setToolTip(tooltip)
        self.LabelTextarea.setEnabled(False)
        self.TextArea.setEnabled(False)
        self.LabelLinedit.setEnabled(False)
        self.Linedit.setEnabled(False)
        self.helpui.fillfromUrl(helpUrl('r.clump'))

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def operatorChanged(self):
        if self.BaseInputCombo.currentText() == 'automatico':
            self.LabelTextarea.setEnabled(False)
            self.TextArea.setEnabled(False)
            self.LabelLinedit.setEnabled(False)
            self.Linedit.setEnabled(True)
            self.helpui.fillfromUrl(helpUrl('r.clump'))
        elif self.BaseInputCombo.currentText() == 'manuale':
            self.LabelTextarea.setEnabled(True)
            self.TextArea.setEnabled(True)
            self.LabelLinedit.setEnabled(False)
            self.Linedit.setEnabled(False)
            self.helpui.fillfromUrl(helpUrl('r.reclass'))
        else:
            self.LabelTextarea.setEnabled(False)
            self.TextArea.setEnabled(False)
            self.LabelLinedit.setEnabled(True)
            self.Linedit.setEnabled(True)
            self.helpui.fillfromUrl(helpUrl('r.reclass.area'))

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            nlayerchoose = STEMUtils.checkLayers(source, self.layer_list)
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            coms = []
            outnames = []
            cut, cutsource, mask = self.cutInput(name, source, typ)
            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = STEMUtils.temporaryFilesGRASS(name)
            gs.import_grass(source, tempin, typ, nlayerchoose)
            if mask:
                gs.check_mask(mask)
            if self.BaseInputCombo.currentText() == 'automatico':
                startcom = ['r.clump']
            elif self.BaseInputCombo.currentText() == 'manuale':
                fname = STEMUtils.writeFile(str(self.TextArea.toPlainText()))
                startcom = ['r.reclass', 'rules={fn}'.format(fn=fname)]
            else:
                startcom = ['r.reclass.area', 'mode=lesser', 'method=rmarea',
                            'value={val}'.format(val=self.Linedit.text())]

            if len(nlayerchoose) > 1:
                raster = file_info()
                raster.init_from_name(source)
                for n in nlayerchoose:
                    com = startcom[:]
                    layer = raster.getColorInterpretation(n)
                    out = '{name}_{lay}'.format(name=tempout, lay=layer)
                    outnames.append(out)
                    com.extend(['input={name}.{lay}'.format(name=tempin,
                                                            lay=layer),
                                'output={outname}'.format(outname=out)])
                    coms.append(com)
                    self.saveCommand(com)
            else:
                outnames.append(tempout)
                startcom.extend(['input={name}'.format(name=tempin),
                                 'output={outname}'.format(outname=tempout)])
                coms.append(startcom)
                self.saveCommand(startcom)

            gs.run_grass(coms)
            if len(nlayerchoose) > 1:
                gs.create_group(outnames, tempout)

            STEMUtils.exportGRASS(gs, self.overwrite, self.TextOut.text(), tempout, typ)

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
