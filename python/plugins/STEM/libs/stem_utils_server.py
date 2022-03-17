# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 11:37:19 2015

@author: lucadelu
"""

from builtins import str
from builtins import range
from builtins import object
import inspect
import re
import tempfile
import time
import sys
import os
import codecs
import logging


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

from qgis.gui import QgsMapLayerComboBox



try:
    import osgeo.ogr as ogr
except ImportError:
    try:
        import ogr
    except ImportError:
        raise Exception('Python GDAL library not found, please install python-gdal')

def filelineno(levels_back):
    """Returns the current line number in our program."""
    frame = inspect.currentframe()
    for i in range(levels_back+1):
        frame = frame.f_back
    frameinfo = inspect.getframeinfo(frame)
    return frameinfo.filename.split(os.path.sep)[-1], frameinfo.lineno

def inverse_mask():
    inverse = STEMSettings.value("mask_inverse", "")
    if inverse == "true":
        return True
    else:
        return False


def check_wkt(wkt):
    """Check if the Well Known Text is valid or not"""
    geom = ogr.CreateGeometryFromWkt(wkt)
    if geom:
        return True
    else:
        return False


def tempFileName():
    """Return a temporary file name"""
    tmp_file = tempfile.NamedTemporaryFile()
    tmp_file.close()
    return tmp_file.name


def read_file(filename, mode='rb', encoding='UTF-8'):
    """Read the input file and return its content

    :param str filename: the input filename to read
    :param str mode: a string for the mode to open the file
    :param str encoding: the encoding for the input file
    """
    output = ''
    with open(filename, mode) as f:
        output = f.read().decode(encoding)
    return output

class STEMLoggingServer(object):
    """Class to log information of modules in a file"""
    def __init__(self, logname):
         import uuid
         unique_id = str(uuid.uuid4()).replace('-', '_')
         self.logger = logging.getLogger('{}_{}_stem_log'.format(logname, unique_id))
         self.logger.setLevel(logging.DEBUG)
         self.logger.propagate = False
         fh = logging.FileHandler('{}_{}_stem.log'.format(logname, unique_id))
         self.logger.addHandler(fh)

    def debug(self, text):
        self.logger.debug(text)

    def warning(self, text):
        self.logger.warning(text)

    def info(self, text):
        self.logger.info(text)

class STEMSettings(object):
    """
    Class to save and to restore settings to QSettings

    STEMSettings.saveWidgetsValue(ui, QSettings("STEM", "STEM"), toolName)
    STEMSettings.restoreWidgetsValue(ui, QSettings("STEM", "STEM"), toolName)
    """
    s = QSettings("STEM16022021", "STEM16022021")
    
    @staticmethod
    def _check(string):
        """Check the type of string

        :param obj string: a string, it should be as UnicodeType or StringType
        """
        if isinstance(string, str):
            return str(string)
        else:
            return str("")

    @staticmethod
    def saveLastDir(inputComponent, inputPath, tool=""):
        if tool:
            tool = re.sub(r"[^\w\s]", '', tool)
            tool = re.sub(r"\s+", '_', tool)
        name = inputComponent.objectName()
        value = os.path.dirname(inputPath)
        if value is None:
            value = ""
        STEMSettings.setValue(tool + "/" + name + "_last", value)
    
    @staticmethod
    def restoreLastDir(inputComponent, tool=""):
        if tool:
            tool = re.sub(r"[^\w\s]", '', tool)
            tool = re.sub(r"\s+", '_', tool)
        name = inputComponent.objectName()
        value = STEMSettings.value(tool + "/" + name + "_last", "", str)
        if value is None:
            vale = ""
        return value
        
    @staticmethod
    def saveWidgetsValue(ui, tool=""):
        """Save the parameters used into a tool in the STEMSettings

        :param obj ui: the obkect of tool's UI
        :param str tool: the name of the tool
        """
        return
 
 
        print("-- Save parameters --")
        
        if tool:
            tool = re.sub(r"[^\w\s]", '', tool)
            tool = re.sub(r"\s+", '_', tool)

        print("tool:", tool)

        for name, obj in inspect.getmembers(ui):

            
            if isinstance(obj, QgsMapLayerComboBox):
                name = obj.objectName()
                index = obj.currentIndex()
                text = obj.itemText(index)
                STEMSettings.setValue(tool + "/" + name, text)
                print("obj:", obj.objectName(), " - value:", text)


            if isinstance(obj, QLineEdit):
                name = obj.objectName()
                value = obj.text()
                STEMSettings.setValue(tool + "/" + name, value)
                print("obj:", obj.objectName(), " - value:", value)


            if isinstance(obj, QCheckBox):
                name = obj.objectName()
                state = obj.isChecked()
                STEMSettings.setValue(tool + "/" + name, state)
                print("obj:", obj.objectName(), " - value:", state)

            if isinstance(obj, QDoubleSpinBox):
                name = obj.objectName()
                value = obj.value()
                STEMSettings.setValue(tool + "/" + name, value)
                print("obj:", obj.objectName(), " - value:", value)


    @staticmethod
    def restoreWidgetsValue(ui, tool=""):
        """Restore the parameters used earlier into a tool in the STEMSettings

        :param obj ui: the obkect of tool's UI
        :param str tool: the name of the tool
        """
        return
        
        print("-- Restore parameters --")
        
        if tool:
            tool = re.sub(r"[^\w\s]", '', tool)
            tool = re.sub(r"\s+", '_', tool)

        #if not tool in STEMSettings.s.childGroups():
        #if not tool in STEMSettings.childGroups():
        #    return
        
        print("tool:", tool)

        for name, obj in inspect.getmembers(ui):
            
            
            if isinstance(obj, QgsMapLayerComboBox):
                index = obj.currentIndex()
                name = obj.objectName()

                value = STEMSettings.value(tool + "/" + name, "", str)
                if value == "":
                    continue

                index = obj.findText(value)
                if index == -1:
                    continue
                else:
                    obj.setCurrentIndex(index)
                    print("obj:", obj.objectName(), " - value:", value)

            if isinstance(obj, QLineEdit):
                name = obj.objectName()
                value = STEMSettings.value(tool + "/" + name, "", str)
                if value:
                    obj.setText(value)
                    print("obj:", obj.objectName(), " - value:", value)
                else:
                    obj.setText("")
                    print("obj:", obj.objectName(), " - value:", value)
                    
                if (name == "NODATAlineEdit"): 
                    obj.setText("")
                    

            if isinstance(obj, QCheckBox):
                name = obj.objectName()
                value = STEMSettings.value(tool + "/" + name, True, bool)
                if value is not None:
                    obj.setChecked(value)
                    print("obj:", obj.objectName(), " - value:", value)
                    
                if (name == "QGISextent"):
                    obj.setChecked(False)
                    print("obj: QGISextent forced to false")
                    

#            if isinstance(obj, CheckableComboBox):
#                    print("obj CheckableComboBox non gestito")

            if isinstance(obj, QComboBox):
                    print("obj QComboBox non gestito")

            if isinstance(obj, QDoubleSpinBox):
                name = obj.objectName()
                value = STEMSettings.value(tool + "/" + name, "", str)
                if value:
                    obj.setValue(float(value))
                    print("obj:", obj.objectName(), " - value:", value)

                    
                    
        
      

    @staticmethod
    def setValue(key, value):
        """Set the value for the given key

        :param str key: the key to set
        :param str value: the value for the given key
        """
        return STEMSettings.s.setValue(key, value)

    @staticmethod
    def value(key, default=None, type=None):
        """Return the value of the given key

        :param str key: the key to get
        :param str default: the default value to return
        :param obj type: the type of value
        """
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

    @staticmethod
    def saveToFile(fil):
        groups = []
        fil.write(u"[General]\n")
        for k in STEMSettings.s.childKeys():
            fil.write(u"{ke}={va}\n".format(ke=k, va=STEMSettings.s.value(k)))
        fil.write(u"\n")
        for k in STEMSettings.allKeys():
            if k.find('/') != -1:
                key = k.split('/')
                if key[0] not in groups:
                    fil.write(u"\n[{ke}]\n".format(ke=key[0]))
                    groups.append(key[0])
                fil.write(u"{ke}={va}\n".format(ke=key[1],
                                                va=STEMSettings.s.value(k)))


def libs_save_command(command, details=None):
    """Save the command history to file

    :param list command: the list of all parameter used
    :param details str or [str]: text details to attach to the command
    """
    historyfilename = 'stem_command_history.txt'
    stemdir = 'stem'
    if sys.platform.startswith('win'):
        from qgis.core import QgsApplication
        historypath = os.path.join(QgsApplication.qgisSettingsDirPath(),
                               stemdir, historyfilename)
    else:
        historypathdir = os.path.join(tempfile.gettempdir(),stemdir)
        if not os.path.exists(historypathdir): #corretto?
            os.mkdir(historypathdir)
        historypath = os.path.join(historypathdir, historyfilename)

    hFile = codecs.open(historypath, 'a', encoding='utf-8')
    
    hFile.write('# {}\n'.format(time.ctime()))
    hFile.write('# File: {} Line: {}\n'.format(*filelineno(1)))
    if details is not None:
        if isinstance(details, str):
            details = [details]
        if isinstance(details, list):
            for l in details:
                hFile.write('# {}\n'.format(l))
    hFile.write(" ".join(command) + '\n')
    hFile.close()
