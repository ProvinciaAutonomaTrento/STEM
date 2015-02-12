# -*- coding: utf-8 -*-

"""
***************************************************************************
    stem_utils.py
    ---------------------
    Date                 : August 2014
    Copyright            : (C) 2014 Luca Delucchi
    Email                : luca.delucchi@fmach.it
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from qgis.core import *
from qgis.gui import *


import os
import sys
import subprocess
import tempfile
import codecs
import platform
from functools import partial
from types import StringType, UnicodeType
from stem_utils import (STEMMessageHandler,
                        STEMSettings)

MSG_BOX_TITLE = "STEM Plugin"

baseDialog = uic.loadUiType(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'base.ui'))[0]
helpDialog = uic.loadUiType(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'help.ui'))[0]
settingsDialog = uic.loadUiType(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'settings.ui'))[0]

def escapeAndJoin(strList):
    """Escapes arguments and return them joined in a string"""
    joined = ''
    for s in strList:
        if s.find(" ") is not -1:
            escaped = '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
        else:
            escaped = s
        joined += escaped + " "
    return joined.strip()


class CheckableComboBox(QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)


class BaseDialog(QDialog, baseDialog):

    def __init__(self, title, parent=None):
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
        self.connect(self.buttonBox, SIGNAL("accepted()"), self._accept)
        self.connect(self.buttonBox, SIGNAL("helpRequested()"), self._help)
        self.connect(self.BrowseButton, SIGNAL("clicked()"),
                     partial(self.BrowseDir, self.TextOut))
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

        self.toolname = title
        self.setWindowTitle(self.toolname)
        self.inlayers = {}
        self.rect_str = None
        self.mask = None
        self.overwrite = False

        self.helpui = helpDialog()

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

    def _accept(self):
        """Function for accept button"""
        if self.LocalCheck.isChecked():
            self.onRunLocal()
        else:
            self.onRunServer()

    def _help(self):
        """Function for help button"""
        self.helpui.exec_()

    def _insertMultipleInput(self):
        """Function to add List Widget where insert multiple input files name"""
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
        self.horizontalLayout_input.addWidget(self.BaseInput)
        self.verticalLayout_input.insertLayout(0, self.horizontalLayout_input)
        self.label.setText(self.tr("", "Dati di input"))

    def _insertFileInput(self, pos=0):
        """Function to add a second output"""
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
        self.verticalLayout_input.insertLayout(0, self.horizontalLayout_input)
        self.labelF.setText(self.tr("", "File LAS di input"))
        self.BrowseButtonIn.setText(self.tr("", "Sfoglia"))
        self.connect(self.BrowseButtonIn, SIGNAL("clicked()"),
                     partial(self.BrowseInFile, self.TextIn))

    def _insertSingleInput(self, label="Dati di input"):
        """Function to add ComboBox Widget where insert a single input file"""
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
        input file"""
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

    def _insertFileInputOption(self, label, pos=0):
        """Function to add a second output"""
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
                     partial(self.BrowseInFile, self.TextInOpt))

    def _insertLayerChoose(self, pos=2):
        # TODO da rimuovere
        """Function to add a LineEdit Widget for the layers list"""
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
        self.verticalLayout_input.insertLayout(pos, self.horizontalLayout_layer)
        self.label_layer.setText(self.tr("", label))

    def _insertLayerChooseCheckBox2(self, label, combo=True, pos=3):
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
        self.verticalLayout_input.insertLayout(pos, self.horizontalLayout_layer2)
        self.label_layer2.setText(self.tr("", label))

    def _insertLayerChooseCheckBox3(self, label, combo=True):
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
        self.verticalLayout_input.insertLayout(4, self.horizontalLayout_layer3)
        self.label_layer3.setText(self.tr("", label))

    def _insertLayerChooseCheckBox4(self, label, pos=5, combo=True):
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
        """Function to add ComboBox Widget"""
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
        """Function to add SpinBox Widget for decimal number"""
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
        """Function to add SpinBox Widget for decimal number"""
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
        """Function to add SpinBox Widget for integer number"""
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
        """Function to add a LineEdit Widget"""
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
        """Function to add a LineEdit Widget"""
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

    def _insertFirstCombobox(self, label, posnum, items=None):
        """Function to add a ComboBox Widget"""
        self.horizontalLayout_combo = QHBoxLayout()
        self.horizontalLayout_combo.setObjectName("horizontalLayout_combo")
        self.LabelCombo = QLabel()
        self.LabelCombo.setObjectName("LabelCombo")
        self.LabelCombo.setWordWrap(True)
        self.horizontalLayout_combo.addWidget(self.LabelCombo)
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
        """Function to add a ComboBox Widget"""
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

    def _insertSecondOutput(self, label, posnum):
        """Function to add a second output"""
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
        """Function to add a text area"""
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

    def _insertCheckbox(self, label, posnum, state=False):
        self.horizontalLayout_checkbox = QHBoxLayout()
        self.horizontalLayout_checkbox.setObjectName("horizontalLayout_checkbox")
        self.LabelCheckbox = QLabel()
        self.LabelCheckbox.setWordWrap(True)
        self.LabelCheckbox.setObjectName("LabelCheckbox")
        self.horizontalLayout_checkbox.addWidget(self.LabelCheckbox)
        self.checkbox = QCheckBox()
        self.checkbox.setObjectName("checkbox")
        self.horizontalLayout_checkbox.addWidget(self.checkbox)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_checkbox)
        self.LabelCheckbox.setText(self.tr("Dialog", label))
        self.checkbox.setChecked(state)

    def _insertSecondCheckbox(self, label, posnum, state=False):
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

    def processError(self, error):
        self.emit(SIGNAL("processError(QProcess::ProcessError)"), error)

    def processFinished(self, exitCode, status):
        self.emit(SIGNAL("processFinished(int, QProcess::ExitStatus)"),
                  exitCode, status)

    # enables the OK button
    def enableRun(self, enable=True):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    def saveCommand(self, command):
        """Save the command history to file"""
        _path = QgsApplication.qgisSettingsDirPath() + "stem_command_history.txt"
        try:
            hFile = codecs.open(_path, 'w', encoding='utf-8')
            hFile.write(" ".join(command) + '\n')
        except:
            raise
        hFile.close()

    def cutInput(self, inp, source, typ):
        self.mapDisplay(inp, typ)
        mask = STEMSettings.value("mask", "")
        bbox = self.QGISextent.isChecked()
        if not bbox and not mask:
            return False, False, False
        if bbox and mask:
            STEMMessageHandler.error("Sono state impostate sia una maschera "
                                     "vettoriale sia una estensione di QGIS. "
                                     "Si prega di rimuoverne una delle due")
        outname = "stem_cut_{name}".format(name=inp)
        out = os.path.join(tempfile.gettempdir(), outname)
        PIPE = subprocess.PIPE
        if typ == 'raster' or typ == 'image':
            if bbox:
                com = ['gdal_translate', source, out, '-projwin']
                com.extend(self.rect_str)
            elif mask:
                com = ['gdalwarp', '-cutline', mask, '-crop_to_cutline',
                       '-overwrite', source, out]
            else:
                return False, False, False
        if typ == 'vector':
            com = ['ogr2ogr']
            if bbox:
                com.append('-clipsrc')
                com.extend(self.rect_str)
            elif mask:
                com.append('-clipsrc {bbox}'.format(bbox=mask))
            else:
                return False, False, False
            com.extend([out, source])

        runcom = subprocess.Popen(com, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        log, err = runcom.communicate()
        if runcom.returncode != 0:
            STEMMessageHandler.error("Errore eseguendo il ritaglio del file di input: "
                                     "Errore eseguendo il comando {err}".format(err=err))

        return outname.strip(), out, mask

    def cutInputMulti(self, inp, source, typ):
        if len(inp) != len(source):
            STEMMessageHandler.error("Errore durante il ritaglio di più immagini")
        newinp = []
        newsource = []
        for n in range(len(inp)):
            newn, news, newm = self.cutInput(inp[n], source[n], typ)
            if not newn:
                return False, False
            else:
                newinp.append(newn)
                newsource.append(news)
        return newinp, newsource

    def mapDisplay(self, source, typ):
        render = self.iface.mapCanvas()
        rect = render.extent()
        self.rect_str = [str(rect.xMinimum()), str(rect.yMaximum()),
                         str(rect.xMaximum()), str(rect.yMinimum())]

    def onRunLocal(self):
        pass

    def onRunServer(self):
        STEMMessageHandler.warning("Esegui sul Server",
                                   "Opzione non ancora implementata")
        pass

    # stop the command execution
    def stop(self):
        self.enableRun(True)
        self.setCursor(Qt.ArrowCursor)
        self.process.kill()

    def BrowseInFile(self, line, filt="LAS file (*.las)"):
        """Function to create new file in a directory"""
        mydir = QFileDialog.getOpenFileName(None, "Selezionare il file di"
                                            " input", "", filt)
        if os.path.exists(mydir):
            line.setText(mydir)
            return
        else:
            # TODO add overwrite option
            STEMMessageHandler.error(u"'%s' file non è presente." % mydir)

    def BrowseDir(self, line):
        """Function to create new file in a directory"""
        fileName = QFileDialog.getSaveFileName(None, "Salva file", "")
        if fileName:
            try:
                self.save(fileName)
                line.setText(fileName)
            except (IOError, OSError), error:
                STEMMessageHandler.error(u'Il file<b>{0}</b> non può essere '
                                         'salvato. Errore: {1}'.format(fileName, error.strerror))

    def save(self, fileName=None):
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
        fileInfo = QFileInfo(outFn)
        if fileInfo.exists():
            STEMMessageHandler.information("Finished", "Processing completed, "
                                           "the output file is {path}".format(path=outFn))
        else:
            STEMMessageHandler.warning("Warning", "{0} not created.".format(outFn))

    def tr(self, context, text):
        if context == '':
            context = 'STEM'
        return QCoreApplication.translate(context, text.decode('utf-8'))

    def SphinxUrl(self):
        filename = "{tool}.html".format(tool=self.toolname.lower().replace(" ",
                                                                           "_"))
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs',
                            'build', 'html', 'tools', filename)
        if platform.system().startswith('linux') or platform.system().startswith('darwin'):
            return "file://{p}".format(p=path)
        else:
            path = path.replace("\\", "/")
            return "file:///{p}".format(p=path)


class SettingsDialog(QDialog, settingsDialog):

    def __init__(self, parent, iface):
        QDialog.__init__(self, parent)
        self.dialog = settingsDialog
        self.iface = iface
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setupUi(self)

        self._onLoad()

        self.connect(self.buttonBox, SIGNAL("rejected()"), self._reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self._accept)
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self._save)
#        self.connect(self.buttonBox, SIGNAL("helpRequested()"), self._help)
        self.connect(self.pushButton_grass, SIGNAL("clicked()"),
                     partial(self.BrowseBin, self.lineEdit_grass))
        self.connect(self.pushButton_grassdata, SIGNAL("clicked()"),
                     partial(self.BrowseDir, self.lineEdit_grassdata))
        self.connect(self.pushButton_gdal, SIGNAL("clicked()"),
                     partial(self.BrowseDir, self.lineEdit_gdal))
        self.connect(self.pushButton_liblas, SIGNAL("clicked()"),
                     partial(self.BrowseDir, self.lineEdit_liblas))
        self.connect(self.pushButton_pdal, SIGNAL("clicked()"),
                     partial(self.BrowseDir, self.lineEdit_pdal))
        self.connect(self.pushButton_proj, SIGNAL("clicked()"),
                     partial(self.BrowseDir, self.lineEdit_proj))
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

    def _check(self, string):
        if isinstance(string, UnicodeType) or isinstance(string, StringType):
            return string
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
        self.lineEdit_liblas.setText(self._check(STEMSettings.value("liblaspath",
                                                                    "")))
        self.lineEdit_gdal.setText(self._check(STEMSettings.value("gdalpath",
                                                                  "")))
        self.lineEdit_pdal.setText(self._check(STEMSettings.value("pdalpath",
                                                                  "")))
        self.epsg.setText(self._check(STEMSettings.value("epsgcode", "")))
        if sys.platform != 'win32':
            self.pushButton_proj.setEnabled(False)
            self.lineEdit_proj.setEnabled(False)
            self.label_proj.setEnabled(False)
        else:
            self.pushButton_proj.setEnabled(True)
            self.lineEdit_proj.setEnabled(True)
            self.label_proj.setEnabled(True)
            if os.path.exists('C:\OSGeo4W\share\proj'):
                self.lineEdit_proj.setText('C:\OSGeo4W\share\proj')

    def BrowseBin(self, line):
        mydir = QFileDialog.getOpenFileName(None, "Selezionare il file desiderato",
                                            "")
        if os.path.exists(mydir):
            line.setText(mydir)
            return
        else:
            # TODO add overwrite option
            STEMMessageHandler.error(u"'{0}' file già presente.".format(mydir))

    def BrowseDir(self, line):
        """"""
        mydir = QFileDialog.getExistingDirectory(None, "Selezionare il percorso desiderato",
                                                 "")
        if os.path.exists(mydir):
            line.setText(mydir)
            return
        else:
            # TODO add overwrite option
            STEMMessageHandler.error(u"'{0}' file già presente.".format(mydir))

    def _reject(self):
        pass

    def _save(self):
        """Save all the keys/values related to stem to a file"""
        keys = [a for a in STEMSettings.allKeys()]
        # TODO maybe add the possibility to choose where save the file
        import tempfile
        f = tempfile.NamedTemporaryFile(delete=False)
        for k in keys:
            line = "{key}:  {value}\n".format(key=k,
                                              value=STEMSettings.value(k, ""))
            f.write(line)
        f.close()
        STEMMessageHandler.information(MSG_BOX_TITLE, 'Impostazioni salvate nel file {0}'.format(f.name))

    def _accept(self):
        """Save the variable in STEM Settings"""
        STEMSettings.setValue("grasspath", self.lineEdit_grass.text())
        STEMSettings.setValue("grassdata", self.lineEdit_grassdata.text())
        STEMSettings.setValue("grasslocation", self.lineEdit_grasslocation.text())
        STEMSettings.setValue("liblaspath",  self.lineEdit_liblas.text())
        STEMSettings.setValue("gdalpath", self.lineEdit_gdal.text())
        STEMSettings.setValue("pdalpath", self.lineEdit_pdal.text())
        STEMSettings.setValue("epsgcode", self.epsg.text())


class helpDialog(QDialog, helpDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        """Set up the help user interface"""
        self.dialog = helpDialog
        self.setupUi(self)

    def fillfromUrl(self, url):
        """Load a url in the Help window"""
        self.webView.load(QUrl(url))
