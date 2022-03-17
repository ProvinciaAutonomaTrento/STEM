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
from STEM import stem_utils
__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import sys

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
from qgis.core import QgsProject                            
import os

import processing
from functools import partial
import traceback
from qgis.core import (QgsTaskManager, QgsMessageLog,
                       QgsProcessingAlgRunnerTask, QgsApplication,
                       QgsProcessingContext, QgsProcessingFeedback,
                       QgsProject, QgsSettings,QgsRasterLayer,QgsCoordinateReferenceSystem)
from qgis.core import (QgsApplication, QgsTask, QgsMessageLog)

MESSAGE_CATEGORY = 'AlgRunnerTask'
context = QgsProcessingContext()
feedback = QgsProcessingFeedback()



from qgis.PyQt.QtWidgets import QMessageBox



def task_finished(context, params, self, addToCanvas, successful, results):
    
    self.runButton.setEnabled(True)
    
    if not successful:
        QgsMessageLog.logMessage('Task finished unsucessfully',
                                MESSAGE_CATEGORY)
    else:
        
        if params['Ritaglio']==0:
            out = params['Percorso_output']
   
        
        if params['Ritaglio']==1:
            print("1st Elaboration completed.")
        
            out = params['Percorso_output_over']
            out_temp = params['Percorso_output']
            out1 = params['Overlap_extent']
        
            processing.run("gdal:cliprasterbyextent",{ 
                    'DATA_TYPE' : 0, 
                    'EXTRA' : '', 
                    'INPUT' : out_temp, 
                    'NODATA' : None, 
                    'OPTIONS' : '', 
                    'OUTPUT' : out, 
                    'OVERCRS' : False, 
                    #'PROJWIN' : '622343.915600000,625533.727300000,5147128.409900000,5149039.586000000 [EPSG:25832]' })
                    'PROJWIN' : out1 })
            
            import os
            if os.path.exists(out_temp):
                os.remove(out_temp)
            else:
                print("The tmp file does not exist") 
      
        #processing.run("gdal:translate",{
        #                                'INPUT' : out, 
        #                                'TARGET_CRS' : "EPSG:"+ params['Definisci_EPSG'],  
         #                               'NODATA' : params['Definisci_EPSG'], 
        #                                'OUTPUT' : out})
   
        #print(results)
        
        print("Elaboration completed.")
        
        if (addToCanvas):
            STEMUtils.addLayerIntoCanvas(out, 'raster')

        STEMMessageHandler.success("{ou} file created".format(ou=out))
        

   



class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='*.tif')
        self.iface = iface
        self.toolName = name
        
        self.LocalCheck.hide()
        self.QGISextent.hide()
        
        self._insertLayerChooseCheckBox2Options('Risoluzione immagine accatastata',False,2)
        
        self._insertMultipleInputTable()

        self.BaseInput.insertColumn(3)
        self.BaseInput.insertColumn(4)
        self.BaseInput.setHorizontalHeaderLabels(['File','EPSG','Valore di nodata', 'Num_Bande', 'Bande_Selezionate' ])
            
        STEMUtils.addLayerToTable(self.BaseInput)


        sources = self.get_input_sources()
        names = [STEMUtils.getNameFromSource(i) for i in sources]
     
        resolution_list = []
        
        for s in names:
            print(s)
            layer = QgsProject.instance().mapLayersByName(s)[0]
            pixelSizeX = layer.rasterUnitsPerPixelX()
            resolution_list.append(str("{:.3f}".format(pixelSizeX)))
                       
        for res in set(resolution_list):
            self.layer_list2.addItem(res)
        
        formats = ['GTIFF', 'ENVI']
        self._insertFirstCombobox('Formato di output', 0, formats)
        self.BaseInputCombo.currentIndexChanged.connect(self.output_file_type_changed)
        
       # mets = ['Selezionare il formato di output', 'numeri interi',
       #         'numeri decimali']
        self.digit = 6
        
        #self.lm = "Selezionare la tipologia del formato di output"
        #self._insertMethod(mets, self.lm, 1)
        #self.MethodInput.currentIndexChanged.connect(self.methodChanged)
        
        
#         label = "Risoluzione per tutte le bande del file di output"
#         self._insertFirstLineEdit(label, 2)


        methods = ['near','bilinear','cubic','cubicspline','lanczos','average','mode','max','min','med','q1','q3']
       
        self._insertSecondCombobox('Metodo di interpolazione', 1, methods)
      






        self._insertCheckbox("Forza ritaglio su overlap",1)

        #label = "Valore di NODATA (default -9999)"
        #self._insertFirstLineEdit(label, 2)

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
        return [str(self.BaseInput.item(row, 0).text()) for row in range(self.BaseInput.rowCount())]

    def get_input_sourcesBands(self):
        return [str(self.BaseInput.item(row, 4).text()) for row in range(self.BaseInput.rowCount())]

    def get_input_numBands(self):
        return [int(self.BaseInput.item(row, 3).text()) for row in range(self.BaseInput.rowCount())]

    def get_input_epsgs(self):
        return [str(self.BaseInput.item(row, 1).text()) for row in range(self.BaseInput.rowCount())]


    def add_prj_files(self, file_path, epsg):
        
       
        try:
            driver = STEMUtils.getFormat(file_path)
            proj  = STEMUtils.getProjection(file_path)
            
            if (driver =="AAIGrid"):
                if (proj ==""):
                   # gdal_translate -a_srs EPSG:25832 -of AAIGrid G:/.shortcut-targets-by-id/1invx6AIKebcfe6GfuxgjIPED9z1u4rmG/STEM-v3/test2022/5h658051265_DTM.asc C:/temp/TEST/altro/test_translata.asc
                    
                    #processing.run('gdal:assignprojection',
                    #                { 'CRS' : QgsCoordinateReferenceSystem('EPSG:25832'), 
                    #                 'INPUT' : file_path })
       
                    #processing.run('gdal:assignprojection',
                    #               { 'CRS' : QgsCoordinateReferenceSystem('EPSG:25832'), 
                    #              #  'INPUT' : 'G:/.shortcut-targets-by-id/1invx6AIKebcfe6GfuxgjIPED9z1u4rmG/STEM-v3/test2022/5h658051265_DTM_2.asc' })
                     #               'INPUT' : 'G:/.shortcut-targets-by-id/1invx6AIKebcfe6GfuxgjIPED9z1u4rmG/STEM-v3/test2022/a_2.asc' })
                    
                    #from qgis.PyQt.QtCore import QUuid, QFile
                    #from qgis.PyQt.QtXml import QDomDocument
        
                    #contentsDoc =  QDomDocument("Create .Prj")

                    #xml_file = QFile(file_path+".aux.xml")
                    #statusOK, errorStr, errorLine, errorColumn = contentsDoc.setContent(xml_file, True)

                    #if not statusOK:
                    #    QtGui.QMessageBox.critical(None, "DOM Parser",
                    #                               "Could not read or find the contents docuement. Error at "
                    #                               "line %d, column %d:\n%s" % (errorLine, errorColumn, errorStr))
                    #    sys.exit(-1)
            
                    #SRS = contentsDoc.elementsByTagName('SRS')   
    
                    #id_node = SRS.at(0)
                    #id_elem = id_node.toElement()
                    #old_id = id_elem.text()
          
                    from osgeo import gdal  
                    from osgeo import osr
            
                    sr = osr.SpatialReference()
                    if sr.SetFromUserInput('EPSG:25832') != 0:
                
                        print('Failed to process SRS definition: %s' % srs)
                        return -1
            
                    wkt = sr.ExportToWkt()
            
                    fs = open(file_path.replace(".asc",".prj"), 'w')
        
                    fs.write(wkt)
                    fs.close()
                   
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
        return
        
               
            #gdal_translate -a_srs EPSG:25832 -of AAIGrid G:/.shortcut-targets-by-id/1invx6AIKebcfe6GfuxgjIPED9z1u4rmG/STEM-v3/test2022/5h658051265_DTM.asc C:/temp/TEST/altro/test_translata.asc


    def changeR_ProjDB_file(self):
        from qgis.core import QgsApplication
        
        projDB = QgsApplication.qgisSettingsDirPath() + "processing/rlibs/rgdal/proj/proj.db"
        
        import shutil

        shutil.copyfile(QgsApplication.qgisSettingsDirPath() + "python/plugins/STEM/dep/proj.db", projDB)


    def onRunLocal(self):
        # Accatastamento
        local = True
        if not self.digit:
            # STEMMessageHandler.error("Selezionare il formato di output")
            QMessageBox.critical(self, "Parametro mancante",
                                 "Selezionare il formato di output")
            return 2
        STEMSettings.saveWidgetsValue(self, self.toolName)
        
        try:
        
            sources = self.get_input_sources()
            epsgs = self.get_input_epsgs()
            bands = self.get_input_sourcesBands()
            n_bands = self.get_input_numBands()
        
        
            if not sources:
                QMessageBox.warning(self, "Errore nei parametri",
                                u"Non è stato selezionato nessun input.")
                # TODO: rilanciare il dialog
                #dialog = STEMToolsDialog(self.iface, self.toolName)
                #dialog.exec_()
                return 2
            
            for i in epsgs:
                if i == "":
                    QMessageBox.warning(self, "Errore nei parametri",
                                u"Uno o più dati di input non hanno EPSG assegnato.")
                    return 2
            
            
            names = [STEMUtils.getNameFromSource(i) for i in sources]
            outformat = str(self.BaseInputCombo.currentText())
            cut, cutsource = self.cutInputMulti(names, sources, local=local)

            input_files = ""
            input_epsgs = ""
            input_bands = ""

            x = 0
        
            bands_offset = 0        
            
            k = 0
            for i in sources:
                
                self.add_prj_files(i,epsgs[k])
                k = k +1
                input_files += "\"" + i + "\";"
                #input_files += "\"" + i + " " + "["+ bands[x] +"]\" "
            
                if bands[x] == "":
                    for z in range(n_bands[x]):
                        input_bands += "" + str(bands_offset + int(z + 1)) + " "
                
                for y in bands[x]:
                    if (y != " ") and (y != ".") and (y != ",") and (y != "#") and (y != ";"):
                        input_bands += "" + str(bands_offset + int(y)) + " "
                    
                bands_offset += n_bands[x]    
                x += 1
            
            overlap_minx = 0
            overlap_miny = 0
            overlap_maxx = 0
            overlap_maxy = 0
            
            
            for i in sources:
                minx,maxx, miny, maxy = STEMUtils.getExtend(i)
                
                if overlap_minx == 0:
                    overlap_minx = minx
                if overlap_miny == 0:
                    overlap_miny = miny
                if overlap_maxx == 0:
                    overlap_maxx = maxx
                if overlap_maxy == 0:
                    overlap_maxy = maxy
                    
                if minx > overlap_minx:
                    overlap_minx = minx
                if maxy < overlap_maxy:
                    overlap_maxy = maxy
                if miny > overlap_miny:
                    overlap_miny = miny
                if maxx < overlap_maxx:
                    overlap_maxx = maxx
            
            for i in epsgs:
                input_epsgs +=  i + ";"
          
            
            if outformat == 'GTIFF':
                input_format = 0
            else:
                input_format = 1   
    
    
            if cut:
                items = cut
                sources = cutsource

            out = self.TextOut.text()
            if outformat == 'GTIFF' and not (out.endswith('.tif') or
                                             out.endswith('.TIF') or out.endswith('.tiff') or out.endswith('.TIFF')):
                out = out + '.tif'
            
            out_orig = out
        
            resolution = float(self.layer_list2.currentText())
            
            method = self.BaseInputCombo2.currentText()
     
            nodata = None
            if self.NODATAlineEdit.text():
                nodata = float(self.NODATAlineEdit.text())

            EPSG = "25832"
            
            if self.EPSGlineEdit.text():
                EPSG = self.EPSGlineEdit.text()
        
            print('Input ' + str("r:Accatastamento_ritaglio"))
            print('Elenco_path_raster ' + str(input_files))
            print('Elenco_EPSGs_input_raster ' + str(input_epsgs))
            print('Formato_di_output ' + str(input_format))
            print('Selezione_bande ' + str(input_bands))
            print('Definisci_valori_NA ' + str(nodata))
            print('Definisci_EPSG ' + str(EPSG))
            print('Percorso_output ' + str(out))
            
            self.runButton.setEnabled(False)
            self.tabWidget.setCurrentIndex(1)
     
            self.changeR_ProjDB_file()
     
            if self.checkbox.isChecked():
        
                alg = QgsApplication.processingRegistry().algorithmById(
                'r:Accatastamento_ritaglio')
            
                params = { 
                    'Elenco_path_raster' : input_files, 
                    'Formato_di_output' : input_format, 
                    'Selezione_bande' : input_bands, 
                    'Definisci_valori_NA' : nodata, 
                    'Definisci_EPSG' : EPSG,
                    'Definisci_Resolution' : resolution,
                    'Definisci_Metodo' : method,
                    'Percorso_output' : out + "_tmp.tif",
                    'Percorso_output_over' : out,
                    'Ritaglio' : 1,
                    'Overlap_extent' : str(overlap_minx) + "," +str(overlap_maxx) + "," +str(overlap_miny) + "," +str(overlap_maxy) + " " + "[EPSG:" + EPSG +"]"
                    }
                   
                ###################################################################
            else:   
            
                alg = QgsApplication.processingRegistry().algorithmById(
                'r:Accatastamento')
            
                params = { 
                    'Elenco_path_raster' : input_files, 
                    'Formato_di_output' : input_format, 
                    'Selezione_bande' : input_bands, 
                    'Definisci_valori_NA' : nodata, 
                    'Definisci_EPSG' : EPSG,
                    'Definisci_Resolution' : resolution,
                    'Definisci_Metodo' : method,
                    'Percorso_output' : out,
                    'Ritaglio' : 0
                    }
                   
            ###################################################################

            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
                             #LogError
            QgsApplication.messageLog().messageReceived.connect(self.write_log_message)
   
            task.executed.connect(partial(task_finished, context, params, self, self.AddLayerToCanvas.isChecked(), self.textBrowser))
            QgsApplication.taskManager().addTask(task)
      
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
#===============================================================================
#         if local:
#             cgdal = convertGDAL()
#         if not self.LocalCheck.isChecked() and sys.platform == 'win32':
#             cgdal.initialize([STEMUtils.pathClientWinToServerLinux(x) for x in sources],
#                              output=STEMUtils.pathClientWinToServerLinux(out),
#                              outformat=outformat,
#                              bandtype=self.digit)
#         else:
# 
#             # with open(r'Z:\idt\tempout\temp.log','a') as f:
#             #     f.write('Non converto i path')
#             cgdal.initialize(sources, output=out, outformat=outformat,
#                              bandtype=self.digit)
# 
#         #if self.Linedit.text():
#         #    resolution = float(self.Linedit.text())
#         #else:
#         #    resolution = None
#         
#        
#         
#         cgdal.write(nodata = nodata)
#===============================================================================


        

