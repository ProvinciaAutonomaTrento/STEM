# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 11:50:27 2014

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

import os
import sys
import subprocess
import itertools
from PyQt4.QtCore import pyqtRemoveInputHook

stats = ['n', 'min', 'max', 'range', 'sum', 'mean', 'stddev', 'variance',
         'coeff_var', 'median', 'percentile', 'skewness', 'trimmean']


def helpUrl(name):
    """Create the url for GRASS manuals page"""
    return "http://grass.osgeo.org/grass70/manuals/{name}.html".format(name=name)


def readfile(path):
    """Read the file and return a string"""
    f = open(path, 'r')
    s = f.read()
    f.close()
    return s


def writefile(path, s):
    """Write the file from a string, new line should be added in the string"""
    f = open(path, 'w')
    f.write(s)
    f.close()


class stemGRASS():

    def __init__(self, pid, grassdatabase, location, grassbin, epsg):
#        s = QSettings()
#        # query GRASS 7 itself for its GISBASE
#        # we assume that GRASS GIS' start script is available and in the PATH
#        if not grassbin:
#            grassbin = str(s.value("stem/grasspath", ""))
#        if not grassdatabase:
#            grassdatabase = str(s.value("stem/grassdata", ""))
#        if not location:
#            location = str(s.value("stem/grasslocation", ""))
        startcmd = [grassbin, '--config path']
        #p = subprocess.Popen(startcmd, shell=True, stdin=subprocess.PIPE,
        #                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = subprocess.Popen(startcmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            raise Exception("Errore eseguendo GRASS: Vanno settate tutte le "
                            "variabili necessarie: GRASSDATA, LOCATION ed "
                            "eseguibile")
        gisbase = out.strip()
        print gisbase
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

        mapset = 'stem_{pid}'.format(pid=pid)
        print "prima di import"
        import grass.script.setup as gsetup
        locexist = os.path.join(grassdatabase, location)
        if not os.path.exists(locexist):
            if not epsg:
                raise Exception("Errore eseguendo GRASS: ",
                                "Manca il codice EPSG nelle impostazioni")
            import grass.script.core as gcore
            gcore.create_location(grassdatabase, location, epsg=epsg)

        self.newmapset = os.path.join(grassdatabase, location, mapset)
        if not os.path.exists(self.newmapset):
            os.mkdir(self.newmapset)
        wind = readfile(os.path.join(grassdatabase, location, "PERMANENT",
                                     "DEFAULT_WIND"))
        writefile(os.path.join(self.newmapset, "WIND"), wind)
        ###########
        # launch session
        gsetup.init(gisbase, grassdatabase, location, mapset)
        if 'GRASS_PROJSHARE' not in os.environ.keys():
            os.environ['GRASS_PROJSHARE'] = 'C:\OSGeo4W\share\proj'

        if 'GRASS_PYTHON' not in os.environ.keys():
            os.environ['GRASS_PYTHON'] = 'C:\OSGeo4W\bin\python.exe'

        if 'SHELL' not in os.environ.keys():
            os.environ['SHELL'] = 'C:\Windows\system32\cmd.exe'

    def check_mask(self, mask):
        import grass.script.core as gcore
        if mask == '':
            runcom = gcore.Popen(['r.mask', '-r'])
            out, err = runcom.communicate()
            #  print out, err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: ",
                                "Errore eseguendo r.mask {err}".format(err=err))
        else:
            name = '_'.join(os.path.split(mask)[-1].split('.')[:-1])
            vecs = list(itertools.chain(*gcore.list_grouped('vect').values()))
            if name not in vecs:
                gcore.run_command('v.in.ogr', dsn=mask, output=name)
                gcore.run_command('r.mask', vector=name)
            else:
                rasts = list(itertools.chain(*gcore.list_grouped('rast').values()))
                if 'MASK' not in rasts:
                    gcore.run_command('r.mask', vector=name)

    def import_grass(self, inp, intemp, typ, nl=None):
        import grass.script.core as gcore
        PIPE = subprocess.PIPE
        if typ == 'raster' or typ == 'image':
            if nl:
                for n in nl:
                    runcom = gcore.Popen(['r.in.gdal', 'input={inp}'.format(inp=inp),
                                          'output={intemp}_{n}'.format(intemp=intemp, n=n)],
                                          stdin=PIPE, stdout=PIPE,
                                          stderr=PIPE)
                    out, err = runcom.communicate()
                    #  print out, err
                    if runcom.returncode != 0:
                        raise Exception("Errore eseguendo GRASS: ",
                                        "Errore eseguendo r.in.gdal {err}".format(err=err))
            runcom = gcore.Popen(['g.region', 'rast={intemp}_{n}'.format(intemp=intemp, n=n)],
                                 stdin=PIPE, stdout=PIPE,
                                 stderr=PIPE)
            out, err = runcom.communicate()
            #  print out,err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo g.region {err}".format(err=err))
            if typ == 'image':
                runcom = gcore.Popen(['i.group', 'group={name}'.format(name=intemp),
                                      'subgroup={name}'.format(name=intemp),
                                      'input={maps}'.format(maps=','.join(self.layer_list))],
                                     stdin=PIPE, stdout=PIPE, stderr=PIPE)
                out, err = runcom.communicate()
                #  print out,err
                if runcom.returncode != 0:
                    raise Exception("Errore eseguendo GRASS: "
                                    "Errore eseguendo i.group {err}".format(err=err))
        elif typ == 'vector':
            gcore.run_command('v.in.ogr', input=inp, output=intemp)
            gcore.run_command('g.region', rast=intemp)

    def export_grass(self, outemp, finalout, typ):
        import grass.script.core as gcore

        PIPE = subprocess.PIPE
        if typ == 'raster':
            runcom = gcore.Popen(['r.out.gdal', 'input={outemp}'.format(outemp=outemp),
                                  'output={finalout}'.format(finalout=finalout)],
                                 stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = runcom.communicate()
            # print out,err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo r.out.gdal {err}".format(err=err))
            # gcore.run_command('r.out.gdal', input=outemp, output=finalout)
        elif typ == 'vector':
            gcore.run_command('v.out.ogr', input=outemp, output=finalout)

    def run_grass(self, comm):
        """Run a GRASS module"""
        import grass.script.core as gcore
        PIPE = subprocess.PIPE

        runcom = gcore.Popen(comm, stdin=PIPE,
                             stdout=PIPE, stderr=PIPE)
        out, err = runcom.communicate()
        #  print out, err
        pyqtRemoveInputHook()
        if runcom.returncode != 0:
            raise Exception("Errore eseguendo GRASS: "
                            "Errore eseguendo il comando {err}".format(err=err))

    def removeMaps(self):
        """Remove mapset with all the contained data"""
        from grass.script import try_rmdir
        try_rmdir(self.newmapset)
