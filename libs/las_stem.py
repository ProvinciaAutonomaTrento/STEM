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

FILTER_NONE = """
import numpy as np

def filter(ins,outs):
   cls = ins['Z']

   excluded_classes = [None]

   keep = np.not_equal(cls, excluded_classes[0])

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
        val = structval[0][0]
        if cmp(val, 0) == -1:
            val = 0
        return val
    except:
        return None

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
            z = None
        if z:
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

    def _run_command(self, comm):
        """Run the command and return the output

        :param list comm: the list containing the command to run
        """
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
                os.remove(self.pdalxml)
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
        source = self._add_option_file(FILTER_NONE, val='source')
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

    def chm(self, inp, out, dtm, compressed=False):
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

    def union(self, inps, out, compressed=False):
        """Merge several LAS file into one LAS file

        :param str inp: full path for the input LAS file
        :param str out: full path for the output LAS file
        :param bool compressed: True to obtain a LAZ file
        """
        if self.pdal:
            command = ['pdal', 'pipeline']
            self.union_xml_pdal(inps, out, compressed)
            command.extend(['-i', self.pdalxml])
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

        clip = self._add_option_file(bbox, val='polygon')
        if inverted:
            clip.set("outside", "true")
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
             compressed=False):
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
        if x:
            x_opt = self._add_option_file('X', val='dimension')
            options = Element('Options')
            minxval = self._add_option_file(x[0], val='min')
            maxxval = self._add_option_file(x[1], val='max')
            options.append(minxval)
            options.append(maxxval)
            x_opt.append(options)
            filt.append(x_opt)
        if y:
            y_opt = self._add_option_file('Y', val='dimension')
            options = Element('Options')
            minyval = self._add_option_file(y[0], val='min')
            maxyval = self._add_option_file(y[1], val='max')
            options.append(minyval)
            options.append(maxyval)
            y_opt.append(options)
            filt.append(y_opt)
        if z:
            z_opt = self._add_option_file('Z', val='dimension')
            options = Element('Options')
            minzval = self._add_option_file(z[0], val='min')
            maxzval = self._add_option_file(z[1], val='max')
            options.append(minzval)
            options.append(maxzval)
            z_opt.append(options)
            filt.append(z_opt)
        if retur:
            if retur == 'first':
                first_opt = self._add_option_file('ReturnNumber[1:1]',
                                                  val='limits')
                filt.append(first_opt)
            else:
                filt = None
                filt = Element('Filter')
                filt.set("type", "filters.predicate")
                funct = self._add_option_file('filter', val='function')
                modu = self._add_option_file('anything', val='module')
                if retur == 'last':
                    source = self._add_option_file(LAST_RETURN, val='source')
                elif retur == 'others':
                    source = self._add_option_file(OTHER_RETURN, val='source')
                filt.append(funct)
                filt.append(modu)
                filt.append(source)
        if clas:
            clas_opt = self._add_option_file('Classification', val='dimension')
            options = Element('Options')
            clasval = self._add_option_file(clas, val='uquals')
            options.append(clasval)
            clas_opt.append(options)
            filt.append(clas_opt)
        if inte:
            int_opt = self._add_option_file('Intensity', val='dimension')
            options = Element('Options')
            minintval = self._add_option_file(inte[0], val='min')
            maxintval = self._add_option_file(inte[1], val='max')
            options.append(minintval)
            options.append(maxintval)
            int_opt.append(options)
            filt.append(int_opt)
        if angle:
            ang_opt = self._add_option_file('ScanAngleRank', val='dimension')
            options = Element('Options')
            minangval = self._add_option_file(angle[0], val='min')
            maxangval = self._add_option_file(angle[1], val='max')
            options.append(minangval)
            options.append(maxangval)
            ang_opt.append(options)
            filt.append(ang_opt)
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

    def filterr(self, inp, out, x=None, y=None, z=None, inte=None, angle=None,
                clas=None, retur=None, forced=False, compressed=False):
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
        else:
            self.filter_xml_pdal(inp, out, compressed, x, y, z,
                                 inte, angle, clas, retur)
            command.extend(['-i', self.pdalxml])
        self._run_command(command)
        return command

    def bosco(self, inp, prefix):
        """
        :param str inp: full path for the input LAS file
        :param str prefix: prefix for the output LAS file
        """
        try:
            from runtime import *
        except ImportError:
            from smop.runtime import *
        import copy
        import struct
        from bosco_stem import read_las_header, readlas_1_2_
        from bosco_stem import compute_layers_, compute_types_
        h_sterpaglia = 1.0
        dim_celle = 4
        n_layers_TOT = 0
        layer1_TOT = 0
        layer2_TOT = 0
        layer3_TOT = 0
        layer4_TOT = 0
        n_layers_riga = 0
        layer1_riga = 0
        layer2_riga = 0
        layer3_riga = 0
        layer4_riga = 0
        presenza_punti = 0
        zona = [2]
        size_zona = len(zona)
        for fascia in range(0, size_zona):
            row_offset = 1
            data_TOT = []
            lasHeaderInfo = read_las_header(inp)
            fid = open(inp, "rb")
            fid.seek(24)
            ionMajor = struct.unpack('B', fid.read(1))[0]
            VersionMinor = struct.unpack('B', fid.read(1))[0]
            fid.seek(96)
            OffsetToPointData = struct.unpack('I', fid.read(4))[0]
            fid.seek(131)
            XScaleFactor = struct.unpack('d', fid.read(8))[0]
            YScaleFactor = struct.unpack('d', fid.read(8))[0]
            ZScaleFactor = struct.unpack('d', fid.read(8))[0]
            XOffset = struct.unpack('d', fid.read(8))[0]
            YOffset = struct.unpack('d', fid.read(8))[0]
            ZOffset = struct.unpack('d', fid.read(8))[0]
            dato = readlas_1_2_(inp, char('xyzir'))
            X = dato[0].X
            Y = dato[0].Y
            Z = dato[0].Z
            R = dato[0].returnNumber
            I = dato[0].intensity

            data = [X, Y, Z, R, I]

            data_inferiore = [[], [], [], [], []]
            data_superiore = [[], [], [], [], []]
            for i in range(0, len(X)):
                if Z[i] <= h_sterpaglia:
                    data_inferiore[0].append(X[i])
                    data_inferiore[1].append(Y[i])
                    data_inferiore[2].append(Z[i])
                    data_inferiore[3].append(R[i])
                    data_inferiore[4].append(I[i])
                else:
                    data_superiore[0].append(X[i])
                    data_superiore[1].append(Y[i])
                    data_superiore[2].append(Z[i])
                    data_superiore[3].append(R[i])
                    data_superiore[4].append(I[i])
            data = data_superiore

            npoint = len(data[0])
            h = 5
            fid.close()
            min_x = min(data[0])
            max_x = max(data[0])
            max_y = max(data[1])
            min_y = min(data[1])
            columns = ceil(max_x - min_x)
            lines = ceil(max_y - min_y)
            x_coord = copy_(min_x)
            y_coord = copy_(max_y)
            ris = 1
            x_coord = x_coord - (ris / 2)
            y_coord = y_coord + (ris / 2)
            mtrows = int(ceil(lines / dim_celle) * dim_celle)
            mtcols = int(ceil(columns / dim_celle) * dim_celle)
            tmp = zeros_(mtrows, mtcols)
            k = 1
            for i in range(0, int(ceil(lines / (dim_celle / 2)) * (dim_celle / 2)),
                           dim_celle):
                for j in range(int(ceil(columns / dim_celle))):
                    tmp[arange_(i, i + dim_celle - 1),
                        arange_(j * dim_celle, (j + 1) * dim_celle-1)] = k
                    k = k + 1
            S = tmp[0:lines, 0:columns]
            tmp = zeros_(ceil(lines / (dim_celle / 2)) * (dim_celle / 2),
                         ceil(columns / (dim_celle / 2)) * (dim_celle / 2))
            k = 1
            for i in range(0, int(ceil(lines / (dim_celle / 2)) * (dim_celle / 2)),
                           int(dim_celle / 2)):
                for j in range(int(ceil(columns / (dim_celle / 2)))):
                    tmp[arange_(i, i + (dim_celle / 2) - 1),
                        arange_(j * (dim_celle / 2),
                                (j + 1) * (dim_celle / 2) - 1)] = k
                    k = k + 1
            nseed = max_(max_(S))
            print nseed
            data_fil = 0
            nseed
            for i in range(1, nseed):
                print 'i=' + str(i)
                data_tmp = [[], [], [], [], []]
                for j in range(npoint):
                    x_c = round_(data[0][j] - x_coord) - 1
                    y_c = round_(y_coord - data[1][j]) - 1
                    if (x_c >= 0) and (y_c >= 0) and (x_c < columns) and (y_c < lines):
                        if (S[y_c, x_c] == i):
                            for di in range(len(data_tmp)):
                                data_tmp[di].append(data[di][j])
                if len(data_tmp[0]) > 3:
                    print 'ans=' + str(len(data_tmp[0]))
                    n_layers, h_medie, T = compute_layers_(data_tmp, nargout=3)
                    data_tmp_T = copy.deepcopy(data_tmp)
                    data_tmp_T.append(T)
                    _type = compute_types_(data_tmp_T, n_layers, h_medie)
                    data_tmp_type = copy.deepcopy(data_tmp_T)
                    data_tmp_type.append(_type)
                    if len(data_TOT) == 0:
                        data_TOT = copy.deepcopy(data_tmp_type)
                    else:
                        for di in range(len(data_TOT)):
                            data_TOT[di].extend(data_tmp_type[di])

            size_data_inferiore = len(data_inferiore[0])
            T_inf = np.empty(size_data_inferiore)
            T_inf.fill(5)
            T_inf = T_inf.tolist()
            Type_inf = copy.deepcopy(T_inf)
            data_inferiore.append(T_inf)
            data_inferiore.append(Type_inf)
            for i in range(len(data_TOT)):
                data_TOT[i].extend(data_inferiore[i])

            savefile = 'fascia_{num}.txt'.format(num=str(zona[fascia]))
            fid = open(savefile, 'w')
            for i in range(len(data_TOT[0])):
                fid.write("%f %f %f %f %f %f %f\n" % (data_TOT[0][i],
                                                      data_TOT[1][i],
                                                      data_TOT[2][i],
                                                      data_TOT[3][i],
                                                      data_TOT[4][i],
                                                      data_TOT[5][i],
                                                      data_TOT[6][i]))
            fid.close()
            out = "{pref}_{num}.las".format(pref=prefix, num=str(zona[fascia]))
            self.txt2las(savefile, out)

    def zonal_statistics(self, inlas, invect, output, stats, overwrite=False,
                         ogrdriver='ESRI Shapefile'):
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
                      'cmean': number_return}
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
            field = ogr.FieldDefn(s, ogr.OFTReal)
            newlayer.CreateField(field)
        for inFeature in newlayer:
            inGeom = inFeature.GetGeometryRef()
            outlas = tempFileName()
            self.clip_xml_pdal(inlas, outlas, inGeom.ExportToWkt(), True)
            xml = read_file(self.pdalxml)
            pipe = libpdalpython.PyPipeline(xml)
            pipe.execute()
            data = pipe.arrays()[0]
            zs = map(lambda x: x[2], data)
            if len(zs) != 0:
                for s in stats:
                    if s in ['hcv', 'max', 'mean']:
                        val = statistics[s](zs)
                    elif s == 'c2m':
                        val = statistics[s](zs, 2)
                    elif s == 'cmean':
                        mean = np.mean(zs)
                        val = statistics[s](zs, mean)
                    else:
                        perc = int(s.replace('p', ''))
                        val = statistics[s](zs, perc)
                    inFeature.SetField(s, val)
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
