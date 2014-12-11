# -*- coding: utf-8 -*-

"""
***************************************************************************
    stem_base_dialogs.py
    ---------------------
    Date                 : June 2014
    Copyright            : (C) 2014 Luca Delucchi
    Email                :
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
__date__ = 'June 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from base import Ui_Dialog
from help_ui import Ui_Dialog as Help_Dialog
from settings_ui import Ui_Dialog as Setting_Dialog

import os
import sys
import subprocess
import tempfile
from functools import partial
from gdal_functions import getNumSubset

MSG_BOX_TITLE = "STEM Plugin Warning"

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


class BaseDialog(QDialog, Ui_Dialog):

    def __init__(self, title, parent=None):
        QDialog.__init__(self, parent)
        self.dialog = Ui_Dialog
        self.setAttribute(Qt.WA_DeleteOnClose)
        #self.iface = iface

        #self.mapCanvas = iface.mapCanvas()
        self.process = QProcess(self)
        self.connect(self.process, SIGNAL("error(QProcess::ProcessError)"),
                     self.processError)
        self.connect(self.process, SIGNAL("finished(int, QProcess::ExitStatus)"),
                     self.processFinished)

        self.setupUi(self)

        self.connect(self.buttonBox, SIGNAL("rejected()"), self._reject)
        self.connect(self.buttonBox, SIGNAL("accepted()"), self._accept)
        self.connect(self.buttonBox, SIGNAL("helpRequested()"), self._help)
        self.connect(self.BrowseButton, SIGNAL("clicked()"), self.BrowseDir)
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

        self.setWindowTitle(title)
        self.inlayers = {}
        self.rect_str = None
        self.mask = None

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

    def _insertFileInput(self):
        """Function to add a second output"""
        self.horizontalLayout_input = QHBoxLayout()
        self.horizontalLayout_input.setObjectName("horizontalLayout_output2")
        self.label = QLabel()
        self.label.setObjectName("LabelOut")
        self.label.setWordWrap(True)
        self.horizontalLayout_input.addWidget(self.label)
        self.TextIn = QLineEdit()
        self.TextIn.setObjectName("TextIn")
        self.horizontalLayout_input.addWidget(self.TextIn)
        self.BrowseButtonIn = QPushButton()
        self.BrowseButtonIn.setObjectName("BrowseButtonIn")
        self.horizontalLayout_input.addWidget(self.BrowseButtonIn)
        self.verticalLayout_input.insertLayout(0, self.horizontalLayout_input)
        self.label.setText(self.tr("", "Selezionare file LAS di input"))
        self.BrowseButtonIn.setText(self.tr("", "Sfoglia"))

    def _insertSingleInput(self):
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
        self.label.setText(self.tr("", "Dati di input"))

    def _insertSecondSingleInput(self):
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
        self.verticalLayout_input.insertLayout(1, self.horizontalLayout_input2)
        self.label2.setText(self.tr("", "Dati di input"))

    def _insertLayerChoose(self):
        """Function to add a LineEdit Widget for the layers list"""
        self.horizontalLayout_layer = QHBoxLayout()
        self.horizontalLayout_layer.setObjectName("horizontalLayout_layer")
        self.label_layer = QLabel()
        self.label_layer.setObjectName("label_layer")
        self.horizontalLayout_layer.addWidget(self.label_layer)
        self.layer_list = QLineEdit()
        self.layer_list.setObjectName("layer_list")
        self.horizontalLayout_layer.addWidget(self.layer_list)
        self.verticalLayout_input.insertLayout(2, self.horizontalLayout_layer)
        self.layer_list.setToolTip(self.tr("", "Inserire i numeri dei "
                                            "layer da utilizzare, separati da\n"
                                            " una virgola e partendo da 1 (se\n"
                                            " lasciato vuoto considererà tutti"
                                            " i layer"))
        self.label_layer.setText(self.tr("", "Inserire numero layers"))

    def _insertLayerChooseCheckBox(self):
        self.horizontalLayout_layer2 = QHBoxLayout()
        self.horizontalLayout_layer2.setObjectName("horizontalLayout_layer2")
        self.label_layer2 = QLabel()
        self.label_layer2.setWordWrap(True)
        self.label_layer2.setObjectName("label_layer2")
        self.horizontalLayout_layer2.addWidget(self.label_layer2)
        self.layer_list2 = CheckableComboBox()
        self.layer_list2.setObjectName("layer_list2")
        self.horizontalLayout_layer2.addWidget(self.layer_list2)
        self.verticalLayout_input.insertLayout(2, self.horizontalLayout_layer2)
        self.label_layer2.setText(self.tr("", "Selezionare le bande "
                                             "da utilizzare cliccandoci sopra."))


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

    def _insertThresholdDouble(self, minn, maxx, step, posnum, deci=2):
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
        self.LabelThred.setText(self.tr("", "Seleziona il threshold da utilizzare"))

    def _insertThresholdInteger(self, minn, maxx, step, posnum):
        """Function to add SpinBox Widget for integer number"""
        self.horizontalLayout_threi = QHBoxLayout()
        self.horizontalLayout_threi.setObjectName("horizontalLayout_threi")
        self.LabelThrei = QLabel()
        self.LabelThrei.setObjectName("LabelThrei")
        self.LabelThrei.setWordWrap(True)
        self.horizontalLayout_threi.addWidget(self.LabelThrei)
        self.thresholdi = QDoubleSpinBox()
        self.thresholdi.setObjectName("thresholdd")
        self.thresholdi.setRange(minn, maxx)
        self.thresholdi.setSingleStep(step)
        self.horizontalLayout_threi.addWidget(self.thresholdi)
        self.verticalLayout_options.insertLayout(posnum,
                                                 self.horizontalLayout_threi)
        self.LabelThred.setText(self.tr("", "Seleziona il threshold da utilizzare"))

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

    def _insertFirstCombobox(self, items, label, posnum):
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
        [self.BaseInputCombo.addItem(m) for m in items]
        self.LabelCombo.setText(self.tr("", label))

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
        self.horizontalLayout_textarea.setObjectName(_fromUtf8("horizontalLayout_textarea"))
        self.LabelTextarea = QLabel()
        self.LabelTextarea.setWordWrap(True)
        self.LabelTextarea.setObjectName(_fromUtf8("LabelOut"))
        self.horizontalLayout_textarea.addWidget(self.LabelTextarea)
        self.TextArea = QTextEdit()
        self.TextArea.setObjectName(_fromUtf8("TextArea"))
        self.horizontalLayout_textarea.addWidget(self.TextArea)
        self.verticalLayout_options.insertLayout(posnum,
                                                self.horizontalLayout_textarea)
        self.LabelTextarea.setText(_translate("Dialog", label, None))

    def processError(self, error):
        self.emit(SIGNAL("processError(QProcess::ProcessError)"), error)

    def processFinished(self, exitCode, status):
        self.emit(SIGNAL("processFinished(int, QProcess::ExitStatus)"),
                  exitCode, status)

    # enables the OK button
    def enableRun(self, enable=True):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    def saveCommand(self, command):
        """Save the command in Qsetting"""
        s = QSettings()
        s.setValue("stem/{com}".format(com=self.toolName.replace(' ', '_')),
                   " ".join(command))

    def cutInput(self, inp, source, typ):
        self.mapDisplay(inp, typ)
        s = QSettings()
        mask = s.value("stem/mask", "")
        bbox = self.QGISextent.isChecked()
        if not bbox and not mask:
            return False, False, False
        if bbox and mask:
            self.onError("Sono state impostate sia una maschera vettoriale "
                         "sia una estensione di QGIS. Si prega di "
                         "rimuoverne una delle due")
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
            com.append(out, source)

        runcom = subprocess.Popen(com, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        log, err = runcom.communicate()
        if runcom.returncode != 0:
            raise Exception("Errore eseguendo il ritaglio del file di input: "
                            "Errore eseguendo il comando {err}".format(err=err))

        return outname.strip(), out, mask

    def mapDisplay(self, source, typ):
        render = self.iface.mapCanvas()
        rect = render.extent()
        self.rect_str = [str(rect.xMinimum()), str(rect.yMaximum()),
                         str(rect.xMaximum()), str(rect.yMinimum())]

    def onRunLocal(self):
        pass

    def onRunServer(self):
        QMessageBox.warning(self, "Warning", "Da Implementare")
        pass

    # stop the command execution
    def stop(self):
        self.enableRun(True)
        self.setCursor(Qt.ArrowCursor)
        self.process.kill()

    # called if an error occurs when the command has not already finished,
    # shows the occurred error message
    def onError(self, error):
        # function to return error
        QMessageBox.warning(self.iface.mainWindow(), MSG_BOX_TITLE, str(error))

    def onFinished(self, exitCode, status):
        """called when the command finished its execution, shows an error message if
        there's one and, if required, load the output file in canvas"""
        if status == QProcess.CrashExit:
            self.stop()
            return

        # show the error message if there's one, otherwise show the process
        # output message
        msg = str(self.process.readAllStandardError())
        if msg == '':
            outMessages = str(self.process.readAllStandardOutput()).splitlines()

            # make sure to not show the help
            for m in outMessages:
                m = string.strip(m)
                if m == '':
                    continue

                if msg:
                    msg += "\n"
                msg += m

        QErrorMessage(self).showMessage(msg.replace("\n", "<br>"))

        if exitCode == 0:
            self.emit(SIGNAL("finished(bool)"), self.loadCheckBox.isChecked())

        self.stop()

    def BrowseDir(self):
        """Function to create new file in a directory"""
        mydir = QFileDialog.getSaveFileName(None, "Selezionare la cartella di"
                                            " destinazione", "")
        if not os.path.exists(mydir):
            self.TextOut.setText(mydir)
            return
        else:
            # TODO add overwrite option
            self.onError("'%s' file già presente." % mydir)

    def finished(self, load):
        outFn = self.getOutputFileName()
        if outFn:
            return

        if outFn == '':
            QMessageBox.warning(self, "Warning", "No output file created.")
            return

        fileInfo = QFileInfo(outFn)
        if fileInfo.exists():
            if load:
                self.addLayerIntoCanvas(fileInfo)
            QMessageBox.information(self, "Finished", "Processing completed.")
        else:
            # QMessageBox.warning(self, self.tr( "Warning" ), self.tr( "%1 not created." ).arg( outFn ) )
            QMessageBox.warning(self, "Warning", "%s not created." % outFn)

    def tr(self, context, text):
        if context == '':
            context = 'STEM'
        return QCoreApplication.translate(context, text.decode('utf-8'))

class SettingsDialog(QDialog, Setting_Dialog):

    def __init__(self, parent, iface):
        QDialog.__init__(self, parent)
        self.dialog = Setting_Dialog
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
                     partial(self.BrowseBin, self.lineEdit_gdal))
        self.connect(self.pushButton_liblas, SIGNAL("clicked()"),
                     partial(self.BrowseBin, self.lineEdit_liblas))
        self.connect(self.pushButton_pdal, SIGNAL("clicked()"),
                     partial(self.BrowseBin, self.lineEdit_pdal))
        self.connect(self.pushButton_proj, SIGNAL("clicked()"),
                     partial(self.BrowseDir, self.lineEdit_proj))
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

    def _onLoad(self):
        """Load the parameters from the settings"""
        s = QSettings()
        self.lineEdit_grass.setText(s.value("stem/grasspath", ""))
        self.lineEdit_grassdata.setText(s.value("stem/grassdata", ""))
        self.lineEdit_grasslocation.setText(s.value("stem/grasslocation", ""))
        self.lineEdit_liblas.setText(s.value("stem/liblaspath", ""))
        self.lineEdit_gdal.setText(s.value("stem/gdalpath", ""))
        self.lineEdit_pdal.setText(s.value("stem/pdalpath", ""))
        self.epsg.setText(s.value("stem/epsgcode", ""))
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
        mydir = QFileDialog.getOpenFileName(None, "Selezionare l'eseguibile desiderato",
                                            "")
        if os.path.exists(mydir):
            line.setText(mydir)
            return
        else:
            # TODO add overwrite option
            self.onError("'%s' file già presente." % mydir)

    def BrowseDir(self, line):
        """"""
        mydir = QFileDialog.getExistingDirectory(None, "Selezionare l'eseguibile desiderato",
                                                 "")
        if os.path.exists(mydir):
            line.setText(mydir)
            return
        else:
            # TODO add overwrite option
            self.onError("'%s' file già presente." % mydir)

    def onError(self, error):
        """Function to return error"""
        QMessageBox.warning(self.iface.mainWindow(), MSG_BOX_TITLE, str(error))

    def _reject(self):
        pass

    def _save(self):
        """Save all the keys/values related to stem to a file"""
        s = QSettings()
        keys = [a for a in s.allKeys() if a.find('stem/') != -1]
        # TODO maybe add the possibility to choose where save the file
        import tempfile
        f = tempfile.NamedTemporaryFile(delete=False)
        for k in keys:
            line = "{key}:  {value}\n".format(key=k.split('/')[1],
                                              value=s.value(k, ""))
            f.write(line)
        f.close()
        QMessageBox.warning(self.iface.mainWindow(), MSG_BOX_TITLE,
                            str("Impostazioni salvate nel file " + f.name))

    def _accept(self):
        """Save the variable in QGIS Settings"""
        s = QSettings()
        s.setValue("stem/grasspath", self.lineEdit_grass.text())
        s.setValue("stem/grassdata", self.lineEdit_grassdata.text())
        s.setValue("stem/grasslocation", self.lineEdit_grasslocation.text())
        s.setValue("stem/liblaspath",  self.lineEdit_liblas.text())
        s.setValue("stem/gdalpath", self.lineEdit_gdal.text())
        s.setValue("stem/pdalpath", self.lineEdit_pdal.text())
        s.setValue("stem/epsgcode", self.epsg.text())


class helpDialog(QDialog, Help_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        """Set up the help user interface"""
        self.dialog = Help_Dialog
        #self.iface = iface
        self.setupUi(self)

    def fillfromUrl(self, url):
        """Load a url in the Help window"""
        self.webView.load(QUrl(url))
