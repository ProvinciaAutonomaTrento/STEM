# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 11:50:05 2015

@author: Trilogis
"""

"""
Tool to patch plus LAS file in one

It use the **las_stem** library

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
from gdal_stem import TreesTools
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import traceback
#from pyro_stem import PYROSERVER
#from pyro_stem import TREESTOOLSNAME
#from pyro_stem import GDAL_PORT
import processing
from functools import partial
import traceback
from qgis.core import (QgsTaskManager, QgsMessageLog,
                       QgsProcessingAlgRunnerTask, QgsApplication,
                       QgsProcessingContext, QgsProcessingFeedback,
                       QgsProject, QgsSettings)
from qgis.core import (QgsApplication, QgsTask, QgsMessageLog)
from qgis.PyQt.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QComboBox

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
        print("Elaboration completed.")
        
        
        out = params['Output_cima'];
     
        
        if (addToCanvas):
            STEMUtils.addLayerIntoCanvas(out, 'vector')

        STEMMessageHandler.success("{ou} file created".format(ou=out))
        


class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='*.shp')
        self.toolName = name
        self.iface = iface
        self.LocalCheck.hide()
        self.QGISextent.hide()
        
        self._insertFileInput()
        
        returns = ['dalponte2016','li2012']
        self._insertFirstCombobox("Algoritmo segmentazione", 1, returns)
        self.BaseInputCombo.currentIndexChanged.connect(self.methodChanged)
      
        
        
        label1 = "Inserire altezza minima albero"
        self._insertThresholdInteger(label=label1, minn=0, maxx=99, step=0.05, posnum =2)
        
        label2 = "Ampiezza minima finestra Dalponte (opzionale)"
        self._insertSecondThresholdInteger(label=label2, minn=0, maxx=99, step=0.05, posnum =3)        
         
        returns = ['square','circular','nulla']
        self._insertSecondCombobox("Forma finestra Dalponte (opzionale)",  4, returns)
         
        self._insertFileInputOption(filt="raster file (*.*)", label="CHM raster Dalponte2016", pos =5)
         
        label3 = "Zu Li (opzionale)"
        self._insertThirdThresholdInteger(label=label3, minn=0, maxx=99, step=0.05, posnum =6)
         
        label4 = "Distanza 1 Li (opzionale)"
        self._insertFourthThresholdInteger(label=label4, minn=0, maxx=99, step=0.05, posnum =7)
         
        label5 = "Distanza 2 Li (opzionale)"
        self._insertFifthThresholdInteger(label=label5, minn=0, maxx=99, step=0.05, posnum =8)
         
        label6 = "Massimo raggio chioma  Li (opzionale)"
        self._insertSixthThresholdInteger(label=label6, minn=0, maxx=99, step=0.05, posnum =9)
        
        self._insertSecondFileOutput(label = "Output Las/Laz", posnum = 10,filt = "LAS files (*.las);;LAZ files (*.laz)")

        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

        
        #Default values
        self.thresholdi3.setValue(15.0)
        self.thresholdi4.setValue(1.5)
        self.thresholdi5.setValue(2.0)
        self.thresholdi6.setValue(10.0)



        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        #self.EPSGlineEdit.hide()
        #self.EPSGLabel.hide()

                #-------------------------------
        #COSA BRUTTA BRUTTA DA CAMBIARE

        self.LabelThrei3.hide()
        self.thresholdi3.hide()
              
        self.LabelThrei4.hide()
        self.thresholdi4.hide()
              
        self.LabelThrei5.hide()
        self.thresholdi5.hide()
             
        self.LabelThrei6.hide()
        self.thresholdi6.hide()
            
        self.LabelThrei2.show()
        self.thresholdi2.show()
          
        self.LabelCombo2.show()
        self.BaseInputCombo2.show()

        self.horizontalLayout_layer = QHBoxLayout()
        self.horizontalLayout_layer.setObjectName("horizontalLayout_layer")
        self.label_layer99 = QLabel()
        self.label_layer99.setObjectName("label_layer_99")
        self.label_layer99.setText("")
        self.horizontalLayout_layer.addWidget(self.label_layer99)
        self.verticalLayout_options.insertLayout(100, self.horizontalLayout_layer)

        #-------------------------------
        #FINE COSA BRUTTA BRUTTA DA CAMBIARE


    def methodChanged(self):
        if self.BaseInputCombo.currentText() == 'dalponte2016':
            
            self.LabelThrei3.hide()
            self.thresholdi3.hide()
              
            self.LabelThrei4.hide()
            self.thresholdi4.hide()
              
            self.LabelThrei5.hide()
            self.thresholdi5.hide()
             
            self.LabelThrei6.hide()
            self.thresholdi6.hide()
            
            self.LabelThrei2.show()
            self.thresholdi2.show()
          
            self.LabelCombo2.show()
            self.BaseInputCombo2.show()
            
            self.labelFO.show()
            self.TextInOpt.show()
            self.BrowseButtonInOpt.show()
           
   
        elif self.BaseInputCombo.currentText() == 'li2012':
            
            self.LabelThrei2.hide()
            self.thresholdi2.hide()
          
            self.LabelCombo2.hide()
            self.BaseInputCombo2.hide()

            self.labelFO.hide()
            self.TextInOpt.hide()
            self.BrowseButtonInOpt.hide()
            
            self.LabelThrei3.show()
            self.thresholdi3.show()
             
            self.LabelThrei4.show()
            self.thresholdi4.show()
             
            self.LabelThrei5.show()
            self.thresholdi5.show()
            
            self.LabelThrei6.show()
            self.thresholdi6.show()            

        else:

            self.LabelThrei2.show()
            self.thresholdi2.show()
          
            self.LabelCombo2.show()
            self.BaseInputCombo2.show()
            
            self.labelFO.show()
            self.TextInOpt.show()
            self.BrowseButtonInOpt.show()
            
            self.LabelThrei3.hide()
            self.thresholdi3.hide()
            
            self.LabelThrei4.hide()
            self.thresholdi4.hide()
            
            self.LabelThrei5.hide()
            self.thresholdi5.hide()
           
            self.LabelThrei6.hide()
            self.thresholdi6.hide()

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
            source = str(self.TextIn.text())
            print('source ' + str(source))
            
            algosegm = self.BaseInputCombo.currentText()
            if algosegm == 'dalponte2016':
                algosegm = 0
            else:
                algosegm = 1
            print('algosegm ' + str(algosegm)) 
            
            altminalb = (self.thresholdi.value())
            if altminalb == 0:
                altminalb = 0            
            print('altminalb ' + str(altminalb))
            
            ampminfindalponte = (self.thresholdi2.value())
            if ampminfindalponte == 0:
                ampminfindalponte = 0
            print('ampminfindalponte ' + str(ampminfindalponte))
            
            formafinestradalponte = self.BaseInputCombo2.currentText() 
            if (formafinestradalponte == 'square'):
                formafinestradalponte = 0
            elif (formafinestradalponte == 'circular'):
                formafinestradalponte = 1
            else:
                formafinestradalponte = 2
            print('formafinestradalponte ' + str(formafinestradalponte))
            
            chmrasterdalponte = str(self.TextInOpt.text())
            print('chmrasterdalponte ' + str(chmrasterdalponte))
            
            if (algosegm==0) and (chmrasterdalponte==""):
                QMessageBox.warning(self, "Errore nei parametri",
                                u"L'algoritmo Dalponte2016 richiede il raster CHM")
            # TODO: rilanciare il dialog
                return 2
            
            
            zuli = (self.thresholdi3.value())
            if zuli == 0:
                zuli = 0
            print('zuli ' + str(zuli))
            
            dist1li = (self.thresholdi4.value())
            if dist1li == 0:
                dist1li = 0            
            print('dist1li ' + str(dist1li))
            
            dist2li = (self.thresholdi5.value())
            if dist2li == 0:
                dist2li = 0            
            print('dist2li ' + str(dist2li))
            
            maxraggchiomali = (self.thresholdi6.value())
            if maxraggchiomali == 0:
                maxraggchiomali = 0            
            print('maxraggchiomali ' + str(maxraggchiomali))
            
            out = str(self.TextOut.text())
            print('out ' + str(out))
            
            outlas = self.TextOut2.text()
            print('outlas ' + str(outlas))
            
            EPSG = "25832"
            if self.EPSGlineEdit.text():
                EPSG = self.EPSGlineEdit.text()
            
            self.runButton.setEnabled(False)
            self.tabWidget.setCurrentIndex(1)

            
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Individuazione_alberi')
            
            
            params = { 
                'CHM_las' : source, 
                'Algoritmo_segmentazione' : algosegm, 
                'Altezza_minima_albero' : altminalb, 
                'Ampiezza_minima_finestra_Dalponte' : ampminfindalponte,
                'Forma_finestra_Dalponte' : formafinestradalponte ,
                'CHM_raster_Dalponte' : chmrasterdalponte, 
                'Zu_Li' : zuli, 
                'Distanza_1_Li' : dist1li, 
                'Distanza_2_Li' : dist2li,
                'Massimo_raggio_chioma_Li' : maxraggchiomali, 
                'Definisci_EPSG' : EPSG, 
                'Output_cima' : out, 
                'Output_las' : outlas 
                }
            
            ###################################################################
           
            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
            
                               #LogError
            QgsApplication.messageLog().messageReceived.connect(self.write_log_message)


            task.executed.connect(partial(task_finished, context, params, self, self.AddLayerToCanvas.isChecked()))
            QgsApplication.taskManager().addTask(task)

      
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return
#==
