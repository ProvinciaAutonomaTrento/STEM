# -*- coding: utf-8 -*-

"""
***************************************************************************
    grass_stem.py
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

import os
import sys
import subprocess
import itertools

stats = ['mean', 'n', 'min', 'max', 'range', 'sum', 'stddev', 'variance',
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

PIPE = subprocess.PIPE


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
        startcmd = [grassbin, '--config', 'path']
        #p = subprocess.Popen(startcmd, shell=True, stdin=subprocess.PIPE,
        #                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = subprocess.Popen(startcmd, shell=False, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            raise Exception("Errore eseguendo GRASS: Vanno settate tutte le "
                            "variabili necessarie: GRASSDATA, LOCATION ed "
                            "eseguibile")
        gisbase = out.strip()
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
        import grass.script.setup as gsetup
        locexist = os.path.join(grassdatabase, location)
        if not os.path.exists(locexist):
            if not epsg:
                raise Exception("Errore eseguendo GRASS: ",
                                "Manca il codice EPSG nelle impostazioni")
            import grass.script.core as gcore
            gcore.create_location(grassdatabase, location, epsg=epsg)

        self.mapsetpath = os.path.join(grassdatabase, location, self.mapset)
        if not os.path.exists(self.mapsetpath):
            os.mkdir(self.mapsetpath)
        wind = readfile(os.path.join(grassdatabase, location, "PERMANENT",
                                     "DEFAULT_WIND"))
        writefile(os.path.join(self.mapsetpath, "WIND"), wind)
        ###########
        # launch session
        gsetup.init(gisbase, grassdatabase, location, self.mapset)
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

        if typ == 'raster' or typ == 'image':
            if len(nl) > 1:
                runcom = gcore.Popen(['r.in.gdal', 'input={inp}'.format(inp=inp),
                                      'output={intemp}'.format(intemp=intemp),
                                      'band={bs}'.format(bs=','.join(nl))],
                                     stdin=PIPE, stdout=PIPE,
                                     stderr=PIPE)
            elif len(nl) == 1 and str(nl[0]) == '1':
                runcom = gcore.Popen(['r.in.gdal', 'input={inp}'.format(inp=inp),
                                      'output={intemp}'.format(intemp=intemp)],
                                     stdin=PIPE, stdout=PIPE,
                                     stderr=PIPE)
            elif len(nl) == 1 and str(nl[0]) != '1':
                runcom = gcore.Popen(['r.in.gdal', 'input={inp}'.format(inp=inp),
                                      'output={intemp}'.format(intemp=intemp),
                                      'band={bs}'.format(bs=','.join(nl))],
                                     stdin=PIPE, stdout=PIPE,
                                     stderr=PIPE)
            out, err = runcom.communicate()
            #  print out, err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: ",
                                "Errore eseguendo r.in.gdal {err}".format(err=err))
            if len(nl) > 1:
                runcom = gcore.Popen(['g.region', 'rast={intemp}.{n}'.format(intemp=intemp,
                                                                             n=max(nl))],
                                     stdin=PIPE, stdout=PIPE,
                                     stderr=PIPE)
            else:
                runcom = gcore.Popen(['g.region', 'rast={intemp}'.format(intemp=intemp)],
                                     stdin=PIPE, stdout=PIPE,
                                     stderr=PIPE)
            out, err = runcom.communicate()
            #  print out,err
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo g.region {err}".format(err=err))

        elif typ == 'vector':
            gcore.run_command('v.in.ogr', input=inp, output=intemp)
            gcore.run_command('g.region', vect=intemp)

    def vtorast(self, inp, column=None):
        import grass.script.core as gcore
        command = ['v.to.rast', 'input={name}'.format(name=inp),
                   'output={name}'.format(name=inp)]
        if column:
            command.extend(['use=attr', 'attribute_column={col}'.format(col=column)])
        else:
            command.append('use=val')
        runcom = gcore.Popen(command)
        out, err = runcom.communicate()
        #  print out,err
        if runcom.returncode != 0:
            raise Exception("Errore eseguendo GRASS: "
                            "Errore eseguendo v.to.rast {err}".format(err=err))

    def create_group(self, maps, gname, base=False):
        import grass.script.core as gcore
        if base:
            maps = gcore.list_grouped('rast', pattern='{base}*'.format(base=maps))[self.mapset]
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
        import grass.script.core as gcore

        if typ == 'raster' or typ == 'image':
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
        if remove:
            self.removeMapset()

    def las_import(self, inp, out, method, returnpulse=None, resolution=None,
                   percentile=None, trim=None):
        """Import LAS file trhough r.in.lidar"""
        import grass.script.core as gcore

        outp = gcore.read_command('r.in.lidar', flags='go', input=inp,
                                  output=out)
        com = ['g.region']
        com.extend(outp.split())
        self.run_grass([com])
        if resolution:
            com2 = ['g.region', 'res={r}'.format(r=str(resolution)), '-a']
        else:
            actual_res = int(gcore.region()['nsres'])
            com2 = ['g.region', 'res={r}'.format(r=str(actual_res)), '-a']
        self.run_grass([com2])
        try:
            if returnpulse and percentile:
                gcore.run_command('r.in.lidar', flags='o', input=inp, output=out,
                                  method=method, return_filter=returnpulse,
                                  percent=percentile)
            elif returnpulse and trim:
                gcore.run_command('r.in.lidar', flags='o', input=inp, output=out,
                                  method=method, return_filter=returnpulse,
                                  trim=trim)
            elif percentile and not returnpulse:
                gcore.run_command('r.in.lidar', flags='o', input=inp, output=out,
                                  method=method, percent=percentile)
            elif trim and not returnpulse:
                gcore.run_command('r.in.lidar', flags='o', input=inp, output=out,
                                  method=method, trim=trim)
            elif returnpulse and not (percentile or trim):
                gcore.run_command('r.in.lidar', flags='o', input=inp, output=out,
                                  method=method, return_filter=returnpulse)
            else:
                gcore.run_command('r.in.lidar', flags='o', input=inp,
                                  output=out, method=method)
        except:
            raise Exception("Errore eseguendo l'importazione del file LAS")

    def run_grass(self, comm):
        """Run a GRASS module"""
        import grass.script.core as gcore

        for i in comm:
            runcom = gcore.Popen(i, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = runcom.communicate()
            if runcom.returncode != 0:
                raise Exception("Errore eseguendo GRASS: "
                                "Errore eseguendo il comando {err}".format(err=err))

    def removeMapset(self):
        """Remove mapset with all the contained data"""
        from grass.script import try_rmdir
        try_rmdir(self.mapsetpath)