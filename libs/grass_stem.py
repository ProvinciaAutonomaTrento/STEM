# -*- coding: utf-8 -*-

"""
Library to work with GRASS inside the STEM project

Date: August 2014
Copyright: (C) 2014 Luca Delucchi

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = 'Luca Delucchi'
__date__ = 'August 2014'
__copyright__ = '(C) 2014 Luca Delucchi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import subprocess
from pyro_stem import PYROSERVER, GRASS_PORT, GRASSPYROOBJNAME
from stem_utils_server import STEMSettings, inverse_mask, libs_save_command

stats = ['mean', 'n', 'min', 'max', 'range', 'sum', 'stddev', 'variance',
         'coeff_var', 'median', 'percentile', 'skewness', 'trimmean']


def helpUrl(name):
    """Create the url for GRASS manuals page

    :param str name: the name of grass command
    """
    return "http://grass.osgeo.org/grass70/manuals/{n}.html".format(n=name)


def readfile(path):
    """Read the file and return a string

    :param str path: the path to a file
    """
    f = open(path, 'r')
    s = f.read()
    f.close()
    return s


def writefile(path, s):
    """Write the file from a string, new line should be added in the string

    :param str path: the path to a file
    :param str s: the string to write into file
    """
    f = open(path, 'w')
    f.write(s)
    f.close()

PIPE = subprocess.PIPE


def QGISettingsGRASS(grassdatabase=None, location=None, grassbin=None,
                     epsg=None, local=True):
    """Read the QGIS's settings and obtain information for GRASS GIS

    :param str grassdatabase: the path to grassdatabase
    :param str location: the name of location
    :param str grassbin: the path to grass7 binary
    :param str epsg: the epsg code to use
    """
    # query GRASS 7 itself for its GISBASE
    # we assume that GRASS GIS' start script is available and in the PATH
    if local:
        if not grassbin:
            grassbin = str(STEMSettings.value("grasspath", ""))
        if not grassdatabase:
            grassdatabase = str(STEMSettings.value("grassdata", ""))
        if not location:
            location = str(STEMSettings.value("grasslocation", ""))
        if not epsg:
            epsg = str(STEMSettings.value("epsgcode", ""))
    else:
        if not grassbin:
            grassbin = str(STEMSettings.value("grasspathserver", ""))
        if not grassdatabase:
            grassdatabase = str(STEMSettings.value("grassdataserver", ""))
        if not location:
            location = str(STEMSettings.value("grasslocationserver", ""))
        if not epsg:
            epsg = str(STEMSettings.value("epsgcode", ""))

    return grassdatabase, location, grassbin, epsg


def temporaryFilesGRASS(name, local=True):
    """Create temporary grass information (input and output data name and
    a stemGRASS object)

    :param str name: the name of input map
    :param bool local: true to create local grass connection otherwise it
                       try to connetc with the server
    """
    pid = os.getpid()
    tempin = 'stem_{name}_{pid}'.format(name=name, pid=pid)
    tempout = 'stem_output_{pid}'.format(pid=pid)
    grassdatabase, location, grassbin, epsg = QGISettingsGRASS(local=local)
    if local:
        gs = stemGRASS()
    else:
        import Pyro4
        gs = Pyro4.Proxy("PYRO:{name}@{ip}:{port}".format(ip=PYROSERVER,
                                                          port=GRASS_PORT,
                                                          name=GRASSPYROOBJNAME))
    gs.initialize(pid, grassdatabase, location, grassbin, epsg)
    return tempin, tempout, gs


class stemGRASS():
    """The class to use GRASS GIS as backend of STEM plugin"""
    def __init__(self):
        self.mapset = None
        self.mapsetpath = None

    def initialize(self, pid, grassdatabase, location, grassbin, epsg):
        startcmd = [grassbin, '--config', 'path']
        p = subprocess.Popen(startcmd, shell=False, stdin=PIPE,
                             stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            raise Exception("Errore eseguendo GRASS: Vanno settate tutte le "
                            "variabili necessarie: GRASSDATA, LOCATION ed "
                            "eseguibile")
        if sys.platform.startswith('linux'):
            gisbase = out.strip()
        elif sys.platform.startswith('win'):
            if out.find("OSGEO4W home is") != -1:
                gisbase = out.strip().splitlines()[1]
            else:
                gisbase = out.strip()
            os.environ['GRASS_SH'] = os.path.join(gisbase, 'msys', 'bin',
                                                  'sh.exe')
        # Set GISBASE environment variable
        os.environ['GISBASE'] = gisbase
        # define GRASS-Python environment
        gpydir = os.path.join(gisbase, "etc", "python")
        sys.path.append(gpydir)

        ########### DATA
        # define GRASS DATABASE
        # Set GISDBASE environment variable
        os.environ['GISDBASE'] = grassdatabase
        os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')

        self.mapset = 'stem_{pid}'.format(pid=pid)
        locexist = os.path.join(grassdatabase, location)
        if not os.path.exists(locexist):
            if not epsg:
                raise Exception("Errore eseguendo GRASS: ",
                                "Manca il codice EPSG nelle impostazioni")
            startcmd = grassbin + ' -c EPSG:' + epsg + ' -e ' + locexist
            p = subprocess.Popen(startcmd, shell=True, stdin=PIPE,
                                 stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                raise Exception("Errore eseguendo GRASS: ",
                                "Creazione della location fallita")
        self.mapsetpath = os.path.join(grassdatabase, location, self.mapset)
        if not os.path.exists(self.mapsetpath):
            os.mkdir(self.mapsetpath)
        wind = readfile(os.path.join(grassdatabase, location, "PERMANENT",
                                     "DEFAULT_WIND"))
        writefile(os.path.join(self.mapsetpath, "WIND"), wind)

        path = os.getenv('LD_LIBRARY_PATH')
        dirlib = os.path.join(gisbase, 'lib')
        if path:
            path = dirlib + os.pathsep + path
        else:
            path = dirlib
        os.environ['LD_LIBRARY_PATH'] = path

        # language
        os.environ['LANG'] = 'en_US'
        os.environ['LOCALE'] = 'C'
        ###########
        # launch session
        import grass.script.setup as gsetup
        gsetup.init(gisbase, grassdatabase, location, self.mapset)
        if 'GRASS_PROJSHARE' not in os.environ.keys():
            os.environ['GRASS_PROJSHARE'] = 'C:\OSGeo4W\share\proj'

        if 'GRASS_PYTHON' not in os.environ.keys():
            os.environ['GRASS_PYTHON'] = 'C:\OSGeo4W\bin\python.exe'

        if 'SHELL' not in os.environ.keys():
            os.environ['SHELL'] = 'C:\Windows\system32\cmd.exe'
        import grass.script.core as gcore
        gcore.os.environ['GRASS_OVERWRITE'] = '1'

    def list_maps(self, typ):
        com = ['g.list', 'type={ty}'.format(ty=typ)]
        runcom = subprocess.Popen(com, stdin=PIPE, stdout=PIPE,
                                  stderr=PIPE)
        out, err = runcom.communicate()
        if runcom.returncode != 0:
            raise Exception("Errore eseguendo GRASS: ",
                            "Errore eseguendo g.list {e}".format(e=err))
        else:
            return out.split()

    def check_mask(self, mask):
        """Check if a mask should be used

        :param str mask: the path to the mask, None to remove it
        """
        
        import grass.script.core as gcore
        if mask == '':
            runcom = gcore.Popen(['r.mask', '-r'])
            out, err = runcom.communicate()
            #  print out, err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: ",
                                "Errore eseguendo r.mask {e}".format(e=err))
        else:
            name = '_'.join(os.path.split(mask)[-1].split('.')[:-1])
            com = ['r.mask', 'vector={ma}'.format(ma=name)]
            # try to fix it
            try:
                vecs = self.list_maps('vector')
            except:
                vecs = []
            inv_mask = inverse_mask()
            if inv_mask:
                com.append('-i')
            if name not in vecs:
                runcom = gcore.Popen(['v.in.ogr', '--overwrite',
                                      'input={ma}'.format(ma=mask),
                                      'output={out}'.format(out=name)],
                                     stdin=PIPE, stdout=PIPE, stderr=PIPE)
                out, err = runcom.communicate()
                #  print out, err
                if runcom.returncode != 0:
                    raise Exception("Errore eseguendo GRASS: ",
                                    "Errore eseguendo v.in.ogr {e}".format(e=err))
                runcom = gcore.Popen(com,
                                     stdin=PIPE, stdout=PIPE, stderr=PIPE)
                out, err = runcom.communicate()
                if runcom.returncode != 0:
                    raise Exception("Errore eseguendo GRASS: ",
                                    "Errore eseguendo r.mask {e}".format(e=err))
            else:
                rasts = self.list_maps('raster')
                if 'MASK' not in rasts:
                    runcom = gcore.Popen(com,
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    out, err = runcom.communicate()
                    if runcom.returncode != 0:
                        raise Exception("Errore eseguendo GRASS: ",
                                        "Errore eseguendo r.mask {e}".format(e=err))

    def import_grass(self, inp, intemp, typ, nl=None):
        """Import data into GRASS database

        :param str inp: the path to source data
        :param str intemp: the name inside GRASS database
        :param str typ: the type of data
        :param list nl: a list containing the band to use of a raster
        """
        import grass.script.core as gcore

        if typ == 'raster' or typ == 'image':
            if len(nl) > 1:
                cmd = ['r.in.gdal', 'input={i}'.format(i=inp),
                                      'output={o}'.format(o=intemp),
                                      'band={bs}'.format(bs=','.join(nl))]
            elif len(nl) == 1 and str(nl[0]) == '1':
                cmd = ['r.in.gdal', 'input={i}'.format(i=inp),
                                      'output={o}'.format(o=intemp),
                                      'band=1']
            elif len(nl) == 1 and str(nl[0]) != '1':
                cmd = ['r.in.gdal', 'input={i}'.format(i=inp),
                                      'output={o}'.format(o=intemp),
                                      'band={bs}'.format(bs=nl[0])]
            print 'Eseguo il comando', cmd
            runcom = gcore.Popen(cmd,
                                 stdin=PIPE, stdout=PIPE,
                                 stderr=PIPE)
            out, err = runcom.communicate()
            #  print out, err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: ",
                                "Errore eseguendo r.in.gdal {e}".format(e=err))
            runcom = gcore.Popen(['g.list', 'type=raster',
                                  'pattern={n}*'.format(n=intemp),
                                  'mapset={maps}'.format(maps=self.mapset)],
                                 stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = runcom.communicate()
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo g.list {e}".format(e=err))
            listfiles = out.splitlines()
            first=listfiles[0]
            runcom = gcore.Popen(['g.region',
                                  'rast={r}'.format(r=first)],
                                 stdin=PIPE, stdout=PIPE, stderr=PIPE)

            out, err = runcom.communicate()
            #  print out,err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo g.region {e}".format(e=err))
            self.create_group(listfiles, intemp)

        elif typ == 'vector':
            runcom = gcore.Popen(['v.in.ogr', 'input={i}'.format(i=inp),
                                  'output={o}'.format(o=intemp)],
                                 stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = runcom.communicate()
            #  print out,err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo v.in.ogr {e}".format(e=err))

            runcom = gcore.Popen(['g.region', 'vect={i}'.format(i=intemp)],
                                 stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = runcom.communicate()
            #  print out,err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo g.region {e}".format(e=err))

    def vtorast(self, inp, column=None):
        """Convert vector to rast

        :param str inp: the input name
        :param str column: the name of cloumn to use to assign value to raster
        """
        import grass.script.core as gcore
        command = ['v.to.rast', 'input={name}'.format(name=inp),
                   'output={name}'.format(name=inp)]
        if column:
            command.extend(['use=attr',
                            'attribute_column={col}'.format(col=column)])
        else:
            command.append('use=val')
        runcom = gcore.Popen(command)
        out, err = runcom.communicate()
        #  print out,err
        if runcom.returncode != 0:
            raise Exception("Errore eseguendo GRASS: "
                            "Errore eseguendo v.to.rast {e}".format(e=err))

    def create_group(self, maps, gname, base=False):
        """Crea a group of raster data

        :param list maps: a list of maps name or a string if base is True
        :param str gname: the name of group
        :param bool base: if True maps is the prefix of maps to look for
        """
        import grass.script.core as gcore
        if base:
            #maps = gcore.list_grouped('rast', pattern='{base}*'.format(base=maps))[self.mapset]
            com = ['g.list', 'type=rast', 'pattern={base}*'.format(base=maps),
                   'mapset={maps}'.format(maps=self.mapset), 'separator=,']
            runcom = gcore.Popen(com,stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = runcom.communicate()
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo g.list {err}".format(err=err))
            maps = out.strip().split(',')
        runcom = gcore.Popen(['i.group', 'group={name}'.format(name=gname),
                              'subgroup={name}'.format(name=gname),
                              'input={maps}'.format(maps=','.join(maps))],
                             stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = runcom.communicate()
        #  print out,err
        if runcom.returncode != 0:
            raise Exception("Errore eseguendo GRASS: "
                            "Errore eseguendo i.group {err}".format(err=err))

    def export_grass(self, outemp, finalout, typ, remove=True):
        """Export the result of analisys

        :param str outemp: the output in GRASS
        :param str finalout: the path for the output
        :param str typ: the type of data
        :param bool remove: remove this mapset
        """
        import grass.script.core as gcore

        if typ == 'raster' or typ == 'image':
            runcom = gcore.Popen(['r.out.gdal',
                                  'input={outemp}'.format(outemp=outemp),
                                  'output={final}'.format(final=finalout)],
                                 stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = runcom.communicate()
            # print out,err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo r.out.gdal {err}".format(err=err))
            # gcore.run_command('r.out.gdal', input=outemp, output=finalout)
        elif typ == 'vector':
            runcom = gcore.Popen(['v.out.ogr', 'input={ip}'.format(ip=outemp),
                                  'output={out}'.format(out=finalout)])
            out, err = runcom.communicate()
            # print out,err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo v.out.ogr {err}".format(err=err))
        if remove:
            self.removeMapset()

    def las_import(self, inp, out, method, returnpulse=None, resolution=None,
                   percentile=None, trim=None, region=None):
        """Import LAS file trhough r.in.lidar

        :param str inp: the input source
        :param str out: the out name in GRASS database
        :param str method: the method to be use during import
        :param str returnpulse: import points of selected return type,
                                acpted values are first, last, mid
        :param str resolution: the resolution for outpat map
        :param str percentile: value of percentile 1-100
        :param str trim: discard <trim> percent of the smallest and <trim>
                         percent of the largest observations 0-50
        :param bool commandOnly: non esegue i comandi, li costruisce e li restituisce
        """
        import grass.script.core as gcore
        
        cmd = ['r.in.lidar', '-go',
               'input={input}'.format(input=inp),
               'output={output}'.format(output=out)]
        libs_save_command(cmd, 'Primo comando di las_import')
        try:
            runcom = gcore.Popen(cmd,
                                 stdin=PIPE, stdout=PIPE, stderr=PIPE)
            outp, errp = runcom.communicate()
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo r.in.lidar {err}".format(err=errp))
        except:
            raise Exception("Probabilmente r.in.lidar non è presente nella"
                            "vostra versione di GRASS GIS")
        com = ['g.region']
        com.extend(outp.split())
        libs_save_command(com)
        self.run_grass([com])
        if resolution and region:
            com2 = ['g.region', 'o={va}'.format(va=self.rect_str[0]),
                    's={va}'.format(va=self.rect_str[1]),
                    'e={va}'.format(va=self.rect_str[2]),
                    'n={va}'.format(va=self.rect_str[3]),
                    'res={va}'.format(va=resolution), '-a']
        elif resolution and not region:
            com2 = ['g.region', 'res={r}'.format(r=str(resolution)), '-a']
        elif not resolution and region:
            actual_res = int(gcore.region()['nsres'])
            com2 = ['g.region', 'o={va}'.format(va=self.rect_str[0]),
                    's={va}'.format(va=self.rect_str[1]),
                    'e={va}'.format(va=self.rect_str[2]),
                    'n={va}'.format(va=self.rect_str[3]),
                    'res={va}'.format(va=actual_res), '-a']
        else:
            actual_res = int(gcore.region()['nsres'])
            com2 = ['g.region', 'res={r}'.format(r=str(actual_res)), '-a']
        libs_save_command(com2)
        self.run_grass([com2])
        try:
            if returnpulse and percentile:
                com3 = ['r.in.lidar', '-o',
                         'input={input}'.format(input=inp),
                         'output={output}'.format(output=out),
                         'method={met}'.format(met=method),
                         'return_filter={pul}'.format(pul=returnpulse),
                         'pth={perc}'.format(perc=percentile)]
            elif returnpulse and trim:
                com3 = ['r.in.lidar', '-o',
                         'input={input}'.format(input=inp),
                         'output={output}'.format(output=out),
                         'method={met}'.format(met=method),
                         'return_filter={pul}'.format(pul=returnpulse),
                         'trim={tri}'.format(tri=trim)]
            elif percentile and not returnpulse:
                com3 = ['r.in.lidar', '-o',
                         'input={input}'.format(input=inp),
                         'output={output}'.format(output=out),
                         'method={met}'.format(met=method),
                         'pth={perc}'.format(perc=percentile)]
            elif trim and not returnpulse:
                com3 = ['r.in.lidar', '-o',
                         'input={input}'.format(input=inp),
                         'output={output}'.format(output=out),
                         'method={met}'.format(met=method),
                         'trim={tri}'.format(tri=trim)]
            elif returnpulse and not (percentile or trim):
                com3 = ['r.in.lidar', '-o',
                         'input={input}'.format(input=inp),
                         'output={output}'.format(output=out),
                         'method={met}'.format(met=method),
                         'return_filter={pul}'.format(pul=returnpulse)
                         ]
            else:
                com3 = ['r.in.lidar', '-o',
                         'input={input}'.format(input=inp),
                         'output={output}'.format(output=out),
                         'method={met}'.format(met=method)]
            libs_save_command(com3)
            self.run_grass([com3])

        except:
            raise Exception("Errore eseguendo l'importazione del file LAS")

    def run_grass(self, comm):
        """Run a GRASS module

        :param list comm: a list with all the command to run
        """
        import grass.script.core as gcore
        for i in comm:
            runcom = gcore.Popen(i, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = runcom.communicate()
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo il comando {i} {err}".format(i=i, err=err))

    def rmarea(self, infile, outfile, thresh):
        # transform user input from hectares to map units (kept this for future)
        # thresh = thresh * 10000.0 / (float(coef)**2)
        # grass.debug("Threshold: %d, coeff linear: %s, coef squared: %d" % (thresh, coef, (float(coef)**2)), 0)

        # transform user input from hectares to meters because currently v.clean
        # rmarea accept only meters as threshold
        thresh = thresh * 10000.0
        vectfile = "%s_vect_%s" % (infile.split('@')[0], outfile)
        self.run_grass([['r.to.vect', 'input={inp}'.format(inp=infile),
                         'output={vect}'.format(vect=vectfile), 'type=area']])
        cleanfile = "%s_clean_%s" % (infile.split('@')[0], outfile)
        self.run_grass([['v.clean', 'input={vect}'.format(vect=vectfile),
                         'output={clea}'.format(clea=cleanfile), 'tool=rmarea',
                         'threshold={thre}'.format(thre=thresh)]])

        self.run_grass([['v.to.rast', 'input={clea}'.format(clea=cleanfile),
                         'output={out}'.format(out=outfile),
                         'use=attr', 'attrcolumn=value']])
        self.removeMaps(names=[vectfile, cleanfile])

    def print_grass(self, comm):
        """Print a GRASS module"""
        import grass.script.core as gcore

        for i in comm:
            runcom = gcore.Popen(i, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = runcom.communicate()
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo il comando {err}".format(err=err))
            else:
                return out

    def removeMaps(self, names=None, pattern=None, typ='raster'):
        """Remove maps from mapset
        :param list names: names of maps to remove
        :param str pattern: a string containing the pattern of maps to remove
        :param str typ: type of data: raster or vector to remove
        """
        com = ['g.remove', 'type={name}'.format(name=typ)]
        if not names and not pattern:
            raise Exception("Errore eseguendo GRASS: Impostare almeno "
                            "una tra le variabili names o pattern")
        elif names and pattern:
            raise Exception("Errore eseguendo GRASS: Impostare almeno "
                            "una tra le variabili names o pattern")
        elif names:
            com.append('name={inps}'.format(inps=','.join(names)))

        elif pattern:
            com.append('pattern={inp}'.format(inp=pattern))
        self.run_grass([com])

    def removeMapset(self):
        """Remove mapset with all the contained data"""
        import shutil
        shutil.rmtree(self.mapsetpath)

    def find_program(self, command, param):
        """Return if a command exist or not"""
        import grass.script.core as gcore
        check = gcore.find_program(command, param)
        if check:
            return True
        else:
            err = "Errore eseguendo GRASS: il comdando {co} non sembra " \
                  "essere presente, si prega di installarlo".format(co=command)
            raise Exception(err)


def get_parser():
    """Create the parser for running as script"""
    import argparse
    parser = argparse.ArgumentParser(description='Script for GRASS operations'
                                                 'on the server')
    parser.add_argument('-s', '--server', action='store_true',
                        dest='server', default=False,
                        help="launch server application")
    return parser


def main():
    """This function is used in the server to activate a Pyro4 server.
       It initialize the stemGRASS objects and it is used by Pyro4
    """
    parser = get_parser()
    args = parser.parse_args()
    if args.server:
        # decomment this two lines if you want activate the logging
        #os.environ["PYRO_LOGFILE"] = "pyrograss.log"
        #os.environ["PYRO_LOGLEVEL"] = "DEBUG"
        import Pyro4
        grass_stem = stemGRASS()
        daemon = Pyro4.Daemon(host=PYROSERVER, port=GRASS_PORT)
        uri = daemon.register(grass_stem,objectId=GRASSPYROOBJNAME,force=True)
        ns = Pyro4.locateNS()
        ns.register("PyroGrassStem",uri)
        daemon.requestLoop()
    else:
        parser.error("--server option is required")

if __name__ == "__main__":
    main()
