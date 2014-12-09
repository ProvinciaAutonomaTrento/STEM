# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 10:04:54 2014

@author: lucadelu
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from stem_base_dialogs import BaseDialog
from base import _translate
from stem_functions import temporaryFilesGRASS
from grass_stem import helpUrl


class STEMToolsDialog(BaseDialog):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.iface = iface
        self.name = "Filtro riduzione del rumore"
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)

        BaseDialog.__init__(self, self.iface.mainWindow(), self.iface,
                            self.name)
        self._insertSingleInput()
        self.addLayerToComboBox(self.BaseInput, 1)
        self._insertLayerChooseCheckBox()

        self.BaseInput.currentIndexChanged.connect(self.AddLayersNumber)
        self.AddLayersNumber()

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
#        self.labelfilter.setText(_translate("Dialog",
#                                            "Selezionare il file dei filtri",
#                                            None))

    def operatorChanged(self):
        if self.BaseInputCombo.currentText() == 'filter':
            self.LabelLinedit.setText(_translate("Dialog", self.lf, None))
            self.labelmethod.setEnabled(False)
            self.MethodInput.setEnabled(False)
#            self.labelfilter.setEnabled(True)
            self.TextOutFilter.setEnabled(True)
            self.BrowseButtonFilter.setEnabled(True)
            self.helpui.fillfromUrl(helpUrl('r.mfilter'))
        else:
            self.LabelLinedit.setText(_translate("Dialog", self.ln, None))
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
        source = self.getLayersSource(name)
        typ = self.checkMultiRaster(source)
        nlayers = self.checkLayers(source)

        cut, cutsource, mask = self.cutInput(name, source, typ)
        if cut:
            name = cut
            source = cutsource
        print "prima di grass"
        tempin, tempout, gs = temporaryFilesGRASS(name)
        print "dopo di grass"
        if nlayers > 0:
            gs.import_grass(source, tempin, typ, nlayers)
        else:
            gs.import_grass(source, tempin, typ)
        print "dopo import"
        if mask:
            gs.check_mask(mask)
        return
        if self.BaseInputCombo.currentText() == 'filter':
            pass
        else:
            com = ['r.neighbors', 'input={name}'.format(name=tempin),
                   'output={name}'.format(name=tempout),
                   'size={val}'.format(val=self.Linedit.text()),
                   'method={met}'.format(met=self.MethodInput.currentText())]
        self.saveCommand(com)
        gs.run_grass(com, source, tempin, tempout, self.TextOut.text(), typ)
        if self.AddLayerToCanvas.isChecked():
            self.addLayerIntoCanvas(self.TextOut.text(), typ)
