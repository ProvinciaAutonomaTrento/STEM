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
from stem_utils import STEMUtils, STEMMessageHandler
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

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        try:
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            name2 = str(self.BaseInput2.currentText())
            source2 = STEMUtils.getLayersSource(name2)
            nlayerchoose = STEMUtils.checkLayers(source, self.layer_list)
            nlayerchoose2 = STEMUtils.checkLayers(source2, self.layer_list)
            if len(nlayerchoose) != len(nlayerchoose2) and len(nlayerchoose) != 1:
                print "selezionare lo stesso numero di bande"
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            coms = []
            outnames = []
            cut, cutsource, mask = self.cutInput(name, source, typ)
            if cut:
                name = cut
                source = cutsource
            pid = tempin.split('_')[2]
            gs.import_grass(source, tempin, typ)
            tempin2 = 'stem_{name}_{pid}'.format(name=name, pid=pid)

            gs.import_grass(source, tempin, typ, nlayerchoose)
        except:
            error = traceback.format_exc()
            STEMMessageHandler.error(error)
            return
