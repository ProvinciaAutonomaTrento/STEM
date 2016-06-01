# -*- coding: utf-8 -*-

"""
Tool to reduce errors after classification

It use the **grass_stem** library and it run *r.neighbors* or *r.reclass.area*
GRASS command depending on the options choosen.

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
from gdal_stem import file_info
from grass_stem import temporaryFilesGRASS
import traceback
import types
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

        items = ['vicinanza', 'area']
        label = "Seleziona il metodo da utilizzare"
        self._insertFirstCombobox(label, 1, items)
        self.BaseInputCombo.currentIndexChanged.connect(self.operatorChanged)

        self.ln = "Dimensione del Neighborhood, dev'essere un numero dispari"
        self.lf = "Inserire la dimensione minima da tenere in considerazione"
        self._insertFirstLineEdit(self.ln, 2)

        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def operatorChanged(self):
        if self.BaseInputCombo.currentText() == 'vicinanza':
            self.LabelLinedit.setText(self.tr(self.toolName, self.ln))
        else:
            self.LabelLinedit.setText(self.tr(self.toolName, self.lf))

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
            local = self.LocalCheck.isChecked()
            cut, cutsource, mask = self.cutInput(name, source, typ,
                                                 local=local)
            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = temporaryFilesGRASS(name, local)
            output = self.TextOut.text()
            if not local and sys.platform == 'win32':
                old_source = source
                source = STEMUtils.pathClientWinToServerLinux(source)
                output = STEMUtils.pathClientWinToServerLinux(output, False)
            gs.import_grass(source, tempin, typ, nlayerchoose)
            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())
            if self.BaseInputCombo.currentText() == 'vicinanza':
                startcom = ['r.neighbors', 'method=mode',
                            'size={val}'.format(val=self.Linedit.text())]
            else:
                startcom = {'val': float(self.Linedit.text()), 'inps': [],
                            'outs': []}

            if len(nlayerchoose) > 1:
                raster = file_info()
                raster.init_from_name(old_source)
                for n in nlayerchoose:
                    layer = raster.getColorInterpretation(n)
                    com = startcom[:]
                    out = '{name}_{lay}'.format(name=tempout, lay=layer)
                    outnames.append(out)
                    inp = '{name}.{lay}'.format(name=tempin, lay=layer)
                    if isinstance(startcom, types.ListType):
                        com.extend(['input={inpn}'.format(inpn=inp),
                                    'output={outn}'.format(outn=out)])
                        coms.append(com)
                        STEMUtils.saveCommand(com)
                    else:
                        startcom['inps'].append(inp)
                        startcom['outs'].append(out)
            else:
                outnames.append(tempout)
                if isinstance(startcom, types.ListType):
                    startcom.extend(['input={name}'.format(name=tempin),
                                     'output={outn}'.format(outn=tempout)])
                    coms.append(startcom)
                    STEMUtils.saveCommand(startcom)
                else:
                    startcom['inps'].append(tempin)
                    startcom['outs'].append(tempout)

            if isinstance(startcom, types.ListType):
                gs.run_grass(coms)
            else:
                for num in range(len(startcom['inps'])):
                    gs.rmarea(startcom['inps'][num], startcom['outs'][num],
                              startcom['val'])
            if len(nlayerchoose) > 1:
                gs.create_group(outnames, tempout)

            STEMUtils.exportGRASS(gs, self.overwrite, output, tempout, typ)

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
            
            if not local:
                gs._pyroRelease()
        except:
            if not local:
                gs._pyroRelease()
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
