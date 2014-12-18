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
try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'

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
    def checkMultiRaster(inmap, checkCombo=None, lineEdit=None):
        nsub = getNumSubset(inmap)
        nlayerchoose = STEMUtils.checkLayers(inmap, checkCombo, lineEdit)
        if nsub > 0 and nlayerchoose > 1:
            return 'image'
        else:
            return 'raster'

    @staticmethod
    def checkLayers(inmap, checkCombo=None, lineEdit=None):
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

    @staticmethod
    def addLayersNumber(combo, checkCombo=None):
        layerName = combo.currentText()
        if not layerName:
            return
        else:
            source = STEMUtils.getLayersSource(layerName)
        gdalF = gdal.Open(source)
        gdalBands = gdalF.RasterCount
        gdalMeta = None
        checkCombo.clear()
        if gdalF.GetDriver().LongName == 'ENVI .hdr Labelled':
            gdalMeta = gdalF.GetMetadata_Dict()
        for n in range(1, gdalBands+1):
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
            item = model.item(n-1)
            item.setCheckState(Qt.Unchecked)

    @staticmethod
    def writeFile(text, name=False):
        if name:
            fs = open(name, 'w')
        else:
            import tempfile
            f = tempfile.NamedTemporaryFile()
            name = f.name
            fs = f.file
        fs.write(text)
        fs.close()
        return name
    
    @staticmethod
    def fileExists(fileName):
        if QFileInfo(fileName).exists():
            res = QMessageBox.question(None, "", u"Esiste già un file con nome {0}. Sostituirlo?"
                                       .format(QFileInfo(fileName).baseName), 
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            #if res == QMessageBox.Cancel: return
            if res:
                return True
        return False

    @staticmethod
    def exportGRASS(gs, overwrite, output, tempout, typ):
        if overwrite:
            tmp = output + '.tmp'
        else:
            tmp = output
        try:
            gs.export_grass(tempout, tmp, typ)
        except:
            pass
        if overwrite:
            os.rename(tmp, output)
            os.rename('{name}.aux.xml'.format(name=tmp),
                      '{name}.aux.xml'.format(name=output))

    @staticmethod
    def QGISettingsGRASS(grassdatabase=None, location=None, grassbin=None,
                     epsg=None):
        """Read the QGIS's settings and obtain information for GRASS GIS"""
        s = QSettings()
        # query GRASS 7 itself for its GISBASE
        # we assume that GRASS GIS' start script is available and in the PATH
        if not grassbin:
            grassbin = str(s.value("stem/grasspath", ""))
        if not grassdatabase:
            grassdatabase = str(s.value("stem/grassdata", ""))
        if not location:
            location = str(s.value("stem/grasslocation", ""))
        if not epsg:
            epsg = str(s.value("stem/epsgcode", ""))
        return grassdatabase, location, grassbin, epsg

    @staticmethod
    def temporaryFilesGRASS(name):
        pid = os.getpid()
        tempin = 'stem_{name}_{pid}'.format(name=name, pid=pid)
        tempout = 'stem_output_{pid}'.format(pid=pid)
        grassdatabase, location, grassbin, epsg = STEMUtils.QGISettingsGRASS()
        gs = stemGRASS(pid, grassdatabase, location, grassbin, epsg)
        return tempin, tempout, gs
