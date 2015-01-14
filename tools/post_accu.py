# -*- coding: utf-8 -*-

"""
***************************************************************************
    post_accu.py
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

from qgis.core import *
from qgis.gui import *
from stem_base_dialogs import BaseDialog
from grass_stem import helpUrl
from stem_utils import STEMUtils, STEMMessageHandler, STEMSettings
import traceback


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        self._insertSecondSingleInput()
        self.label2.setText(self.tr(name, "Input mappa training area"))
        self.label.setText(self.tr(name, "Input mappa classificata"))
        self.helpui.fillfromUrl(helpUrl('r.kappa'))

        STEMSettings.restoreWidgetsValue(self, self.toolName)

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
            name2 = str(self.BaseInput2.currentText())
            source2 = STEMUtils.getLayersSource(name2)
            nlayerchoose = STEMUtils.checkLayers(source, self.layer_list)
            nlayerchoose2 = STEMUtils.checkLayers(source2, self.layer_list)
            if len(nlayerchoose) != len(nlayerchoose2):
                err = "Selezionare lo stesso numero di bande"
                STEMMessageHandler.error(err)
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            coms = []
            outnames = []
            cut, cutsource, mask = self.cutInput(name, source, typ)
            if cut:
                name = cut
                source = cutsource
            tempin, tempout, gs = STEMUtils.temporaryFilesGRASS(name)
            pid = tempin.split('_')[2]
            gs.import_grass(source, tempin, typ)
            tempin2 = 'stem_{name}_{pid}'.format(name=name, pid=pid)

            gs.import_grass(source, tempin, typ, nlayerchoose)
            gs.import_grass(source2, tempin2, typ, nlayerchoose2)

            if len(nlayerchoose) > 1:
                for n in nlayerchoose:
                    out = '{name}_{lay}'.format(name=tempout, lay=n)
                    outnames.append(out)
                    com = ['r.kappa',
                           'classification={name}.{lay}'.format(name=tempin,
                                                                lay=n),
                           'reference={name}.{lay}'.format(name=tempin2,
                                                           lay=n),
                           'output={outname}'.format(outname=out)]
                    coms.append(com)
                    self.saveCommand(com)
            else:
                outnames.append(tempout)
                com = ['r.kappa',
                       'classification={name}'.format(name=tempin),
                       'reference={name}'.format(name=tempin2),
                       'output={outname}'.format(outname=tempout)]
                coms.append(com)
                self.saveCommand(com)
            for n in nlayerchoose:
                out = '{name}_{lay}'.format(name=tempout, lay=n)
                outnames.append(out)

                coms.append(com)
                self.saveCommand(com)
            gs.run_grass(coms)
            if len(nlayerchoose) > 1:
                gs.create_group(outnames, tempout)

            STEMUtils.exportGRASS(gs, self.overwrite, self.TextOut.text(),
                                  tempout, typ)

            if self.AddLayerToCanvas.isChecked():
                STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
