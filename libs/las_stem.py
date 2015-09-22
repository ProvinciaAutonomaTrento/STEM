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
from pyro_stem import PYROSERVER, LAS_PORT
from gdal_stem import file_info
from stem_utils import STEMUtils, STEMMessageHandler
import os
import json
import sys
PIPE = subprocess.PIPE

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
    inrast = '{NAME}'
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
                    STEMMessageHandler.warning(laserr[0].strip())
                    return False
            else:
                STEMMessageHandler.warning(laserr[0].strip())
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
        option.text = fil
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

        if com.returncode != 0 and err != '':
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
            STEMUtils.saveCommand(command)
            self._run_command(command)
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
            tmp_file.write(tostring(root))
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
            STEMUtils.saveCommand(command)
            self._run_command(command)
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
            tmp_file.write(tostring(root))
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
        wkt = STEMUtils.check_wkt(area)
        if wkt:
            command = self._start_command('pdal')
        else:
            command = self._start_command(forced)
        if 'las2las' in command:
            if compressed:
                command.append('-c')
            if inverted:
                STEMMessageHandler.warning("Non è possibile utilizzare "
                                           "l'opzione 'Maschera inversa' con "
                                           "la libreria liblas")
            command.extend(['-i', inp, '-o', out, '-e', area])
        else:
            if not wkt:
                coors = area.split()
                area = "POLYGON (({minx} {miny}, {minx} {maxy}, {maxx} {maxy}" \
                       ", {maxx} {miny}, {minx} {miny}))".format(minx=coors[0],
                                                                 miny=coors[1],
                                                                 maxx=coors[1],
                                                                 maxy=coors[1])
            self.clip_xml_pdal(inp, out, area, compressed, inverted)
            command.extend(['-i', self.pdalxml])
        STEMUtils.saveCommand(command)
        self._run_command(command)

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
            minxval = self._add_option_file(x[0], val='min')
            maxxval = self._add_option_file(x[1], val='max')
            x_opt.append(minxval)
            x_opt.append(maxxval)
            filt.append(x_opt)
        if y:
            y_opt = self._add_option_file('Y', val='dimension')
            minyval = self._add_option_file(y[0], val='min')
            maxyval = self._add_option_file(y[1], val='max')
            y_opt.append(minyval)
            y_opt.append(maxyval)
            filt.append(y_opt)
        if z:
            z_opt = self._add_option_file('Z', val='dimension')
            minzval = self._add_option_file(z[0], val='min')
            maxzval = self._add_option_file(z[1], val='max')
            z_opt.append(minzval)
            z_opt.append(maxzval)
            filt.append(z_opt)
        if retur:
            if retur == 'first':
                first_opt = self._add_option_file('ReturnNumber',
                                                  val='dimension')
                firstval = self._add_option_file(1, val='uquals')
                first_opt.append(firstval)
                filt.append(first_opt)
            else:
                filt_ret = Element('Filter')
                filt_ret.set("type", "filters.predicate")
                funct = self._add_option_file('filter', val='function')
                modu = self._add_option_file('anything', val='module')
                if retur == 'last':
                    source = self._add_option_file(LAST_RETURN, val='source')
                elif retur == 'others':
                    source = self._add_option_file(OTHER_RETURN, val='source')
                filt_ret.append(funct)
                filt_ret.append(modu)
                filt_ret.append(source)
        if clas:
            clas_opt = self._add_option_file('Classification', val='dimension')
            clasval = self._add_option_file(clas, val='uquals')
            clas_opt.append(clasval)
            filt.append(clas_opt)
        if inte:
            int_opt = self._add_option_file('Intensity', val='dimension')
            minintval = self._add_option_file(inte[0], val='min')
            maxintval = self._add_option_file(inte[1], val='max')
            int_opt.append(minintval)
            int_opt.append(maxintval)
            filt.append(int_opt)
        if angle:
            ang_opt = self._add_option_file('ScanAngleRank', val='dimension')
            minangval = self._add_option_file(angle[0], val='min')
            maxangval = self._add_option_file(angle[1], val='max')
            ang_opt.append(minangval)
            ang_opt.append(maxangval)
            filt.append(ang_opt)
        filt.append(self._add_reader(inp))
        write.append(filt)
        root.append(write)
        if sys.platform == 'win32':
            tmp_file.write(tostring(root))
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
        STEMUtils.saveCommand(command)
        self._run_command(command)


def get_parser():
    """Create the parser for running as script"""
    import argparse
    parser = argparse.ArgumentParser(description='Script for LAS operations')
    parser.add_argument('input', metavar='input', type=str, nargs='+',
                        help='the path to the input LAS file')
    parser.add_argument('output', metavar='output', type=str, nargs='+',
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
        Pyro4.Daemon.serveSimple({las_stem: "stem.las"},
                                 host=PYROSERVER, port=LAS_PORT, ns=True)
    else:
        print args

if __name__ == "__main__":

    main()
