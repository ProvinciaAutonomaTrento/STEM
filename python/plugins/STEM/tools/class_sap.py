# -*- coding: utf-8 -*-

"""
Tool to classify maps through Spectral Angle Mapper

It use the grass_stem library to run i.spec.sam

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
import traceback
from grass_stem import temporaryFilesGRASS
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

        self.lio = "File di selezione delle matrici"
        self._insertFileInputOption(self.lio, 5, "Text file (*.txt)")
        self.helpui.fillfromUrl(self.SphinxUrl())
        
        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        self.EPSGlineEdit.hide()
        self.EPSGLabel.hide()

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
            matrixfile = self.TextInOpt.text()
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
            gs.import_grass(source, tempin, typ, nlayerchoose)
            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())
            gs.find_program('i.spec.sam', '--help')
            com = ['i.spec.sam', 'group={name}'.format(name=tempin),
                   'matrix={name}'.format(name=matrixfile),
                   'output={outname}'.format(outname=tempout)]

            coms.append(com)
            STEMUtils.saveCommand(com)

            gs.run_grass(coms)

            STEMUtils.exportGRASS(gs, self.overwrite, output, tempout, typ,
                                  False, local = local)
            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
            # TODO test
            if not local:
                gs._pyroRelease()
        except:
            if not local and gs is not None:
                gs._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
