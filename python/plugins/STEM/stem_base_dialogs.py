# -*- coding: utf-8 -*-

"""
Date: December 2020

Authors: Trilogis

Copyright: (C) 2020 Trilogis

This file contain some dialogs (base, settings and help) of STEM project.
"""
from __future__ import print_function
from __future__ import absolute_import

from builtins import str
from builtins import range

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

from qgis.gui import *
# from Scripts import epsg_tr

__author__ = 'Trilogis'
__date__ = 'december 2020'
__copyright__ = '(C) 2020 Trilogis'

import os
import os.path
import sys
import subprocess
import tempfile
import platform
from functools import partial

import traceback

import qgis.core
import qgis.gui

from stem_utils import STEMMessageHandler
from stem_utils import STEMUtils
from stem_utils import CheckableComboBox
from stem_utils import PathMapping
from libs.stem_utils_server import STEMSettings, inverse_mask
from libs import gdal_stem
from qgis.core import QgsApplication
from qgis.core import QgsProject

try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise Exception('Python GDAL library not found, please install python-gdal')
try:
    import osgeo.ogr as ogr
except ImportError:
    try:
        import ogr
    except ImportError:
        raise Exception('Python GDAL library not found, please install python-gdal')

import processing
from functools import partial
import traceback
from qgis.core import (QgsTaskManager, QgsMessageLog,
                       QgsProcessingAlgRunnerTask, QgsApplication,
                       QgsProcessingContext, QgsProcessingFeedback,
                       QgsProject, QgsSettings)
    
MESSAGE_CATEGORY = 'AlgRunnerTask'
context = QgsProcessingContext()
feedback = QgsProcessingFeedback()


baseDialog = uic.loadUiType(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'base.ui'))[0]
helpDialog = uic.loadUiType(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'help.ui'))[0]
settingsDialog = uic.loadUiType(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'settings.ui'))[0]

def escapeAndJoin(strList):
    """Escapes arguments and return them joined in a string

    :param list strList: a list of string
    """
    joined = ''
    for s in strList:
        if s.find(" ") is not -1:
            escaped = '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
        else:
            escaped = s
        joined += escaped + " "
    return joined.strip()

class TableWidgetDragRows(QTableWidget):
    """A custom implementation derived from QTableWidget that supports dragging & dropping.
    """
    
    def __init__(self, *args, **kwargs):
        QTableWidget.__init__(self, *args, **kwargs)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.SingleSelection) 
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)   
        self.keyPressEvent = self.handleDeleteKeyPress

    def dropEvent(self, event):
        if event.source() == self and (event.dropAction() == Qt.MoveAction or self.dragDropMode() == QAbstractItemView.InternalMove):
            success, row, col, topIndex = self.dropOn(event)
            if success:             
                selRows = self.getSelectedRowsFast()                        

                top = selRows[0]
                # print 'top is %d'%top
                dropRow = row
                if dropRow == -1:
                    dropRow = self.rowCount()
                # print 'dropRow is %d'%dropRow
                offset = dropRow - top
                # print 'offset is %d'%offset

                for i, row in enumerate(selRows):
                    r = row + offset
                    if r > self.rowCount() or r < 0:
                        r = 0
                    self.insertRow(r)
                    # print 'inserting row at %d'%r


                selRows = self.getSelectedRowsFast()
                # print 'selected rows: %s'%selRows

                top = selRows[0]
                # print 'top is %d'%top
                offset = dropRow - top                
                # print 'offset is %d'%offset
                for i, row in enumerate(selRows):
                    r = row + offset
                    if r > self.rowCount() or r < 0:
                        r = 0

                    for j in range(self.columnCount()):
                        # print 'source is (%d, %d)'%(row, j)
                        # print 'item text: %s'%self.item(row,j).text()
                        source = QTableWidgetItem(self.item(row, j))
                        # print 'dest is (%d, %d)'%(r,j)
                        self.setItem(r, j, source)

                # Why does this NOT need to be here?
                # for row in reversed(selRows):
                    # self.removeRow(row)

                event.accept()

        else:
            QTableView.dropEvent(event)                

    def getSelectedRowsFast(self):
        selRows = []
        for item in self.selectedItems():
            
            item
            
            if item.row() not in selRows:
                selRows.append(item.row())
        return selRows

    def droppingOnItself(self, event, index):
        dropAction = event.dropAction()

        if self.dragDropMode() == QAbstractItemView.InternalMove:
            dropAction = Qt.MoveAction

        if event.source() == self and event.possibleActions() & Qt.MoveAction and dropAction == Qt.MoveAction:
            selectedIndexes = self.selectedIndexes()
            child = index
            #while child.checkExpression() and child != self.rootIndex():
            while child.isValid() and child != self.rootIndex():
                if child in selectedIndexes:
                    return True
                child = child.parent()

        return False

    def dropOn(self, event):
        if event.isAccepted():
            return False, None, None, None

        index = QModelIndex()
        row = -1
        col = -1

        if self.viewport().rect().contains(event.pos()):
            index = self.indexAt(event.pos())
            #if not index.checkExpression() or not self.visualRect(index).contains(event.pos()):
            if not index.isValid() or not self.visualRect(index).contains(event.pos()):
                index = self.rootIndex()

        if self.model().supportedDropActions() & event.dropAction():
            if index != self.rootIndex():
                dropIndicatorPosition = self.position(event.pos(), self.visualRect(index), index)

                if dropIndicatorPosition == QAbstractItemView.AboveItem:
                    row = index.row()
                    col = index.column()
                    # index = index.parent()
                elif dropIndicatorPosition == QAbstractItemView.BelowItem:
                    row = index.row() + 1
                    col = index.column()
                    # index = index.parent()
                else:
                    row = index.row()
                    col = index.column()

            if not self.droppingOnItself(event, index):
                # print 'row is %d'%row
                # print 'col is %d'%col
                return True, row, col, index

        return False, None, None, None

    def position(self, pos, rect, index):
        r = QAbstractItemView.OnViewport
        margin = 2
        if pos.y() - rect.top() < margin:
            r = QAbstractItemView.AboveItem
        elif rect.bottom() - pos.y() < margin:
            r = QAbstractItemView.BelowItem 
        elif rect.contains(pos, True):
            r = QAbstractItemView.OnItem

        if r == QAbstractItemView.OnItem and not (self.model().flags(index) & Qt.ItemIsDropEnabled):
            r = QAbstractItemView.AboveItem if pos.y() < rect.center().y() else QAbstractItemView.BelowItem

        return r
    
    def handleDeleteKeyPress(self, event):
        if event.key() == Qt.Key_Delete:
            rows = self.getSelectedRowsFast()
            #test = self.selectRow()
            test1 = self.selectedItems()
            
            #for a in test1:
            #    self.removeRow(a.row())
          
            a = 0
            for row in rows:
                self.removeRow(int(row - a))
                a += 1 

class CustomMessageBoxWithDetail(QMessageBox):
    """A custom implementation derived from QMessageBox that implements resizing.
    """

    def __init__(self):
        QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

#         def resizeEvent(self, event):
#             result = super(CustomMessageBoxWithDetail, self).resizeEvent(event)
#             details_box = self.findChild(QTextEdit)
#             if details_box is not None:
#                 details_box.setFixedSize(details_box.sizeHint())
#     
#             return result

    def event(self, e):
        result = QMessageBox.event(self, e)
 
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
 
        textEdit = self.findChild(QTextEdit)
        if textEdit is not None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
 
        return result

class BaseDialog(QDialog, baseDialog):
    """The main class for all the tools.
    It has most of the functions to exchange information beetween user, tool
    and backend.

    :param str title: the name of the tool
    """
    
    def task_finished(context, params, self, successful, results):

        STEMMessageHandler.success("R Library downloaded.")
  
    def __init__(self, title, parent=None, suffix='*.tif'):
        QDialog.__init__(self, parent)
        self.dialog = baseDialog
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.process = QProcess(self)
        self.process.error.connect(self.processError)
        self.process.finished.connect(self.processFinished)

        self.setupUi(self)

        self.buttonBox.rejected.connect(self._reject)
        self.runButton.clicked.connect(self.run)
        # self.connect(self.buttonBox, SIGNAL("accepted()"), self._accept)
        self.buttonBox.helpRequested.connect(self._help)
        self.BrowseButton.clicked.connect(partial(self.browseDir, self.TextOut, suffix))
        # self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

        self.toolname = title
        self.setWindowTitle(self.toolname)
        self.setWindowModality(Qt.WindowModal)
        
        self.inlayers = {}
        self.rect_str = None
        self.mask = None
        self.overwrite = False
        self.overwrite2 = False
        self.overwrite3 = False
        
        self.fileToDelete = []
        
        self.error = None
        
        self.helpui = helpDialog()
        STEMUtils.stemMkdir()

    def write_log_message(self,message, tag, level):
        filename = 'C://temp//qgis.log'

        with open(filename, 'a') as logfile:
            logfile.write('{tag}({level}): {message}\n'.format(tag=tag, level=level, message=message))
        
        self.textBrowser.append('{tag}({level}): {message}'.format(tag=tag, level=level, message=message))


    def error_detail(self):
        # motivazione: rimosso perche` potrebbe "coprire" altri errori dietro,
        # per esempio se accade un errore durante l'estrazione di feature lidar da poligoni
#         STEMMessageHandler.warning("STEM", "Errore!", 0)
        message_box = CustomMessageBoxWithDetail()
        message_box.setWindowTitle("Errore STEM")
        message_box.setText("STEM ha riscontrato un errore durante l'esecuzione.")
        message_box.setInformativeText("Vuoi avere maggiori informazioni?")
        message_box.setDetailedText(self.error)
        message_box.setIcon(QMessageBox.Critical)
        self.error = None
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.setDefaultButton(QMessageBox.Ok)
        message_box.setEscapeButton(QMessageBox.Ok)
        ret = message_box.exec_()

    def _reject(self):
        """Function for reject button"""
        if self.process.state() != QProcess.NotRunning:
            ret = QMessageBox.warning(self, "Warning",
                                      "The command is still running. \nDo"
                                      " you want terminate it anyway?",
                                      QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return

            self.process.error.disconnect(self.processError)
            self.process.finished.disconnect(self.processFinished)
            self.stop()
        QDialog.reject(self)

    def run(self):
        """Function for accept button"""        
        #if not self.overwrite and self.TextOut.isEnabled():
        if self.TextOut.isEnabled():
            res, self.overwrite = STEMUtils.fileExists(self.TextOut.text())
            if not res: return
            
        if hasattr(self, 'TextOut2'):
            #if not self.overwrite2 and self.TextOut2.isEnabled():
            if  self.TextOut2.isEnabled():
                res, self.overwrite2 = STEMUtils.fileExists(self.TextOut2.text())
                if not res: return

        if hasattr(self, 'TextOut3'):
            #if not self.overwrite3 and self.TextOut3.isEnabled():
            if  self.TextOut3.isEnabled():
                res, self.overwrite3 = STEMUtils.fileExists(self.TextOut3.text())
                if not res: return

        errors = []
        
        e = self.check_paths_validity()
        if e:
            #errors.append('I percorsi inseriti per i file di output sono nulli o non validi:\n\n' + u'\n\n'.join([u'• '+x for x in e]))
            errors.append('I percorsi inseriti per i file di output sono nulli o non validi.\n\n') 
                        
    
        e = [] if self.local_execution() else self.check_server_paths()
        if e:
            errors.append('I seguenti path non possono essere usati per elaborazioni remote:\n\n' + u'\n\n'.join([u'• {}'.format(x) for x in e]))

        e = self.check_number_of_folds()
        if e:
            errors.append(e)
            
        e = self.check_cell_size()
            
        e = self.check_vettoriale_validazione()
        if e:
            errors.append(e)
        
        errors.extend(self.check_form_fields())

        if errors:
            QMessageBox.warning(self, "Errore", '\n\n'.join(errors))
            return

        #RETURN_STATE = 0 -> ok , -1 -> critical -> 2 -> warning
        RETURN_STATE = 0
        
        try:
            RETURN_STATE = self.onRunLocal()
            #self.onRunLocal()
        except:
             self.error = traceback.format_exc()
        finally:
            if self.error is not None:
                self.error_detail()
        
        if (RETURN_STATE == 2):
            return
        
        #self.accept()

    def check_cell_size(self):
        return ""

    def check_vettoriale_validazione(self):
        return ""

    def check_number_of_folds(self):
        return ""

    def get_input_path_fields(self):
        """Metodo astratto
        Questo metodo deve essere ridefinito nei tool,
        deve fornire la lista con i valori usati dal tool
        come path di file di input
        """
        return []
    
    def get_output_path_fields(self):
        """Metodo astratto
        Questo metodo deve essere ridefinito nei tool,
        deve fornire la lista con i valori usati dal tool
        come path di file di output
        """
        return []
    
    def check_form_fields(self):
        """Metodo astratto
        Questo metodo deve essere ridefinito nei tool,
        deve fornire la lista di errori sui campi che non
        sono verificati dalle funzioni precedenti.
        """
        return []
    
    def check_paths_validity(self):
        """Controlla se i file di input esistono e
        se i file di output sono validi.
        Ogni plugin deve indicare quali controllare"""
        errors = []
        
        for p in [x for x in self.get_input_path_fields() if x is not None]:
            if not os.path.exists(p):
                errors.append(p)
        # TextOut e` comune a tutti i plugin
        paths = [x for x in self.get_output_path_fields() if x is not None]
        if not self.TextOut.isHidden() and self.TextOut.isEnabled():
            paths.append(self.TextOut.text())
        for p in paths:
            # Controllo che esista la cartella 
            # del file di output
            if not os.path.isdir(os.path.split(p)[0]):
                errors.append(p)
                continue
            # Controllo che il path non sia una cartella
            if os.path.isdir(p):
                errors.append(p)
                continue
            
        return errors
    
    def check_server_paths(self):
        """Controlla che i path siano compatibili con l'esecuzione remota"""
        paths = self.get_input_path_fields() + self.get_output_path_fields()
        if not self.TextOut.isHidden() and self.TextOut.isEnabled():
            paths.append(self.TextOut.text())
        print('input :{}, output: {}, all: {}'.format(self.get_input_path_fields(), self.get_output_path_fields(), paths))
        errors = []
        for p in paths:
            if STEMUtils.pathClientWinToServerLinux(p, gui_warning=False) == p:
               errors.append(p) 
        return errors

    def _help(self):
        """Function for help button"""
        self.helpui.exec_()

    def _insertLoadParametersButton(self):
        self.LoadButtonIn = QPushButton()
        self.LoadButtonIn.setObjectName("btnLoadParams")
        self.horizontalLayout_input.addWidget(self.LoadButtonIn)
        self.verticalLayout_input.insertLayout(0, self.horizontalLayout_input)
        self.LoadButtonIn.setText(self.tr("", "Carica Statistiche"))
        self.LoadButtonIn.clicked.connect(self.loadReturnsAndClassfromLAS)
        

    def _insertMultipleInput(self, multi=False):
        """Function to add ListWidget where insert multiple input files name"""
        self.horizontalLayout_input = QVBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_input")
        self.label = QLabel()
        self.label.setObjectName("label")
        self.label.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.label)
        self.BaseInput = QListWidget()
        self.BaseInput.setGeometry(QRect(10, 30, 341, 211))
        self.BaseInput.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.BaseInput.setObjectName("BaseInput")
        self.BaseInput.setDragDropMode(QAbstractItemView.InternalMove)
        self.horizontalLayout_input.addWidget(self.BaseInput)
        self.BrowseButtonIn = QPushButton()
        self.BrowseButtonIn.setObjectName("BrowseButtonIn")
        self.horizontalLayout_input.addWidget(self.BrowseButtonIn)
        self.verticalLayout_input.insertLayout(0, self.horizontalLayout_input)
        self.label.setText(self.tr("", "Dati di input"))
        self.BrowseButtonIn.setText(self.tr("", "Sfoglia"))
        self.BrowseButtonIn.clicked.connect(partial(self.browseInFile, self.BaseInput, multi=multi,
                             filt='*'))
        
    def _insertMultipleInputTable(self):
        """Function to add ListWidget where insert multiple input file names, adds information about the value of nodata"""
        self.horizontalLayout_input = QVBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_input")
        self.label = QLabel()
        self.label.setObjectName("label")
        self.label.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.label)
        self.BaseInput = TableWidgetDragRows()
        self.BaseInput.insertColumn(0) #NAME
        self.BaseInput.insertColumn(1) #EPSG
        self.BaseInput.insertColumn(2) #NODATA
        self.BaseInput.setHorizontalHeaderLabels(['File', 'EPSG', 'Valore di nodata'])
        self.BaseInput.setGeometry(QRect(10, 30, 341, 211))
        self.BaseInput.setObjectName("BaseInputTable")
        self.BaseInput.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.BaseInput.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.BaseInput.setDragDropMode(QAbstractItemView.InternalMove)
        self.horizontalLayout_input.addWidget(self.BaseInput)
        self.BrowseButtonIn = QPushButton()
        self.BrowseButtonIn.setObjectName("BrowseButtonIn")
        self.horizontalLayout_input.addWidget(self.BrowseButtonIn)
        self.verticalLayout_input.insertLayout(0, self.horizontalLayout_input)
        self.label.setText(self.tr("", "Dati di input"))
        self.BrowseButtonIn.setText(self.tr("", "Sfoglia"))
        self.BrowseButtonIn.clicked.connect(partial(self.browseInFile, self.BaseInput, table=True,
                             filt='*'))

    def _insertFileInput(self, pos=0, multi=False,
                         filterr="LAS file (*.las *.laz)"):
        """Function to add QLineEdit and QPushButton to select the data
        outside QGIS (for example LAS files)

        :param int pos: the position of form in the input layout
        :param bool multi: True to select more files
        :param str filterr: the file to select files
        """
        self.horizontalLayout_input = QHBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_output")
        self.labelF = QLabel()
        self.labelF.setObjectName("LabelOut")
        self.labelF.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.labelF)
        self.TextIn = QLineEdit()
        self.TextIn.setObjectName("TextIn")
        self.horizontalLayout_input.addWidget(self.TextIn)
        self.BrowseButtonIn = QPushButton()
        self.BrowseButtonIn.setObjectName("BrowseButtonIn")
        self.horizontalLayout_input.addWidget(self.BrowseButtonIn)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_input)
        self.labelF.setText(self.tr("", "File LAS di input"))
        self.BrowseButtonIn.setText(self.tr("", "Sfoglia"))
        self.BrowseButtonIn.clicked.connect(partial(self.browseInFile, self.TextIn, multi=multi,
                             filt=filterr))
                             
    def _insertSecondFileInput(self, pos=0, multi=False,
                         filterr="LAS file (*.las *.laz)", label="File LAS di input"):
        """Function to add QLineEdit and QPushButton to select the data
        outside QGIS (for example LAS files)

        :param int pos: the position of form in the input layout
        :param bool multi: True to select more files
        :param str filterr: the file to select files
        """
        self.horizontalLayout_input = QHBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_output")
        self.labelF2 = QLabel()
        self.labelF2.setObjectName("LabelOut2")
        self.labelF2.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.labelF2)
        self.TextIn2 = QLineEdit()
        self.TextIn2.setObjectName("TextIn2")
        self.horizontalLayout_input.addWidget(self.TextIn2)
        self.BrowseButtonIn2 = QPushButton()
        self.BrowseButtonIn2.setObjectName("BrowseButtonIn2")
        self.horizontalLayout_input.addWidget(self.BrowseButtonIn2)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_input)
        self.labelF2.setText(self.tr("", label))
        self.BrowseButtonIn2.setText(self.tr("", "Sfoglia"))
        self.BrowseButtonIn2.clicked.connect(partial(self.browseInFile, self.TextIn2, multi=multi,
                             filt=filterr))                             
                             
    def _insertFileDtmInput(self, pos=0, multi=False,
                         filterr="DTM file (*.dtm)"):
        """Function to add QLineEdit and QPushButton to select the data
        outside QGIS (for example LAS files)

        :param int pos: the position of form in the input layout
        :param bool multi: True to select more files
        :param str filterr: the file to select files
        """
        self.horizontalLayout_input = QHBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_output")
        self.labelF_Dtm = QLabel()
        self.labelF_Dtm.setObjectName("LabelOut_Dtm")
        self.labelF.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.labelF_Dtm)
        self.TextIn_Dtm = QLineEdit()
        self.TextIn_Dtm.setObjectName("TextIn_Dtm")
        self.horizontalLayout_input.addWidget(self.TextIn_Dtm)
        self.BrowseButtonIn_Dtm = QPushButton()
        self.BrowseButtonIn_Dtm.setObjectName("BrowseButtonIn_Dtm")
        self.horizontalLayout_input.addWidget(self.BrowseButtonIn_Dtm)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_input)
        self.labelF_Dtm.setText(self.tr("", "File DTM di input"))
        self.BrowseButtonIn_Dtm.setText(self.tr("", "Sfoglia"))
        self.BrowseButtonIn_Dtm.clicked.connect(partial(self.browseInFile, self.TextIn_Dtm, multi=multi,
                             filt=filterr))                                                          

    def _insertDirectory(self, label, pos=0):
        self.horizontalLayout_input = QHBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_output")
        self.labelD = QLabel()
        self.labelD.setObjectName("LabelOut")
        self.labelD.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.labelD)
        self.TextDir = QLineEdit()
        self.TextDir.setObjectName("TextDir")
        self.horizontalLayout_input.addWidget(self.TextDir)
        self.BrowseButtonIn = QPushButton()
        self.BrowseButtonIn.setObjectName("BrowseButtonIn")
        self.horizontalLayout_input.addWidget(self.BrowseButtonIn)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_input)
        self.labelD.setText(self.tr("", label))
        self.BrowseButtonIn.setText(self.tr("", "Sfoglia"))
        self.BrowseButtonIn.clicked.connect(partial(self.browseInFile, self.TextDir, dire=True))

    def _insertDirectory2(self, label, pos=0):
        self.horizontalLayout_input = QHBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_output")
        self.labelD2 = QLabel()
        self.labelD2.setObjectName("LabelOut")
        self.labelD2.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.labelD2)
        self.TextDir2 = QLineEdit()
        self.TextDir2.setObjectName("TextDir")
        self.horizontalLayout_input.addWidget(self.TextDir2)
        self.BrowseButtonIn2 = QPushButton()
        self.BrowseButtonIn2.setObjectName("BrowseButtonIn")
        self.horizontalLayout_input.addWidget(self.BrowseButtonIn2)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_input)
        self.labelD2.setText(self.tr("", label))
        self.BrowseButtonIn2.setText(self.tr("", "Sfoglia"))
        self.BrowseButtonIn2.clicked.connect(partial(self.browseInFile, self.TextDir2, dire=True))

    def _insertDirectory3(self, label, pos=0):
        self.horizontalLayout_input = QHBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_output")
        self.labelD3 = QLabel()
        self.labelD3.setObjectName("LabelOut")
        self.labelD3.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.labelD3)
        self.TextDir3 = QLineEdit()
        self.TextDir3.setObjectName("TextDir")
        self.horizontalLayout_input.addWidget(self.TextDir3)
        self.BrowseButtonIn3 = QPushButton()
        self.BrowseButtonIn3.setObjectName("BrowseButtonIn")
        self.horizontalLayout_input.addWidget(self.BrowseButtonIn3)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_input)
        self.labelD3.setText(self.tr("", label))
        self.BrowseButtonIn3.setText(self.tr("", "Sfoglia"))
        self.BrowseButtonIn3.clicked.connect(partial(self.browseInFile, self.TextDir3, dire=True))

    def _insertSingleInput(self, label="Dati di input"):
        """Function to add ComboBox Widget where insert a single input file

        :param str label: the label of form
        """
        self.horizontalLayout_input = QHBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_input")
        self.label = QLabel()
        self.label.setObjectName("label")
        self.label.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.label)
        self.BaseInput = QComboBox()
        #self.BaseInput.setEditable(True)
        self.BaseInput.setObjectName("BaseInput")
        self.horizontalLayout_input.addWidget(self.BaseInput)
        self.verticalLayout_input.insertLayout(0, self.horizontalLayout_input)
        self.verticalLayout_input
        self.label.setText(self.tr("", label))

    def _insertSecondSingleInput(self, pos=1, label="Dati di input"):
        """Function to add a second ComboBox Widget where insert a single
        input file

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_input2 = QHBoxLayout()
        self.horizontalLayout_input2.setObjectName("horizontalLayout_input2")
        self.label2 = QLabel()
        self.label2.setObjectName("label2")
        self.label2.setWordWrap(True)
        self.horizontalLayout_input2.addWidget(self.label2)
        self.BaseInput2 = QComboBox()
        #self.BaseInput2.setEditable(True)
        self.BaseInput2.setObjectName("BaseInput2")
        self.horizontalLayout_input2.addWidget(self.BaseInput2)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_input2)
        self.label2.setText(self.tr("", label))
        
    def _insertThirdSingleInput(self, pos=1, label="Dati di input"):
        """Function to add a second ComboBox Widget where insert a single
        input file

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_input3 = QHBoxLayout()
        self.horizontalLayout_input3.setObjectName("horizontalLayout_input3")
        self.label3 = QLabel()
        self.label3.setObjectName("label3")
        self.label3.setWordWrap(True)
        self.horizontalLayout_input3.addWidget(self.label3)
        self.BaseInput3 = QComboBox()
        #self.BaseInput3.setEditable(True)
        self.BaseInput3.setObjectName("BaseInput3")
        self.horizontalLayout_input3.addWidget(self.BaseInput3)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_input3)
        self.label3.setText(self.tr("", label))        

    def _insertFileInputOption(self, label, pos=0,
                               filt="LAS file (*.las *.laz)"):
        """Function to add a second output

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_inputopt = QHBoxLayout()
        self.horizontalLayout_inputopt.setObjectName("horizontalLayout_inputopt")
        self.labelFO = QLabel()
        self.labelFO.setObjectName("labelFO")
        self.labelFO.setWordWrap(True)
        self.horizontalLayout_inputopt.addWidget(self.labelFO)
        self.TextInOpt = QLineEdit()
        self.TextInOpt.setObjectName("TextInOpt")
        self.horizontalLayout_inputopt.addWidget(self.TextInOpt)
        self.BrowseButtonInOpt = QPushButton()
        self.BrowseButtonInOpt.setObjectName("BrowseButtonIn")
        self.horizontalLayout_inputopt.addWidget(self.BrowseButtonInOpt)
        self.verticalLayout_options.insertLayout(pos, self.horizontalLayout_inputopt)
        self.labelFO.setText(self.tr("", label))
        self.BrowseButtonInOpt.setText(self.tr("", "Sfoglia"))
        self.BrowseButtonInOpt.clicked.connect(partial(self.browseInFile, self.TextInOpt, filt))

    def _insertLayerChoose(self, pos=2):
        """Function to add a LineEdit Widget for the layers list

        :param int pos: the position of form in the input layout
        """
        self.horizontalLayout_layer = QHBoxLayout()
        self.horizontalLayout_layer.setObjectName("horizontalLayout_layer")
        self.label_layer = QLabel()
        self.label_layer.setObjectName("label_layer")
        self.horizontalLayout_layer.addWidget(self.label_layer)
        self.layer_list = QComboBox()
        self.layer_list.setObjectName("layer_list")
        self.horizontalLayout_layer.addWidget(self.layer_list)
        self.verticalLayout_input.insertLayout(pos, self.horizontalLayout_layer)
#        self.layer_list.setToolTip(self.tr("", "Inserire i numeri dei "
#                                            "layer da utilizzare, separati da\n"
#                                            " una virgola e partendo da 1 (se\n"
#                                            " lasciato vuoto considererà tutti"
#                                            " i layer"))
        self.label_layer.setText(self.tr("", "Selezionare una sola banda"))
        
    def _insertSecondLayerChoose(self, pos=2):
        """Function to add a LineEdit Widget for the layers list

        :param int pos: the position of form in the input layout
        """
        self.horizontalLayout_layer2 = QHBoxLayout()
        self.horizontalLayout_layer2.setObjectName("horizontalLayout_layer2")
        self.label_layer2 = QLabel()
        self.label_layer2.setObjectName("label_layer2")
        self.horizontalLayout_layer2.addWidget(self.label_layer2)
        self.layer_list2 = QComboBox()
        self.layer_list2.setObjectName("layer_list2")
        self.horizontalLayout_layer2.addWidget(self.layer_list2)
        self.verticalLayout_input.insertLayout(pos, self.horizontalLayout_layer2)
#        self.layer_list.setToolTip(self.tr("", "Inserire i numeri dei "
#                                            "layer da utilizzare, separati da\n"
#                                            " una virgola e partendo da 1 (se\n"
#                                            " lasciato vuoto considererà tutti"
#                                            " i layer"))
        self.label_layer2.setText(self.tr("", "Selezionare una sola banda"))
        
    def _insertThirdLayerChoose(self, pos=2):
        """Function to add a LineEdit Widget for the layers list

        :param int pos: the position of form in the input layout
        """
        self.horizontalLayout_layer3 = QHBoxLayout()
        self.horizontalLayout_layer3.setObjectName("horizontalLayout_layer3")
        self.label_layer3 = QLabel()
        self.label_layer3.setObjectName("label_layer3")
        self.horizontalLayout_layer3.addWidget(self.label_layer3)
        self.layer_list3 = QComboBox()
        self.layer_list3.setObjectName("layer_list3")
        self.horizontalLayout_layer3.addWidget(self.layer_list3)
        self.verticalLayout_input.insertLayout(pos, self.horizontalLayout_layer3)
#        self.layer_list.setToolTip(self.tr("", "Inserire i numeri dei "
#                                            "layer da utilizzare, separati da\n"
#                                            " una virgola e partendo da 1 (se\n"
#                                            " lasciato vuoto considererà tutti"
#                                            " i layer"))
        self.label_layer3.setText(self.tr("", "Selezionare una sola banda"))        


    def _insertLASReturnChooseCheckBox(self, label="Selezionare il ritorno da "
                                               "utilizzare",
                                   combo=True, pos=2):
        """Function to insert a CheckBox

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        :param bool combo: boolean to choose if the CheckBox should be
                           checkable or not
        """
        self.horizontalLayout_return = QHBoxLayout()
        self.horizontalLayout_return.setObjectName("horizontalLayout_Return")
        self.label_return = QLabel()
        self.label_return.setWordWrap(True)
        self.label_return.setObjectName("label_Return")
        self.horizontalLayout_return.addWidget(self.label_return)
        if combo:
            self.return_list = CheckableComboBox()
        else:
            self.return_list = QComboBox()
        self.return_list.setObjectName("return_list")
        self.horizontalLayout_return.addWidget(self.return_list)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_return)
        self.label_return.setText(self.tr("", label))

    def _insertLASClassChooseCheckBox(self, label="Selezionare la classe da "
                                               "utilizzare",
                                   combo=True, pos=2):
        """Function to insert a CheckBox

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        :param bool combo: boolean to choose if the CheckBox should be
                           checkable or not
        """
        self.horizontalLayout_class = QHBoxLayout()
        self.horizontalLayout_class.setObjectName("horizontalLayout_Class")
        self.label_class = QLabel()
        self.label_class.setWordWrap(True)
        self.label_class.setObjectName("label_Class")
        self.horizontalLayout_class.addWidget(self.label_class)
        if combo:
            self.class_list = CheckableComboBox()
        else:
            self.class_list = QComboBox()
        self.class_list.setObjectName("class_list")
        self.horizontalLayout_class.addWidget(self.class_list)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_class)
        self.label_class.setText(self.tr("", label))



    def _insertLayerChooseCheckBox(self, label="Selezionare le bande da "
                                               "utilizzare cliccandoci sopra",
                                   combo=True, pos=2):
        """Function to insert a CheckBox

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        :param bool combo: boolean to choose if the CheckBox should be
                           checkable or not
        """
        self.horizontalLayout_layer = QHBoxLayout()
        self.horizontalLayout_layer.setObjectName("horizontalLayout_layer")
        self.label_layer = QLabel()
        self.label_layer.setWordWrap(True)
        self.label_layer.setObjectName("label_layer")
        self.horizontalLayout_layer.addWidget(self.label_layer)
        if combo:
            self.layer_list = CheckableComboBox()
        else:
            self.layer_list = QComboBox()
        self.layer_list.setObjectName("layer_list")
        self.horizontalLayout_layer.addWidget(self.layer_list)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_layer)
        self.label_layer.setText(self.tr("", label))

    def _insertLayerChooseCheckBox2Options(self, label, combo=True, pos=3):
        """Function to insert a second CheckBox

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        :param bool combo: boolean to choose if the CheckBox should be
                           checkable or not
        """
        self.horizontalLayout_layer2 = QHBoxLayout()
        self.horizontalLayout_layer2.setObjectName("horizontalLayout_layer2")
        self.label_layer2 = QLabel()
        self.label_layer2.setWordWrap(True)
        self.label_layer2.setObjectName("label_layer2")
        self.horizontalLayout_layer2.addWidget(self.label_layer2)
        if combo:
            self.layer_list2 = CheckableComboBox()
        else:
            self.layer_list2 = QComboBox()
        self.layer_list2.setObjectName("layer_list2")
        self.horizontalLayout_layer2.addWidget(self.layer_list2)
        self.verticalLayout_options.insertLayout(pos,
                                               self.horizontalLayout_layer2)
        self.label_layer2.setText(self.tr("", label))
        
    def _insertLayerChooseCheckBox2(self, label, combo=True, pos=3):
        """Function to insert a second CheckBox

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        :param bool combo: boolean to choose if the CheckBox should be
                           checkable or not
        """
        self.horizontalLayout_layer2 = QHBoxLayout()
        self.horizontalLayout_layer2.setObjectName("horizontalLayout_layer2")
        self.label_layer2 = QLabel()
        self.label_layer2.setWordWrap(True)
        self.label_layer2.setObjectName("label_layer2")
        self.horizontalLayout_layer2.addWidget(self.label_layer2)
        if combo:
            self.layer_list2 = CheckableComboBox()
        else:
            self.layer_list2 = QComboBox()
        self.layer_list2.setObjectName("layer_list2")
        self.horizontalLayout_layer2.addWidget(self.layer_list2)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_layer2)
        self.label_layer2.setText(self.tr("", label))

    def _insertLayerChooseCheckBox3(self, label, combo=True, pos=4):
        """Function to insert a third CheckBox

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        :param bool combo: boolean to choose if the CheckBox should be
                           checkable or not
        """
        self.horizontalLayout_layer3 = QHBoxLayout()
        self.horizontalLayout_layer3.setObjectName("horizontalLayout_layer3")
        self.label_layer3 = QLabel()
        self.label_layer3.setWordWrap(True)
        self.label_layer3.setObjectName("label_layer3")
        self.horizontalLayout_layer3.addWidget(self.label_layer3)
        if combo:
            self.layer_list3 = CheckableComboBox()
        else:
            self.layer_list3 = QComboBox()
        self.layer_list3.setObjectName("layer_list3")
        self.horizontalLayout_layer3.addWidget(self.layer_list3)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_layer3)
        self.label_layer3.setText(self.tr("", label))

    def _insertLayerChooseCheckBox4(self, label, pos=5, combo=True):
        """Function to insert a fourth CheckBox

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        :param bool combo: boolean to choose if the CheckBox should be
                           checkable or not
        """
        self.horizontalLayout_layer4 = QHBoxLayout()
        self.horizontalLayout_layer4.setObjectName("horizontalLayout_layer4")
        self.label_layer4 = QLabel()
        self.label_layer4.setWordWrap(True)
        self.label_layer4.setObjectName("label_layer4")
        self.horizontalLayout_layer4.addWidget(self.label_layer4)
        if combo:
            self.layer_list4 = CheckableComboBox()
        else:
            self.layer_list4 = QComboBox()
        self.layer_list4.setObjectName("layer_list4")
        self.horizontalLayout_layer4.addWidget(self.layer_list4)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_layer4)
        self.label_layer4.setText(self.tr("", label))



    def _insertLocalLayerChooseCheckBox69(self, label, combo=True, pos=3):
        """Function to insert a second CheckBox

        :param int pos: the position of form in the input layout
        :param str label: the label of form
        :param bool combo: boolean to choose if the CheckBox should be
                           checkable or not
        """
        self.horizontalLayout_layer69 = QHBoxLayout()
        self.horizontalLayout_layer69.setObjectName("horizontalLayout_layer2")
        self.label_layer69 = QLabel()
        self.label_layer69.setWordWrap(True)
        self.label_layer69.setObjectName("label_layer2")
        self.horizontalLayout_layer69.addWidget(self.label_layer69)
        if combo:
            self.layer_list69 = CheckableComboBox()
        else:
            self.layer_list69 = QComboBox()
        self.layer_list69.setObjectName("layer_list2")
        self.horizontalLayout_layer69.addWidget(self.layer_list69)
        self.verticalLayout_options.insertLayout(pos,
                                               self.horizontalLayout_layer69)
        self.label_layer69.setText(self.tr("", label))
        
        
    def _insertMethod(self, methods, label, posnum):
        """Function to add ComboBox Widget

        :param list methods: list of method to add to the ComboBox
        :param int pos: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_method = QHBoxLayout()
        self.horizontalLayout_method.setObjectName("horizontalLayout_method")
        self.labelmethod = QLabel()
        self.labelmethod.setObjectName("labelmethod")
        self.labelmethod.setWordWrap(True)
        self.horizontalLayout_method.addWidget(self.labelmethod)
        self.MethodInput = QComboBox()
        self.MethodInput.setEnabled(True)
        self.MethodInput.setObjectName("MethodInput")
        self.horizontalLayout_method.addWidget(self.MethodInput)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_method)
        [self.MethodInput.addItem(m) for m in methods]
        self.labelmethod.setText(self.tr("", label))

    def _insertMethodInput(self, methods, label, posnum):
        """Function to add ComboBox Widget

        :param list methods: list of method to add to the ComboBox
        :param int pos: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_method = QHBoxLayout()
        self.horizontalLayout_method.setObjectName("horizontalLayout_method")
        self.labelmethod = QLabel()
        self.labelmethod.setObjectName("labelmethod")
        self.labelmethod.setWordWrap(True)
        self.horizontalLayout_method.addWidget(self.labelmethod)
        self.MethodInput = QComboBox()
        self.MethodInput.setEnabled(True)
        self.MethodInput.setObjectName("MethodInput")
        self.horizontalLayout_method.addWidget(self.MethodInput)
        self.verticalLayout_input.insertLayout(posnum,
                                                 self.horizontalLayout_method)
        [self.MethodInput.addItem(m) for m in methods]
        self.labelmethod.setText(self.tr("", label))
        
        
    def _insertThresholdDouble(self, minn, maxx, step, posnum, deci=2,
                               label="Seleziona il threshold da utilizzare"):
        """Function to add SpinBox Widget for decimal number

        :param float minn: minimum value for SpinBox
        :param float maxx: maximum value for SpinBox
        :param float step: the value for step in the SpinBox
        :param int posnum: the position of form in the input layout
        :param deci int: the number of decimal to use
        :param str label: the label of form
        """
        self.horizontalLayout_thred = QHBoxLayout()
        self.horizontalLayout_thred.setObjectName("horizontalLayout_thred")
        self.LabelThred = QLabel()
        self.LabelThred.setObjectName("LabelThred")
        self.LabelThred.setWordWrap(True)
        self.horizontalLayout_thred.addWidget(self.LabelThred)
        self.thresholdd = QDoubleSpinBox()
        self.thresholdd.setDecimals(deci)
        self.thresholdd.setObjectName("thresholdd")
        self.thresholdd.setRange(minn, maxx)
        self.thresholdd.setSingleStep(step)
        self.horizontalLayout_thred.addWidget(self.thresholdd)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_thred)
        self.LabelThred.setText(self.tr("", label))

    def _insertSecondThresholdDouble(self, minn, maxx, step, posnum, deci=2,
                                     label="Seleziona il threshold da utilizzare"):
        """Function to add second SpinBox Widget for decimal number

        :param float minn: minimum value for SpinBox
        :param float maxx: maximum value for SpinBox
        :param float step: the value for step in the SpinBox
        :param int posnum: the position of form in the input layout
        :param deci int: the number of decimal to use
        :param str label: the label of form
        """
        self.horizontalLayout_thred2 = QHBoxLayout()
        self.horizontalLayout_thred2.setObjectName("horizontalLayout_thred2")
        self.LabelThred2 = QLabel()
        self.LabelThred2.setObjectName("LabelThred2")
        self.LabelThred2.setWordWrap(True)
        self.horizontalLayout_thred2.addWidget(self.LabelThred2)
        self.thresholdd2 = QDoubleSpinBox()
        self.thresholdd2.setDecimals(deci)
        self.thresholdd2.setObjectName("thresholdd")
        self.thresholdd2.setRange(minn, maxx)
        self.thresholdd2.setSingleStep(step)
        self.horizontalLayout_thred2.addWidget(self.thresholdd2)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_thred2)
        self.LabelThred2.setText(self.tr("", label))

    def _insertThresholdInteger(self, minn, maxx, step, posnum,
                                label="Seleziona il threshold da utilizzare"):
        """Function to add SpinBox Widget for integer number

        :param int minn: minimum value for SpinBox
        :param int maxx: maximum value for SpinBox
        :param int step: the value for step in the SpinBox
        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_threi = QHBoxLayout()
        self.horizontalLayout_threi.setObjectName("horizontalLayout_threi")
        self.LabelThrei = QLabel()
        self.LabelThrei.setObjectName("LabelThrei")
        self.LabelThrei.setWordWrap(True)
        self.horizontalLayout_threi.addWidget(self.LabelThrei)
        self.thresholdi = QDoubleSpinBox()
        self.thresholdi.setObjectName("thresholdi")
        self.thresholdi.setRange(minn, maxx)
        self.thresholdi.setSingleStep(step)
        self.horizontalLayout_threi.addWidget(self.thresholdi)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_threi)
        self.LabelThrei.setText(self.tr("", label))
        
    def _insertSecondThresholdInteger(self, minn, maxx, step, posnum,
                                label="Seleziona il threshold da utilizzare"):
        self.horizontalLayout_threi2 = QHBoxLayout()
        self.horizontalLayout_threi2.setObjectName("horizontalLayout_threi2")
        self.LabelThrei2 = QLabel()
        self.LabelThrei2.setObjectName("LabelThrei2")
        self.LabelThrei2.setWordWrap(True)
        self.horizontalLayout_threi2.addWidget(self.LabelThrei2)
        self.thresholdi2 = QDoubleSpinBox()
        self.thresholdi2.setObjectName("thresholdi2")
        self.thresholdi2.setRange(minn, maxx)
        self.thresholdi2.setSingleStep(step)
        self.horizontalLayout_threi2.addWidget(self.thresholdi2)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_threi2)
        self.LabelThrei2.setText(self.tr("", label))
        
    def _insertThirdThresholdInteger(self, minn, maxx, step, posnum,
                                label="Seleziona il threshold da utilizzare"):
        self.horizontalLayout_threi3 = QHBoxLayout()
        self.horizontalLayout_threi3.setObjectName("horizontalLayout_threi3")
        self.LabelThrei3 = QLabel()
        self.LabelThrei3.setObjectName("LabelThrei3")
        self.LabelThrei3.setWordWrap(True)
        self.horizontalLayout_threi3.addWidget(self.LabelThrei3)
        self.thresholdi3 = QDoubleSpinBox()
        self.thresholdi3.setObjectName("thresholdi3")
        self.thresholdi3.setRange(minn, maxx)
        self.thresholdi3.setSingleStep(step)
        self.horizontalLayout_threi3.addWidget(self.thresholdi3)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_threi3)
        self.LabelThrei3.setText(self.tr("", label))
        
    def _insertFourthThresholdInteger(self, minn, maxx, step, posnum,
                                label="Seleziona il threshold da utilizzare"):
        self.horizontalLayout_threi4 = QHBoxLayout()
        self.horizontalLayout_threi4.setObjectName("horizontalLayout_threi4")
        self.LabelThrei4 = QLabel()
        self.LabelThrei4.setObjectName("LabelThrei4")
        self.LabelThrei4.setWordWrap(True)
        self.horizontalLayout_threi4.addWidget(self.LabelThrei4)
        self.thresholdi4 = QDoubleSpinBox()
        self.thresholdi4.setObjectName("thresholdi4")
        self.thresholdi4.setRange(minn, maxx)
        self.thresholdi4.setSingleStep(step)
        self.horizontalLayout_threi4.addWidget(self.thresholdi4)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_threi4)
        self.LabelThrei4.setText(self.tr("", label))
        
    def _insertFifthThresholdInteger(self, minn, maxx, step, posnum,
                                label="Seleziona il threshold da utilizzare"):
        self.horizontalLayout_threi5 = QHBoxLayout()
        self.horizontalLayout_threi5.setObjectName("horizontalLayout_threi5")
        self.LabelThrei5 = QLabel()
        self.LabelThrei5.setObjectName("LabelThrei5")
        self.LabelThrei5.setWordWrap(True)
        self.horizontalLayout_threi5.addWidget(self.LabelThrei5)
        self.thresholdi5 = QDoubleSpinBox()
        self.thresholdi5.setObjectName("thresholdi5")
        self.thresholdi5.setRange(minn, maxx)
        self.thresholdi5.setSingleStep(step)
        self.horizontalLayout_threi5.addWidget(self.thresholdi5)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_threi5)
        self.LabelThrei5.setText(self.tr("", label))
        
    def _insertSixthThresholdInteger(self, minn, maxx, step, posnum,
                                label="Seleziona il threshold da utilizzare"):
        self.horizontalLayout_threi6 = QHBoxLayout()
        self.horizontalLayout_threi6.setObjectName("horizontalLayout_threi6")
        self.LabelThrei6 = QLabel()
        self.LabelThrei6.setObjectName("LabelThrei6")
        self.LabelThrei6.setWordWrap(True)
        self.horizontalLayout_threi6.addWidget(self.LabelThrei6)
        self.thresholdi6 = QDoubleSpinBox()
        self.thresholdi6.setObjectName("thresholdi6")
        self.thresholdi6.setRange(minn, maxx)
        self.thresholdi6.setSingleStep(step)
        self.horizontalLayout_threi6.addWidget(self.thresholdi6)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_threi6)
        self.LabelThrei6.setText(self.tr("", label))        
        
    def _insertsSeventhThresholdInteger(self, minn, maxx, step, posnum,
                                label="Seleziona il threshold da utilizzare"):
        self.horizontalLayout_threi7 = QHBoxLayout()
        self.horizontalLayout_threi7.setObjectName("horizontalLayout_threi7")
        self.LabelThrei7 = QLabel()
        self.LabelThrei7.setObjectName("LabelThrei7")
        self.LabelThrei7.setWordWrap(True)
        self.horizontalLayout_threi7.addWidget(self.LabelThrei7)
        self.thresholdi7 = QDoubleSpinBox()
        self.thresholdi7.setObjectName("thresholdi7")
        self.thresholdi7.setRange(minn, maxx)
        self.thresholdi7.setSingleStep(step)
        self.horizontalLayout_threi7.addWidget(self.thresholdi7)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_threi7)
        self.LabelThrei7.setText(self.tr("", label))        

    def _insertEighthThresholdInteger(self, minn, maxx, step, posnum,
                                label="Seleziona il threshold da utilizzare"):
        self.horizontalLayout_threi8 = QHBoxLayout()
        self.horizontalLayout_threi8.setObjectName("horizontalLayout_threi8")
        self.LabelThrei8 = QLabel()
        self.LabelThrei8.setObjectName("LabelThrei8")
        self.LabelThrei8.setWordWrap(True)
        self.horizontalLayout_threi8.addWidget(self.LabelThrei8)
        self.thresholdi8 = QDoubleSpinBox()
        self.thresholdi8.setObjectName("thresholdi8")
        self.thresholdi8.setRange(minn, maxx)
        self.thresholdi8.setSingleStep(step)
        self.horizontalLayout_threi8.addWidget(self.thresholdi8)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_threi8)
        self.LabelThrei8.setText(self.tr("", label))        

    def _insertFirstLineEdit(self, label, posnum):
        """Function to add a LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit = QHBoxLayout()
        self.horizontalLayout_linedit.setObjectName("horizontalLayout_linedit")
        self.LabelLinedit = QLabel()
        self.LabelLinedit.setObjectName("LabelLinedit")
        self.LabelLinedit.setWordWrap(True)
        self.horizontalLayout_linedit.addWidget(self.LabelLinedit)
        self.Linedit = QLineEdit()
        self.Linedit.setObjectName("Linedit")
        self.horizontalLayout_linedit.addWidget(self.Linedit)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit)
        self.LabelLinedit.setText(self.tr("", label))

    def _insertSecondLineEdit(self, label, posnum):
        """Function to add a second LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit2 = QHBoxLayout()
        self.horizontalLayout_linedit2.setObjectName("horizontalLayout_linedit2")
        self.LabelLinedit2 = QLabel()
        self.LabelLinedit2.setObjectName("LabelLinedit2")
        self.LabelLinedit2.setWordWrap(True)
        self.horizontalLayout_linedit2.addWidget(self.LabelLinedit2)
        self.Linedit2 = QLineEdit()
        self.Linedit2.setObjectName("Linedit2")
        self.horizontalLayout_linedit2.addWidget(self.Linedit2)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit2)
        self.LabelLinedit2.setText(self.tr("", label))

    def _insertThirdLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit3 = QHBoxLayout()
        self.horizontalLayout_linedit3.setObjectName("horizontalLayout_linedit3")
        self.LabelLinedit3 = QLabel()
        self.LabelLinedit3.setObjectName("LabelLinedit3")
        self.LabelLinedit3.setWordWrap(True)
        self.horizontalLayout_linedit3.addWidget(self.LabelLinedit3)
        self.Linedit3 = QLineEdit()
        self.Linedit3.setObjectName("Linedit3")
        self.horizontalLayout_linedit3.addWidget(self.Linedit3)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit3)
        self.LabelLinedit3.setText(self.tr("", label))

    def _insertFourthLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit4 = QHBoxLayout()
        self.horizontalLayout_linedit4.setObjectName("horizontalLayout_linedit4")
        self.LabelLinedit4 = QLabel()
        self.LabelLinedit4.setObjectName("LabelLinedit4")
        self.LabelLinedit4.setWordWrap(True)
        self.horizontalLayout_linedit4.addWidget(self.LabelLinedit4)
        self.Linedit4 = QLineEdit()
        self.Linedit4.setObjectName("Linedit4")
        self.horizontalLayout_linedit4.addWidget(self.Linedit4)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit4)
        self.LabelLinedit4.setText(self.tr("", label))

    def _insertFifthLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit5 = QHBoxLayout()
        self.horizontalLayout_linedit5.setObjectName("horizontalLayout_linedit5")
        self.LabelLinedit5 = QLabel()
        self.LabelLinedit5.setObjectName("LabelLinedit5")
        self.LabelLinedit5.setWordWrap(True)
        self.horizontalLayout_linedit5.addWidget(self.LabelLinedit5)
        self.Linedit5 = QLineEdit()
        self.Linedit5.setObjectName("Linedit5")
        self.horizontalLayout_linedit5.addWidget(self.Linedit5)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit5)
        self.LabelLinedit5.setText(self.tr("", label))

    def _insertSixthLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit6 = QHBoxLayout()
        self.horizontalLayout_linedit6.setObjectName("horizontalLayout_linedit6")
        self.LabelLinedit6 = QLabel()
        self.LabelLinedit6.setObjectName("LabelLinedit6")
        self.LabelLinedit6.setWordWrap(True)
        self.horizontalLayout_linedit6.addWidget(self.LabelLinedit6)
        self.Linedit6 = QLineEdit()
        self.Linedit6.setObjectName("Linedit6")
        self.horizontalLayout_linedit6.addWidget(self.Linedit6)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit6)
        self.LabelLinedit6.setText(self.tr("", label))
        
    def _insertSeventhLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit7 = QHBoxLayout()
        self.horizontalLayout_linedit7.setObjectName("horizontalLayout_linedit7")
        self.LabelLinedit7 = QLabel()
        self.LabelLinedit7.setObjectName("LabelLinedit7")
        self.LabelLinedit7.setWordWrap(True)
        self.horizontalLayout_linedit7.addWidget(self.LabelLinedit7)
        self.Linedit7 = QLineEdit()
        self.Linedit7.setObjectName("Linedit7")
        self.horizontalLayout_linedit7.addWidget(self.Linedit7)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit7)
        self.LabelLinedit7.setText(self.tr("", label))
        
    def _insertEighthLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit8 = QHBoxLayout()
        self.horizontalLayout_linedit8.setObjectName("horizontalLayout_linedit8")
        self.LabelLinedit8 = QLabel()
        self.LabelLinedit8.setObjectName("LabelLinedit8")
        self.LabelLinedit8.setWordWrap(True)
        self.horizontalLayout_linedit8.addWidget(self.LabelLinedit8)
        self.Linedit8 = QLineEdit()
        self.Linedit8.setObjectName("Linedit8")
        self.horizontalLayout_linedit8.addWidget(self.Linedit8)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit8)
        self.LabelLinedit8.setText(self.tr("", label))                
        
    def _insertNinthLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit9 = QHBoxLayout()
        self.horizontalLayout_linedit9.setObjectName("horizontalLayout_linedit9")
        self.LabelLinedit9 = QLabel()
        self.LabelLinedit9.setObjectName("LabelLinedit9")
        self.LabelLinedit9.setWordWrap(True)
        self.horizontalLayout_linedit9.addWidget(self.LabelLinedit9)
        self.Linedit9 = QLineEdit()
        self.Linedit9.setObjectName("Linedit9")
        self.horizontalLayout_linedit9.addWidget(self.Linedit9)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit9)
        self.LabelLinedit9.setText(self.tr("", label))
        
    def _insertTenthLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit10 = QHBoxLayout()
        self.horizontalLayout_linedit10.setObjectName("horizontalLayout_linedit10")
        self.LabelLinedit10 = QLabel()
        self.LabelLinedit10.setObjectName("LabelLinedit10")
        self.LabelLinedit10.setWordWrap(True)
        self.horizontalLayout_linedit10.addWidget(self.LabelLinedit10)
        self.Linedit10 = QLineEdit()
        self.Linedit10.setObjectName("Linedit10")
        self.horizontalLayout_linedit10.addWidget(self.Linedit10)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit10)
        self.LabelLinedit10.setText(self.tr("", label))
        
    def _insertEleventhLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit11 = QHBoxLayout()
        self.horizontalLayout_linedit11.setObjectName("horizontalLayout_linedit11")
        self.LabelLinedit11 = QLabel()
        self.LabelLinedit11.setObjectName("LabelLinedit11")
        self.LabelLinedit11.setWordWrap(True)
        self.horizontalLayout_linedit11.addWidget(self.LabelLinedit11)
        self.Linedit11 = QLineEdit()
        self.Linedit11.setObjectName("Linedit11")
        self.horizontalLayout_linedit11.addWidget(self.Linedit11)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit11)
        self.LabelLinedit11.setText(self.tr("", label))
        
    def _insertTwelfthLineEdit(self, label, posnum):
        """Function to add a third LineEdit Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_linedit12 = QHBoxLayout()
        self.horizontalLayout_linedit12.setObjectName("horizontalLayout_linedit12")
        self.LabelLinedit12 = QLabel()
        self.LabelLinedit12.setObjectName("LabelLinedit12")
        self.LabelLinedit12.setWordWrap(True)
        self.horizontalLayout_linedit12.addWidget(self.LabelLinedit12)
        self.Linedit12 = QLineEdit()
        self.Linedit12.setObjectName("Linedit12")
        self.horizontalLayout_linedit12.addWidget(self.Linedit12)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_linedit12)
        self.LabelLinedit12.setText(self.tr("", label))        

    def _insertFirstCombobox(self, label, posnum, items=None, combo=False):
        """Function to add a ComboBox Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        :param list items: the list of elements to add in the ComboBox
        """
        self.horizontalLayout_combo = QHBoxLayout()
        self.horizontalLayout_combo.setObjectName("horizontalLayout_combo")
        self.LabelCombo = QLabel()
        self.LabelCombo.setObjectName("LabelCombo")
        self.LabelCombo.setWordWrap(True)
        self.horizontalLayout_combo.addWidget(self.LabelCombo)
        if combo:
            self.BaseInputCombo = CheckableComboBox()
        else:
            self.BaseInputCombo = QComboBox()
        self.BaseInputCombo.setEditable(True)
        self.BaseInputCombo.setObjectName("BaseInputCombo")
        self.horizontalLayout_combo.addWidget(self.BaseInputCombo)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_combo)
        if items:
            [self.BaseInputCombo.addItem(m) for m in items]
        self.LabelCombo.setText(self.tr("", label))

    def _insertSecondCombobox(self, label, posnum, items=None):
        """Function to add a second ComboBox Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        :param list items: the list of elements to add in the ComboBox"""
        self.horizontalLayout_combo2 = QHBoxLayout()
        self.horizontalLayout_combo2.setObjectName("horizontalLayout_combo2")
        self.LabelCombo2 = QLabel()
        self.LabelCombo2.setObjectName("LabelCombo2")
        self.LabelCombo2.setWordWrap(True)
        self.horizontalLayout_combo2.addWidget(self.LabelCombo2)
        self.BaseInputCombo2 = QComboBox()
        self.BaseInputCombo2.setEditable(True)
        self.BaseInputCombo2.setObjectName("BaseInputCombo2")
        self.horizontalLayout_combo2.addWidget(self.BaseInputCombo2)
        
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_combo2)
        if items:
            [self.BaseInputCombo2.addItem(m) for m in items]
        self.LabelCombo2.setText(self.tr("", label))

    def _insertThirdCombobox(self, label, posnum, items=None):
        """Function to add a third ComboBox Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        :param list items: the list of elements to add in the ComboBox
        """
        self.horizontalLayout_combo3 = QHBoxLayout()
        self.horizontalLayout_combo3.setObjectName("horizontalLayout_combo3")
        self.LabelCombo3 = QLabel()
        self.LabelCombo3.setObjectName("LabelCombo3")
        self.LabelCombo3.setWordWrap(True)
        self.horizontalLayout_combo3.addWidget(self.LabelCombo3)
        self.BaseInputCombo3 = QComboBox()
        self.BaseInputCombo3.setEditable(True)
        self.BaseInputCombo3.setObjectName("BaseInputCombo3")
        self.horizontalLayout_combo3.addWidget(self.BaseInputCombo3)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_combo3)
        if items:
            [self.BaseInputCombo3.addItem(m) for m in items]
        self.LabelCombo3.setText(self.tr("", label))

    def _insertFourthCombobox(self, label, posnum, items = None):
        """Function to add a third ComboBox Widget

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        :param list items: the list of elements to add in the ComboBox
        """
        self.horizontalLayout_combo4 = QHBoxLayout()
        self.horizontalLayout_combo4.setObjectName("horizontalLayout_combo4")
        self.LabelCombo4 = QLabel()
        self.LabelCombo4.setObjectName("LabelCombo4")
        self.LabelCombo4.setWordWrap(True)
        self.horizontalLayout_combo4.addWidget(self.LabelCombo4)
        self.BaseInputCombo4 = QComboBox()
        self.BaseInputCombo4.setEditable(True)
        self.BaseInputCombo4.setObjectName("BaseInputCombo4")
        self.horizontalLayout_combo4.addWidget(self.BaseInputCombo4)
        
        self.verticalLayout_options.insertLayout(posnum, self.horizontalLayout_combo4)
        if items:
            [self.BaseInputCombo4.addItem(m) for m in items]
        self.LabelCombo4.setText(self.tr("", label))


    def _insertSecondOutput(self, label, posnum):
        """Function to add a second output

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_output2 = QHBoxLayout()
        self.horizontalLayout_output2.setObjectName("horizontalLayout_output2")
        self.LabelOut2 = QLabel()
        self.LabelOut2.setObjectName("LabelOut")
        self.LabelOut2.setWordWrap(True)
        self.horizontalLayout_output2.addWidget(self.LabelOut2)
        self.TextOut2 = QLineEdit()
        self.TextOut2.setObjectName("TextOut2")
        self.horizontalLayout_output2.addWidget(self.TextOut2)
        self.BrowseButton2 = QPushButton()
        self.BrowseButton2.setObjectName("BrowseButton")
                                                          
        self.horizontalLayout_output2.addWidget(self.BrowseButton2)
        self.verticalLayout_output.insertLayout(posnum,
                                                self.horizontalLayout_output2)
        self.LabelOut2.setText(self.tr("", label))
                                                  


    def _insertSecondFileOutput(self, label, posnum, filt=""):
        """Function to add a second output

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_output2 = QHBoxLayout()
        self.horizontalLayout_output2.setObjectName("horizontalLayout_output2")
        self.LabelOut2 = QLabel()
        self.LabelOut2.setObjectName("LabelOut2")
        self.LabelOut2.setWordWrap(True)
        self.horizontalLayout_output2.addWidget(self.LabelOut2)
        self.TextOut2 = QLineEdit()
        self.TextOut2.setObjectName("TextOut2")
        self.horizontalLayout_output2.addWidget(self.TextOut2)
        self.BrowseButton2 = QPushButton()
        self.BrowseButton2.setObjectName("BrowseButton")
        self.BrowseButton2.setText(self.tr("", "Sfoglia"))
        self.horizontalLayout_output2.addWidget(self.BrowseButton2)
        self.verticalLayout_output.insertLayout(posnum, self.horizontalLayout_output2)
        self.LabelOut2.setText(self.tr("", label))
        self.BrowseButton2.clicked.connect(partial(self.browseDir, self.TextOut2, filt))
        
    def _insertThirdFileOutput(self, label, posnum, filt=""):
        """Function to add a second output

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_output3 = QHBoxLayout()
        self.horizontalLayout_output3.setObjectName("horizontalLayout_output3")
        self.LabelOut3 = QLabel()
        self.LabelOut3.setObjectName("LabelOut3")
        self.LabelOut3.setWordWrap(True)
        self.horizontalLayout_output3.addWidget(self.LabelOut3)
        self.TextOut3 = QLineEdit()
        self.TextOut3.setObjectName("TextOut3")
        self.horizontalLayout_output3.addWidget(self.TextOut3)
        self.BrowseButton3 = QPushButton()
        self.BrowseButton3.setObjectName("BrowseButton")
        self.BrowseButton3.setText(self.tr("", "Sfoglia"))
        self.horizontalLayout_output3.addWidget(self.BrowseButton3)
        self.verticalLayout_output.insertLayout(posnum, self.horizontalLayout_output3)
        self.LabelOut3.setText(self.tr("", label))
        self.BrowseButton3.clicked.connect(partial(self.browseDir, self.TextOut3, filt))        

    def _insertDirOutput(self, label, posnum):
        """Function to add a second output

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_output3 = QHBoxLayout()
        self.horizontalLayout_output3.setObjectName("horizontalLayout_output3")
        self.LabelOut3 = QLabel()
        self.LabelOut3.setObjectName("LabelOut3")
        self.LabelOut3.setWordWrap(True)
        self.horizontalLayout_output3.addWidget(self.LabelOut3)
        self.TextOut3 = QLineEdit()
        self.TextOut3.setObjectName("TextOut3")
        self.horizontalLayout_output3.addWidget(self.TextOut3)
        self.BrowseButton3 = QPushButton()
        self.BrowseButton3.setObjectName("BrowseButton")
        self.BrowseButton3.setText(self.tr("", "Sfoglia"))
        self.horizontalLayout_output3.addWidget(self.BrowseButton3)
        self.verticalLayout_output.insertLayout(posnum, self.horizontalLayout_output3)
        self.LabelOut3.setText(self.tr("", label))
        self.BrowseButton3.clicked.connect(partial(self.browseDir2, self.TextOut3))   
        
    def _insertTextArea(self, label, posnum):
        """Function to add a text area

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        """
        self.horizontalLayout_textarea = QHBoxLayout()
        self.horizontalLayout_textarea.setObjectName("horizontalLayout_textarea")
        self.LabelTextarea = QLabel()
        self.LabelTextarea.setWordWrap(True)
        self.LabelTextarea.setObjectName("LabelOut")
        self.horizontalLayout_textarea.addWidget(self.LabelTextarea)
        self.TextArea = QTextEdit()
        self.TextArea.setObjectName("TextArea")
        self.horizontalLayout_textarea.addWidget(self.TextArea)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_textarea)
        self.LabelTextarea.setText(self.tr("Dialog", label))

    def _insertCheckbox(self, label, posnum, state=False, output=False):
        """Function to add a QCheckBox

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        :param bool state: set True o False to che checkbox
        """
        self.horizontalLayout_checkbox = QHBoxLayout()
        self.horizontalLayout_checkbox.setObjectName("horizontalLayout_checkbox")
        self.LabelCheckbox = QLabel()
        self.LabelCheckbox.setWordWrap(True)
        self.LabelCheckbox.setObjectName("LabelCheckbox")
        self.horizontalLayout_checkbox.addWidget(self.LabelCheckbox)
        self.checkbox = QCheckBox()
        self.checkbox.setObjectName("checkbox")
        self.horizontalLayout_checkbox.addWidget(self.checkbox)
        if output:
            self.verticalLayout_output.insertLayout(posnum,
                                                    self.horizontalLayout_checkbox)
        else:
            self.verticalLayout_options.insertLayout(posnum,
                                                     self.horizontalLayout_checkbox)
        self.LabelCheckbox.setText(self.tr("Dialog", label))
        self.checkbox.setChecked(state)

    def _insertSecondCheckbox(self, label, posnum, state=False):
        """Function to add a second QCheckBox

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        :param bool state: set True o False to che checkbox
        """
        self.horizontalLayout_checkbox2 = QHBoxLayout()
        self.horizontalLayout_checkbox2.setObjectName("horizontalLayout_checkbox2")
        self.LabelCheckbox2 = QLabel()
        self.LabelCheckbox2.setWordWrap(True)
        self.LabelCheckbox2.setObjectName("LabelCheckbox2")
        self.horizontalLayout_checkbox2.addWidget(self.LabelCheckbox2)
        self.checkbox2 = QCheckBox()
        self.checkbox2.setObjectName("checkbox2")
        self.horizontalLayout_checkbox2.addWidget(self.checkbox2)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_checkbox2)
        self.LabelCheckbox2.setText(self.tr("Dialog", label))
        self.checkbox2.setChecked(state)

    def _insertThirdCheckbox(self, label, posnum, state=False):
        """Function to add a third QCheckBox

        :param int posnum: the position of form in the input layout
        :param str label: the label of form
        :param bool state: set True o False to che checkbox
        """
        self.horizontalLayout_checkbox3 = QHBoxLayout()
        self.horizontalLayout_checkbox3.setObjectName("horizontalLayout_checkbox3")
        self.LabelCheckbox3 = QLabel()
        self.LabelCheckbox3.setWordWrap(True)
        self.LabelCheckbox3.setObjectName("LabelCheckbox3")
        self.horizontalLayout_checkbox3.addWidget(self.LabelCheckbox3)
        self.checkbox3 = QCheckBox()
        self.checkbox3.setObjectName("checkbox3")
        self.horizontalLayout_checkbox3.addWidget(self.checkbox3)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_checkbox3)
        self.LabelCheckbox3.setText(self.tr("Dialog", label))
        self.checkbox3.setChecked(state)

    def _insertSingleInputOption(self, pos, label="Dati di input"):
        """Function to add ComboBox Widget where insert a single input file"""
        self.horizontalLayout_inputOpt = QHBoxLayout()
        self.horizontalLayout_inputOpt.setObjectName("horizontalLayout_inputOpt")
        self.labelOpt = QLabel()
        self.labelOpt.setObjectName("labelOpt")
        self.labelOpt.setWordWrap(True)
        self.horizontalLayout_inputOpt.addWidget(self.labelOpt)
        self.BaseInputOpt = QComboBox()
        self.BaseInputOpt.setEditable(True)
        self.BaseInputOpt.setObjectName("BaseInputOpt")
        self.horizontalLayout_inputOpt.addWidget(self.BaseInputOpt)
        self.verticalLayout_options.insertLayout(pos, self.horizontalLayout_inputOpt)
        self.labelOpt.setText(self.tr("", label))

    def _checkExtention(self, out, ext, remove=True):
        """Function to add extention if it was not set

        :param str out: the name to check
        :param str ext: the prefix to add if missing
        :param bool remove: if True remove the file is it exist
        """
        if not out.endswith(ext):
            out += ext
        if os.path.exists(out):
            STEMUtils.removeFiles(out)
        return out

    def processError(self, error):
        """"""
        self.processError.emit(error)

    def processFinished(self, exitCode, status):
        """"""
        self.processFinished.emit(exitCode, status)

    # enables the OK button
    def enableRun(self, enable=True):
        """Set to true the OK button

        :param bool enable: Value to set
        """
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    def cutInput(self, inp, source, typ, inverse=False, local=True):
        """Cut the input data according to a bounding box or a vector geometry

        :param str inp: the name of input data
        :param str source: the full path to source data
        :param str typ: the type of data, it should be raster, image, vector
        :param bool inverse: if True create an inverse mask
        :param bool local: if True it use the local disk for the cut info
        """
        self.mapDisplay()
        mask = STEMSettings.value("mask", "")
        bbox = self.QGISextent.isChecked()
        mask_inverse = None
        if not bbox and not mask:
            return False, False, False
        if bbox and mask:
            STEMMessageHandler.error("Sono state impostate sia una maschera "
                                     "vettoriale sia una estensione di QGIS. "
                                     "Si prega di rimuoverne una delle due")
            return False, False, False
        if mask:
            mask_inverse = inverse_mask()
        if local:
            path = tempfile.gettempdir()
        else:
            # Esecuzione sul server, ma il file viene generato sul client
            # Quindi bisogna usare un path accessibile a server e client

            # soluzione temporanea: scelgo il path locale del primo mapping definito dall'utente
            # TODO: aggiungere alla tabella un radio button per scegliere la cartella dei file temporanei
            
            try:
                path = STEMUtils.get_temp_dir()
            except:
                STEMMessageHandler.error("È necessario configurare almeno un mapping fra le "
                                         "risorse locali e remote")
                return False, False, False
        outname = "stem_cut_{name}".format(name=inp)
        out = os.path.join(path, outname)
        PIPE = subprocess.PIPE
        if mask_inverse:            
            if typ == 'raster' or typ == 'image':
                raster = gdal_stem.convertGDAL()
                raster.initialize([source], out)
                raster.write(leave_output=True)
                if bbox:
                    raster.cutInputInverse(bbox=bbox)
                elif mask:
                    raster.cutInputInverse(erase=mask)
                else:
                    return False, False, False
            elif typ == 'vector':
                out = self._checkExtention(out, '.shp')
                vector = gdal_stem.infoOGR()
                vector.initialize(source)
                if bbox:
                    vector.cutInputInverse(out, bbox=bbox)
                elif mask:
                    vector.cutInputInverse(out, erase=mask)
                else:
                    return False, False, False
        else:
            if typ == 'raster' or typ == 'image':
                #if os.path.exists(out):
                #    os.remove(out) # Errore: file in uso da un altro processo
                i = 0
                out_new = out
                while os.path.exists(out_new):
                    # Si cerca di rimuovere il vecchio file temporaneo,
                    # se non e` possibile si usa un altro nome.
                    try:
                        os.remove(out_new)
                    except:
                        out_new = '{}{}'.format(out, i)
                        i += 1
                out = out_new
                if bbox:
                    com = ['gdal_translate', source, out, '-projwin']
                    com.extend(self.rect_str)
                elif mask:
                    com = ['gdalwarp', '-cutline', mask, '-crop_to_cutline',
                           '-overwrite', source, out]
                else:
                    return False, False, False
            elif typ == 'vector':
                out = self._checkExtention(out, '.shp')
                com = ['ogr2ogr']
                if bbox:
                    com.append('-clipsrc')
                    com.extend(self.rect_str)
                elif mask:
                    com.append('-clipsrc')
                    com.append('{bbox}'.format(bbox=mask))
                else:
                    return False, False, False
                com.extend([out, source])

            runcom = subprocess.Popen(com, stdin=PIPE, stdout=PIPE,
                                      stderr=PIPE)
            log, err = runcom.communicate()
            if runcom.returncode != 0:
                STEMMessageHandler.error("Errore eseguendo il ritaglio del "
                                         "file di input. Errore eseguendo il "
                                         "comando {err}".format(err=err))
        return outname.strip(), out, mask

    def local_execution(self):
        return self.LocalCheck.isChecked()

    def cutInputMulti(self, inp, source, local=True):
        """Cut multiple data according to a bounding box or a vector geometry

        :param str inp: the name of input data
        :param str source: the full path to source data
        :param str typ: the type of data, it should be raster, image, vector
        :param bool local: if True it use the local disk for the cut info
        """
        if len(inp) != len(source):
            STEMMessageHandler.error("Errore durante il ritaglio di più immagini")
        newinp = []
        newsource = []
        for n in range(len(inp)):
            typ = STEMUtils.checkMultiRaster(source[n])
            newn, news, newm = self.cutInput(inp[n], source[n], typ,
                                             local=local)
            if not newn:
                return False, False
            else:
                newinp.append(newn)
                newsource.append(news)
        return newinp, newsource

    def mapDisplay(self):
        """Return the bounding box of QGIS map display"""
        #render = self.iface.context()
        #rect = render.extent()
        rect = self.iface.mapCanvas().extent()
        self.rect_str = [str(rect.xMinimum()), str(rect.yMaximum()),
                         str(rect.xMaximum()), str(rect.yMinimum())]

    def onRunLocal(self):
        """Metodo astratto
        Function to run the command locally, redefined in each module"""
        pass

    def onRunServer(self):
        """Function to run the command on the server, not yet developed"""
        STEMMessageHandler.warning("Esegui sul Server",
                                   "Opzione non ancora implementata")

    def stop(self):
        """Stop the command execution"""
        self.enableRun(True)
        self.setCursor(Qt.ArrowCursor)
        self.process.kill()

    def chooseDirectory(self, line, caption):
        """Function to select a directory

        :param obj line: the QLineEdit object to update
        """
        mydir = QFileDialog.getExistingDirectory(parent=None,
                                                 caption=caption, directory="")
        if os.path.exists(mydir):
            line.setText(mydir)
            return

    def loadReturnsAndClassfromLAS(self,b):
        
        import csv
        import processing
        
        
        source = self.TextIn.text()
        
        if not os.path.exists(source) or source == "":
            QMessageBox.warning(self, "Errore nei parametri",
                                "File LAS non impostato correttamente")
            return
        
        
        out_ritorni = source + "_ritorni.csv"
        out_classi = source + "_classi.csv"
        
        ###################### R script here ##############################
        processing.run("r:elenco_ritorni_classi", { 'FileLas' : source,'Ritorni' : out_ritorni, 'Classi' : out_classi})
        ###################################################################

        
        lista_ritorni = []
        
        with open(out_ritorni, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            
            line_count = 0
            
            lista_ritorni = []
            
            for row in spamreader:
               
                if line_count == 0:
                    lista_ritorni.append("")
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    
                   # lista_ritorni.append(row[1]) <- vecchia versione LIDR 
                    lista_ritorni.append(row[0])
                    #print(f'\t{row[0]} works in the {row[1]} department.')
                    line_count += 1
            
        #try:
        #    self.BaseInputCombo.clear()
      
        #    for x in lista_ritorni:
        #        self.BaseInputCombo.addItem(x)
        #except:
        #    print("")        
            
            
        self.return_list.clear()
      
        for x in lista_ritorni:
            self.return_list.addItem(x)
        
                      
        lista_classi = []
                
        with open(out_classi, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            
            line_count = 0
            
            for row in spamreader:
               
                if line_count == 0:
                    #print(f'Column names are {", ".join(row)}')
                    #self.BaseInputCombo2.addItem("")
                    lista_classi.append("")
                    line_count += 1
                else:
                    #self.BaseInputCombo2.addItem(row[1])
                    #lista_classi.append(row[1]) <- vecchio LIDR
                    lista_classi.append(row[0])
                    
                    #print(f'\t{row[0]} works in the {row[1]} department.')
                    line_count += 1
      
     
         #try:
         #   self.BaseInputCombo2.clear()
      
         #   for x in lista_classi:
         #       self.BaseInputCombo2.addItem(x)
        #except:
        #    print("")        
            
            
        self.class_list.clear()
      
        for x in lista_classi:
            self.class_list.addItem(x)
        

    def browseInFile(self, line, filt="LAS file (*.las *.laz)", multi=False,
                     dire=False, table=False):
        """Function to select existing file in a directory

        :param obj line: the QLineEdit object to update
        :param str filt: a string with the filter of directory
        :param bool multi: True to select more files
        :param bool dire: True to select a directory instead a file
        """
        if table:
            mydir, __ = QFileDialog.getOpenFileNames(parent=None, filter=filt,
                                                 caption="Selezionare i file "
                                                 "di input", directory=STEMSettings.restoreLastDir(line, self.toolname))
            position = self.BaseInput.rowCount()
            for fil in mydir:
                if os.path.exists(fil):
                    STEMSettings.saveLastDir(line, fil, self.toolname)
     
                    line.insertRow(position)
                    line.setItem(position, 0, QTableWidgetItem(fil))
                    try:
                        rast = gdal.Open(fil)
                        #band = rast.GetRasterBand(1)
                        #nodata = band.GetNoDataValue()
                        #line.setItem(position, 1, QTableWidgetItem(str(nodata)))
                        
                        import osr
                        
                        proj = osr.SpatialReference(wkt=rast.GetProjection())
                        epsg = "EPSG:" + (proj.GetAttrValue('AUTHORITY',1))
                        
                        try:
                            resolution_list=[]
                            resolution_list = [self.layer_list2.itemText(i) for i in range(self.layer_list2.count())]
         
                            resolution_list.append(str("{:.3f}".format(rast.GetGeoTransform()[1])))

                            self.layer_list2.clear()
                            for res in set(resolution_list):
                                self.layer_list2.addItem(res)
                        except:
                            resolution_list=[]
                            
                        item = QTableWidgetItem(epsg)
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        line.setItem(position, 1, item)
                        
                        #table.setItem(position, 1, QTableWidgetItem((epsg)))
                    except:
                        item = QTableWidgetItem("Non disponibile")
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        line.setItem(position, 1, item)
                        
                        #table.setItem(position, 1, QTableWidgetItem("Non disponibile"))
                  
                    try:
                        rast = gdal.Open(fil)
                        band = rast.GetRasterBand(1)
                        nodata = band.GetNoDataValue()
                        
                        item = QTableWidgetItem(str(nodata))
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        line.setItem(position, 2, item)
                        
                        #table.setItem(position, 2, QTableWidgetItem(str(nodata)))
                    except:
                        #table.setItem(position, 2, QTableWidgetItem("Non disponibile"))
                        
                        item = QTableWidgetItem("Non disponibile")
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        line.setItem(position, 2, item)
                    try:
                        rast = gdal.Open(fil)
                        num_bands = rast.RasterCount
                        
                        item = QTableWidgetItem(str(num_bands))
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        line.setItem(position, 3, item)
                        
                        #table.setItem(position, 3, QTableWidgetItem(str(num_bands)))
                    except:
                        #table.setItem(position, 3, QTableWidgetItem("Non disponibile"))
                    
                        item = QTableWidgetItem("Non disponibile")
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        line.setItem(position, 3, item)
                    try:
                        line.setItem(position, 4, QTableWidgetItem(str("")))
                    except:
                        line.setItem(position, 4, QTableWidgetItem(""))
                        
                        
                        
                        
                        
                    #except:
                    #    line.setItem(position, 1, QTableWidgetItem("Non disponibile"))
                    line.resizeColumnsToContents()
                    position += 1
                elif fil != '':
                    STEMMessageHandler.warning(u"'%s' file non è presente." % fil)
                    pass
            return
        if multi:
            mydir, __ = QFileDialog.getOpenFileNames(parent=None, filter=filt,
                                                 caption="Selezionare i file "
                                                 "di input", directory=STEMSettings.restoreLastDir(line, self.toolname))
            for fil in mydir:
                if os.path.exists(fil):
                    line.addItem(fil)
                    STEMSettings.saveLastDir(line, fil, self.toolname)
                elif fil != '':
                    STEMMessageHandler.warning(u"'%s' file non è presente." % fil)
                    pass
            return
        else:
            if dire:
                label = "Selezionare la directory dei files"
                mydir = QFileDialog.getExistingDirectory(parent=None,
                                                         caption=label,
                                                         directory=STEMSettings.restoreLastDir(line, self.toolname))
            else:
                mydir, __ = QFileDialog.getOpenFileName(parent=None, filter=filt,
                                                    caption="Selezionare il "
                                                    "file di input",
                                                    directory=STEMSettings.restoreLastDir(line, self.toolname))
            if os.path.exists(mydir):
                try:
                    line.setText(mydir)
                    STEMSettings.saveLastDir(line, mydir, self.toolname)
                    return
                except AttributeError:
                    try:
                        line.addItem(mydir)
                        STEMSettings.saveLastDir(line, mydir, self.toolname)
                        return
                    except Exception:
                        STEMMessageHandler.error(u"Errore caricando il file")
        #STEMMessageHandler.error(u"'%s' file non è presente." % mydir)

    def browseDir(self, line, suffix='*.tif'):
        """Function to create new file in a directory

        :param obj line: the QLineEdit object to update
        """
        fileName, __ = QFileDialog.getSaveFileName(None, "Salva file", STEMSettings.restoreLastDir(line, tool=self.toolname),suffix)
        if fileName:
            #if suffix:
            #    if fileName.rfind(suffix) == -1:
            #        fileName += suffix
            try:
                self.save(fileName)
                line.setText(fileName)
                STEMSettings.saveLastDir(line, fileName, tool=self.toolname)
            except (IOError, OSError) as error:
                STEMMessageHandler.error(u'Il file<b>{0}</b> non può essere salvato. Errore: {1}'.format(fileName, error.strerror))
    
    def browseDir2(self, line):
        """Choose an existing directory and set it to a QLineEdit

        :param obj line: the QLineEdit object to update
        """
        mydir = QFileDialog.getExistingDirectory(None, "Selezionare il percorso desiderato",
                                                 "")
        if os.path.exists(mydir):
            line.setText(mydir)
            return
        else:
            # TODO add overwrite option
            #STEMMessageHandler.error(u"'{0}' file già presente.".format(mydir))
            pass


    def save(self, fileName=None):
        """Function set the name of output file

        :param str fileName: name of output file
        """
        if fileName:
            self.path = fileName
        if self.path is None:
            self.path = QFileDialog().getSaveFileName(self,
                                                      "",
                                                      "",
                                                      "Output file (*.tiff)")
            # If the user didn't select a file, abort the save operation
            if len(self.path) == 0:
                self.path = None
                return
            STEMMessageHandler.success("File salvato correttamente.")
        # Rename the original file, if it exists
        path = str(self.path)
        self.overwrite = QFileInfo(path).exists()

        
    def finished(self, outFn):
        """Function to advice the user about the status of analysis

        :param str outFn: output full path
        """
        fileInfo = QFileInfo(outFn)
        if fileInfo.exists():
            STEMMessageHandler.information("Finished", "Processing completed, "
                                           "the output file is {path}".format(path=outFn))
        else:
            STEMMessageHandler.warning("Warning", "{0} not created.".format(outFn))

    def tr(self, context, text):
        """Translate the text"""
        if context == '':
            context = 'STEM'
        return QCoreApplication.translate(context, text)

    def SphinxUrl(self):
        """Create the local url for the tool"""
        filename = "{tool}.html".format(tool=self.toolname.lower().replace(" ",
                                                                           "_"))
        filename = filename.replace("/", "_")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs',
                            'build', 'html', 'tools', filename)
        if platform.system().startswith('linux') or platform.system().startswith('darwin'):
            return "file://{p}".format(p=path)
        else:
            path = path.replace("\\", "/")
            return "file:///{p}".format(p=path)

class SettingsDialog(QDialog, settingsDialog):
    
   
    
    
           
  
    
    """Dialog for setting"""
    def __init__(self, parent, iface):
        QDialog.__init__(self, parent)
        self.dialog = settingsDialog
        self.parent = parent
        self.iface = iface
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setupUi(self)

        self._onLoad()

        self.buttonBox.rejected.connect(self._reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self._accept)
        # self.connect(self.buttonBox, SIGNAL("helpRequested()"), self._help)
        self.pushButton_grass.clicked.connect(partial(self.browseBin, self.lineEdit_grass))
        self.pushButton_grassdata.clicked.connect(partial(self.browseDir, self.lineEdit_grassdata))
        # self.connect(self.pushButton_datalocal, SIGNAL("clicked()"),
        #              partial(self.browseDir, self.lineEdit_datalocal))
        self.pushButton_proj.clicked.connect(partial(self.browseDir, self.lineEdit_proj))
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)
        
        
        self.WARNINGlabel.setText("ATTENZIONE: la configurazione automatica ricrea la LOCATION di GRASS, cancellandone in contenuto." + "\n" + 
                                  "Cartella LOCATION predefinita: " + QgsApplication.qgisSettingsDirPath() + "grassdata/STEM" + "\n" +  
                                  "Cartella GRASS predefinita: "  + QgsApplication.libexecPath() + "../../bin/grass78.bat" + "\n" +  
                                  "Cartella PROJ predefinita: " + QgsApplication.libexecPath() + "../../share/proj/" +"\n" +
                                  "EPSG predefinito: 25832")  
        
        
        self.pushButton_init.clicked.connect(self.initVariables)
        
        
    def initVariables(self,b):
       
        
        
        self.pushButton_proj.setEnabled(True)
        self.lineEdit_proj.setEnabled(True)
        self.label_proj.setEnabled(True)
    
        grass = self._check(STEMSettings.value("grasspath", ""))
        proj = self._check(STEMSettings.value("proj", ""))
      
        self.lineEdit_grassdata.setText(self._check(STEMSettings.value("grassdata","")))
        self.lineEdit_grasslocation.setText(self._check(STEMSettings.value("grasslocation","")))
 
        self.epsg.setText(self._check(STEMSettings.value("epsgcode", "")))
        self.lineEditMemory.setText(self._check(STEMSettings.value("memory","")))
        #=======================================================================
        # if grass:
        #     if os.path.exists(grass):
        #         self.lineEdit_grass.setText(grass)
        #     else:
        #     # QMessageBox.about(self, SETTINGS_ERROR_TITLE, u'\n\n'.join([u'• '+x for x in errors]))
        #         self.warning_message("Controllare il path di GRASS")
        # else:
        #=======================================================================
            # Impostazione di default
            
        self.epsg.setText("25832")
        self.lineEditMemory.setText("1")
        self.lineEdit_grasslocation.setText("STEM")    
            
        grass = QgsApplication.libexecPath() + "../../bin/grass78.bat"
        if os.path.exists(grass):
            self.lineEdit_grass.setText(grass)      
        else:
        # QMessageBox.about(self, SETTINGS_ERROR_TITLE, u'\n\n'.join([u'• '+x for x in errors]))
            self.warning_message("Controllare il path di GRASS")
            

        #=======================================================================
        # if proj:
        #     if os.path.exists(proj):
        #         self.lineEdit_proj.setText(proj)
        #     else:
        #     # QMessageBox.about(self, SETTINGS_ERROR_TITLE, u'\n\n'.join([u'• '+x for x in errors]))
        #         self.warning_message("Controllare il path di proj")
        # else:
        #=======================================================================
        proj = QgsApplication.libexecPath() + "../../share/proj/"

        if os.path.exists(proj):
            self.lineEdit_proj.setText(proj)
        else:
        # QMessageBox.about(self, SETTINGS_ERROR_TITLE, u'\n\n'.join([u'• '+x for x in errors]))
            self.warning_message("Controllare il path di PROJ")
    
        
        grassdata = QgsApplication.qgisSettingsDirPath() + "grassdata"
        if os.path.exists(grassdata):
            self.lineEdit_grassdata.setText(grassdata)
        else:
            try:
                os.makedirs(grassdata)
            except:
                self.warning_message("Controllare il path di grassdata")
            finally:
                self.lineEdit_grassdata.setText(grassdata)
            
        # QMessageBox.about(self, SETTINGS_ERROR_TITLE, u'\n\n'.join([u'• '+x for x in errors]))
            
        try:
            
            import shutil
            shutil.rmtree(grassdata + '/STEM')
            
            
            command = grass + " -e -c EPSG:" + self.epsg.text() + " " + grassdata + "/" + self.lineEdit_grasslocation.text() 
            
            import subprocess
            
            
            result = []
            process = subprocess.Popen(command,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
            for line in process.stdout:
                result.append(line)
            errcode = process.returncode
            for line in result:
                print(line)
            if errcode is not None:
                raise Exception('cmd %s failed, see above for details', command)
        except:
            
            print("Verificare la creazione della Location.")
            #return
            # self.warning_message("Errore. Creare manualmente la LOCATION di GRASS nella cartella GRASSDATA scelta")
        
        
        qm = QMessageBox
        ret = qm.question(self,'', "Si desidera avviare il download delle liberie R necessarie al funzionamento del plugin (può richiedere qualche minuto)?\nIn alternativa il download delle librerie avviene all'avvio del singolo modulo.", qm.Yes | qm.No)

        if ret == qm.Yes:
        
            print("Procedo con lo scarico")
       
        else:
            return 
         
   
   
       
        alg = QgsApplication.processingRegistry().algorithmById(
                'r:InstallLib')
            
        params = {}
            
        task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
            
      #  task.executed.connect(partial(task_finished, context, params, self ))
        QgsApplication.taskManager().addTask(task)       
       
       
 #       processing.run("r:InstallLib",{})
                   
  
        #=========================================================================
      #   else:
      #       # Impostazione di default
      #       for path in [r'C:\OSGeo4W\share\proj', r'C:\OSGeo4W64\share\proj']:
      #           if os.path.exists(path):
      #               self.lineEdit_proj.setText(path)
      #               break
      # 
      #=========================================================================
      
      
        
        
         
        #=======================================================================
        # if os.path.exists(path):
        # else:
        #     # QMessageBox.about(self, SETTINGS_ERROR_TITLE, u'\n\n'.join([u'• '+x for x in errors]))
        #     self.warning_message("Controllare il path di PROJ")
        #=======================================================================
       
       
        #C:/Program Files/QGIS 3.10/share/proj
                                                                           
        #self.lineEdit_grassserver.setText(self._check(STEMSettings.value("grasspathserver",
        #                                                            "")))
        #self.lineEdit_grassdataserver.setText(self._check(STEMSettings.value("grassdataserver",
        #                                                          "")))
        #self.lineEdit_grasslocationserver.setText(self._check(STEMSettings.value("grasslocationserver",
        #                                                          "")))
        
        #assert self.tableWidget.rowCount() >= 2
        #assert self.tableWidget.columnCount() >= 2
        #i = 0
        #for mapping in STEMUtils.get_mapping_table():
        #    self.tableWidget.setItem(i, 0, QTableWidgetItem(mapping.remote))
        #    self.tableWidget.setItem(i, 1, QTableWidgetItem(mapping.local))
        #    i += 1
        #self.tableWidget.resizeColumnsToContents()



    def task_finished(context, params, self, successful, results):

        STEMMessageHandler.success("R Library downloaded.")
  



    
        
    def _check(self, string):
        """Check the type of string

        :param obj string: a string, it should be as UnicodeType or StringType
        """
        if isinstance(string, str):
            return str(string)
        else:
            return str("")

    def _onLoad(self):
        """Load the parameters from the settings"""
        self.lineEdit_grass.setText(self._check(STEMSettings.value("grasspath",
                                                                   "")))
        self.lineEdit_grassdata.setText(self._check(STEMSettings.value("grassdata",
                                                                       "")))
        self.lineEdit_grasslocation.setText(self._check(STEMSettings.value("grasslocation",
                                                                           "")))
        #self.lineEdit_grassserver.setText(self._check(STEMSettings.value("grasspathserver",
        #                                                            "")))
        #self.lineEdit_grassdataserver.setText(self._check(STEMSettings.value("grassdataserver",
        #                                                          "")))
        #self.lineEdit_grasslocationserver.setText(self._check(STEMSettings.value("grasslocationserver",
        #                                                          "")))
        
        #assert self.tableWidget.rowCount() >= 2
        #assert self.tableWidget.columnCount() >= 2
        #i = 0
        #for mapping in STEMUtils.get_mapping_table():
        #    self.tableWidget.setItem(i, 0, QTableWidgetItem(mapping.remote))
        #    self.tableWidget.setItem(i, 1, QTableWidgetItem(mapping.local))
        #    i += 1
        #self.tableWidget.resizeColumnsToContents()

        self.epsg.setText(self._check(STEMSettings.value("epsgcode", "")))
        self.lineEditMemory.setText(self._check(STEMSettings.value("memory",
                                                                   "")))
        if sys.platform != 'win32':
            self.pushButton_proj.setEnabled(False)
            self.lineEdit_proj.setEnabled(False)
            self.label_proj.setEnabled(False)
        else:
            self.pushButton_proj.setEnabled(True)
            self.lineEdit_proj.setEnabled(True)
            self.label_proj.setEnabled(True)
            proj = self._check(STEMSettings.value("proj", ""))
            if proj:
                self.lineEdit_proj.setText(proj)
            else:
                # Impostazione di default
                for path in [r'C:\OSGeo4W\share\proj', r'C:\OSGeo4W64\share\proj']:
                    if os.path.exists(path):
                        self.lineEdit_proj.setText(path)
                        break
        # TODO: caricare le impostazioni di default se non sono definite
    def browseBin(self, line):
        """Choose an existing file and set it to a QLineEdit

        :param obj line: the QLineEdit object to update
        """
        mydir, __ = QFileDialog.getOpenFileName(None, "Selezionare il file desiderato",
                                            "")
        if os.path.exists(mydir):
            line.setText(mydir)
            return
        else:
            # TODO add overwrite option
            #STEMMessageHandler.error(u"'{0}' file già presente.".format(mydir))
            pass

    def browseDir(self, line):
        """Choose an existing directory and set it to a QLineEdit

        :param obj line: the QLineEdit object to update
        """
        mydir = QFileDialog.getExistingDirectory(None, "Selezionare il percorso desiderato",
                                                 "")
        if os.path.exists(mydir):
            line.setText(mydir)
            return
        else:
            # TODO add overwrite option
            #STEMMessageHandler.error(u"'{0}' file già presente.".format(mydir))
            pass

    def _reject(self):
        """"""
        QDialog.reject(self)

    def _accept(self):
        """Save the variable in STEM Settings"""
        # TODO: Controllare se i path locali sono validi
        grasspath = self.lineEdit_grass.text()
        grassdata = self.lineEdit_grassdata.text()
        projdir = self.lineEdit_proj.text()
        errors = []
        if not grasspath or os.path.isfile(grasspath):
            STEMSettings.setValue("grasspath", grasspath)
        else:
            errors.append("Eseguibile di GRASS non trovato, corregere le impostazioni.\nValore errato: {}".format(grasspath))
        if not grassdata or os.path.isdir(grassdata):
            STEMSettings.setValue("grassdata", grassdata)
        else:
            errors.append("Cartella GRASSDATA non esistente, corregere le impostazioni.\nValore errato: {}".format(grassdata))
        if not projdir or os.path.isdir(projdir):
            STEMSettings.setValue("proj", projdir)
        else:
            errors.append("Cartella PROJ non esistente, corregere le impostazioni.\nValore errato: {}".format(projdir))
            

            
        STEMSettings.setValue("grasslocation",
                              self.lineEdit_grasslocation.text())
        #STEMSettings.setValue("grasspathserver",
        #                      self.lineEdit_grassserver.text())
        #STEMSettings.setValue("grassdataserver",
        #                      self.lineEdit_grassdataserver.text())
        #STEMSettings.setValue("grasslocationserver",
        #                      self.lineEdit_grasslocationserver.text())
        STEMSettings.setValue("epsgcode", self.epsg.text())
        STEMSettings.setValue("memory", self.lineEditMemory.text())

        #table = []
        #for i in range(self.tableWidget.rowCount()):
        #    remote = self.tableWidget.item(i, 0)
        #    local = self.tableWidget.item(i, 1)
        #    r = remote.text().strip() if remote else ''
        #    l = local.text().strip() if local else ''
            
        #    if r and l:
        #        if os.path.isdir(l):
        #            table.append(PathMapping(r, l))
        #        else:
        #            errors.append(u"Mapping risosrse: la cartella locale ({}) non è attiva".format(l))
        #    elif bool(r) != bool(l):
        #        errors.append("Mapping delle risosrse non definito correttamente, ricontrolla le impostazioni (mapping: {})".format(r or l))
            
        #STEMUtils.set_mapping_table(table)
        
        if errors:
            # QMessageBox.about(self, SETTINGS_ERROR_TITLE, u'\n\n'.join([u'• '+x for x in errors]))
            self.warning_message(u'\n\n'.join([u'• '+x for x in errors]))
            
            # TODO: Fare in modo che in caso di errore la finestra non si chiuda, senza riinizializzarla da zero
            # dialog = SettingsDialog(self.parent, self.iface)
            # dialog.exec_()

    def warning_message(self, message):
        SETTINGS_ERROR_TITLE = "Errore"
        # StandardButton warning (QWidget parent, QString title, QString text, 
        # StandardButtons buttons = QMessageBox.Ok, StandardButton defaultButton = QMessageBox.NoButton)
        QMessageBox.warning(self, SETTINGS_ERROR_TITLE, message)
        

class helpDialog(QDialog, helpDialog):
    """Dialog for help manual"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        """Set up the help user interface"""
        self.dialog = helpDialog
        self.setupUi(self)
        self.backButton.clicked.connect(self._back)
        self.forwardButton.clicked.connect(self._forward)

    def _back(self):
        """Function to go back to previous page"""
        try:
            self.webView.back()
        except Exception:
            pass

    def _forward(self):
        """Function to go forward to next page"""
        try:
            self.webView.forward()
        except Exception:
            pass

    def fillfromUrl(self, url):
        """Load a url in the Help window

        :param str url: the url to open, it should be local or web
        """
        self.webView.load(QUrl(url))

    def home(self):
        """Load the home page from local path"""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs',
                            'build', 'html', 'index.html')
        if platform.system().startswith('linux') or platform.system().startswith('darwin'):
            url = "file://{p}".format(p=path)
        else:
            path = path.replace("\\", "/")
            url = "file:///{p}".format(p=path)
        self.webView.load(QUrl(url))


from qgis.core import QgsProcessingFeedback

class MyFeedBack(QgsProcessingFeedback):
    
    #def __init__(self, logTextEdit):
    def __init__(self):
        super(MyFeedBack,self).__init__()
        self.logTextEdit = None
        self.textBrowser = None
        
    
    def setProgressText(self, text):
        print(text)
        #self.logTextEdit.se(text)
# 
    def setLogTextEdit(self, logTextEdit, textBrowser):
        self.logTextEdit = logTextEdit
        self.textBrowser = textBrowser

    def pushInfo(self, info):
        print(info)
        testo = info
        #self.textBrowser.append(testo)
        #self.logTextEdit.appendPlainText(info)
# 
#        def pushCommandInfo(self, info):
     #   print(info)
        #testo = info
        #self.textBrowser.append(testo)
    
        #self.logTextEdit.appendPlainText(info)
# 
    def pushDebugInfo(self, info):
        print(info)
        #self.textBrowser.append(info)
        
        #self.logTextEdit.appendPlainText(info)
# 
    def pushConsoleInfo(self, info):
        print(info)
        #self.logTextEdit.appendPlainText(info)
        #self.textBrowser.append(info)
    
    def reportError(self, error, fatalError=False):
#        self.logTextEdit.appendPlainText(error)
        print(error)
        #self.logTextEdit.appendPlainText(error)
#     #    print("STEM " + info)
