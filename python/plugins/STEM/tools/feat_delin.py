# -*- coding: utf-8 -*-

"""

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
#from gdal_stem import TreesTools
from stem_utils import STEMUtils, STEMMessageHandler
from stem_utils_server import STEMSettings
import traceback
#from pyro_stem import PYROSERVER
#from pyro_stem import TREESTOOLSNAME
#from pyro_stem import GDAL_PORT

from time import sleep

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



from qgis.PyQt.QtWidgets import QMessageBox



def task_finished(context, params, self, addToCanvas, successful, results):
    
    self.runButton.setEnabled(True)

    if not successful:
        QgsMessageLog.logMessage('Task finished unsucessfully',
                                MESSAGE_CATEGORY)
    else:
        print("Elaboration completed.")
        
        out = params['Output_chiome'];
        out2 = params['Output_cime_chiome'];
      
        if (addToCanvas):
            STEMUtils.addLayerIntoCanvas(out, 'vector')
            STEMUtils.addLayerIntoCanvas(out2, 'vector')

        STEMMessageHandler.success("{ou},{ou2} files created".format(ou=out,ou2=out2))
        

   



class STEMToolsDialog(BaseDialog):
    def __init__(self, iface, name):
        BaseDialog.__init__(self, name, iface.mainWindow(), suffix='*.shp')
        self.toolName = name
        self.iface = iface
        self.LocalCheck.hide()
        self.QGISextent.hide()
        
        self._insertSecondFileInput(filterr="raster file (*.*)", label="File raster di input")
        
        label1 = "Risoluzione"
        self._insertThresholdInteger(label=label1, minn=0, maxx=99, step=0.05, posnum =0)
        
        label2 = "Ampiezza minima finestra"
        self._insertSecondThresholdInteger(label=label2, minn=3, maxx=99, step=0.05, posnum =1)
        
        label3 = "Ampiezza massima finestra"
        self._insertThirdThresholdInteger(label=label3, minn=3, maxx=99, step=0.05, posnum =2)
        
        label4 = "Soglia crescita chioma"
        self._insertFourthThresholdInteger(label=label4, minn=0, maxx=1, step=0.01, posnum =3)
        
        label5 = "Soglia crescita albero"
        self._insertFifthThresholdInteger(label=label5, minn=0, maxx=1, step=0.01, posnum =4)
        
        label6 = "Soglia minima diametro chioma"
        self._insertSixthThresholdInteger(label=label6, minn=0, maxx=99, step=0.05, posnum =5)

        label7 = "Soglia massima diametro chioma"
        self._insertsSeventhThresholdInteger(label=label7, minn=0, maxx=99, step=0.05, posnum =6)

        label8 = "Altezza minima albero"
        self._insertEighthThresholdInteger(label=label8, minn=0, maxx=99, step=0.05, posnum =7)
        
        self._insertSecondFileOutput(label = "Output cime chiome", posnum = 2,filt= "SHP files (*.shp)")

        self.helpui.fillfromUrl(self.SphinxUrl())
        STEMSettings.restoreWidgetsValue(self, self.toolName)

        self.NODATAlineEdit.hide()
        self.NODATALabel.hide()
        #self.EPSGlineEdit.hide()
        #self.EPSGLabel.hide()

    def show_(self):
        self.switchClippingMode()
        self.show_(self)

    def onClosing(self):
        self.onClosing(self)

    def onRunLocal(self):
        STEMSettings.saveWidgetsValue(self, self.toolName)
        try:
#            name = str(self.BaseInput.currentText())
#            source = STEMUtils.getLayersSource(name)
            
#             rasttyp = STEMUtils.checkMultiRaster(source)
#             cut, cutsource, mask = self.cutInput(name, source, rasttyp, local=self.LocalCheck.isChecked())
#             
#             if cut:
#                 name = cut
#                 source = cutsource
            
#            name2 = str(self.BaseInput2.currentText())
#            source2 = STEMUtils.getLayersSource(name2)

            source = str(self.TextIn2.text())
            print('source ' + str(source))
            
            risoluzione = (self.thresholdi.value())
            print('risoluzione ' + str(risoluzione))
            
            ampiezzaminimafinestra = (self.thresholdi2.value())
            print('ampiezzaminimafinestra ' + str(ampiezzaminimafinestra))
            
            ampiezzamassimafinestra = (self.thresholdi3.value())
            print('ampiezzamassimafinestra ' + str(ampiezzamassimafinestra))
            
            sogliacrescitachioma = (self.thresholdi4.value())
            print('sogliacrescitachioma ' + str(sogliacrescitachioma))
            
            sogliacrescitaalbero = (self.thresholdi5.value())
            print('sogliacrescitaalbero ' + str(risoluzione))
            
            sogliaminimadiametrochioma = (self.thresholdi6.value())
            print('sogliaminimadiametrochioma ' + str(sogliaminimadiametrochioma))
            
            sogliamassimadiametrochioma = int(self.thresholdi7.value())
            print('sogliamassimadiametrochioma ' + str(sogliamassimadiametrochioma)) 
            
            altezzaminimaalbero = int(self.thresholdi8.value())
            print('altezzaminimaalbero ' + str(altezzaminimaalbero))
            
            out = str(self.TextOut.text())
            print('out ' + str(out))
            
            out2 = str(self.TextOut2.text())
            print('out2 ' + str(out2))
            
            EPSG = "25832"
            if self.EPSGlineEdit.text():
                EPSG = self.EPSGlineEdit.text()
            
            self.runButton.setEnabled(False)
            self.tabWidget.setCurrentIndex(1)

            
            alg = QgsApplication.processingRegistry().algorithmById(
                'r:Delimitazione_chiome')
            
            params = { 
                    'File_CHM_raster' : source, 
                    'Risoluzione' : risoluzione, 
                    'Ampiezza_minima_finestra' : ampiezzaminimafinestra, 
                    'Ampiezza_massima_finestra' : ampiezzamassimafinestra,
                    'Soglia_crescita_chioma' : sogliacrescitachioma ,
                    'Soglia_crescita_albero' : sogliacrescitaalbero, 
                    'Soglia_minima_diametro_chioma' : sogliaminimadiametrochioma, 
                    'Soglia_massima_diametro_chioma' : sogliamassimadiametrochioma, 
                    'Altezza_minima_albero' : altezzaminimaalbero, 
                    'Definisci_EPSG' : EPSG,
                    'Output_chiome' : out, 
                    'Output_cime_chiome' : out2
                    }
   
   
            task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
                               #LogError
            QgsApplication.messageLog().messageReceived.connect(self.write_log_message)

            task.executed.connect(partial(task_finished, context, params, self, self.AddLayerToCanvas.isChecked()))
            QgsApplication.taskManager().addTask(task)

      
        except:
            self.error = traceback.format_exc()
            STEMMessageHandler.error(self.error)
            return