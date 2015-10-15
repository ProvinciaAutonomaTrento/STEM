# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 11:37:19 2015

@author: lucadelu
"""

from PyQt4.QtCore import QSettings
from PyQt4.QtGui import QComboBox, QLineEdit, QCheckBox
import inspect
import re
try:
    import osgeo.ogr as ogr
except ImportError:
    try:
        import ogr
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'


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
        raise 'WKT non valido'
        return False


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

        :param obj ui: the obkect of tool's UI
        :param str tool: the name of the tool
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

        :param obj ui: the obkect of tool's UI
        :param str tool: the name of the tool
        """
        if tool:
            tool = re.sub(r"[^\w\s]", '', tool)
            tool = re.sub(r"\s+", '_', tool)

        if not tool in STEMSettings.s.childGroups():
            return

        for name, obj in inspect.getmembers(ui):
            if isinstance(obj, QComboBox):
                index = obj.currentIndex()
                name = obj.objectName()

                value = STEMSettings.value(tool + "/" + name, "", unicode)
                if value == "":
                    continue

                index = obj.findText(value)
                if index == -1:
                    continue
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
        fil.write("[General]\n")
        for k in STEMSettings.s.childKeys():
            fil.write("{ke}={va}\n".format(ke=k, va=STEMSettings.s.value(k)))
        fil.write("\n")
        for k in STEMSettings.allKeys():
            if k.find('/') != -1:
                key = k.split('/')
                if key[0] not in groups:
                    fil.write("\n[{ke}]\n".format(ke=key[0]))
                    groups.append(key[0])
                fil.write("{ke}={va}\n".format(ke=key[1],
                                               va=STEMSettings.s.value(k)))
