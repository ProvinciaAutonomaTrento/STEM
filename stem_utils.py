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

from gdal_functions import getNumSubset

class STEMUtils:

    registry = QgsMapLayerRegistry.instance()

    @staticmethod
    def addLayerToComboBox(combo, typ):
        """Add layers to input files list"""
        combo.clear()
        layerlist = []
        layermap = STEMUtils.registry.mapLayers()
        for name, layer in layermap.iteritems():
            if layer.type() == typ:
                layerlist.append( layer.name() )

        combo.addItems(layerlist)

    @staticmethod
    def getLayersSource(layerName):
        layermap = STEMUtils.registry.mapLayers()

        for name, layer in layermap.iteritems():
            if layer.name() == layerName:
                if layer.isValid():
                    return layer.source()
                else:
                    return None

    @staticmethod
    def addLayerIntoCanvas(filename, typ):
        """Add the output in the QGIS canvas"""
        layerName = QFileInfo(filename).baseName()
        if typ == 'raster' or typ=='image':
            layer = QgsRasterLayer(filename, layerName)
        elif typ == 'vector':
            layer = QgsVectorLayer(filename, layerName, 'ogr')
        if not layer.isValid():
            print "Layer failed to load!"
        else:
            STEMUtils.registry.addMapLayer(layer)

    @staticmethod
    def checkMultiRaster(inmap, checkCombo, lineEdit=None):
        nsub = getNumSubset(inmap)
        nlayerchoose = STEMUtils.checkLayers(inmap, checkCombo, lineEdit)
        if nsub > 0 and nlayerchoose > 1:
            return 'image'
        else:
            return 'raster'

    @staticmethod
    def checkLayers(inmap, checkCombo, lineEdit=None):
        """Function to check if layers are choosen"""
        try:
            if lineEdit.text() == u'':
                return getNumSubset(inmap)
            else:
                return lineEdit.text().split(',')
        except:
            itemlist = []
            for i in range(checkCombo.count()):
                item = checkCombo.model().item(i)
                if item.checkState() == Qt.Checked:
                    itemlist.append(str(i + 1))
            if len(itemlist) == 0:
                return getNumSubset(inmap)
            return itemlist
