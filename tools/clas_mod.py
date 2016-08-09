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
from grass_stem import temporaryFilesGRASS
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings, inverse_mask
import traceback
from gdal_stem import file_info
import types
import sys
import os


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


        labelText = "Regole per la classificazione manuale"
        self._insertTextArea(labelText, 3)
        tooltip = self.tr(name, "Inserire le regole per la riclassificazione "
                                "secondo lo stile richiesto dal comando di "
                                "GRASS GIS r.reclass. Per maggiori "
                                "informazioni consultare l'help")
        self.TextArea.setToolTip(tooltip)
        self.LabelTextarea.setToolTip(tooltip)
        self.LabelTextarea.setEnabled(True)
        self.TextArea.setEnabled(True)
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
            out = self.TextOut.text()
            if not local and sys.platform == 'win32':
                old_source = source
                source = STEMUtils.pathClientWinToServerLinux(source)
                out = STEMUtils.pathClientWinToServerLinux(out)
            gs.import_grass(source, tempin, typ, nlayerchoose)
            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())

            if local:
                fname = STEMUtils.writeFile(str(self.TextArea.toPlainText()))
            else:
                import uuid
                unique_id = str(uuid.uuid4()).replace('-', '_')
                fname = STEMUtils.writeFile(str(self.TextArea.toPlainText()),
                                            name = str(os.path.join(STEMUtils.get_temp_dir(), unique_id)))
                fname = STEMUtils.pathClientWinToServerLinux(fname)
                
            startcom = ['r.reclass', 'rules={fn}'.format(fn=fname)]

            if len(nlayerchoose) > 1:
                raster = file_info()
                raster.init_from_name(old_source)
                for n in nlayerchoose:
                    com = startcom[:]
                    layer = raster.getColorInterpretation(n)
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

            STEMUtils.exportGRASS(gs, self.overwrite, out, tempout, typ)

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
