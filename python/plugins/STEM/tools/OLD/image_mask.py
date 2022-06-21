# -*- coding: utf-8 -*-

"""
Tool to create a new raster map with all the bands of input data

It use the **gdal_stem** library.

Date: December 2020

Copyright: (C) 2020 Trilogis

Authors: Trilogis

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import str
from builtins import range
from _ast import Try
__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import sys

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
from gdal_stem import convertGDAL
from pyro_stem import PYROSERVER
from pyro_stem import GDALCONVERTPYROOBJNAME
from pyro_stem import GDAL_PORT
import os
import processing

from PyQt5.QtCore import *

from qgis.core import QgsProject

from qgis.PyQt.QtWidgets import QMessageBox

class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow())
        self.iface = iface
        self.toolName = name
        
        self.LocalCheck.hide()
        self.QGISextent.hide()

        
        self._insertMultipleInputTable()
        STEMUtils.addLayerToTable(self.BaseInput, 1)
        
        self._insertSecondSingleInput()
        STEMUtils.addLayerToComboBox(self.BaseInput2, 0)
        self.label2.setText(self.tr("", "Layer da utilizzare come maschera"))
        
        
        self._insertCheckbox('Usa Maschera Inversa', 1)  

        self._insertDirOutput("Cartella output",2)
        
        #self.groupBox_4.hide()
        #self.groupBox.hide()
        self.TextOut.hide()
        self.LabelOut.hide()
        self.BrowseButton.hide()
       
        STEMSettings.restoreWidgetsValue(self, self.toolName)
        self.helpui.fillfromUrl(self.SphinxUrl())
        
    def output_file_type_changed(self):
        output = os.path.splitext(self.TextOut.text())[0]
        if self.BaseInputCombo.currentText() == 'GTIFF':
            self.TextOut.setText(output + ".tif")
        elif self.BaseInputCombo.currentText() == 'ENVI':
            self.TextOut.setText(output)
        
    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def methodChanged(self):
        if self.MethodInput.currentText() == 'numeri interi':
            # int32
            self.digit = 5
        elif self.MethodInput.currentText() == 'numeri decimali':
            # float32
            self.digit = 6
        else:
            self.digit = None

    def onClosing(self):
        self.onClosing(self)

    def get_input_path_fields(self):
        """Fornisce al padre una lista di path di input da verificare
        prima di invocare onRunLocal().
        """
        return self.get_input_sources()


    def get_output_path_fields(self):
        """Fornisce al padre una lista di path di output da verificare
        prima di invocare onRunLocal().
        """
        return []

    def get_input_sources(self):
        """Fornisce al padre una lista di path di input da verificare
        prima di invocare onRunLocal()"""
        
        return [str(self.BaseInput.item(row, 0).text()) for row in range(self.BaseInput.rowCount())]

    def get_input_epsg(self):
        """Fornisce al padre una lista di path di input da verificare
        prima di invocare onRunLocal()"""
        
        for row in range(self.BaseInput.rowCount()):
            if (str(self.BaseInput.item(row, 1).text()) == ""):
                return 0
        
        return 1

    def onRunLocal(self):
        local = self.LocalCheck.isChecked()
        
        STEMSettings.saveWidgetsValue(self, self.toolName)
        sources = self.get_input_sources()
        if not sources:
            QMessageBox.warning(self, "Errore nei parametri",
                                u"Non è stato selezionato nessun input")
            # TODO: rilanciare il dialog
            dialog = STEMToolsDialog(self.iface, self.toolName)
            dialog.exec_()
            return
        
        if self.checkbox.isChecked():
            mask_typ = 1
        else:
            mask_typ = 0

        mask = str(self.BaseInput2.currentText())
        mask_source = STEMUtils.getLayersSource(mask)
        
        output_path = self.TextOut3.text()
  
        if (output_path == ""):
            QMessageBox.warning(self, "Errore nei parametri",
                                u"Non è stata selezionata nessuna cartella di output per le maschere")
            # TODO: rilanciare il dialog
            dialog = STEMToolsDialog(self.iface, self.toolName)
            dialog.exec_()
            return
  
        if (self.get_input_epsg() == 0):
            QMessageBox.warning(self, "Errore nei parametri",
                                u"EPSG non impostato nei layer di input. Assegnarlo nel file di origine oppure tramite la TOC di Qgis.")
            # TODO: rilanciare il dialog
            dialog = STEMToolsDialog(self.iface, self.toolName)
            dialog.exec_()
            return
  
        
        
        for i in sources:
  
            conversion_required = False
            
            names = STEMUtils.getNameFromSource(i)
            tipo = STEMUtils.getLayersType(names)
            
            input_epsg = QgsProject.instance().mapLayersByName(names)[0].crs().authid()
          
            
            
            #output_file = i.replace(names,"mask_" + names)
            extension = os.path.splitext(i)[1]
            filename = os.path.basename(i)
            
            output_file = output_path + "/" + "mask_" + names + extension
            
            count = 0
            
            while QFileInfo(output_file).exists():
                count += 1
                #output_file = i.replace(names,"mask" + str(count) + "_"+ names)
                output_file = output_path + "/" + "mask_" + str(count) + "_" + names + extension
  
            
            if (extension != ".tif"):
                conversion_required = True
  
            if (conversion_required):
                input_file__tif  = output_path + "/" + names + extension + "___.tif"
                output_file__tif = output_file + "___.tif"
            else:
                input_file__tif  = output_path + "/" + names + extension 
                output_file__tif = output_file
           
            nodata = 0
            if self.NODATAlineEdit.text():
                nodata = float(self.NODATAlineEdit.text())
        
            EPSG = "25832"
            if self.EPSGlineEdit.text():
                EPSG = self.EPSGlineEdit.text()
            
            if tipo == 1:
                
                import gdal
                  
                src_ds = gdal.Open(i)
                hDriver = src_ds.GetDriver()
                                        
                metadata = hDriver.GetMetadata()
                    
                if metadata.get(gdal.DCAP_CREATE) == "YES":
                    print("Driver {} supports Create() method.".format(hDriver.ShortName))

                if metadata.get(gdal.DCAP_CREATECOPY) == "YES":
                    print("Driver {} supports CreateCopy() method.".format(hDriver.ShortName))
                    
                
                   
                if (mask_typ==0):
                    
                
                    processing.run("gdal:translate",{
                                                'INPUT' : i, 
                                                'TARGET_CRS' : "EPSG:"+ EPSG,  
                                                'NODATA' : nodata, 
                                                'OUTPUT' : input_file__tif})
           
                    processing.run("gdal:cliprasterbymasklayer",
                                    { 
                                        'INPUT' : input_file__tif, 
                                        'SOURCE_CRS' : input_epsg,            
                                        'MASK' : mask_source,  
                                        'NODATA' : nodata, 
                                        'TARGET_CRS' : "EPSG:"+ EPSG, 
                                        'OUTPUT' : output_file__tif
                                    })
                
                else:
                              
                    
                    rast = gdal.Open(i)
                    num_bands = rast.RasterCount
                   
                    bands = ''
                    
                    for j in range(num_bands):
                        bands = bands + '-b ' + str(j + 1) + ' '
                    
                    extra = bands
                    #extra += " -a_srs " +  "EPSG:"+ EPSG + " -ts 100 100"
                    
                     
                    processing.run("gdal:translate",{
                                                'INPUT' : i, 
                                                'TARGET_CRS' : "EPSG:"+ EPSG,  
                                                'NODATA' : nodata, 
                                                'OUTPUT' : output_file__tif})
           
                    
                    processing.run("gdal:rasterize_over_fixed_value",
                                   { 
                                        'INPUT' : mask_source, 
                                        'INPUT_RASTER' : output_file__tif,  
                                        'BURN' : 0, 
                                        'ADD' : False,
                                        'EXTRA' : bands
                                    })
                    
                        
                                            
                output_file_asc = output_file__tif.replace("___.tif","")
                
                    
                if output_file_asc.endswith('.jp2'): 
                    output_file_asc = output_file_asc.replace("jp2","tif")
                if output_file_asc.endswith('.ecw'): 
                    output_file_asc = output_file_asc.replace("ecw","tif")
                                              
                processing.run("gdal:translate",{
                                                'INPUT' : output_file__tif, 
                                                'TARGET_CRS' : "EPSG:"+ EPSG,  
                                                'NODATA' : nodata, 
                                                'OUTPUT' : output_file_asc})
  
                output_file = output_file_asc
              
                    
                ####################### R script here ##############################
                #    processing.run("r:Ritaglio_raster", { 'Seleziona_raster' : i, 
                #                                     'Seleziona_la_maschera' : mask_source, 'Definisci_tipologia_di_ritaglio' : mask_typ, 
                #                                     'Definisci_valori_NA' : nodata, 'Definisci_EPSG' : EPSG, 'Output_raster' : output_file})
                # 
                ####################################################################
       
       
                    
               # processing.run("gdal:translate",{
               #                                 'INPUT' : output_file, 
               #                                 'TARGET_CRS' : "EPSG:"+ EPSG,  
#                                                'NODATA' : nodata, 
#                                                'OUTPUT' : output_file})
               
                if (conversion_required):
                    if os.path.exists(output_file__tif):
                        os.remove(output_file__tif)
                    if os.path.exists(input_file__tif):
                        os.remove(input_file__tif)
     
                
                if self.AddLayerToCanvas.isChecked():
                    STEMUtils.addLayerIntoCanvas(output_file, 'raster')

            
            if tipo == 0:
            
                ###################### R scrpt here ##############################
                processing.run("r:Ritaglio_vettore", { 'Seleziona_vettore' : i, 
                                                      'Seleziona_la_maschera' : mask_source, 'Definisci_tipologia_di_ritaglio' : mask_typ, 
                                                      'Definisci_EPSG' : EPSG, 'Output_vettore' : output_file})
                ###################################################################
                
                if self.AddLayerToCanvas.isChecked():
                    STEMUtils.addLayerIntoCanvas(output_file, 'vector')

      
            
        ####################### R script here ##############################
        #processing.run("r:Ritaglio_raster", { 'Seleziona_raster' : sources[0], 'Seleziona_vettore' : trainingaree, 
        #'Seleziona_la_maschera' : colindiceclasse, 'Definisci_tipologia_di_ritaglio' : elencofeaturs, 'Output_raster' : filefeatures,
        #'Output_vettore' : creazionemappa})
        ####################################################################

        #STEMMessageHandler.success("{ou} ".format(ou=command_string))
        
        #STEMMessageHandler.success("{ou} file created".format(ou=output_file))
        
        
        
        
        