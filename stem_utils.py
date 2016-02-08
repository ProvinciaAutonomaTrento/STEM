# -*- coding: utf-8 -*-

"""
Date: August 2014

Authors: Luca Delucchi, Salvatore La Rosa

Copyright: (C) 2014 Luca Delucchi

Some classes useful for the plugin
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
import codecs
import os
import inspect
import re
import tempfile
import shutil
import glob
import logging
import pickle, base64
import time
try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'
try:
    import osgeo.ogr as ogr
except ImportError:
    try:
        import ogr
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'
from stem_utils_server import STEMSettings


class CheckableComboBox(QComboBox):
    """New class to create chackable QComboBox"""
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


class STEMUtils:
    """Class to gather together several functions"""
    registry = QgsMapLayerRegistry.instance()

    @staticmethod
    def getNameFromSource(path):
        """From path return the basename without extension

        :param str path: the full path of source
        """
        base = os.path.basename(path)
        spl = base.split('.')
        return "_".join(spl[:-1])

    @staticmethod
    def addLayerToComboBox(combo, typ, clear=True, empty=False, alls=False,
                           source=False):
        """Add layers to input files list

        :param obj combo: the ComboBox object where add layers
        :param int typ: the type of layers to add, 0 for vector, 1 for raster
        :param bool clear: True to clear the ComboBox
        :param bool empty: True to add a empty record
        :paran str alls: String to add in the layer list
        :param bool source: True to add source instead name
        """
        if clear:
            combo.clear()
        layerlist = []
        layermap = STEMUtils.registry.mapLayers()
        if empty:
            layerlist.append("")
        if alls:
            layerlist.append(alls)
        for name, layer in layermap.iteritems():
            if layer.type() == typ:
                if source:
                    layerlist.append(layer.source())
                else:
                    layerlist.append(layer.name())

        combo.addItems(layerlist)

    @staticmethod
    def getLayer(layerName):
        """Return the layer object starting from the name

        :param str layerName: the name of layer
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

        :param str layerName: the name of layer
        """
        layer = STEMUtils.getLayer(layerName)

        print 'layerName: {} layer: {} '.format(layerName, layer)
        if layer:
            return layer.source()
        else:
            return None

    @staticmethod
    def getLayersType(layerName):
        """Return the type of the layer

        :param str layerName: the name of layer
        """
        layer = STEMUtils.getLayer(layerName)

        if layer:
            return layer.type()
        else:
            return None

    @staticmethod
    def reloadVectorLayer(layerName):
        """Return the type of the layer

        :param str layerName: the name of layer
        """
        layer = STEMUtils.getLayer(layerName)
        source = layer.source()
        STEMUtils.registry.instance().removeMapLayer(layer.id())
        newlayer = QgsVectorLayer(source, layerName, "ogr")
        if newlayer.isValid():
            STEMUtils.registry.instance().addMapLayer(newlayer)
        else:
            STEMMessageHandler.warning("STEM Plugin", "Problema ricaricando "
                                       "il layer {na}".format(na=layerName))

    @staticmethod
    def addLayerIntoCanvas(filename, typ):
        """Add the output in the QGIS canvas

        :param str filename: the name of layer
        :param str typ: the type of data
        """
        # E` necessario un po' di tempo per rilevare l'esistenza del file
        while not QFileInfo(filename).exists():
            time.sleep(.1)
            pass
        print 'Output filename', filename
        layer = QFileInfo(filename)
        layerName = layer.baseName()
        if not layer.exists():
            STEMMessageHandler.error("Problema ricaricando il layer {na}, "
                                     "potrebbe non essere stato scritto "
                                     "correttamente".format(na=layerName))
        if typ == 'raster' or typ == 'image':
            layer = QgsRasterLayer(filename, layerName)
        elif typ == 'vector':
            layer = QgsVectorLayer(filename, layerName, 'ogr')
        if not layer.isValid():
            STEMMessageHandler.error("Problema ricaricando il layer {na}, "
                                     "potrebbe non essere stato scritto "
                                     "correttamente".format(na=layerName))
        else:
            STEMUtils.registry.addMapLayer(layer)

    @staticmethod
    def checkMultiRaster(inmap, checkCombo=None, lineEdit=None):
        """Check if raster is multiband or singleband.

        :param str inmap: the input map
        :param obj checkCombo: a ComboBox object containing the bands of map
        :param obj lineEdit: a lineEdit object containing the bands of map
        """
        nsub = STEMUtils.getNumSubset(inmap)
        nlayerchoose = STEMUtils.checkLayers(inmap, checkCombo, lineEdit)
        if nsub > 0 and nlayerchoose > 1:
            return 'image'
        else:
            return 'raster'

    @staticmethod
    def checkLayers(inmap, form=None, index=True):
        """Function to check if layers are choosen

        :param str inmap: the input map
        :param obj form: a object containing the bands of map
        :param bool index:
        """
        if not form:
            return STEMUtils.getNumSubset(inmap)
        if isinstance(form, QCheckBox) or isinstance(form, CheckableComboBox):
            itemlist = []
            for i in range(form.count()):
                item = form.model().item(i)
                if item.checkState() == Qt.Checked:
                    if index:
                        itemlist.append(str(i + 1))
                    else:
                        itemlist.append(str(item.text()))
            if len(itemlist) == 0:
                try:
                    return STEMUtils.getNumSubset(inmap)
                except:
                    for i in range(form.count()):
                        item = form.model().item(i)
                        if index:
                            itemlist.append(str(i + 1))
                        else:
                            itemlist.append(str(item.text()))
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

        :param obj combo: a ComboBox containing the list of vector files
        :param obj checkCombo: the ComboBox to fill with column's name
        :param bool empty: True to add an empty record
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
    def addColumnsName(combo, checkCombo, multi=False, empty=False):
        """Add the column's name to a ComboBox

        :param obj combo: a ComboBox containing the list of vector files
        :param obj checkCombo: the ComboBox to fill with column's name
        :param bool multi: True if it is a checkableComboBox
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
                if empty:
                    checkCombo.addItem("")
                    item = model.item(i)
                    item.setCheckState(Qt.Unchecked)
                for i in range(len(fields)):
                    model = checkCombo.model()
                    name = fields[i].name()
                    checkCombo.addItem(name)
                    item = model.item(i)
                    item.setCheckState(Qt.Unchecked)
            else:
                if empty:
                    cols.append("")
                [cols.append(i.name()) for i in fields]
                checkCombo.addItems(cols)
            return

    @staticmethod
    def writeFile(text, name=False):
        """Write the the into a file

        :param str text: the text to write into file
        :param str name: the path of the file, without name it create a file
                         using tempfile functions
        """
        if name:
            fs = open(name, 'w')
        else:
            f = tempfile.NamedTemporaryFile(delete=False)
            name = f.name
            fs = f.file
        fs.write(text)
        fs.close()
        return name

    @staticmethod
    def fileExists(fileName):
        """Check if a file already exist

        :param str fileName: the path of file
        """
        if QFileInfo(fileName).exists():
            res = QMessageBox.question(None, "STEM Plugin", u"Esiste già un "
                                       "file con nome {0}. Sostituirlo?".format(QFileInfo(fileName).baseName()),
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if res == QMessageBox.Yes:
                return True, True
            else:
                return False, False
        return True, False

    @staticmethod
    def renameRast(tmp, out):
        """Rename a raster file

        :param str tmp: the temporary file name
        :param str out: the final output file name
        """
        print 'stem_utils renameRast', tmp, out

        t = time.time()
        while not os.path.isfile(tmp):
            if time.time()-t > 5:
                raise Exception("Il file di output non è stato creato: {}".format(tmp))
            time.sleep(.1)
        
        shutil.move(tmp, out)
        try:
            shutil.move('{name}.aux.xml'.format(name=tmp),
                        '{name}.aux.xml'.format(name=out))
        except:
            pass

    @staticmethod
    def removeFiles(path, pref="stem_cut_*"):
        """Remove file from path with prefix

        :param str path: the directory where remove files
        :param str pref: the prefix for the file to remove
        """
        files = glob.glob1(path, pref)
        for f in files:
            f = os.path.join(path, f)
            try:
                shutil.rmtree(f)
            except:
                try:
                    os.remove(f)
                except:
                    continue


    @staticmethod
    def exportGRASS(gs, overwrite, output, tempout, typ, remove=True):
        """Export data from GRASS environment

        :param obj gs: a stemGRASS object
        :param bool overwrite: overwrite existing files
        :param str output: the output path
        :param str tempout: the temporary output inside GRASS
        :param str typ: the type of data
        :param bool remove: True to remove the mapset, otherwise it is kept
        """
        original_dir = os.path.dirname(output)
        if typ == 'vector':

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
            try:
                gs.export_grass(tempout, output, typ, remove)
            except Exception as e:
                print 'gs.export_grass error:', e
        STEMUtils.removeFiles(original_dir)

    @staticmethod
    def getNumSubset(name):
        """Return a list with the subsets of a raster

        :param str name: the name of raster map
        """
        src_ds = gdal.Open(str(name))
        if len(src_ds.GetSubDatasets()) != 0:
            return [str(i) for i in range(1, src_ds.GetSubDatasets() + 1)]
        else:
            return [str(i) for i in range(1, src_ds.RasterCount + 1)]

    @staticmethod
    def saveParameters():
        """Save all the keys/values stem related into a file"""
        keys = [a for a in STEMSettings.allKeys()]
        # TODO maybe add the possibility to choose where save the file
        f = tempfile.NamedTemporaryFile(delete=False)
        for k in keys:
            line = "{key}:  {value}\n".format(key=k,
                                              value=STEMSettings.value(k, ""))
            f.write(line)
        f.close()
        STEMMessageHandler.information("STEM Plugin", 'Impostazioni salvate '
                                       'nel file {0}'.format(f.name))

    @staticmethod
    def splitIntoList(st, sep=' '):
        """Split a text into a list, splitting using the sep value

        :param str st: the string to split
        :param str sep: the character to use to split
        """
        if st:
            st = st.strip()
            return st.split(sep)
        else:
            return None

    @staticmethod
    def saveCommand(command, details=None):
        """Save the command history to file

        :param list command: the list of all parameter used
        """
        historypath = os.path.join(QgsApplication.qgisSettingsDirPath(),
                                   "stem", "stem_command_history.txt")

        hFile = codecs.open(historypath, 'a', encoding='utf-8')
        if details is not None:
            hFile.write('# {}\n'.format(details))
        hFile.write(" ".join(command) + '\n')
        hFile.close()

    @staticmethod
    def stemMkdir():
        """Create the directory to store some files of STEM project.
        It's create in ~/.qgis2
        """
        home = os.path.join(QgsApplication.qgisSettingsDirPath(), "stem")
        if not os.path.exists(home):
            os.mkdir(home)
        STEMSettings.setValue('stempath', home)

    @staticmethod
    def copyFile(inp, outfile):
        """Copy a file in the same directory of output file"""
        path = os.path.dirname(outfile)
        inp = str(inp)
        if os.path.exists(inp):
            if os.path.exists(path):
                shutil.copy2(inp, path)
            else:
                os.makedirs(path)
                shutil.copy2(inp, path)

    @staticmethod
    def pathClientWinToServerLinux(path, inp=True):
        """Convert path from windows to linux for client and server connection

        :param str path: the path to rename
        :param bool inp: DEPRECATED
        """

        table = STEMSettings.value("mappingTable", None)
        if table:
            table = [x for x in pickle.loads(base64.b64decode(table)) if len(x)==2 and x[0] and x[1]] # [[remote0,local0],[rlocal,remote1]]
        else:
            table = []

        converted = False
        print 'table:', table
        for remote, local in table:
            try:
                path = os.path.join(remote, os.path.relpath(path, local)).replace('\\','/')
            except Exception as e:
                pass
            else:
                converted = True
        if not converted:
            STEMMessageHandler.warning("STEM Plugin", 'Percorso non convertibile,'
                                       ' potrebbero esserci problemi nelle '
                                       'prossimi analisi')
        return path
        # try:
        #     if inp or not STEMSettings.value("datalocal", ""):
        #         old_local = STEMSettings._check(STEMSettings.value("datalocal",
        #                                                            ""))
        #         old_server = STEMSettings._check(STEMSettings.value("dataserver",
        #                                                             ""))
        #     else:
        #         old_local = STEMSettings._check(STEMSettings.value("outdatalocal",
        #                                                            ""))
        #         old_server = STEMSettings._check(STEMSettings.value("outdataserver",
        #                                                            ""))
        #
        #     old = os.path.relpath(path, old_local)
        #     new = os.path.join(old_server, old)
        #     new = new.replace("\\", "/")
        # except:
        #     STEMMessageHandler.warning("STEM Plugin", 'Percorso non convertibile,'
        #                                ' potrebbero esserci problemi nelle '
        #                                'prossimi analisi')
        #     new = path
        # return new


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
    try:
        messageTime = iface.messageTimeout()
    except:
        pass

    @staticmethod
    def information(title="", text="", timeout=0):
        """Function used to display an information message

        :param str title: the title of message
        :param str text: the text of message
        :param int timeout: timeout duration of message in seconds
        """
        level = STEMMessageHandler.messageLevel[0]
        if timeout:
            timeout = STEMMessageHandler.messageTime
        STEMMessageHandler.messageBar(title, text, level, timeout)

    @staticmethod
    def warning(title="", text="", timeout=0):
        """Function used to display a warning message

        :param str title: the title of message
        :param str text: the text of message
        :param int timeout: timeout duration of message in seconds
        """
        level = STEMMessageHandler.messageLevel[1]
        if timeout:
            timeout = STEMMessageHandler.messageTime
        STEMMessageHandler.messageBar(title, text, level, timeout)

    @staticmethod
    def critical(title="", text="", timeout=0):
        """Function used to display a critical message

        :param str title: the title of message
        :param str text: the text of message
        :param int timeout: timeout duration of message in seconds
        """
        level = STEMMessageHandler.messageLevel[2]
        if timeout:
            timeout = STEMMessageHandler.messageTime
        STEMMessageHandler.messageBar(title, text, level, timeout)

    @staticmethod
    def success(title="", text="", timeout=0):
        """Function used to display a succeded message

        :param str title: the title of message
        :param str text: the text of message
        :param int timeout: timeout duration of message in seconds
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

        :param str message: the text of message
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
            try:
                iface.messageBar().pushMessage(title.decode('utf-8'),
                                               text.decode('utf-8'), level,
                                               timeout)
            except Exception:
                iface.messageBar().pushMessage(str(title), str(text), level,
                                               timeout)
        else:
            try:
                iface.messageBar().pushMessage(text.decode('utf-8'), level,
                                               timeout)
            except Exception:
                iface.messageBar().pushMessage(str(text), level,
                                               timeout)

class STEMLogging:
    """Class to log information of modules in a file"""

    def __init__(self, logname=None):
        if logname:
            logfile = logname
        else:
            stempath = STEMSettings.value("stempath")
            logfile = os.path.join(stempath, 'stem.log')
        logging.basicConfig(filename=logfile, filemode='w',
                            level=logging.DEBUG)

    def debug(self, text):
        logging.debug(text)

    def warning(self, text):
        logging.warning(text)

    def info(self, text):
        logging.info(text)
