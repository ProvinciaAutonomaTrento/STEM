# -*- coding: utf-8 -*-

"""
Date: August 2014

Authors: Luca Delucchi

Copyright: (C) 2014 Luca Delucchi

This file contain some dialogs (base, settings and help) of STEM project.
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

import os
import os.path
import sys
import subprocess
import tempfile
import platform
from functools import partial
from types import StringType, UnicodeType

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from qgis.core import *
from qgis.gui import *

from stem_utils import STEMMessageHandler
from stem_utils import STEMUtils
from stem_utils import CheckableComboBox
from stem_utils import PathMapping
from stem_utils_server import STEMSettings, inverse_mask
import gdal_stem

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


class BaseDialog(QDialog, baseDialog):
    """The main class for all the tools.
    It has most of the functions to exchange information beetween user, tool
    and backend.

    :param str title: the name of the tool
    """
    def __init__(self, title, parent=None, suffix='.tif'):
        QDialog.__init__(self, parent)
        self.dialog = baseDialog
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.process = QProcess(self)
        self.connect(self.process, SIGNAL("error(QProcess::ProcessError)"),
                     self.processError)
        self.connect(self.process,
                     SIGNAL("finished(int, QProcess::ExitStatus)"),
                     self.processFinished)

        self.setupUi(self)

        self.connect(self.buttonBox, SIGNAL("rejected()"), self._reject)
        self.runButton.clicked.connect(self.run)
        # self.connect(self.buttonBox, SIGNAL("accepted()"), self._accept)
        self.connect(self.buttonBox, SIGNAL("helpRequested()"), self._help)
        self.connect(self.BrowseButton, SIGNAL("clicked()"),
                     partial(self.browseDir, self.TextOut, suffix))
        # self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

        self.toolname = title
        self.setWindowTitle(self.toolname)
        self.inlayers = {}
        self.rect_str = None
        self.mask = None
        self.overwrite = False
        
        self.helpui = helpDialog()
        STEMUtils.stemMkdir()

    def _reject(self):
        """Function for reject button"""
        if self.process.state() != QProcess.NotRunning:
            ret = QMessageBox.warning(self, "Warning",
                                      "The command is still running. \nDo"
                                      " you want terminate it anyway?",
                                      QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return

            self.disconnect(self.process,
                            SIGNAL("error(QProcess::ProcessError)"),
                            self.processError)
            self.disconnect(self.process,
                            SIGNAL("finished(int, QProcess::ExitStatus)"),
                            self.processFinished)
            self.stop()
        QDialog.reject(self)

    def run(self):
        """Function for accept button"""
        if not self.overwrite and self.TextOut.isEnabled():
            old_overwrite = self.overwrite
            res, self.overwrite = STEMUtils.fileExists(self.TextOut.text())
            if not res: return
            
        if hasattr(self, 'TextOut2'):
            if old_overwrite and self.TextOut2.isEnabled():
                res, self.overwrite = STEMUtils.fileExists(self.TextOut.text())
                if not res: return

        errors = []
        
        e = self.check_paths_validity()
        if e:
            errors.append('I seguenti percorsi inseriti non sono validi:\n\n' + u'\n\n'.join([u'• '+x for x in e]))
        
        e = [] if self.local_execution() else self.check_server_paths()
        if e:
            errors.append('I seguenti path non possono essere usati per elaborazioni remote:\n\n' + u'\n\n'.join([u'• '+x for x in e]))
        
        e = self.check_input_cross_validation()
        if e:
            errors.append(e)
        
        errors.extend(self.check_form_fields())

        if errors:
            QMessageBox.question(self, "Errore", '\n\n'.join(errors))
            return

        self.onRunLocal()
        self.accept()

    def check_input_cross_validation(self):
        return ''

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
        errors = []
        for p in paths:
            if STEMUtils.pathClientWinToServerLinux(p, gui_warning=False) == p:
               errors.append(p) 
        return errors

    def _help(self):
        """Function for help button"""
        self.helpui.exec_()

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
        self.connect(self.BrowseButtonIn, SIGNAL("clicked()"),
                     partial(self.browseInFile, self.BaseInput, multi=multi,
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
        self.connect(self.BrowseButtonIn, SIGNAL("clicked()"),
                     partial(self.browseInFile, self.TextIn, multi=multi,
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
        self.connect(self.BrowseButtonIn, SIGNAL("clicked()"),
                     partial(self.browseInFile, self.TextDir, dire=True))

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
        self.BaseInput.setEditable(True)
        self.BaseInput.setObjectName("BaseInput")
        self.horizontalLayout_input.addWidget(self.BaseInput)
        self.verticalLayout_input.insertLayout(0, self.horizontalLayout_input)
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
        self.BaseInput2.setEditable(True)
        self.BaseInput2.setObjectName("BaseInput2")
        self.horizontalLayout_input2.addWidget(self.BaseInput2)
        self.verticalLayout_input.insertLayout(pos,
                                               self.horizontalLayout_input2)
        self.label2.setText(self.tr("", label))

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
        self.connect(self.BrowseButtonInOpt, SIGNAL("clicked()"),
                     partial(self.browseInFile, self.TextInOpt, filt))

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

    def _insertFourthCombobox(self, label, posnum, items=None):
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
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_combo4)
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
        self.emit(SIGNAL("processError(QProcess::ProcessError)"), error)

    def processFinished(self, exitCode, status):
        """"""
        self.emit(SIGNAL("processFinished(int, QProcess::ExitStatus)"),
                  exitCode, status)

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
            layer = STEMUtils.getLayersSource(source[n])
            typ = STEMUtils.checkMultiRaster(source[n], layer)
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
        render = self.iface.mapCanvas()
        rect = render.extent()
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

    def browseInFile(self, line, filt="LAS file (*.las *.laz)", multi=False,
                     dire=False):
        """Function to select existing file in a directory

        :param obj line: the QLineEdit object to update
        :param str filt: a string with the filter of directory
        :param bool multi: True to select more files
        :param bool dire: True to select a directory instead a file
        """
        if multi:
            mydir = QFileDialog.getOpenFileNames(parent=None, filter=filt,
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
                mydir = QFileDialog.getOpenFileName(parent=None, filter=filt,
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

    def browseDir(self, line, suffix='.tif'):
        """Function to create new file in a directory

        :param obj line: the QLineEdit object to update
        """
        fileName = QFileDialog.getSaveFileName(None, "Salva file", STEMSettings.restoreLastDir(line, tool=self.toolname))
        if fileName:
            if suffix:
                if fileName.rfind(suffix) == -1:
                    fileName += suffix
            try:
                self.save(fileName)
                line.setText(fileName)
                STEMSettings.saveLastDir(line, fileName, tool=self.toolname)
            except (IOError, OSError), error:
                STEMMessageHandler.error(u'Il file<b>{0}</b> non può essere salvato. Errore: {1}'.format(fileName, error.strerror))

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
        path = unicode(self.path)
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
        return QCoreApplication.translate(context, text.decode('utf-8'))

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

        self.connect(self.buttonBox, SIGNAL("rejected()"), self._reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self._accept)
        # self.connect(self.buttonBox, SIGNAL("helpRequested()"), self._help)
        self.connect(self.pushButton_grass, SIGNAL("clicked()"),
                     partial(self.browseBin, self.lineEdit_grass))
        self.connect(self.pushButton_grassdata, SIGNAL("clicked()"),
                     partial(self.browseDir, self.lineEdit_grassdata))
        # self.connect(self.pushButton_datalocal, SIGNAL("clicked()"),
        #              partial(self.browseDir, self.lineEdit_datalocal))
        self.connect(self.pushButton_proj, SIGNAL("clicked()"),
                     partial(self.browseDir, self.lineEdit_proj))
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

    def _check(self, string):
        """Check the type of string

        :param obj string: a string, it should be as UnicodeType or StringType
        """
        if isinstance(string, UnicodeType) or isinstance(string, StringType):
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
        self.lineEdit_grassserver.setText(self._check(STEMSettings.value("grasspathserver",
                                                                    "")))
        self.lineEdit_grassdataserver.setText(self._check(STEMSettings.value("grassdataserver",
                                                                  "")))
        self.lineEdit_grasslocationserver.setText(self._check(STEMSettings.value("grasslocationserver",
                                                                  "")))
        
        assert self.tableWidget.rowCount() >= 2
        assert self.tableWidget.columnCount() >= 2
        i = 0
        for mapping in STEMUtils.get_mapping_table():
            self.tableWidget.setItem(i, 0, QTableWidgetItem(mapping.remote))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(mapping.local))
            i += 1
        self.tableWidget.resizeColumnsToContents()

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
        mydir = QFileDialog.getOpenFileName(None, "Selezionare il file desiderato",
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
        STEMSettings.setValue("grasspathserver",
                              self.lineEdit_grassserver.text())
        STEMSettings.setValue("grassdataserver",
                              self.lineEdit_grassdataserver.text())
        STEMSettings.setValue("grasslocationserver",
                              self.lineEdit_grasslocationserver.text())
        STEMSettings.setValue("epsgcode", self.epsg.text())
        STEMSettings.setValue("memory", self.lineEditMemory.text())

        table = []
        for i in range(self.tableWidget.rowCount()):
            remote = self.tableWidget.item(i, 0)
            local = self.tableWidget.item(i, 1)
            r = remote.text().strip() if remote else ''
            l = local.text().strip() if local else ''
            
            if r and l:
                if os.path.isdir(l):
                    table.append(PathMapping(r, l))
                else:
                    errors.append(u"Mapping risosrse: la cartella locale ({}) non è attiva".format(l))
            elif bool(r) != bool(l):
                errors.append("Mapping delle risosrse non definito correttamente, ricontrolla le impostazioni (mapping: {})".format(r or l))
            
        STEMUtils.set_mapping_table(table)
        
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
