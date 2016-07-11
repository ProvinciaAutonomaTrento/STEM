# -*- coding: utf-8 -*-

"""
Tool to filtering images using neighbors pixel

It use the **grass_stem** library and it run *r.neighbors* GRASS command.

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

        # TODO add filter
        items = ['neighbors']
        label = "Seleziona l'algortimo da utilizzare"
        self._insertFirstCombobox(label, 1, items)
        self.BaseInputCombo.currentIndexChanged.connect(self.operatorChanged)

        methods = ['average', 'median', 'mode', 'minimum', 'maximum', 'range',
                   'stddev', 'sum', 'count', 'variance', 'diversity',
                   'interspersion', 'quart1', 'quart3', 'perc90', 'quantile']

        lm = "Selezionare il metodo per il neighbors"
        self._insertMethod(methods, lm, 2)

        self.ln = "Dimensione del Neighborhood, dev'essere un numero dispari"
        self.lf = "Numero di ripetizioni del filtro"
        self._insertFirstLineEdit(self.ln, 3)

        self.lq = "Valore del quantile (compreso tra 0.0 e 1.0)"
        self._insertSecondLineEdit(self.lq, 4)
        self.LabelLinedit2.setEnabled(False)
        self.Linedit2.setEnabled(False)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)

        self._insertCheckbox('Usa Neighborhood circolare', 4)

        self.helpui.fillfromUrl(self.SphinxUrl())
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

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list)

    def operatorChanged(self):
        if self.BaseInputCombo.curremarkerntText() == 'filter':
            self.LabelLinedit.setText(self.tr(self.toolName, self.lf))
            self.labelmethod.setEnabled(False)
            self.MethodInput.setEnabled(False)
#            self.labelfilter.setEnabled(True)
            self.TextOutFilter.setEnabled(True)
            self.BrowseButtonFilter.setEnabled(True)
        else:
            self.LabelLinedit.setText(self.tr(self.toolName, self.ln))
            self.labelmethod.setEnabled(True)
            self.MethodInput.setEnabled(True)
#            self.labelfilter.setEnabled(False)
            self.TextOutFilter.setEnabled(False)
            self.BrowseButtonFilter.setEnabled(False)

    def methodChanged(self):
        if self.MethodInput.currentText() == 'quantile':
            self.LabelLinedit2.setEnabled(True)
            self.Linedit2.setEnabled(True)
        else:
            self.LabelLinedit2.setEnabled(False)
            self.Linedit2.setEnabled(False)

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def get_output_path_fields(self):
        """Fornisce al padre una lista di path di output da verificare
        prima di invocare onRunLocal().
        """
        return []
    
    def get_input_sources(self):
        """Fornisce al padre una lista di path di input da verificare
        prima di invocare onRunLocal()"""
        return []    

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        # Riduzione rumore
        try:
            gs = None
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            nlayerchoose = STEMUtils.checkLayers(source, self.layer_list)
            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            method = self.MethodInput.currentText()
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
            old_source = source
            if not local and sys.platform == 'win32':
                source = STEMUtils.pathClientWinToServerLinux(source)
                output = STEMUtils.pathClientWinToServerLinux(output)
                
            gs.import_grass(source, tempin, typ, nlayerchoose)

            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())
            if self.BaseInputCombo.currentText() == 'filter':
                pass
            else:
                if len(nlayerchoose) > 1:
                    raster = file_info()
                    raster.init_from_name(old_source)
                    for n in nlayerchoose:
                        layer = raster.getColorInterpretation(n)
                        out = '{name}_{lay}'.format(name=tempout, lay=layer)
                        outnames.append(out)
                        com = ['r.neighbors', 'input={n}.{l}'.format(n=tempin,
                                                                     l=layer),
                               'output={outname}'.format(outname=out),
                               'size={val}'.format(val=self.Linedit.text()),
                               'method={met}'.format(met=method)]
                        if method == 'quantile':
                            com.append('quantile={v}'.format(v=self.Linedit2.text()))
                        if self.checkbox.isChecked():
                            com.append('-c')
                        coms.append(com)
                        STEMUtils.saveCommand(com)
                else:
                    outnames.append(tempout)
                    com = ['r.neighbors', 'input={name}'.format(name=tempin),
                           'output={outname}'.format(outname=tempout),
                           'size={val}'.format(val=self.Linedit.text()),
                           'method={met}'.format(met=method)]
                    if method == 'quantile':
                        com.append('quantile={val}'.format(val=self.Linedit2.text()))
                    if self.checkbox.isChecked():
                        com.append('-c')
                    coms.append(com)
                    STEMUtils.saveCommand(com)
            gs.run_grass(coms)
            if len(nlayerchoose) > 1:
                gs.create_group(outnames, tempout)

            STEMUtils.exportGRASS(gs, self.overwrite, output, tempout, typ)

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
