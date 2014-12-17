# -*- coding: utf-8 -*-

"""
***************************************************************************
    error_reduction.py
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
from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from grass_stem import helpUrl
import traceback


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox()
        self.BaseInput.currentIndexChanged.connect(STEMUtils.addLayersNumber)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

        items = ['vicinanza', 'area']
        label = "Seleziona il metodo da utilizzare"
        self._insertFirstCombobox(items, label, 1)
        self.BaseInputCombo.currentIndexChanged.connect(self.operatorChanged)

        self.ln = "Dimensione del Neighborhood, dev'essere un numero dispari"
        self.lf = "Inserire la dimensione minima da tenere in considerazione"
        self._insertFirstLineEdit(self.ln, 2)

    def operatorChanged(self):
        if self.BaseInputCombo.currentText() == 'vicinanza':
            self.LabelLinedit.setText(self.tr(self.toolName, self.ln))
            self.helpui.fillfromUrl(helpUrl('r.neighbors'))
        else:
            self.LabelLinedit.setText(self.tr(self.toolName, self.lf))
            self.helpui.fillfromUrl(helpUrl('r.reclass.area'))

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
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
            if self.BaseInputCombo.currentText() == 'vicinanza':
                com = ['r.neighbors', 'size={val}'.format(val=self.Linedit.text()),
                       'method=mode']
            else:
                com = ['r.reclass.area', 'mode=lesser', 'method=rmarea',
                       'value={val}'.format(val=self.Linedit.text())]
    
            if len(nlayerchoose) > 1:
                for n in nlayerchoose:
                    out = '{name}_{lay}'.format(name=tempout, lay=n)
                    outnames.append(out)
                    com.extend(['input={name}.{lay}'.format(name=tempin, lay=n),
                                'output={outname}'.format(outname=out)])
                    coms.append(com)
                    self.saveCommand(com)
            else:
                outnames.append(tempout)
                com.extend(['input={name}'.format(name=tempin),
                            'output={outname}'.format(outname=tempout)])
                coms.append(com)
                self.saveCommand(com)
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
