# -*- coding: utf-8 -*-

"""
Create a raster map starting from LAS file using univariate statistics

It use the **grass_stem** library and it run several times *r.in.lidar* GRASS
command.

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
from qgis._core import Qgis
__author__ = 'Trilogis'
__date__ = 'December 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from stem_base_dialogs import BaseDialog
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import os
import traceback
import sys
import processing # aggiunto
from las_stem import stemLAS
#from pyro_stem import PYROSERVER
#from pyro_stem import LASPYROOBJNAME
#from pyro_stem import LAS_PORT
from qgis.PyQt.QtCore import Qt
import processing
from functools import partial
import traceback
from qgis.core import (QgsTaskManager, QgsMessageLog,
                       QgsProcessingAlgRunnerTask, QgsApplication,
                       QgsProcessingContext, QgsProcessingFeedback,
                       QgsProject, QgsSettings)
from qgis.core import (QgsApplication, QgsTask, QgsMessageLog)

MESSAGE_CATEGORY = 'AlgRunnerTask'
context = QgsProcessingContext()
feedback = QgsProcessingFeedback()

from stem_base_dialogs import MyFeedBack
mySTEMfeedback = MyFeedBack()
      





from qgis.PyQt.QtWidgets import QMessageBox



def task_finished(context, params, self, addToCanvas, addToLog, successful, results):
    
    self.runButton.setEnabled(True)
 
    if not successful:
        QgsMessageLog.logMessage('Task finished unsucessfully',
                                MESSAGE_CATEGORY)
    else:
        print("Elaboration completed.")
        
        addToLog.append("Elaboration completed.")
        
        out = params['Risultato'];
      
        if (addToCanvas):
            STEMUtils.addLayerIntoCanvas(out, 'vector')

        STEMMessageHandler.success("{ou} file created".format(ou=out))
        

   

"""
STATS = {'max': "Valore massimo della dimensione selezionata",
         'mean': "Media della dimensione selezionata", 
         'mode': "Moda della dimensione selezionata",
         'hcv': "Coefficiente di variazione della dimensione selezionata",
         'p10': "10mo percentile della dimensione selezionata",
         'p20': "20mo percentile della dimensione selezionata",
         'p30': "30mo percentile della dimensione selezionata",
         'p40': "40mo percentile della dimensione selezionata",
         'p50': "50mo percentile della dimensione selezionata",
         'p60': "60mo percentile della dimensione selezionata",
         'p70': "70mo percentile della dimensione selezionata",
         'p80': "80mo percentile della dimensione selezionata",
         'p90': "90mo percentile della dimensione selezionata",
         'c2m': "Numero ritorni sopra 2 metri diviso il totale dei ritorni",
         'cmean': "Numero ritorni sopra la media della dimensione selezionata diviso il totale dei ritorni"}

DIMENSIONS = ["Z","X","Y","Intensity","ReturnNumber","NumberOfReturns","ScanDirectionFlag","EdgeOfFlightLine","Classification","ScanAngleRank","UserData","PointSourceId","GpsTime","Red","Green","Blue"]
"""
class STEMToolsDialog(BaseDialog):

    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='*.shp')
        self.toolName = name
        self.iface = iface
        self.LocalCheck.hide()
        self.QGISextent.hide()        
        self.groupBox.hide()
           
        self._insertSingleInput(label='Layer poligonale')
        STEMUtils.addLayerToComboBox(self.BaseInput, 0)
        self.BaseInput.setCurrentIndex(-1)
        
        self._insertFileInput(pos=1)
        
        statist_list = ['max','mean','mode','hcv','p10','p20','p30','p40','p50','p60','p70','p80','p90']
        #self._insertFirstCombobox("Selezione statistiche da calcolare", 2, statist_list)
        
        self._insertLayerChooseCheckBox2Options("Selezione statistiche da calcolare",True,2)
        self.layer_list2.addItems(statist_list)
        
        dimension_list = ['Z','X','Y','Intensity','ReturnNumber','NumberOfReturns','ScanDirectionFlag','EdgeOfFlightLine','Classification','ScanAngleRank','UserData','PointSourceId','GpsTime','GpsTime','Red','Green','Blue']
        self._insertSecondCombobox("Seleziona la dimensione", 3, dimension_list)

        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

    def show_(self):
        self.switchClippingMode()
        self.show_(self)
        

    def write_log_message(self,message, tag, level):
        filename = 'C://temp//qgis.log'

        with open(filename, 'a') as logfile:
            logfile.write('{tag}({level}): {message}\n'.format(tag=tag, level=level, message=message))
        
        self.textBrowser.append('{tag}({level}): {message}'.format(tag=tag, level=level, message=message))





    def onRunLocal(self):
        # Estrazione feature LiDAR da poligoni
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            datinput = str(self.BaseInput.currentText())
            datinput = STEMUtils.getLayersSource(datinput)
            print('datinput ' + str(datinput)) 
            
            
            
            layer = STEMUtils.getLayer(self.BaseInput.currentText())
            data = layer.dataProvider()
            fields = data.fields()
            
            if (len(fields) == 1):
                QMessageBox.warning(self, "Verificare i dati di input", "Nel dataset di input è presente solo un attributo.")
                return 2
            else:
                trovato_id = False
                for i in fields:
                    if (i.name() == "id"):
                        trovato_id = True
                if not (trovato_id):
                    QMessageBox.warning(self, "Verificare i dati di input", "Nel dataset di input non è presente l'attributo id.")
                    return 2
            
            source_las = str(self.TextIn.text())
            print('source_las ' + str(source_las))            
        
            #statist_list = ['max','mean','mode','hcv','p10','p20','p30','p40','p50','p60','p70','p80','p90']
            #statistiche_val = self.BaseInputCombo.currentText()
            #statistiche = statist_list.index(statistiche_val)
            
            #statistiche_val  = self.layer_list2.lineEdit().text()
            
            statistiche_val = str(self.layer_list2.currentData())
            statistiche_val = statistiche_val.replace("'", "")
            statistiche_val = statistiche_val.replace("[", "")
            statistiche_val = statistiche_val.replace("]", "")
             
            
            
            
            statistiche_val = statistiche_val.replace("max", "0")
            statistiche_val = statistiche_val.replace("mean", "1")
            statistiche_val = statistiche_val.replace("mode", "2")
            statistiche_val = statistiche_val.replace("hcv", "3")
            statistiche_val = statistiche_val.replace("p10", "4")
            statistiche_val = statistiche_val.replace("p20", "5")
            statistiche_val = statistiche_val.replace("p30", "6")
            statistiche_val = statistiche_val.replace("p40", "7")
            statistiche_val = statistiche_val.replace("p50", "8")
            statistiche_val = statistiche_val.replace("p60", "9")
            statistiche_val = statistiche_val.replace("p70", "10")
            statistiche_val = statistiche_val.replace("p80", "11")
            statistiche_val = statistiche_val.replace("p90", "12")
             
            
            print('statistiche ' + str(statistiche_val))
            
            dimension_list = ['Z','X','Y','Intensity','ReturnNumber','NumberOfReturns','ScanDirectionFlag','EdgeOfFlightLine','Classification','ScanAngleRank','UserData','PointSourceId','GpsTime','GpsTime','Red','Green','Blue']
            dimensione_val = self.BaseInputCombo2.currentText()
            dimensione = dimension_list.index(dimensione_val)
            print('dimensione ' + str(dimensione))
            
            out = self.TextOut.text()
            print('out ' + str(out))

            self.runButton.setEnabled(False)
            self.tabWidget.setCurrentIndex(1)
     
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Estrazione_feature_lidar')
            
            
            params = {
                     'Dati_di_input' : datinput, 
                     'File_LAS_di_input' : source_las, 
                     'Seleziona_le_statistiche_da_calcolare' : statistiche_val, 
                     'Seleziona_la_dimensione' : dimensione, 
                     'Risultato' : out}
            
            ###################################################################

            #mySTEMfeedback.setLogTextEdit(self.logTextEdit, self.textBrowser)
            
            
  
            #task = QgsProcessingAlgRunnerTask(alg, params, context, feedback=mySTEMfeedback)
            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback= feedback)
      
            QgsApplication.messageLog().messageReceived.connect(self.write_log_message)
            
            task.executed.connect(partial(task_finished, context, params, self, self.AddLayerToCanvas.isChecked(), self.textBrowser))
            
            QgsApplication.taskManager().addTask(task)

            
      
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
        
        
 