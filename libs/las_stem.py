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
from stem_utils import STEMUtils, STEMMessageHandler
import os
import json
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

    def initialize(self):
        """Initialization of class"""
        self._check()

    def _check(self):
        """Check which libraries is present on the system"""
        self.pdal = self._checkLibs('pdal-config --version')
        self.liblas = self._checkLibs('liblas-config --version',
                                      'las2las --help')

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
                com = subprocess.Popen(command, shell=True, stdin=PIPE,
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
            return ['las2las']

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

        clip = self._add_option_file(bbox, 'polygon')
        if inverted:
            clip.set("outside", "true")
        filt.append(clip)
        filt.append(self._add_reader(inp))
        write.append(filt)
        root.append(write)
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
                funct = self._add_option_file('filter_class', val='function')
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
            if x:
                command.extend(['--minx', x[0], '--maxx', x[1]])
            if y:
                command.extend(['--miny', y[0], '--maxy', y[1]])
            if z:
                command.extend(['--minz', z[0], '--maxz', z[1]])
            if clas:
                command.extend(['--keep-classes', str(clas)])
            if inte:
                command.extend(['--keep-intensity', '>={va}'.format(va=inte[0]),
                                '--keep-intensity', '<={va}'.format(va=inte[1])])
            if angle:
                command.extend(['--keep-scan-angle', '>={va}'.format(va=angle[0]),
                                '--keep-scan-angle', '<={va}'.format(va=angle[1])])
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


def main():
    """This function is used in the server to activate three Pyro4 servers.
       It initialize the three objects and after these are used by Pyro4
    """
    # decomment this two lines if you want activate the logging
    #os.environ["PYRO_LOGFILE"] = "pyrolas.log"
    #os.environ["PYRO_LOGLEVEL"] = "DEBUG"
    import Pyro4
    las_stem = stemLAS()
    Pyro4.Daemon.serveSimple({las_stem: "stem.las"},
                             host=PYROSERVER, port=LAS_PORT, ns=True)

if __name__ == "__main__":
    main()
