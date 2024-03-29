# -*- coding: utf-8 -*-

"""
Date: December 2020

Authors: Trilogis

Copyright: (C) 2020 Trilogis

Some classes useful for the plugin
"""
from __future__ import print_function

from builtins import str
from builtins import range
from builtins import object

from qgis.core import Qgis, QgsApplication
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsProject
from STEM.libs.libsmop import false

__author__ = 'Trilogis'
__date__ = 'december 2020'
__copyright__ = '(C) 2020 Trilogis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import codecs
import os
import sys
import inspect
import re
import tempfile
import shutil
import glob
import logging
import pickle, base64
import time
import subprocess
from collections import namedtuple
import json
from shutil import rmtree

import qgis.core
from qgis.core import QgsRasterLayer
import qgis.gui
from qgis.utils import iface
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

from osgeo import ogr, osr

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from stem_utils_server import STEMSettings
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsMapLayer

#○class CheckableComboBox(QgsMapLayerComboBox):
#    """New class to create chackable QComboBox"""
#    def __init__(self):
#        super(CheckableComboBox, self).__init__()
#        self.view().pressed.connect(self.handleItemPressed)
#        self.setModel(QStandardItemModel(self))
#        self.setModel(QStandardItemModel(self))
#
#    def handleItemPressed(self, index):
#        item = self.model().itemFromIndex(index)
#        item = self.model().itemFromIndex(index)
#        if item.checkState() == Qt.Checked:
#            item.setCheckState(Qt.Unchecked)
#        else:
#            item.setCheckState(Qt.Checked)

class CheckableComboBox(QComboBox):

    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = qApp.palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event):

        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res



PathMapping = namedtuple('PathMapping', 'remote local')

class STEMUtils(object):
    """Class to gather together several functions"""
    registry = QgsProject.instance()

    @staticmethod
    def getNameFromSource(path):
        """From path return the basename without extension

        :param str path: the full path of source
        """
        base = os.path.basename(path)
        spl = base.split('.')
        
        if ("_".join(spl[:-1]) != ""):
            return "_".join(spl[:-1])
        else:
            return base
         

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
        
        if typ == 0:
            enum_typ = QgsMapLayer.VectorLayer;
        if typ == 1:
            enum_typ = QgsMapLayer.RasterLayer;
        
        for name, layer in list(layermap.items()):
            if layer.type() == enum_typ:
                if source:
                    print("- " + str(layer.source()))
                    layerlist.append(layer.source())
                else:
                    print("- " + str(layer.name()))
                    layerlist.append(layer.name())

        combo.addItems(layerlist)
        
    @staticmethod
    def addLayerToTable(table, all=False):
        table.clearContents()
        layerlist = []
        layermap = STEMUtils.registry.mapLayers()
        for _, layer in list(layermap.items()):
            # 1 is 'raster' in the LayerType enum
            if (layer.type() == 1) or (all is True):
                layerlist.append(layer.source())
        position = 0
        
        for fil in layerlist:
     
            fil = fil.replace("\\","/")
            
            if os.path.exists(fil):
                table.insertRow(position)
                
                item = QTableWidgetItem(fil)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                table.setItem(position, 0, item)
                
                names = STEMUtils.getNameFromSource(fil)
                tipo = STEMUtils.getLayersType(names)
                
                if tipo == 1:
                
                  
                    try:
                        rast = gdal.Open(fil)
                        
                       
                       # proj = osr.SpatialReference(wkt=rast.GetProjection())
                       # epsg = proj.GetAttrValue('AUTHORITY',1)
                        
                        layer = QgsProject.instance().mapLayersByName(names)[0]
                        
                        
                        epsg = layer.crs().authid()
                        
                        item = QTableWidgetItem(epsg)
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(position, 1, item)
                        
                        #table.setItem(position, 1, QTableWidgetItem((epsg)))
                    except:
                        item = QTableWidgetItem("Non disponibile")
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(position, 1, item)
                        
                        #table.setItem(position, 1, QTableWidgetItem("Non disponibile"))
                  
                    try:
                        rast = gdal.Open(fil)
                        band = rast.GetRasterBand(1)
                        nodata = band.GetNoDataValue()
                        
                        item = QTableWidgetItem(str(nodata))
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(position, 2, item)
                        
                        #table.setItem(position, 2, QTableWidgetItem(str(nodata)))
                    except:
                        #table.setItem(position, 2, QTableWidgetItem("Non disponibile"))
                        
                        item = QTableWidgetItem("Non disponibile")
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(position, 2, item)
                    try:
                        rast = gdal.Open(fil)
                        num_bands = rast.RasterCount
                        
                        item = QTableWidgetItem(str(num_bands))
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(position, 3, item)
                        
                        #table.setItem(position, 3, QTableWidgetItem(str(num_bands)))
                    except:
                        #table.setItem(position, 3, QTableWidgetItem("Non disponibile"))
                    
                        item = QTableWidgetItem("Non disponibile")
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(position, 3, item)
                    try:
                        table.setItem(position, 4, QTableWidgetItem(str("")))
                    except:
                        table.setItem(position, 4, QTableWidgetItem(""))
                        
                        
                if tipo == 0:
                
                    try:
                        vect = ogr.Open(fil)
                        
                        # from Layer
                        layer = vect.GetLayer()
                        spatialRef = layer.GetSpatialRef()
                        
                        ## from Geometry
                        #feature = layer.GetNextFeature()
                        #geom = feature.GetGeometryRef()
                        #spatialRef = geom.GetSpatialReference()
                        
                        epsg = spatialRef.GetAttrValue('AUTHORITY',1)
                        
                        layer = QgsProject.instance().mapLayersByName(names)[0]
                        
                  #      crs = layer.crs()
                  #      layer.setName('{} - ({}) - ({}) - ({})'.format(layer.name(), crs.authid(), crs.srsid(),crs.postgisSrid()))
                
                        
                        
                        item = QTableWidgetItem(epsg)
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(position, 1, item)
                        
                        #table.setItem(position, 1, QTableWidgetItem((epsg)))
                    except:
                        item = QTableWidgetItem("Non disponibile")
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(position, 1, item)
                        
                        
                        
                        
                        #table.setItem(position, 1, QTableWidgetItem((epsg)))
                    #except:
                     #   table.setItem(position, 1, QTableWidgetItem("Non disponibile"))
                  
                  
                    item = QTableWidgetItem("Non disponibile")
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    table.setItem(position, 2, item)
                    table.setItem(position, 3, item)
                    table.setItem(position, 4, item)
                    
                    #table.setItem(position, 2, QTableWidgetItem("Non disponibile"))
                        
                    #table.setItem(position, 3, QTableWidgetItem("Non disponibile"))
                    
                    #table.setItem(position, 4, QTableWidgetItem(""))
                        
                    
                table.resizeColumnsToContents()
                position += 1

    @staticmethod
    def addLayerIntoCanvasMaxMin(filename):
        t = time.time()
        while not QFileInfo(filename).exists():
            if time.time()-t > 5:
                STEMMessageHandler.error("{ou} file does not appear to exist".format(ou=filename))
                return
            time.sleep(.1)
        layer = QFileInfo(filename)
        layerName = layer.baseName()
        if not layer.exists():
            STEMMessageHandler.error("Problema ricaricando il layer {na}, "
                                     "potrebbe non essere stato scritto "
                                     "correttamente".format(na=layerName))

        layer = QgsRasterLayer(filename, layerName)
        renderer = layer.renderer()
        provider = layer.dataProvider()
        layer_extent = layer.extent()
        uses_band = renderer.usesBands()
        myType = renderer.dataType(uses_band[0])
        stats = provider.bandStatistics(uses_band[0],
                                        QgsRasterBandStats.All,
                                        layer_extent,
                                        0)
        myEnhancement = QgsContrastEnhancement(myType)
        contrast_enhancement = QgsContrastEnhancement.StretchToMinimumMaximum

        myEnhancement.setContrastEnhancementAlgorithm(contrast_enhancement,True)
        myEnhancement.setMinimumValue(stats.minimumValue)
        myEnhancement.setMaximumValue(stats.maximumValue)

        layer.renderer().setContrastEnhancement(myEnhancement)

        #if not layer.checkExpression():
        if not layer.isValid():
            STEMMessageHandler.error("Problema ricaricando il layer {na}, "
                                     "potrebbe non essere stato scritto "
                                     "correttamente".format(na=layerName))
        else:
            STEMUtils.registry.addMapLayer(layer)

    @staticmethod
    def getLayer(layerName):
        """Return the layer object starting from the name

        :param str layerName: the name of layer
        """
        layermap = STEMUtils.registry.mapLayers()

        for name, layer in list(layermap.items()):
            if layer.name() == layerName:
                #if layer.checkExpression():
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

        #print 'layerName: {} layer: {} '.format(layerName, layer)
        if layer:
            return str(layer.source())
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
        #if newlayer.checkExpression():
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
        t = time.time()
        while not QFileInfo(filename).exists():
            if time.time()-t > 5:
                STEMMessageHandler.error("{ou} file does not appear to exist".format(ou=filename))
                return
            time.sleep(.1)
        print('Output filename', filename)
        layer = QFileInfo(filename)
        layerName = layer.baseName()
        print("layerName: " + layerName)
        if not layer.exists():
            STEMMessageHandler.error("Problema ricaricando il layer {na}, "
                                     "potrebbe non essere stato scritto "
                                     "correttamente".format(na=layerName))
        if typ == 'raster' or typ == 'image':
            layer = QgsRasterLayer(filename, layerName)
        elif typ == 'vector':
            layer = QgsVectorLayer(filename, layerName, 'ogr')
        #if not layer.checkExpression():
        if not layer.isValid():
            print("layer is not valid")
            STEMMessageHandler.error("Problema ricaricando il layer {na}, "
                                     "potrebbe non essere stato scritto "
                                     "correttamente".format(na=layerName))
        else:
            STEMUtils.registry.addMapLayer(layer)

    @staticmethod
    def validinput(prompt):
        """Function to valid

        :param int prompt: the input 
        """
        while True:
            try:
                value = int(prompt) 
                return value
            except ValueError:
                return 0

    @staticmethod
    def checkMultiRaster(inmap, checkCombo=None, lineEdit=None):
        """Check if raster is multiband or singleband.

        :param str inmap: the input map
        :param obj checkCombo: a ComboBox object containing the bands of map
        :param obj lineEdit: a lineEdit object containing the bands of map
        """
        nsub = STEMUtils.getNumSubset(inmap)
        nlayerchoose = STEMUtils.checkLayers(inmap, checkCombo, lineEdit)
        
        #if nsub > 0 and nlayerchoose > 1:
        #    return 'image'
        #else:
        #    return 'raster'
        

        return 'image'



    @staticmethod
    def checkLayers(inmap, form=None, index=True, boolean=False):
        """Function to check if layers are choosen

        :param str inmap: the input map
        :param obj form: a object containing the bands of map
        :param bool index:
        :param bool boolean: add 1.0 for selected layer and 0.0 for unselected
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
                    elif boolean:
                        itemlist.append(1.0)
                    else:
                        itemlist.append(str(item.text()))
                elif item.checkState() != Qt.Checked and boolean:
                    itemlist.append(0.0)
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
        elif isinstance(form, QgsMapLayerComboBox):
            first = form.itemText(0)
            if index:
                val = form.currentIndex()
                if val == 0 and first == "Seleziona banda":
                    return None
                elif val != 0 and first == "Seleziona banda":
                    return val
                elif first != "Seleziona banda":
                    return val + 1
            else:
                return form.currentText()
        
        elif isinstance(form, QComboBox):
            first = form.itemText(0)
            if index:
                val = form.currentIndex()
                if val == 0 and first == "Seleziona banda":
                    return None
                elif val != 0 and first == "Seleziona banda":
                    return val
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
    def addLayersNumber(combo, checkCombo=None, empty=False, is_checkable=True):
        """Add the subsets name  of a raster to a ComboBox

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
            if is_checkable:
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
            if is_checkable:
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
    def addColumnsNameWithCheck(combo1,combo2,checkCombo):
     
        layerName1 = combo1.currentText()
        layerName2 = combo2.currentText()
       
        cols = []
  
        if not layerName1 or not layerName2:
            checkCombo.clear()
            return
        else:
            checkCombo.clear()
            
            layer1 = STEMUtils.getLayer(layerName1)
            data1 = layer1.dataProvider()
            fields1 = data1.fields()
            
            layer2 = STEMUtils.getLayer(layerName2)
            data2 = layer2.dataProvider()
            fields2 = data2.fields()
            
            cols.append("")
                
            for i in fields1:
                for y in fields2:
                    
                    if i.name()==y.name():
                        if i.typeName()==y.typeName():
                            cols.append(i.name()) 
                
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
        fs.write(text.encode())
        fs.close()
        return name

    @staticmethod
    def fileExists(fileName):
        """Check if a file already exist

        :param str fileName: the path of file
        """
        if (QFileInfo(fileName).exists()):
            if not(os.path.isdir(fileName)):
                res = QMessageBox.question(None, "STEM Plugin", u"Esiste già un "
                                       "file con nome {0}. Sostituirlo?".format(QFileInfo(fileName).fileName()),
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            else:
                res = QMessageBox.Yes

            if res == QMessageBox.Yes:
                if os.path.exists(fileName) and not os.path.isdir(fileName):
                    layerName = QFileInfo(fileName).baseName()
                    #layers = STEMUtils.registry.mapLayersByName(layerName)
                    layers = STEMUtils.registry.mapLayers().values()
                   
                    if layers:
                        for lay in layers:
                            #if (lay.dataProvider().dataSourceUri()[0:lay.dataProvider().dataSourceUri().find("|")]==fileName):
                            if (lay.dataProvider().dataSourceUri()==fileName):
                        #STEMUtils.registry.removeMapLayers(layers[0].id)
                                QMessageBox.warning(None, "STEM Plugin", 
                                                    "Uno dei file che si vuole sovrascrivere è un layer attivo, si prega di rimuoverlo prima di procedere.", 
                                                    QMessageBox.Ok, QMessageBox.Ok)
                                return False, False
                        ##QgsProject.instance().removeMapLayers(layers[0].id())
                        #QgsProject.instance().removeMapLayer(layers[0].id())
                    os.remove(fileName)
                    #shutil.rmtree(fileName)
                
                elif os.path.exists(fileName) and os.path.isdir(fileName):
                    return True, False     
                
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

        print('stem_utils renameRast', tmp, out)

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
    def exportGRASS(gs, overwrite, output, tempout, typ, remove=True, forced_output = False, local = True):
        """Export data from GRASS environment

        :param obj gs: a stemGRASS object
        :param bool overwrite: overwrite existing files
        :param str output: the output path
        :param str tempout: the temporary output inside GRASS
        :param str typ: the type of data
        :param bool remove: True to remove the mapset, otherwise it is kept
        """
        original_dir = os.path.dirname(output)
        if not local:
            original_dir = STEMUtils.pathServerLinuxToClientWin(original_dir)
        
        if typ == 'vector':
            if local:
                path = tempfile.gettempdir()
            else:
                path = STEMUtils.get_temp_dir()
            newdir = os.path.join(path, "shpdir")
            if not os.path.exists(newdir):
                os.mkdir(newdir)
            original_basename = os.path.basename(output)
            tmp = os.path.join(newdir, original_basename)
            try:
                if not local:
                    tmp = STEMUtils.pathClientWinToServerLinux(tmp)
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
                        pass
            shutil.rmtree(newdir)
            STEMUtils.removeFiles(newdir)
        else:
            gs.export_grass(tempout, output, typ, remove, forced_output = forced_output)

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
        scr_ds = None

    @staticmethod
    def saveParameters():
        """Save all the keys/values stem related into a file"""
        keys = [a for a in STEMSettings.allKeys()]
        # TODO maybe add the possibility to choose where save the file
        f = tempfile.NamedTemporaryFile(delete=False)
        for k in keys:
            table = "{key}:  {value}\n".format(key=k,
                                              value=STEMSettings.value(k, ""))
            f.write(table)
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
        hFile.write(" ".join(str(c) for c in command) + '\n')
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
    def pathClientWinToServerLinux(path, inp=True, gui_warning=True):
        """Convert path from windows to linux for client and server connection

        :param str path: the path to rename
        :param bool inp: DEPRECATED
        :param boo gui_warning: notifica all'utente gli errori
        """
        if not sys.platform == 'win32' or path is None:
            return path

        table = STEMUtils.get_mapping_table()

        converted = False
        #print 'table:', table
        for remote, local in table:
            try:
                path = os.path.join(remote, os.path.relpath(path, local)).replace('\\','/')
            except Exception as e:
                pass
            else:
                converted = True
        if not converted and gui_warning:
            STEMMessageHandler.warning("STEM Plugin", 'Percorso non convertibile,'
                                       ' potrebbero esserci problemi nelle '
                                       'prossimi analisi')
        return str(path)
    
    @staticmethod
    def pathServerLinuxToClientWin(path):
        table = STEMUtils.get_mapping_table()
        for remote, local in table:
            try:
                path = os.path.join(local, os.path.relpath(path, remote)).replace('\\','/')
            except Exception as e:
                pass
            else:
                converted = True
        return str(path)

    @staticmethod
    def get_temp_dir():
        """Cartella temporanea valida per client e server
        """
        mt = STEMUtils.get_mapping_table()
        if mt:
            return mt[0].local
        raise Exception("Risorse remote non configurate")

    @staticmethod
    def decode_mapping_table(encoded):
        """
        :param encoded: STEMSettings.value("mappingTable", None)
        :raram return: python object [[r0,r0],[r1,r1]]
        """
        if encoded is not None:
            table = pickle.loads(base64.b64decode(encoded))
            if all([type(x) == list and len(x) in [0, 2] for x in table]):
                # converto dal vecchio formato
                table = [PathMapping(*x) for x in table if x]
            # Dopo la serializzazione il controllo sul tipo non funziona
            assert all([hasattr(x, 'local') and hasattr(x, 'remote') for x in table]), table
            return table
        else:
            return []

    @staticmethod
    def get_mapping_table():
        return STEMUtils.decode_mapping_table(STEMSettings.value("mappingTable", None))

    @staticmethod
    def encode_mapping_table(table):
        """
        :param table: object [(remote, local),(remote, local)]
        :raram return: ASCII encoded table
        """
        assert all([type(x) == PathMapping for x in table]), table
        return base64.b64encode(pickle.dumps(table))

    @staticmethod
    def set_mapping_table(new_table):
        STEMSettings.setValue("mappingTable", STEMUtils.encode_mapping_table(new_table))

    @staticmethod
    def check_las_compress(inp, compr):
        """
        :param str inp: the input path
        :param bool compr: True if the output will be compressed, so extension
                           should be .laz
        """
        if compr and inp.endswith('.las'):
            inp = inp.rstrip('.las')
            return inp + '.laz'
        elif not compr and inp.endswith('.laz'):
            inp = inp.rstrip('.laz')
            return inp + '.laz'
        return inp

    @staticmethod
    def isNodataNan(image_src):
        rast = gdal.Open(image_src)
        banda = rast.GetRasterBand(1)
        nodata = band.GetNoDataValue()

    @staticmethod
    def getFormat(image_src):
        rast = gdal.Open(image_src)
        driver = rast.GetDriver()
        return driver.ShortName

    @staticmethod
    def getProjection(image_src):
        rast = gdal.Open(image_src)
        proj = rast.GetProjection()
        return proj

    @staticmethod
    def getExtend(image_src):
        rast = gdal.Open(image_src)
        geoTransform = rast.GetGeoTransform()
        minx = geoTransform[0]
        maxy = geoTransform[3]
        maxx = minx + geoTransform[1] * rast.RasterXSize
        miny = maxy + geoTransform[5] * rast.RasterYSize
        
        return minx, maxx, miny, maxy

 # proj = osr.SpatialReference(wkt=rast.GetProjection())


    @staticmethod
    def copySetNodata(image, image_src, number):
        if local:
            path = tempfile.gettempdir()
        else:
            try:
                path = STEMUtils.get_temp_dir()
            except:
                STEMMessageHandler.error("È necessario configurare almeno un mapping fra le "
                                         "risorse locali e remote")
                return False, False, False
        outname = "nodata_{name}".format(name=image).strip()
        out = os.path.join(path, outname)
        #com = "gdal_calc.py -A {0} --outfile={1} --overwrite --calc=A --NoDataValue={2}".format(image_src, out, number)
        com = "gdal_translate -a_nodata {0} {1} {2}".format(number, image_src, out)
        com = com.split()
        runcom = subprocess.Popen(com, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log, err = runcom.communicate()
        return outname, out

    @staticmethod
    def copyRemoveNan(image, image_src, number):
        if isNodataNan(image_src):
            return copySetNodata(image, image_src, number)
        else:
            return image, image_src


class STEMMessageHandler(object):
    """
    Handler of message notification via QgsMessageBar to display
    non-blocking messages to the user.

    STEMMessageHandler.[information, warning, critical, success](title, text, timeout)
    STEMMessageHandler.[information, warning, critical, success](title, text)
    STEMMessageHandler.error(message)
    """

    messageLevel = [Qgis.Info,
                    Qgis.Warning,
                    Qgis.Critical]

    ## SUCCESS was introduced in 2.7
    ## if it throws an AttributeError INFO will be used
    try:
        messageLevel.append(Qgis.Success)
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

#         STEMMessageHandler.warning("STEM", "Errore! Controllare i messaggi di log di QGIS", 0)
        #QgsMessageLog.logMessage(message, "STEM Plugin")
        pass

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


class STEMLogging(object):
    """Class to log information of modules in a file"""

    def __init__(self, logname=None):
        if logname:
            logfile = logname
        else:
            stempath = STEMSettings.value("stempath")
            logfile = os.path.join(stempath, 'stem.log')
        reload(logging)
        logging.basicConfig(filename=logfile, filemode='w',
                            level=logging.DEBUG)

    def debug(self, text):
        logging.debug(text)

    def warning(self, text):
        logging.warning(text)

    def info(self, text):
        logging.info(text)
