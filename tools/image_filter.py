# -*- coding: utf-8 -*-

"""
***************************************************************************
    image_filter.py
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
from stem_functions import temporaryFilesGRASS
from stem_utils import STEMUtils
from grass_stem import helpUrl


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)
        self._insertLayerChooseCheckBox()

        self.BaseInput.currentIndexChanged.connect(STEMUtils.addLayersNumber)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list2)

        # TODO add filter
        items = ['neighbors']
        label = "Seleziona l'algortimo da utilizzare"
        self._insertFirstCombobox(items, label, 1)
        self.BaseInputCombo.currentIndexChanged.connect(self.operatorChanged)

        methods = ['average', 'median', 'mode', 'minimum', 'maximum', 'range',
                   'stddev', 'sum', 'count', 'variance', 'diversity',
                   'interspersion', 'quart1', 'quart3', 'perc90', 'quantile']

        lm = "Selezionare il metodo per il neighbors"
        self._insertMethod(methods, lm, 3)

        self.ln = "Dimensione del Neighborhood, dev'essere un numero dispari"
        self.lf = "Numero di ripetizioni del filtro"
        self._insertFirstLineEdit(self.ln, 2)

        self.helpui.fillfromUrl(helpUrl('r.neighbors'))
#        self.horizontalLayout_filter = QHBoxLayout()
#        self.horizontalLayout_filter.setObjectName(_fromUtf8("horizontalLayout_filter"))
#        self.labelfilter = QLabel()
#        self.labelfilter.setObjectName(_fromUtf8("labelfilter"))
#        self.horizontalLayout_filter.addWidget(self.labelfilter)
#        self.labelfilter.setEnabled(False)
#        self.TextOutFilter = QLineEdit()
#        self.TextOutFilter.setObjectName(_fromUtf8("TextOutFilter"))
#        self.horizontalLayout_filter.addWidget(self.TextOutFilter)
#        self.TextOutFilter.setEnabled(False)
#        self.BrowseButtonFilter = QPushButton()
#        self.BrowseButtonFilter.setObjectName(_fromUtf8("BrowseButtonFilter"))
#        self.horizontalLayout_filter.addWidget(self.BrowseButtonFilter)
#        self.BrowseButtonFilter.setEnabled(False)
#        self.verticalLayout_options.insertLayout(4, self.horizontalLayout_filter)
#        self.labelfilter.setText(self.tr(name, "Selezionare il file dei filtri"))

    def operatorChanged(self):
        if self.BaseInputCombo.currentText() == 'filter':
            self.LabelLinedit.setText(self.tr(name, self.lf))
            self.labelmethod.setEnabled(False)
            self.MethodInput.setEnabled(False)
#            self.labelfilter.setEnabled(True)
            self.TextOutFilter.setEnabled(True)
            self.BrowseButtonFilter.setEnabled(True)
            self.helpui.fillfromUrl(helpUrl('r.mfilter'))
        else:
            self.LabelLinedit.setText(self.tr(name, self.ln))
            self.labelmethod.setEnabled(True)
            self.MethodInput.setEnabled(True)
#            self.labelfilter.setEnabled(False)
            self.TextOutFilter.setEnabled(False)
            self.BrowseButtonFilter.setEnabled(False)
            self.helpui.fillfromUrl(helpUrl('r.neighbors'))

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onRunLocal(self):
        name = str(self.BaseInput.currentText())
        source = STEMUtils.getLayersSource(name)
        nlayerchoose = STEMUtils.checkLayers(source, self.layer_list2)
        typ = STEMUtils.checkMultiRaster(source, self.layer_list2)
        coms = []
        outnames = []

        cut, cutsource, mask = self.cutInput(name, source, typ)
        if cut:
            name = cut
            source = cutsource
        tempin, tempout, gs = temporaryFilesGRASS(name)
        if len(nlayerchoose) > 0:
            gs.import_grass(source, tempin, typ, nlayerchoose)
        else:
            gs.import_grass(source, tempin, typ)
        if mask:
            gs.check_mask(mask)
        if self.BaseInputCombo.currentText() == 'filter':
            pass
        else:
            for n in nlayerchoose:
                out = '{name}_{lay}'.format(name=tempout, lay=n)
                outnames.append(out)
                com = ['r.neighbors', 'input={name}.{lay}'.format(name=tempin,
                                                                  lay=n),
                       'output={outname}'.format(outname=out),
                       'size={val}'.format(val=self.Linedit.text()),
                       'method={met}'.format(met=self.MethodInput.currentText())]
                coms.append(com)
                self.saveCommand(com)
        gs.run_grass(coms)
        if len(nlayerchoose) > 1:
            gs.create_group(outnames, tempout)
            gs.export_grass(tempout, self.TextOut.text(), typ)
        else:
            gs.export_grass(outnames[0], self.TextOut.text(), typ)
        if self.AddLayerToCanvas.isChecked():
            STEMUtils.addLayerIntoCanvas(self.TextOut.text(), typ)
