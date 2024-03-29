# -*- coding: utf-8 -*-

"""
Tool to performs Pansharpening

It use the **grass_stem** library and it run *i.pansharpen* GRASS command.

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
from gdal_stem import file_info
import sys


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.toolName = name
        self.iface = iface

        self._insertSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput, 1)

        self._insertLayerChooseCheckBox(label="Selezionare la banda per il canale rosso",
                                        combo=False)
        self.BaseInput.currentIndexChanged.connect(self.indexChanged)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list, is_checkable=False)

        self._insertLayerChooseCheckBox2(label="Selezionare la banda per il canale verde",
                                         combo=False)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list2, is_checkable=False)

        self._insertLayerChooseCheckBox3(label="Selezionare la banda per il canale blu",
                                         combo=False)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list3, is_checkable=False)

        self._insertSecondSingleInput(5)
        STEMUtils.addLayerToComboBox(self.BaseInput2, 1)
        self._insertLayerChooseCheckBox4(label="Selezionare la banda con risoluzione migliore",
                                         combo=False, pos=6)
        self.BaseInput2.currentIndexChanged.connect(self.indexChanged2)
        STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list4, is_checkable=False)

        methods = ['brovey', 'ihs', 'pca']
        self._insertMethod(methods, "Seleziona tipo di Pansharpening", 0)

#        self._insertLayerChoose()
#        tooltip = self.tr(name, "Inserire i numeri dei "
#                                "layer da utilizzare, divisi da \n"
#                                "una virgola, il primo "
#                                "dev'essere il canale per il rosso,\n"
#                                " il secondo per verde, il terzo "
#                                "per il blu, mentre il quarto deve\n"
#                                " essere la banda con risoluzione"
#                                " più alta")
#        self.layer_list.setToolTip(tooltip)
#        self.label_layer.setToolTip(tooltip)

        self.LabelOut.setText(self.tr(name, "Risultato"))
        self.helpui.fillfromUrl(self.SphinxUrl())

        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def indexChanged(self):
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list, is_checkable=False)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list2, is_checkable=False)
        STEMUtils.addLayersNumber(self.BaseInput, self.layer_list3, is_checkable=False)

    def indexChanged2(self):
        STEMUtils.addLayersNumber(self.BaseInput2, self.layer_list4, is_checkable=False)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

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
        try:
            gs = None
            name = str(self.BaseInput.currentText())
            source = STEMUtils.getLayersSource(name)
            namepan = str(self.BaseInput2.currentText())

            red = str(self.layer_list.currentIndex() + 1)
            green = str(self.layer_list2.currentIndex() + 1)
            blu = str(self.layer_list3.currentIndex() + 1)
            pan = str(self.layer_list4.currentIndex() + 1)
            nlayers = [red, green, blu]

            typ = STEMUtils.checkMultiRaster(source, self.layer_list)
            method = str(self.MethodInput.currentText())
            coms = []
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
                output = STEMUtils.pathClientWinToServerLinux(output, False)
            if name == namepan:
                nlayers.append(pan)
                gs.import_grass(source, tempin, typ, nlayers)
            else:
                gs.import_grass(source, tempin, typ, nlayers)
                sourcepan = STEMUtils.getLayersSource(namepan)
                if not local and sys.platform == 'win32':
                    sourcepan = STEMUtils.pathClientWinToServerLinux(sourcepan)
                gs.import_grass(sourcepan, namepan, typ, [pan])
            if mask:
                if not local:
                    mask = STEMUtils.pathClientWinToServerLinux(mask)
                gs.check_mask(mask, inverse_mask())
            raster = file_info()
            raster.init_from_name(old_source)
            red = raster.getColorInterpretation(red)
            green = raster.getColorInterpretation(green)
            blu = raster.getColorInterpretation(blu)
            com = ['i.pansharpen', 'red={name}.{l}'.format(name=tempin, l=red),
                   'green={name}.{l}'.format(name=tempin, l=green),
                   'blue={name}.{l}'.format(name=tempin, l=blu),
                   'output={name}'.format(name=tempout),
                   'method={met}'.format(met=method)]
            if name == namepan:
                pan = raster.getColorInterpretation(pan)
                com.append('pan={name}.{l}'.format(name=tempin, l=pan))
            else:
                com.append('pan={name}'.format(name=namepan))
    #        pdb.set_trace()
            coms.append(com)
            STEMUtils.saveCommand(com)
            
            group_name = '{}_group'.format(tempout)
            input = ['{}_red'.format(tempout), '{}_green'.format(tempout), '{}_blue'.format(tempout)]
            com_gruppo = 'i.group group={group_name} subgroup={group_name} input={input}'.format(group_name = group_name, input = ','.join(input))
            coms.append(com_gruppo.split())
            STEMUtils.saveCommand(com_gruppo)
            
            gs.run_grass(coms)
            
            STEMUtils.exportGRASS(gs, self.overwrite, output, group_name, typ, forced_output = True, local = local)

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
