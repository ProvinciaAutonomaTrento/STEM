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

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

from grass_stem import stemGRASS
import os
import inspect
import re
import tempfile
import stem_base_dialogs

try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'


class STEMUtils:
    """Class to gather together several functions"""
    registry = QgsMapLayerRegistry.instance()

    @staticmethod
    def addLayerToComboBox(combo, typ, clear=True, empty=False):
        """Add layers to input files list

        :param combo obj: the ComboBox object where add layers
        :param typ str: the type of layers to add
        :param clear bool: True to clear the ComboBox
        :param empty bool: True to add a empty record
        """
        if clear:
            combo.clear()
        layerlist = []
        layermap = STEMUtils.registry.mapLayers()
        if empty:
            layerlist.append("")
        for name, layer in layermap.iteritems():
            if layer.type() == typ:
                layerlist.append(layer.name())

        combo.addItems(layerlist)

    @staticmethod
    def getLayer(layerName):
        """Return the layer object starting from the name

        :param layerName str: the name of layer
        """
        layermap = STEMUtils.registry.mapLayers()

        for name, layer in layermap.iteritems():
            if layer.name() == layerName:
                if layer.isValid():
                    return layer
                else:
                    return None

    @staticmethod
    def getLayersSource(layerName):
        """Return the source path of the layer

        :param layerName str: the name of layer
        """
        layer = STEMUtils.getLayer(layerName)

        if layer:
            return layer.source()
        else:
            return None

    @staticmethod
    def getLayersType(layerName):
        """Return the type of the layer

        :param layerName str: the name of layer
        """
        layer = STEMUtils.getLayer(layerName)

        if layer:
            return layer.type()
        else:
            return None

    @staticmethod
    def addLayerIntoCanvas(filename, typ):
        """Add the output in the QGIS canvas

        :param filename str: the name of layer
        :param typ str: the type of data
        """
        layerName = QFileInfo(filename).baseName()
        if typ == 'raster' or typ == 'image':
            layer = QgsRasterLayer(filename, layerName)
        elif typ == 'vector':
            layer = QgsVectorLayer(filename, layerName, 'ogr')
        if not layer.isValid():
            print "Layer failed to load!"
        else:
            STEMUtils.registry.addMapLayer(layer)

    @staticmethod
    def checkMultiRaster(inmap, checkCombo=None, lineEdit=None):
        """Check if raster is multiband or singleband.

        :param inmap str: the input map
        :param checkCombo obj: a ComboBox object containing the bands of map
        :param lineEdit obj: a lineEdit object containing the bands of map
        """
        nsub = STEMUtils.getNumSubset(inmap)
        nlayerchoose = STEMUtils.checkLayers(inmap, checkCombo, lineEdit)
        if nsub > 0 and nlayerchoose > 1:
            return 'image'
        else:
            return 'raster'

    @staticmethod
    def checkLayers(inmap, form, index=True):
        """Function to check if layers are choosen

        :param inmap str: the input map
        :param form obj: a object containing the bands of map
        :param index bool:
        """
        if isinstance(form, QCheckBox) or isinstance(form, stem_base_dialogs.CheckableComboBox):
            itemlist = []
            for i in range(form.count()):
                item = form.model().item(i)
                if item.checkState() == Qt.Checked:
                    if index:
                        itemlist.append(str(i + 1))
                    else:
                        itemlist.append(str(item.text()))
            if len(itemlist) == 0:
                return STEMUtils.getNumSubset(inmap)
            return itemlist
        elif isinstance(form, QComboBox):
            first = form.itemText(0)
            if index:
                val = form.currentIndex()
                if val == 0 and first == "Seleziona banda":
                    return None
                elif val != 0 and first == "Seleziona banda":
                    return val + 2
                elif first != "Seleziona banda":
                    return val + 1
            else:
                return form.currentText()

        elif isinstance(form, QLineEdit):
            if form.text() == u'':
                return STEMUtils.getNumSubset(inmap)
            else:
                return form.text().split(',')

    @staticmethod
    def addLayersNumber(combo, checkCombo=None, empty=False):
        """Add the subsets name  of a rasterto a ComboBox

        :param combo obj: a ComboBox containing the list of vector files
        :param checkCombo obj: the ComboBox to fill with column's name
        :param empty bool: True to add an empty record
        """
        layerName = combo.currentText()
        if not layerName:
            return
        else:
            source = STEMUtils.getLayersSource(layerName)
        gdalF = gdal.Open(source)
        gdalBands = gdalF.RasterCount
        gdalMeta = None
        checkCombo.clear()
        i = 1
        if gdalF.GetDriver().LongName == 'ENVI .hdr Labelled':
            gdalMeta = gdalF.GetMetadata_Dict()
        if empty:
            checkCombo.addItem("Seleziona banda")
            model = checkCombo.model()
            item = model.item(0)
            item.setCheckState(Qt.Unchecked)
            i += 1
        for n in range(1, gdalBands + 1):
            st = "Banda {i}".format(i=n)
            if gdalMeta:
                try:
                    band = gdalMeta["Band_{i}".format(i=n)].split()
                    st += " {mm} {nano}".format(mm=" ".join(band[2:5]),
                                                nano=" ".join(band[-2:]))
                except:
                    pass
            checkCombo.addItem(st)
            model = checkCombo.model()
            if empty:
                item = model.item(n + 2 - i)
            else:
                item = model.item(n - i)
            item.setCheckState(Qt.Unchecked)

    @staticmethod
    def addColumnsName(combo, checkCombo, multi=False):
        """Add the column's name to a ComboBox

        :param combo obj: a ComboBox containing the list of vector files
        :param checkCombo obj: the ComboBox to fill with column's name
        :param multi bool: True if it is a checkableComboBox
        """
        layerName = combo.currentText()
        cols = []
        if not layerName:
            checkCombo.clear()
            return
        else:
            checkCombo.clear()
            layer = STEMUtils.getLayer(layerName)
            data = layer.dataProvider()
            fields = data.fields()
            if multi:
                for i in range(len(fields)):
                    model = checkCombo.model()
                    name = fields[i].name()
                    checkCombo.addItem(name)
                    item = model.item(i)
                    item.setCheckState(Qt.Unchecked)
            else:
                [cols.append(i.name()) for i in fields]
                checkCombo.addItems(cols)
            return

    @staticmethod
    def writeFile(text, name=False):
        """Write the the into a file

        :param text str: the text to write into file
        :param name str: the path of the file, without name it create a file
                         using tempfile functions
        """
        if name:
            fs = open(name, 'w')
        else:
            f = tempfile.NamedTemporaryFile()
            name = f.name
            fs = f.file
        fs.write(text)
        fs.close()
        return name

    @staticmethod
    def fileExists(fileName):
        """Check if a file already exist

        :param fileName str: the path of file
        """
        if QFileInfo(fileName).exists():
            res = QMessageBox.question(None, "STEM Plugin", u"Esiste già un "
                                       "file con nome {0}. Sostituirlo?".format(QFileInfo(fileName).baseName()),
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if res:
                return True
        return False

    @staticmethod
    def renameRast(tmp, out):
        """Rename a raster file

        :param tmp str: the temporary file name
        :param out str: the final output file name
        """
        os.rename(tmp, out)
        try:
            os.rename('{name}.aux.xml'.format(name=tmp),
                      '{name}.aux.xml'.format(name=out))
        except:
            pass

    @staticmethod
    def removeFiles(path, pref="stem_cut_*"):
        """Remove file from path with prefix

        :param path str: the directory where remove files
        :param pref str: the prefix for the file to remove
        """
        import glob
        files = glob.glob1(path, pref)
        for f in files:
            shutil.rmtree(out)


    @staticmethod
    def exportGRASS(gs, overwrite, output, tempout, typ):
        """Export data from GRASS environment

        :param gs obj: a stemGRASS object
        :param overwrite bool:
        :param output str:
        :param tempout str:
        :param typ str:
        """
        original_dir = os.path.dirname(output)
        if typ == 'vector' and overwrite:
            import shutil

            newdir = os.path.join(tempfile.gettempdir(), "shpdir")
            if not os.path.exists(newdir):
                os.mkdir(newdir)
            original_basename = os.path.basename(output)
            tmp = os.path.join(newdir, original_basename)
            try:
                gs.export_grass(tempout, tmp, typ)
                saved = True
            except:
                return
            if saved:
                files = os.listdir(newdir)
                for f in files:
                    try:
                        p = os.path.join(newdir, f)
                        shutil.copy(p, original_dir)
                    except:
                        return
            shutil.rmtree(newdir)
            STEMUtils.removeFiles(newdir)
        else:
            if overwrite:
                tmp = output + '.tmp'
            else:
                tmp = output
            try:
                gs.export_grass(tempout, tmp, typ)
            except:
                pass
            if overwrite:
                STEMUtils.renameRast(tmp, output)
        STEMUtils.removeFiles(original_dir)

    @staticmethod
    def QGISettingsGRASS(grassdatabase=None, location=None, grassbin=None,
                         epsg=None):
        """Read the QGIS's settings and obtain information for GRASS GIS

        :param grassdatabase str: the path to grassdatabase
        :param location str: the name of location
        :param grassbin str: the path to grass7 binary
        :param epsg str: the epsg code to use
        """
        # query GRASS 7 itself for its GISBASE
        # we assume that GRASS GIS' start script is available and in the PATH
        if not grassbin:
            grassbin = str(STEMSettings.value("grasspath", ""))
        if not grassdatabase:
            grassdatabase = str(STEMSettings.value("grassdata", ""))
        if not location:
            location = str(STEMSettings.value("grasslocation", ""))
        if not epsg:
            epsg = str(STEMSettings.value("epsgcode", ""))

        return grassdatabase, location, grassbin, epsg

    @staticmethod
    def temporaryFilesGRASS(name):
        """Create temporary grass information (input and output data name and
        a stemGRASS object)

        :param name str: the name of input map
        """
        pid = os.getpid()
        tempin = 'stem_{name}_{pid}'.format(name=name, pid=pid)
        tempout = 'stem_output_{pid}'.format(pid=pid)
        grassdatabase, location, grassbin, epsg = STEMUtils.QGISettingsGRASS()
        gs = stemGRASS(pid, grassdatabase, location, grassbin, epsg)
        return tempin, tempout, gs

    @staticmethod
    def getNumSubset(name):
        """Return a list with the subsets of a raster

        :param name str: the name of raster map
        """
        src_ds = gdal.Open(name)
        if len(src_ds.GetSubDatasets()) != 0:
            return [str(i) for i in range(1, src_ds.GetSubDatasets() + 1)]
        else:
            return [str(i) for i in range(1, src_ds.RasterCount + 1)]

    @staticmethod
    def saveParameters():
        """Save all the keys/values stem related into a file"""
        keys = [a for a in STEMSettings.allKeys()]
        # TODO maybe add the possibility to choose where save the file
        import tempfile
        f = tempfile.NamedTemporaryFile(delete=False)
        for k in keys:
            line = "{key}:  {value}\n".format(key=k,
                                              value=STEMSettings.value(k, ""))
            f.write(line)
        f.close()
        STEMMessageHandler.information("STEM Plugin", 'Impostazioni salvate '
                                       'nel file {0}'.format(f.name))


class STEMMessageHandler:
    """
    Handler of message notification via QgsMessageBar to display
    non-blocking messages to the user.

    STEMMessageHandler.[information, warning, critical, success](title, text, timeout)
    STEMMessageHandler.[information, warning, critical, success](title, text)
    STEMMessageHandler.error(message)
    """

    messageLevel = [QgsMessageBar.INFO,
                    QgsMessageBar.WARNING,
                    QgsMessageBar.CRITICAL]

    ## SUCCESS was introduced in 2.7
    ## if it throws an AttributeError INFO will be used
    try:
        messageLevel.append(QgsMessageBar.SUCCESS)
    except:
        pass
    messageTime = iface.messageTimeout()

    @staticmethod
    def information(title="", text="", timeout=0):
        """Function used to display an information message

        :param title str: the title of message
        :param text str: the text of message
        :param timeout int: timeout duration of message in seconds
        """
        level = STEMMessageHandler.messageLevel[0]
        if timeout:
            timeout = STEMMessageHandler.messageTime
        STEMMessageHandler.messageBar(title, text, level, timeout)

    @staticmethod
    def warning(title="", text="", timeout=0):
        """Function used to display a warning message

        :param title str: the title of message
        :param text str: the text of message
        :param timeout int: timeout duration of message in seconds
        """
        level = STEMMessageHandler.messageLevel[1]
        if timeout:
            timeout = STEMMessageHandler.messageTime
        STEMMessageHandler.messageBar(title, text, level, timeout)

    @staticmethod
    def critical(title="", text="", timeout=0):
        """Function used to display a critical message

        :param title str: the title of message
        :param text str: the text of message
        :param timeout int: timeout duration of message in seconds
        """
        level = STEMMessageHandler.messageLevel[2]
        if timeout:
            timeout = STEMMessageHandler.messageTime
        STEMMessageHandler.messageBar(title, text, level, timeout)

    @staticmethod
    def success(title="", text="", timeout=0):
        """Function used to display a succeded message

        :param title str: the title of message
        :param text str: the text of message
        :param timeout int: timeout duration of message in seconds
        """
        ## SUCCESS was introduced in 2.7
        ## if it throws an AttributeError INFO will be used
        try:
            level = STEMMessageHandler.messageLevel[3]
        except:
            level = STEMMessageHandler.messageLevel[0]
        if timeout:
            timeout = STEMMessageHandler.messageTime
        STEMMessageHandler.messageBar(title, text, level, timeout)

    @staticmethod
    def error(message):
        """Function used to display an error message

        :param message str: the text of message
        """
        ## TODO: add an action to message bar to trigger the Log Messages Viewer
        # button = QToolButton()
        # action = QAction(button)
        # action.setText("Apri finestra dei logs")
        # button.setCursor(Qt.PointingHandCursor)
        # button.setStyleSheet("background-color: rgba(255, 255, 255, 0); color: black; "
        #                   "text-decoration: underline;")
        # button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        # button.addAction(action)
        # button.setDefaultAction(action)
        # level = STEMMessageHandler.messageLevel[1]
        # messageBarItem = QgsMessageBarItem(u"Error", u"Un errore è avvenuto, controllare i messaggi di log",
        #                                 button, level, 0, iface.messageBar())
        #
        # iface.messageBar().pushItem(messageBarItem)

        STEMMessageHandler.warning("STEM",
                                   "Errore! Controllare i messaggi di log di QGIS", 0)
        QgsMessageLog.logMessage(message, "STEM Plugin")

    @staticmethod
    def messageBar(title, text, level, timeout):
        if title:
            iface.messageBar().pushMessage(title.decode('utf-8'),
                                           text.decode('utf-8'), level,
                                           timeout)
        else:
            iface.messageBar().pushMessage(text.decode('utf-8'), level,
                                           timeout)


class STEMSettings:
    """
    Class to save and to restore settings to QSettings

    STEMSettings.saveWidgetsValue(ui, QSettings("STEM", "STEM"), toolName)
    STEMSettings.restoreWidgetsValue(ui, QSettings("STEM", "STEM"), toolName)
    """
    s = QSettings("STEM", "STEM")

    @staticmethod
    def saveWidgetsValue(ui, tool=""):
        """Save the parameters used into a tool in the STEMSettings

        :param ui obj: the obkect of tool's UI
        :param tool str: the name of the tool
        """
        if tool:
            tool = re.sub(r"[^\w\s]", '', tool)
            tool = re.sub(r"\s+", '_', tool)

        for name, obj in inspect.getmembers(ui):
            if isinstance(obj, QComboBox):
                name = obj.objectName()
                index = obj.currentIndex()
                text = obj.itemText(index)
                STEMSettings.setValue(tool + "/" + name, text)

            if isinstance(obj, QLineEdit):
                name = obj.objectName()
                value = obj.text()
                STEMSettings.setValue(tool + "/" + name, value)

            if isinstance(obj, QCheckBox):
                name = obj.objectName()
                state = obj.isChecked()
                STEMSettings.setValue(tool + "/" + name, state)

    @staticmethod
    def restoreWidgetsValue(ui, tool=""):
        """Restore the parameters used earlier into a tool in the STEMSettings

        :param ui obj: the obkect of tool's UI
        :param tool str: the name of the tool
        """
        if tool:
            tool = re.sub(r"[^\w\s]", '', tool)
            tool = re.sub(r"\s+", '_', tool)

        if not tool in STEMSettings.s.childGroups():
            return

        for name, obj in inspect.getmembers(ui):
            if isinstance(obj, QComboBox):
                index = obj.currentIndex()
                #text   = obj.itemText(index)
                name = obj.objectName()

                value = STEMSettings.value(tool + "/" + name, "", unicode)
                if value == "":
                    continue

                index = obj.findText(value)
                if index == -1:
                    continue
                    #obj.insertItems(0,[value])
                    #index = obj.findText(value)
                    #obj.setCurrentIndex(index)
                else:
                    obj.setCurrentIndex(index)

            if isinstance(obj, QLineEdit):
                name = obj.objectName()
                value = STEMSettings.value(tool + "/" + name, "", unicode)
                if value:
                    obj.setText(value)

            if isinstance(obj, QCheckBox):
                name = obj.objectName()
                value = STEMSettings.value(tool + "/" + name, True, bool)
                if value is not None:
                    obj.setChecked(value)

    @staticmethod
    def setValue(key, value):
        """Set the value for the given key"""
        return STEMSettings.s.setValue(key, value)

    @staticmethod
    def value(key, default=None, type=None):
        """Return the value of the given key"""
        if default and type:
            return STEMSettings.s.value(key, default, type=type)
        elif default and not type:
            return STEMSettings.s.value(key, default)
        else:
            return STEMSettings.s.value(key)

    @staticmethod
    def allKeys():
        """Return all keys of STEMSettings"""
        return STEMSettings.s.allKeys()
