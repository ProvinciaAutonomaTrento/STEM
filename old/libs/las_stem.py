# -*- coding: utf-8 -*-
"""
Created on Mon Dec  1 10:56:52 2014

@author: lucadelu

***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import subprocess
from xml.etree.ElementTree import Element, tostring, fromstring
import tempfile
from pyro_stem import PYROSERVER, LAS_PORT, LASPYROOBJNAME
from gdal_stem import file_info, infoOGR, ogr
import os
import json
import sys
from stem_utils_server import check_wkt, tempFileName, read_file
from math import *
import numpy as np
PIPE = subprocess.PIPE
try:
    import pdal
    from pdal import libpdalpython
except:
    PDAL = False
else:
    PDAL = True

from stem_utils_server import read_file

LAST_RETURN = """
import numpy as np

def filter(ins,outs):
    ret = ins['ReturnNumber']
    ret_no = ins['NumberOfReturns']

    # Use the first test for our base array.
    rets = np.equal(ret, ret_no)

    outs['Mask'] = rets
    return True
"""

FILTER_NAN = """
import numpy as np

def filter(ins,outs):
   cls = ins['Z']

   keep = ~np.isnan(cls)

   outs['Mask'] = keep
   return True
"""

CHM = """
import numpy as np
import struct
import osgeo.gdal as gdal

def get_value(x,y, band, band_type, geomt):
    px = int((x - geomt[0]) / geomt[1])  # x pixel
    py = int((y - geomt[3]) / geomt[5])  # y pixel
    try:
        structval = band.ReadAsArray(px, py, 1, 1)
        nodata_value = band.GetNoDataValue()
        val = structval[0][0]
        if val == nodata_value:
            return np.nan
        elif cmp(val, 0) == -1:
            val = 0
        return val
    except:
        return np.nan

def chm(ins,outs):
    inrast = r'{NAME}'
    rast = gdal.Open(inrast)
    band = rast.GetRasterBand(1)
    geomtransf = rast.GetGeoTransform()
    band_type = band.DataType
    Zs = ins['Z']
    Xs = ins['X']
    Ys = ins['Y']
    newZ = []
    for i in range(len(Xs)):
        try:
            z = get_value(Xs[i], Ys[i], band, band_type, geomtransf)
        except:
            z = np.nan
        if not np.isnan(z):
            z = Zs[i] - z
            if cmp(z,0) == -1:
                z = 0
        newZ.append(z)
    outs['Z'] = np.array(newZ)
    return True
"""

OTHER_RETURN = """
import numpy as np

def filter(ins,outs):
    ret = ins['ReturnNumber']
    ret_last = ins['NumberOfReturns']
    ret_first = np.ones(len(ret))

    # Use the first test for our base array.
    returns_last = np.not_equal(ret, ret_last)
    returns_first = np.not_equal(ret, ret_first)

    others = np.logical_and(returns_last, returns_first)
    outs['Mask'] = others
    return True
"""

def mode(a, axis=0):
    scores = np.unique(np.ravel(a))       # get ALL unique values
    testshape = list(a.shape)
    testshape[axis] = 1
    oldmostfreq = np.zeros(testshape)
    oldcounts = np.zeros(testshape)

    for score in scores:
        template = (a == score)
        counts = np.expand_dims(np.sum(template, axis),axis)
        mostfrequent = np.where(counts > oldcounts, score, oldmostfreq)
        oldcounts = np.maximum(counts, oldcounts)
        oldmostfreq = mostfrequent

    return mostfrequent, oldcounts

def number_return(inps, value):
    """Count the number of inps major than value and after divide them for
    value

    :param array inps: numpy array with input height values
    :param float value: the threshold to cut inps
    """
    return float((inps > value).sum()) / float(len(inps))


def hcv(inps):
    """Calculate coefficient of variation height points,
    standard_deviation/mean

    :param array inps: numpy array with input height values
    """
    return (np.std(inps) / np.mean(inps))


class stemLAS():
    """The class to manage LAS files from STEM plugin"""
    def __init__(self):
        self.pdalxml = None
        self.pdal = None
        self.liblas = None
        self.returns = []
        self.classes = []
        self.mins = []
        self.maxs = []

    def initialize(self):
        """Initialization of class"""
        self._check()

    def _check(self):
        """Check which libraries is present on the system"""
        self.pdal = self._checkLibs('pdal --version')
        self.liblas = self._checkLibs('las2las --help')

    def _checkLibs(self, command, second=None):
        """Check the single library

        :param str command: the bash command to run
        """
        com = subprocess.Popen(command, shell=True, stdin=PIPE, stderr=PIPE,
                               stdout=PIPE)
        lasout = com.stdout.readlines()
        laserr = com.stderr.readlines()
        if lasout:
            return True
        elif laserr:
            if second:
                com = subprocess.Popen(second, shell=True, stdin=PIPE,
                                       stderr=PIPE, stdout=PIPE)
                lasout = com.stdout.readlines()
                laserr = com.stderr.readlines()
                if lasout:
                    return True
                elif laserr:
                    return False
            else:
                return False
        else:
            return False

    def _add_option_file(self, fil, key="name", val="filename"):
        """Add an option element in the Pipeline XML file

        :param str fil: the text to add in the option
        :param str key: the key of tag to add in the element
        :param str val: the value of tag to add in the element
        """
        option = Element('Option')
        option.set(key, val)
        option.text = str(fil)
        return option

    def _add_write(self, output, compres):
        """Add the writer element in the Pipeline XML file

        :param str output: the output LAS full path
        :param bool compres: the output has to be compressed
        """
        writer = Element('Writer')
        writer.set("type", "writers.las")
        writer.append(self._add_option_file(output))
        if compres:
            writer.append(self._add_option_file('true', val='compression'))
        return writer
    
    def _add_txt_write(self, output):
        """Add the writer element in the Pipeline XML file

        :param str output: the output txt full path
        """
        writer = Element('Writer')
        writer.set("type", "writers.text")
        writer.append(self._add_option_file(output))
        return writer

    def _add_reader(self, inpu):
        """Add the reader element in the Pipeline XML file

        :param str inpu: the input LAS full path
        """
        reader = Element('Reader')
        reader.set("type", "readers.las")
        reader.append(self._add_option_file(inpu))
        return reader

    def _create_xml(self):
        """Create the root of the Pipeline XML file"""
        root = Element('Pipeline')
        root.set('version', '1.0')
        root.set('encoding', 'utf-8')
        return root

    def _start_command(self, forced):
        """According with the existing library it set the command to run

        :param str forced: parameter to force to use a library, the accepted
                           values are 'liblas' and 'pdal'
        """
        if forced == 'liblas' and self.liblas:
            return ['las2las']
        elif forced == 'liblas' and not self.liblas:
            raise Exception("LibLAS non trovato")
        elif forced == 'pdal' and self.pdal:
            return ['pdal', 'pipeline']
        elif forced == 'pdal' and not self.pdal:
            raise Exception("pdal non trovato")
        elif self.pdal:
            return ['pdal', 'pipeline']
        else:
            raise Exception('Not able to find a library to work with LAS files')

    def _run_command(self, comm, disable_win_errors = False):
        """Run the command and return the output

        :param list comm: the list containing the command to run
        """
        if disable_win_errors:
            import win32api
            import win32con
            previous_error_mode = win32api.SetErrorMode(win32con.SEM_FAILCRITICALERRORS |
                                                        win32con.SEM_NOGPFAULTERRORBOX)
            try:
                com = subprocess.Popen(comm, stdin=PIPE,
                                       stdout=PIPE, stderr=PIPE)
                out, err = com.communicate()
            finally:
                win32api.SetErrorMode(previous_error_mode)
        else:
            com = subprocess.Popen(comm, stdin=PIPE,
                                   stdout=PIPE, stderr=PIPE)
            out, err = com.communicate()

        # Pdal da` errore anche se restituisce 0 come returncode
        if err != '':
            raise Exception('Problem executing "{com}", the error is :'
                            '{er}'.format(com=' '.join(comm), er=err))
        elif com.returncode == -11:
            raise Exception('Problem executing "{com}", the error is :'
                            'Segmantation fault'.format(com=' '.join(comm)))
        else:
            if self.pdalxml:
                try:
                    os.remove(self.pdalxml)
                except OSError:
                    pass
        return out

    def lasinfo(self, inp):
        """Run `lasinfo` command from liblas to obtain information about the
        LAS file

        :param str inp: full path for the input LAS file
        """
        comm = ['lasinfo', '--xml', inp]
        xml = self._run_command(comm)
        tree = fromstring(xml)
        header = tree.find('header')
        mins = header.find('minimum')
        self.mins = [mins.find('x').text, mins.find('y').text,
                     mins.find('z').text]
        maxs = header.find('maximum')
        self.maxs = [maxs.find('x').text, maxs.find('y').text,
                     maxs.find('z').text]
        returns = header.find('returns')
        for ret in returns.findall('return'):
            self.returns.append(ret.find('id').text)
        points = tree.find('points')
        mini = points.find('minimum')
        maxi = points.find('maximum')
        mini_clas = mini.find('classification')
        maxi_clas = maxi.find('classification')
        self.classes.extend(range(int(mini_clas.find('id').text),
                                  int(maxi_clas.find('id').text) + 1))

    def pdalinfo(self, inp):
        """Run `pdal info` command from pdal to obtain information about the
        LAS file

        :param str inp: full path for the input LAS file
        """
        comm = ['pdal', 'info', inp]
        out = json.loads(self._run_command(comm))
        for sta in out['stats'][0]['statistic']:
            if sta['name'] == 'Classification':
                self.classes.extend(range(int(sta['minimum']),
                                          int(sta['maximum'])))
            if sta['name'] == 'NumberOfReturns':
                self.returns.extend(range(int(sta['minimum']),
                                          int(sta['maximum'])))

    def txt2las(self, inp, out, parser="xyzricp"):
        """Convert txt file to las

        :param str inp: path to input file
        :param str out: path to output file
        :param str parser: the string of parser
        """
        if self.liblas:
            comm = ["txt2las", "-i", inp, "-o", out, "-parse", parser]
        else:
            raise Exception("LibLAS non trovato")
            # TODO pdal not support txt to las yet
            #comm = ["pdal", "translate", "-i", "-o"]
        self._run_command(comm)

    def chm_xml_pdal(self, inp, out, dtm, bbox, compres=False):
        """Create the XML file to use in `pdal pipeline` to obtain CHM

        :param str inp: full path for several input LAS files
        :param str out: the output LAS full path
        :param str dtm: the path to DTM file
        :param str bbox: a WKT string rappresenting a polygon
        :param bool compres: the output has to be compressed
        """
        # create a temporal file
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        # create xml file
        root = self._create_xml()
        # add Writer element
        write = self._add_write(out, compres)
        # first we add predicate to remove values with None value
        filt_ret = Element('Filter')
        filt_ret.set("type", "filters.predicate")
        funct = self._add_option_file('filter', val='function')
        modu = self._add_option_file('anything', val='module')
        source = self._add_option_file(FILTER_NAN, val='source')
        filt_ret.append(funct)
        filt_ret.append(modu)
        filt_ret.append(source)
        # second if the function to calculate the CHM
        filt_prog = Element('Filter')
        filt_prog.set("type", "filters.programmable")
        funct = self._add_option_file('chm', val='function')
        modu = self._add_option_file('anything', val='module')
        python = CHM.format(NAME=dtm)
        source = self._add_option_file(python, val='source')
        filt_prog.append(funct)
        filt_prog.append(modu)
        filt_prog.append(source)
        # last is the crop filter to cut the LAS file with the bounding box of
        # raster
        filt = Element('Filter')
        filt.set("type", "filters.crop")
        clip = self._add_option_file(bbox, val='polygon')
        filt.append(clip)
        # add reader element for input LAS file
        filt.append(self._add_reader(inp))
        # add the crop filter to programmable
        filt_prog.append(filt)
        # add the programmable filter to the predicate one
        filt_ret.append(filt_prog)
        write.append(filt_ret)
        root.append(write)
        if sys.platform == 'win32':
            tmp_file.write(tostring(root, 'iso-8859-1'))
        else:
            tmp_file.write(tostring(root, 'utf-8'))
        tmp_file.close()
        self.pdalxml = tmp_file.name
        return 0

    def chm(self, inp, out, dtm, compressed=False, local=False):
        """Merge several LAS file into one LAS file

        :param str inp: full path for the input LAS file
        :param str out: full path for the output LAS file
        :param str dtm: the path to DTM file
        :param bool compressed: True to obtain a LAZ file
        """
        if self.pdal:
            command = ['pdal', 'pipeline']

            fi = file_info()
            fi.init_from_name(dtm)
            bbox = fi.getBBoxWkt()
            self.chm_xml_pdal(inp, out, dtm, bbox, compressed)
            command.extend(['-i', self.pdalxml])
            
            if not local:
                xml = read_file(self.pdalxml)
                pipe = libpdalpython.PyPipeline(xml)
                pipe.execute()
            else:
                if sys.platform.startswith("win"):
                    self._run_command(command, disable_win_errors = True)
                else:
                    self._run_command(command)
            return command
        else:
            raise Exception("pdal è necessario per calcolare il CHM")

    def union_xml_pdal(self, inps, out, compres):
        """Create the XML file to use in `pdal pipeline` to merge serveral
        LAS files

        :param str inp: full path for several input LAS files
        :param str out: the output LAS full path
        :param bool compres: the output has to be compressed
        """
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        root = self._create_xml()
        write = self._add_write(out, compres)
        filt = Element('Filter')
        filt.set("type", "filters.merge")

        for i in inps:
            filt.append(self._add_reader(i))

        write.append(filt)
        root.append(write)
        if sys.platform == 'win32':
            tmp_file.write(tostring(root, 'iso-8859-1'))
        else:
            tmp_file.write(tostring(root, 'utf-8'))
        tmp_file.close()
        self.pdalxml = tmp_file.name
        return 0

    def union(self, inps, out, compressed=False, local=False):
        """Merge several LAS file into one LAS file

        :param str inp: full path for the input LAS file
        :param str out: full path for the output LAS file
        :param bool compressed: True to obtain a LAZ file
        """
        if self.pdal:
            command = ['pdal', 'pipeline']
            self.union_xml_pdal(inps, out, compressed)
            command.extend(['-i', self.pdalxml])
            if not local:
                xml = read_file(self.pdalxml)
                pipe = libpdalpython.PyPipeline(xml)
                pipe.execute()
            else:          
                self._run_command(command)
            return command
        else:
            raise Exception("pdal è necessario per unire più file LAS")

    def clip_xml_pdal(self, inp, out, bbox, compres, inverted=False):
        """Clip a LAS file using a polygon

        :param str inp: full path for the input LAS file
        :param str out: full path for the output LAS file
        :param str bbox: a well-known text string to crop the LAS file
        :param bool compres: the output has to be compressed
        :param bool inverted: invert the cropping logic and only take points
                              outside the cropping polygon
        """
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        root = self._create_xml()
        write = self._add_write(out, compres)
        filt = Element('Filter')
        filt.set("type", "filters.crop")

        if inverted:
            clip_inverted = self._add_option_file('true', val='outside')
            filt.append(clip_inverted)

        clip = self._add_option_file(bbox, val='polygon')
#         if inverted:
#             clip.set("outside", "true")
        filt.append(clip)
        filt.append(self._add_reader(inp))
        write.append(filt)
        root.append(write)
        if sys.platform == 'win32':
            tmp_file.write(tostring(root, 'iso-8859-1'))
        else:
            tmp_file.write(tostring(root, 'utf-8'))
        tmp_file.close()
        self.pdalxml = tmp_file.name
        return 0
    
    def clip_txt_pdal(self, inp, out, bbox, inverted=False):
        """Clip a LAS file using a polygon, returns text file

        :param str inp: full path for the input LAS file
        :param str out: full path for the output txt file
        :param str bbox: a well-known text string to crop the LAS file
        :param bool inverted: invert the cropping logic and only take points
                              outside the cropping polygon
        """
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        root = self._create_xml()
        write = self._add_txt_write(out)
        filt = Element('Filter')
        filt.set("type", "filters.crop")

        if inverted:
            clip_inverted = self._add_option_file('true', val='outside')
            filt.append(clip_inverted)

        clip = self._add_option_file(bbox, val='polygon')
#         if inverted:
#             clip.set("outside", "true")
        filt.append(clip)
        filt.append(self._add_reader(inp))
        write.append(filt)
        root.append(write)
        if sys.platform == 'win32':
            tmp_file.write(tostring(root, 'iso-8859-1'))
        else:
            tmp_file.write(tostring(root, 'utf-8'))
        tmp_file.close()
        self.pdalxml = tmp_file.name
        return 0

    def clip(self, inp, out, area, inverted=False, forced=False,
             compressed=False, local=False):
        """
        :param str inp: full path for the input LAS file
        :param str out: full path for the outpu LAS file
        :param area string: bbox or polygon to cut the las file
        :param bool inverted: use for inverted clip
        :param str forced: liblas o pdal as value
        :param bool compressed: True to obtain a LAZ file
        """
        wkt = check_wkt(area)
        if wkt:
            command = self._start_command('pdal')
        else:
            command = self._start_command(forced)
        if 'las2las' in command:
            if compressed:
                command.append('-c')
            if inverted:
                print("Non è possibile utilizzare l'opzione 'Maschera inversa'"
                      " con la libreria liblas")
            command.extend(['-i', inp, '-o', out, '-e', area])
            self._run_command(command)
        else:
            if not wkt:
                coors = area.split()
                area = "POLYGON (({minx} {miny}, {minx} {maxy}, {maxx} {maxy}" \
                       ", {maxx} {miny}, {minx} {miny}))".format(minx=coors[0],
                                                                 miny=coors[1],
                                                                 maxx=coors[2],
                                                                 maxy=coors[3])
            self.clip_xml_pdal(inp, out, area, compressed, inverted)
            command.extend(['-i', self.pdalxml])
#             if not local:
#                 xml = read_file(self.pdalxml)
#                 pipe = libpdalpython.PyPipeline(xml)
#                 pipe.execute()
#             else:          
#                 self._run_command(command)
            self._run_command(command)
        return command

    def filter_xml_pdal(self, inp, out, compres, x=None, y=None, z=None,
                        inte=None, angle=None, clas=None, retur=None):
        """
        :param str inp: full path for the input LAS file
        :param str out: full path for the outpu LAS file
        :param bool compres: True to obtain a LAZ file
        :param list x: a two values list with min and max value for x
        :param list y: a two values list with min and max value for y
        :param list z: a two values list with min and max value for z
        :param list inte: a two values list with min and max value for intesity
        :param list angle: a two values list with min and max value for scan
                           angle
        :param str clas: number of class to maintain
        :param str retur: the return to keep, the accepted values are:
                           first, last, others
        """
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        root = self._create_xml()
        write = self._add_write(out, compres)
        filt = Element('Filter')
        filt.set("type", "filters.range")
        limits = []
        filt_pred = None
        if x:
            limits.append('X[{0}:{1}]'.format(x[0], x[1]))
        if y:
            limits.append('Y[{0}:{1}]'.format(y[0], y[1]))
        if z:
            limits.append('Z[{0}:{1}]'.format(z[0], z[1]))
        if retur:
            if retur == 'first':
                limits.append('ReturnNumber[1:1]')
            else:
                filt_pred = Element('Filter')
                filt_pred.set("type", "filters.predicate")
                funct = self._add_option_file('filter', val='function')
                modu = self._add_option_file('anything', val='module')
                if retur == 'last':
                    source = self._add_option_file(LAST_RETURN, val='source')
                elif retur == 'others':
                    source = self._add_option_file(OTHER_RETURN, val='source')
                filt_pred.append(funct)
                filt_pred.append(modu)
                filt_pred.append(source)
        else:
            limits.append('ReturnNumber[:]')
        if clas:
            limits.append('Classification[{0}:{1}]'.format(clas, clas))
        if inte:
            limits.append('Intensity[{0}:{1}]'.format(inte[0], inte[1]))
        if angle:
            limits.append('ScanAngleRank[{0}:{1}]'.format(angle[0], angle[1]))
        
        if limits:
            filt.append(self._add_option_file(",".join(limits), val='limits'))
            if filt_pred is None:
                filt.append(self._add_reader(inp))
            else:
                filt_pred.append(self._add_reader(inp))
                filt.append(filt_pred)
            write.append(filt)
        else:
            # The only case in which we have no limits is when we have a filt_pred
            filt_pred.append(self._add_reader(inp))
            write.append(filt_pred)
            
        root.append(write)
        if sys.platform == 'win32':
            tmp_file.write(tostring(root, 'iso-8859-1'))
        else:
            tmp_file.write(tostring(root, 'utf-8'))
        tmp_file.close()
        self.pdalxml = tmp_file.name
        return 0

    def filterr(self, inp, out, x=None, y=None, z=None, inte=None, angle=None,
                clas=None, retur=None, forced=False, compressed=False, local=False):
        """
        :param str inp: full path for the input LAS file
        :param str out: full path for the outpu LAS file
        :param list x: a two values list with min and max value for x
        :param list y: a two values list with min and max value for y
        :param list z: a two values list with min and max value for z
        :param list inte: a two values list with min and max value for intesity
        :param list angle: a two values list with min and max value for scan
                           angle
        :param str clas: number of class to maintain
        :param str retur: the return to keep, the accepted values are:
                           first, last, others
        :param str forced: liblas o pdal as value
        :param bool compressed: True to obtain a LAZ file
        """
        command = self._start_command(forced)
        
        try:
            os.remove(out)
        except OSError:
            pass
        
        if 'las2las' in command:
            if compressed:
                command.append('-c')
            command.extend(['-i', inp, '-o', out])
            self.lasinfo(inp)
            if x:
                command.extend(['-e', "{minx} {miny} {minz} {maxx} {maxy} "
                                "{maxz}".format(minx=x[0], miny=self.mins[1],
                                                minz=self.mins[2], maxx=x[0],
                                                maxy=self.maxs[1],
                                                maxz=self.maxs[2])])
            if y:
                command.extend(['-e', "{minx} {miny} {minz} {maxx} {maxy} "
                                "{maxz}".format(minx=self.mins[0], miny=y[0],
                                                minz=self.mins[2], maxx=self.maxs[0],
                                                maxy=y[1], maxz=self.maxs[2])])
            if z:
                command.extend(['-e', "{minx} {miny} {minz} {maxx} {maxy} "
                                "{maxz}".format(minx=self.mins[0],
                                                miny=self.mins[1], minz=z[0],
                                                maxx=self.maxs[0], maxy=self.maxs[1],
                                                maxz=z[1])])
            if clas:
                command.extend(['--keep-classes', str(clas)])
            if inte:
                command.extend(['--keep-intensity',
                                '{mi}-{ma}'.format(mi=inte[0],  ma=inte[1])])
            if angle:
                command.extend(['--keep-scan-angle',
                                '{mi}-{ma}'.format(mi=angle[0], ma=angle[1])])
            if retur == 'first':
                command.extend(['--first-return-only'])
            elif retur == 'last':
                command.extend(['--last-return-only'])
            elif retur == 'others':
                self.lasinfo(inp)
                command.extend(['--drop-returns',
                                '1 {last}'.format(last=max(self.returns))])
            self._run_command(command)
        else:
            self.filter_xml_pdal(inp, out, compressed, x, y, z,
                                 inte, angle, clas, retur)
            command.extend(['-i', self.pdalxml])
            if not local:
                xml = read_file(self.pdalxml)
                pipe = libpdalpython.PyPipeline(xml)
                pipe.execute()
            else:
                self._run_command(command)
        return command

    def bosco(self, inp, out, h_sterpaglia = None, cell_size = None, thickness_min = None, R2_min_perc = None, delta_R = None):
        import os
        import sys
        import numpy as np
        from laspy.file import File
        
        import layers as ls
        import typess
        
        h_sterpaglia = h_sterpaglia if h_sterpaglia is not None else 1
        cell_size = cell_size if cell_size is not None else 4
        
        layers = ls.LayersComputation()
        layers.initialize(thickness_min = thickness_min, R2_min_perc = R2_min_perc, delta_R = delta_R)
        
        # -------------------------------------------------------------------------------- 
        # --------------------------- Vegetation Classifier --------------------------- 
        # -------------------------------------------------------------------------------- 
        # Coded by Lake Ishikawa
        # Base on algorithms published by G. Serafini and G. Webber
        
        # Read input file
        inFile = File(inp, mode = "r")
        
        # Find out what the point format looks like.
        print("--------------------------------------------")
        print("--- Welcome to vegetation-classifier 1.0 ---")
        print("--------------------------------------------")
        
        print("---Input file format:-----------------------")
        pointformat = inFile.point_format
        for spec in inFile.point_format:
            print(spec.name)
            
        # Grab all of the points from the file.
        all_points = np.vstack([inFile.x, inFile.y, inFile.z, inFile.return_num, inFile.intensity]).transpose()
        
        max_return_num = max(set(inFile.return_num))
        
#         print("---Header info:-----------------------------")
        maximum = inFile.header.max
        minimum = inFile.header.min
#         print("Scale: " + str(inFile.header.scale))
#         print("Offset: " + str(inFile.header.offset))
#         print("Max: " + str(max))
#         print("Min: " + str(min))
#         
#         print("---Number of points:------------------------")
#         print(len(all_points))
        
        # Divide in small chunks so you don't run out of memory
        #chunk_points = all_points[:
        
#         # Filter out sterpaglia
#         sterpaglia_points = []
#         for p in all_points:
#             if h_sterpaglia > p[2]:
#                 sterpaglia_points.append(p)
#         print("---Sterpaglia points:-----------------------")
#         print(len(sterpaglia_points))
#         
#         # Take non-sterpaglia points
#         valid_points = []
#         for p in all_points:
#             if h_sterpaglia <= p[2]:
#                 valid_points.append(p)
#         print("---Non-sterpaglia points:-------------------")
#         print(len(valid_points))

        sterpaglia_points = [p for p in all_points if h_sterpaglia > p[2]]
        valid_points = [p for p in all_points if h_sterpaglia <= p[2]]
        
        # Calculate the number of required tile squares
        tilesNumX = int((inFile.header.max[0] - inFile.header.min[0]) / cell_size) + 1
        tilesNumY = int((inFile.header.max[1] - inFile.header.min[1]) / cell_size) + 1
        print("---Number of tiles: " + str(tilesNumX)+ " x " + str(tilesNumY))
        
        # Construct tile map data to map points to their tiles.
        # Every tile will contain the points that are inside that tile.
        tiles = [None] * (tilesNumX * tilesNumY)
        for p in valid_points:
            try:
                x = int((p[0] - minimum[0]) / cell_size)
                y = int((p[1] - minimum[1]) / cell_size)
                cellId = y*tilesNumX + x;
                if tiles[ cellId ] == None: tiles[ cellId ] = []
                tiles[ cellId ].append(p)
            except IndexError as err:
                print "x:{0}; y:{1}; tilesNumX:{2}; cellId:{3}".format(x, y, tilesNumX, cellId)
                raise err
            
        # Process every tile with its points!
        clusters = []
        for i, tile in enumerate(tiles):
            if 1%100 == 0:
                print("Processing tile " + str(i+1) + "/" + str(len(tiles)))
            
            # Only if it has any point at all
            if tile != None:
                # ALGORYTHM PART 1 - LAYER NUMBER COMPUTATION
                newClusters = layers.compute_layers(tile, max_return_num)
                clusters.extend(newClusters)
                
                # ALGORYTHM PART 2 - TYPE COMPUTATION
                typess.compute_types(newClusters)
            
        # Write everything to a txt!
        fid = open("fascia.txt", 'w')
        for cluster in clusters:
            for i in range(len(cluster.points)):
                point = cluster.points[i]
                type = cluster.typess[i]
                fid.write("%f %f %f %f %f %f %f\n" % (point[0], point[1], point[2], point[3], point[4], cluster.clusterId+1, type))
            
        # Sterpaglia
        for p in sterpaglia_points:
            fid.write("%f %f %f %f %f %f %f\n" % (p[0], p[1], p[2], p[3], p[4], 5, 5))
            
        # Convert to las
        fid.close()
        exe_string = "txt2las -i fascia.txt -o {0} -parse xyzricp".format(out)
        os.system(exe_string)

    def zonal_statistics(self, inlas, invect, output, stats, overwrite=False,
                         ogrdriver='ESRI Shapefile', dimension='Z'):
        """Calculate statistics of point cloud heigths for each polygon in
        invect

        :param str inlas: the input LAS file
        :param str invect: the input vector polygon file
        :param str output: the output vector file
        :param list stats: a list with stats to calculate
        :param bool overwrite: overwrite existing files
        :param str ogrdriver: the name of OGR driver to use
        """
        import osgeo.ogr as ogr
        statistics = {'hcv': hcv, 'max': np.max, 'mean': np.mean,
                      'p10': np.percentile, 'p20': np.percentile,
                      'p30': np.percentile, 'p40': np.percentile,
                      'p50': np.percentile, 'p60': np.percentile,
                      'p70': np.percentile, 'p80': np.percentile,
                      'p90': np.percentile, 'c2m': number_return,
                      'cmean': number_return, 'mode': mode}
        vect = infoOGR()
        vect.initialize(invect)
        if vect.getType() not in [ogr.wkbPolygon, ogr.wkbPolygon25D,
                                  ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D]:
            raise Exception("Geometry type is not supported, please use a "
                            "polygon vector file")
            return 1
        driver = ogr.GetDriverByName(ogrdriver)
        if overwrite:
            try:
                # driver.DeleteDataSource(outvect)
                driver.DeleteDataSource(output)
            except Exception:
                pass
        # newdata = driver.CreateDataSource(outvect)
        newdata = driver.CreateDataSource(output)
        newdata.CopyLayer(vect.lay0, 'las_zonal_stats')
        newlayer = newdata.GetLayer()
        for s in stats:
            field = ogr.FieldDefn(str(s), ogr.OFTReal)
            newlayer.CreateField(field)
        for inFeature in newlayer:
            inGeom = inFeature.GetGeometryRef()
            output_file = tempFileName()
            self.clip_txt_pdal(inlas, output_file, inGeom.ExportToWkt())
            
#             # extract output file name
#             import xml.etree.ElementTree as ElementTree
#             
#             tree = ElementTree.parse(self.pdalxml)
#             root = tree.getroot()
#             
#             # substitute output type to be text (for easier processing)
#             elements = root.findall("Writer[@type='writers.las']")
#             elements[0].attrib['type'] = 'writers.text'
#             pdalxml_csv_output = self.pdalxml + "_csv_output"
#             tree.write(pdalxml_csv_output)           
#             
#             tree = ElementTree.parse(self.pdalxml)
#             root = tree.getroot()
#             elements = root.findall("Writer[@type='writers.las']/Option[@name='filename']")
#           
#             # get pipeline output file
#             output_file = elements[0].text
            
            # execute the pipeline using the command line tools
            p = subprocess.Popen(['pdal', 'pipeline', '-i', self.pdalxml], shell=False, stdin=PIPE,
                                 stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            
            if p.returncode != 0:
                raise Exception("Errore eseguendo pdal pipeline: "+err)
            

            # read output as csv file
            import csv
            zs = []
            with open(output_file) as csvfile:
                reader = csv.DictReader(csvfile)
                zs = [float(row[dimension]) for row in reader]
                
#             xml = read_file(self.pdalxml)            
#             pipe = libpdalpython.PyPipeline(xml)                     
#             pipe.execute()
#             data = pipe.arrays()[0]
#             zs = map(lambda x: x[2], data)
            if len(zs) != 0:
                for s in stats:
                    if s in ['hcv', 'max', 'mean']:
                        val = statistics[s](zs)
                    elif s == 'mode':
                        val, _ = mode(np.asarray(zs))
                        val = val[0] #we estract the element from the array
                    elif s == 'c2m':
                        val = statistics[s](np.asarray(zs), 2)
                    elif s == 'cmean':
                        mean = np.mean(zs)
                        val = statistics[s](np.asarray(zs), mean)
                    else:
                        perc = int(s.replace('p', ''))
                        val = statistics[s](zs, perc)
                    inFeature.SetField(str(s), val)
            newlayer.SetFeature(inFeature)
            inFeature = None
        newdata.Destroy()


def get_parser():
    """Create the parser for running as script"""
    import argparse
    parser = argparse.ArgumentParser(description='Script for LAS operations')
    parser.add_argument('input', metavar='input', type=str, nargs='*',
                        help='the path to the input LAS file')
    parser.add_argument('output', metavar='output', type=str, nargs='*',
                        help='the path to the output LAS file')
    parser.add_argument('-c', '--clip', dest='clip', type=str,
                        help='sum the integers (default: find the max)')
    parser.add_argument('-s', '--server', action='store_true',
                        dest='server', default=False,
                        help="launch server application")
    return parser


def main():
    """This function is used in the server to activate three Pyro4 servers.
       It initialize the three objects and after these are used by Pyro4
    """
    parser = get_parser()
    args = parser.parse_args()
    if args.server:
        # decomment this two lines if you want activate the logging
        #os.environ["PYRO_LOGFILE"] = "pyrolas.log"
        #os.environ["PYRO_LOGLEVEL"] = "DEBUG"
        import Pyro4
        las_stem = stemLAS()
        daemon = Pyro4.Daemon(host=PYROSERVER, port=LAS_PORT)
        uri = daemon.register(las_stem, objectId=LASPYROOBJNAME, force=True)
        ns = Pyro4.locateNS()
        ns.register("PyroLasStem", uri)
        daemon.requestLoop()
    else:
        print args

if __name__ == "__main__":

    main()
