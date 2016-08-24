# -*- coding: utf-8 -*-

"""
Tool to calculate DOS for Landsat images

It use the **grass_stem** library and it run several times *r.univar* GRASS
command.

Date: July 2015

Copyright: (C) 2015 Luca Delucchi

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
from stem_utils_server import STEMSettings
from grass_stem import temporaryFilesGRASS
import traceback
import glob
import os
import sys

from functools import partial
from PyQt4.QtCore import SIGNAL

def basename(name):
    suffix = ['.tif', '.TIF']
    for suf in suffix:
        if name.find(suf) != -1:
            return name.replace(suf, '')
    return None

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix="")
        self.toolName = name
        self.iface = iface

        label = "Selezionare la cartella contenente i file Landsat"
        self._insertDirectory(label)
        self._insertFileInput(pos=1, filterr="Text file (*)")
        self.labelF.setText(self.tr("", "Selezionare il file dei metadata dei "
                                        "dati Landsat da analizzare"))
        labline = "Selezionare il prefisso dei dati Landsat"
        self._insertFirstLineEdit(labline, posnum=0)
        methods = ['uncorrected', 'dos1', 'dos2', 'dos2b', 'dos3', 'dos4']
        labmet = "Metodo di correzione atmosferica"
        self._insertMethod(methods, labmet, posnum=1)
        self.MethodInput.currentIndexChanged.connect(self.methodChanged)
        labprec = "Percentuale della radianza solare"
        self._insertSecondLineEdit(labprec, posnum=2)
        self.Linedit2.setEnabled(False)
        labpix = "Numero minimo di pixel da considerare numero digitale come "\
                 "dark object"
        self._insertThirdLineEdit(labpix, posnum=3)
        self.Linedit3.setEnabled(False)
        labray = "Valore dello scattering di Rayleigh, si utilizza solo con "\
                 "il metodo `dos3`"
        self._insertFourthLineEdit(labray, posnum=4)
        self.Linedit4.setEnabled(False)

        self.LabelOut.setText('Selezionare prefisso per salvare i risultati')
        
        self.QGISextent.hide()
        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)
    
    def check_paths_validity(self):
        errors = []
        
        for p in self.get_input_path_fields():
            if not os.path.exists(p):
                errors.append(p)
        # TextOut e` comune a tutti i plugin
        paths = self.get_output_path_fields()
        if not self.TextOut.isHidden() and self.TextOut.isEnabled():
            paths.append(self.TextOut.text())
        for p in paths:
            # Controllo che esista la cartella 
            # del file di output
            if not os.path.isdir(os.path.split(p)[0]):
                errors.append(p)
                continue
            
        return errors

    def methodChanged(self):
        if self.MethodInput.currentText().find('dos') != -1:
            self.Linedit2.setEnabled(True)
            self.Linedit3.setEnabled(True)
        else:
            self.Linedit2.setEnabled(False)
            self.Linedit3.setEnabled(False)
        if self.MethodInput.currentText() == 'dos3':
            self.Linedit4.setEnabled(True)
        else:
            self.Linedit4.setEnabled(False)

    def show_(self):
        self.switchClippingMode()
        BaseDialog.show_(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            gs = None
            coms = []
            tempouts = []
            outdir = str(self.TextOut.text())
            metfile = str(self.TextIn.text())
            sourcedir = str(self.TextDir.text())
            pref = str(self.Linedit.text())
            files = glob.glob1(sourcedir, '{pre}*'.format(pre=pref))
            sources = [os.path.join(sourcedir, fi) for fi in files if fi.find('aux') == -1 and fi.find('txt') == -1]
            method = str(self.MethodInput.currentText())
            suffix = 'dos'
            local = self.LocalCheck.isChecked()
            cut, cutsource = self.cutInputMulti(files, sources, local=local)
            if cut:
                files = cut
                sources = cutsource
            tempin, tempout, gs = temporaryFilesGRASS(files[0], local)
            for sou in sources:
                key = basename(sou).split('_B')[-1]
                tempin = '{}.{}'.format(pref, key)
                if (key != 'QA'):
                    # we don't output the quality assurance band
                    tempout = "{pref}_{suf}{key}".format(pref=pref, suf=suffix,
                                                         key=key)
                    tempouts.append(tempout)
                if not local and sys.platform == 'win32':
                    source = STEMUtils.pathClientWinToServerLinux(sou)
                else:
                    source = sou
                gs.import_grass(source, tempin, 'raster', [1])

            if not local and sys.platform == 'win32':
                metfile = STEMUtils.pathClientWinToServerLinux(metfile)
            else:
                metfile = metfile
                                
            com = ['i.landsat.toar', 'input={name}'.format(name=pref + '.'),
                   'output={outname}'.format(outname='_'.join([pref, suffix])),
                   'metfile={met}'.format(met=metfile),
                   'method={met}'.format(met=method)]
            if self.Linedit2.text():
                com.append('percent={per}'.format(per=self.Linedit2.text()))
            if self.Linedit3.text():
                com.append('pixel={per}'.format(per=self.Linedit3.text()))
            if self.Linedit4.text():
                com.append('rayleigh={per}'.format(per=self.Linedit4.text()))
            coms.append(com)
            STEMUtils.saveCommand(com)
            gs.run_grass(coms)
            for tpo in tempouts:
                out = "{di}_{name}.tif".format(di=outdir, name=tpo)
                if not local and sys.platform == 'win32':
                    output = STEMUtils.pathClientWinToServerLinux(out, False)
                else:
                    output = out
                STEMUtils.exportGRASS(gs, self.overwrite, output, tpo,
                                      'raster', remove=False)
                if self.AddLayerToCanvas.isChecked():
                    STEMUtils.addLayerIntoCanvas(out, 'raster')
                
            if not local:
                gs._pyroRelease()
        except:
            if not local and gs is not None:
                gs._pyroRelease()
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
