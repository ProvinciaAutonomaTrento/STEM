# -*- coding: utf-8 -*-

"""
Library to work with GDAL/OGR inside the STEM project

Date: August 2014

Authors: Luca Delucchi

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

try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'

try:
    import osgeo.ogr as ogr
except ImportError:
    try:
        import ogr
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'
try:
    import osgeo.osr as osr
except ImportError:
    try:
        import osr
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'
import os
import sys
import numpy
from types import StringType, ListType
from pyro_stem import PYROSERVER, GDAL_PORT

NP2GDAL_CONVERSION = {
  "int8": 1,
  "uint16": 2,
  "int16": 3,
  "uint32": 4,
  "int32": 5,
  "float32": 6,
  "float64": 7,
  "complex64": 10,
  "complex128": 11,
}

GDAL2NP_CONVERSION = {
  1: "int8",
  2: "uint16",
  3: "int16",
  4: "uint32",
  5: "int32",
  6: "float32",
  7: "float64",
  10: "complex64",
  11: "complex128",
}

CODES = {'ab': {'a': 1.62898357199892E-04, 'b': 1.70656012564636,
                'c': 0.94190457472194, 'd0': 3.69465, 'mh': 38.2},
         'ar': {'a': 1.77367991170896E-04	, 'b': 1.56425370572013,
                'c': 1.05156473615877, 'd0': 3.69465, 'mh': 42.3},
         'al': {'a': 5.52712344957134E-05, 'b': 1.94208862027426,
                'c': 1.00642023166998, 'd0': 4.0091, 'mh': 31.4},
         'fa': {'a': 5.52712344957134E-05, 'b': 1.94208862027426,
                'c': 1.00642023166998, 'd0': 4.0091, 'mh': 31.4},
         'la': {'a': 1.07820129127088E-04, 'b': 1.40775581651764,
                'c': 1.34137722851875, 'd0': 3.69465, 'mh': 37.2},
         'pc': {'a': 1.88167619876239E-04	, 'b': 1.61371288034635,
                'c': 0.985265642143746, 'd0': 3.69465, 'mh': 27.0},
         'pn': {'a': 1.28924310780902E-04, 'b': 1.76308589457555,
                'c': 0.938444909041497, 'd0': 3.69465, 'mh': 34.1},
         'ps': {'a': 1.01825735269425E-04, 'd': 1.91818421016015,
                'c': 0.830164143958094, 'd0': 3.69465, 'mh': 34.1}}


def formula_vol(a, b, c, d0, d, h):
    """"""
    power1 = numpy.power(d - d0, b)
    power2 = numpy.power(h, c)
    return a * power1 * power2


def createMaskFromBbox(coord):
    """Function to create an OGR polygon geometry

    :param coord: a list or a string (space separator) with for values
                  xmin ymin xmax ymax
    """
    if type(coord) == StringType:
        coord = coord.split()
    elif type(coord) != ListType:
        raise IOError('coord parameter must be a string or a list')
    if len(coord) != 4:
        raise IOError('coord parameter must contain 4 values: xmin ymin xmax ymax')
    poly = ogr.Geometry(ogr.wkbPolygon)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    coords = []
    for c in coord:
        coords.append(float(c))
    ring.AddPoint(coords[0], coords[1])
    ring.AddPoint(coords[0], coords[3])
    ring.AddPoint(coords[2], coords[3])
    ring.AddPoint(coords[2], coords[1])
    poly.AddGeometry(ring)
    return poly


class infoOGR:
    """A class to work with vector data"""
    def initialize(self, iname, update=0):
        self.inp = ogr.Open(iname, update)
        if self.inp is None:
            raise IOError('Could not open vector data: {n}'.format(n=iname))
        self.lay0 = self.inp.GetLayer(0)

    def getType(self):
        """Return the type of vector geometry"""
        return self.lay0.GetGeomType()

    def getWkt(self):
        """Return a WKT string of features"""
        if self.getType() not in [3, 6, -2147483645, -2147483642]:
            raise Exception("Geometry type is not supported, please use a "
                            "polygon vector file")
        if self.lay0.GetFeatureCount() > 1:
            wkt = "MULTIPOLYGON (("
        else:
            wkt = "POLYGON ("
        for feature in self.lay0:
            geom = feature.GetGeometryRef()
            featwkt = geom.ExportToWkt()
            if 'MULTIPOLYGON' in featwkt:
                featwkt = featwkt.replace("MULTIPOLYGON ((", "")[:-2]
            elif 'POLYGON' in featwkt:
                featwkt = featwkt.replace("POLYGON (", "")[:-1]
            wkt += "{po},".format(po=featwkt)
        wkt = wkt.rstrip(',')
        if self.lay0.GetFeatureCount() > 1:
            wkt += '))'
        else:
            wkt += ')'
        return wkt

    def cutInputInverse(self, output, erase=None, bbox=None):
        """Create an inverse mask and remove/cut the elements inside erase
        polygon

        :param str output: path for the output file
        :param str erase: the path to vector file containing one polygon
        :param str bbox: a string containin a bounding box with the four values
                         xmin ymin xmax ymax
        """
        if erase:
            mask = ogr.Open(erase, 0)
            if mask is None:
                raise IOError('Could not open vector data: {n}'.format(n=erase))

            laymask = mask.GetLayer()
            featmask = laymask.GetFeature(0)
            geomfeat2 = featmask.GetGeometryRef()
        elif bbox:
            geomfeat2 = createMaskFromBbox(bbox)
        else:
            raise IOError('erase or bbox paramater must be set')

        self.lay0.ResetReading()

        driver = ogr.GetDriverByName("ESRI Shapefile")
        # create a new data source and layer
        if os.path.exists(output):
            driver.DeleteDataSource(output)
        outDS = driver.CreateDataSource(output)
        if outDS is None:
            raise IOError('Could not create file for inverse mask')
        outLayer = outDS.CreateLayer('inverse_mask', geom_type=self.getType(),
                                     srs=self.lay0.GetSpatialRef())
        # get the FeatureDefn for the output shapefile
        featureDefn = self.lay0.GetLayerDefn()

        # loop through input layer
        for inFeature in self.lay0:
            # create a new feature
            outFeature = ogr.Feature(featureDefn)

            # copy the attributes and set geometry
            outFeature.SetFrom(inFeature)

            # get Geometry of feature and apply the difference method
            inGeom = inFeature.GetGeometryRef()
            GeomDiff = inGeom.Difference(geomfeat2)
            if GeomDiff:
                # Set geometry of the outfeature
                outFeature.SetGeometry(GeomDiff)

                # add the feature to the output layer
                outLayer.CreateFeature(outFeature)
        outLayer = None
        outDS = None

    def calc_vol(self, out_col, height, diam, specie):
        self.lay0.ResetReading()

        field = ogr.FieldDefn(out_col, ogr.OFTReal)
        self.lay0.CreateField(field)
        # loop through input layer
        for inFeature in self.lay0:
            volu = None

            spec = inFeature.GetField(str(specie))
            diameter = inFeature.GetField(str(diam))
            heig = inFeature.GetField(str(height))
            values = CODES[spec]
            # TODO check with province
            #if diameter > 85:
            #    diameter = 85
            if heig > values['mh']:
                heig = values['mh']
            if spec in ['ab', 'ar', 'la', 'pc', 'pn', 'ps']:
                if diameter > 3.69465:
                    volu = formula_vol(values['a'], values['b'], values['c'],
                                       values['d0'], diameter, heig)
            elif spec in ['fa', 'al']:
                if diameter > 4.0091:
                    volu = formula_vol(values['a'], values['b'], values['c'],
                                       values['d0'], diameter, heig)
            inFeature.SetField(out_col, volu)

            self.lay0.SetFeature(inFeature)
        self.lay0 = None
        self.inp = None
        return 0


class convertGDAL:
    """A class to run operation on raster data from using GDAL in STEM tools"""
    def __init__(self):
        self.file_infos = []

    def initialize(self, innames, output=None, outformat='GTIFF'):
        """Function for the initialize the object

       :param str inname: name of input data
       :param str output: prefix for output data
       :param str outformat: the name of output format according with gdal
                             format names
        """
        # Open source dataset
        self.in_names = innames
        self.driver = gdal.GetDriverByName(str(outformat))
        if self.driver is None:
            raise IOError('Format driver %s not found, pick a supported '
                          'driver.' % outformat)
        self._checkPara()
        outbands = self._checkOutputBands()
        self.output = self.driver.Create(output, self.xsize, self.ysize,
                                         outbands, self.bandtype)
        self.output.SetProjection(self.proj)
        self.output.SetGeoTransform(self.geotrasf)

    def _names_to_fileinfos(self):
        """Translate a list of GDAL filenames, into file_info objects.
        Returns a list of file_info objects. There may be less file_info
        objects than names if some of the names could not be opened as GDAL
        files.
        """
        for n in range(len(self.in_names)):
            fi = file_info()
            if fi.init_from_name(self.in_names[n]) == 1:
                self.file_infos.append(fi)
                # TODO check if the files have same information like
                # projections, size etc
            #else:
                # return error

    def _checkPara(self):
        """Set information from the first raster"""
        self._names_to_fileinfos()
        self.xsize = self.file_infos[0].xsize
        self.ysize = self.file_infos[0].ysize
        self.proj = self.file_infos[0].projection
        self.geotrasf = self.file_infos[0].geotransform
        self.bandtype = self.file_infos[0].band_type

    def _checkOutputBands(self):
        """Set the number of bands for the output file"""
        output = 0
        for fi in self.file_infos:
            output += fi.bands
        return output

    def write(self):
        """Write the output file"""
        targetband = 0
        for f in range(len(self.file_infos)):
            fi = self.file_infos[f]
            if fi.bands > 1:
                for b in range(fi.bands):
                    targetband += 1
                    fi.copy_into(self.output, targetband, b + 1)
            else:
                targetband += 1
                fi.copy_into(self.output, targetband)
        self.output = None

    def cutInputInverse(self, erase=None, bbox=None):
        """Create an inverted mask, returning a raster containing only data
        external to the given polygon

        :param str erase: the path to vector file containing one polygon
        :param str bbox: a string containin a bounding box with the four values
                         xmin ymin xmax ymax
        """
        numpycode = GDAL2NP_CONVERSION[self.bandtype]
        numpytype = numpy.dtype(numpycode)
        if erase:
            mask = ogr.Open(erase, 0)
            if mask is None:
                raise IOError('Could not open vector data: {n}'.format(n=erase))

            laymask = mask.GetLayer()
            featmask = laymask.GetFeature(0)
            geom = featmask.GetGeometryRef()
        elif bbox:
            geom = createMaskFromBbox(bbox)
        for f in range(len(self.file_infos)):
            fi = self.file_infos[f]
            fi.cutInputInverse(geom, self.output, numpytype)
        self.output = None


# =============================================================================
def raster_copy(s_fh, s_xoff, s_yoff, s_xsize, s_ysize, s_band_n,
                t_fh, t_xoff, t_yoff, t_xsize, t_ysize, t_band_n,
                nodata=None):
    """Copy a band of raster into the output file.

       Function copied from gdal_merge.py
    """
    if nodata is not None:
        return raster_copy_with_nodata(s_fh, s_xoff, s_yoff, s_xsize, s_ysize,
                                       s_band_n, t_fh, t_xoff, t_yoff, t_xsize,
                                       t_ysize, t_band_n, nodata)

    s_band = s_fh.GetRasterBand(s_band_n)
    t_band = t_fh.GetRasterBand(t_band_n)

#    data = s_band.ReadRaster(s_xoff, s_yoff, s_xsize, s_ysize,
#                             t_xsize, t_ysize, t_band.DataType)
#
#    t_band.WriteRaster(t_xoff, t_yoff, t_xsize, t_ysize, data, t_xsize,
#                       t_ysize, t_band.DataType)

    data_src = s_band.ReadAsArray(s_xoff, s_yoff, s_xsize, s_ysize,
                                  t_xsize, t_ysize)
    t_band.WriteArray(data_src, t_xoff, t_yoff)

    return 0


def raster_copy_with_nodata(s_fh, s_xoff, s_yoff, s_xsize, s_ysize, s_band_n,
                            t_fh, t_xoff, t_yoff, t_xsize, t_ysize, t_band_n,
                            nodata):
    """Copy a band of raster into the output file with nodata values.

       Function copied from gdal_merge.py
    """
    try:
        import numpy as Numeric
    except ImportError:
        import Numeric

    s_band = s_fh.GetRasterBand(s_band_n)
    t_band = t_fh.GetRasterBand(t_band_n)

    data_src = s_band.ReadAsArray(s_xoff, s_yoff, s_xsize, s_ysize,
                                  t_xsize, t_ysize)
    data_dst = t_band.ReadAsArray(t_xoff, t_yoff, t_xsize, t_ysize)

    nodata_test = Numeric.equal(data_src, nodata)
    to_write = Numeric.choose(nodata_test, (data_src, data_dst))

    t_band.WriteArray(to_write, t_xoff, t_yoff)

    return 0


class file_info:
    """A class holding information about a GDAL file.

       Class copied from gdal_merge.py, extended by Luca Delucchi

       :param str filename: Name of file to read.

       :return: 1 on success or 0 if the file can't be opened.
    """

    def init_from_name(self, filename):
        """Initialize file_info from filename"""
        self.s_fh = gdal.Open(filename)
        if self.s_fh is None:
            return 0

        self.bands = self.s_fh.RasterCount
        self.xsize = self.s_fh.RasterXSize
        self.ysize = self.s_fh.RasterYSize
        self.band = self.s_fh.GetRasterBand(1)
        self.band_type = self.band.DataType
        self.block_size = self.band.GetBlockSize()
        self.projection = self.s_fh.GetProjection()
        self.geotransform = self.s_fh.GetGeoTransform()
        self.ulx = self.geotransform[0]
        self.uly = self.geotransform[3]
        self.lrx = self.ulx + self.geotransform[1] * self.xsize
        self.lry = self.uly + self.geotransform[5] * self.ysize

        self.meta = self.s_fh.GetMetadata()
        if '_FillValue' in self.meta.keys():
            self.fill_value = self.meta['_FillValue']
        else:
            self.fill_value = None

        ct = self.band.GetRasterColorTable()
        if ct is not None:
            self.ct = ct.Clone()
        else:
            self.ct = None

        return 1

    def getColorInterpretation(self, n):
        band = self.s_fh.GetRasterBand(int(n))
        name = gdal.GetColorInterpretationName(band.GetColorInterpretation())
        if name in ['Undefined', 'Gray']:
            return str(n)
        else:
            return name.lower()

    def get_pixel_value(self, x, y):
        """Return a value for a coordinate

        :param numeric x: longitude of coordinate
        :param numeric y: latitude of coordinate
        """
        import struct
        px = int((x - self.geotransform[0]) / self.geotransform[1])  # x pixel
        py = int((y - self.geotransform[3]) / self.geotransform[5])  # y pixel
        structval = self.band.ReadRaster(px, py, 1, 1, buf_type=self.band_type)
        if self.band_type in [1, 3, 5, 8, 9]:
            intval = struct.unpack('i', structval)
        elif self.band_type in [2, 4]:
            intval = struct.unpack('I', structval)
        elif self.band_type in [6, 7]:
            intval = struct.unpack('f', structval)
        print intval[0]

    def getBBoxWkt(self, buff=0):
        """Return the bounding box in wkt format

        :param numeric buff: the internal buffer to apply at the bounding box
        """
        mix = self.ulx + buff
        miy = self.lry + buff
        mx = self.lrx - buff
        may = self.uly - buff
        wkt = "POLYGON (({minx} {miny},{minx} {maxy},{maxx} {maxy},{maxx} " \
              "{miny},{minx} {miny}))".format(minx=mix, miny=miy, maxx=mx,
                                              maxy=may)
        return wkt

    def cutInputInverse(self, geom, output, datatype):
        """Create an inverted mask, returning a raster containing only data
        external to the given polygon

        :param obj geom: an OGR geometry object
        :param obj output: a GDAL object containing the output raster
        :param obj datatype: Numpy dtype object
        """
        import json
        geomjs = json.loads(geom.ExportToJson())
        coors = geomjs['coordinates'][0]
        pointsX = []
        pointsY = []
        for c in coors:
            pointsX.append(c[0])
            pointsY.append(c[1])
        xmin = min(pointsX)
        xmax = max(pointsX)
        ymin = min(pointsY)
        ymax = max(pointsY)
        xoff = int((xmin - self.geotransform[0]) / self.geotransform[1])
        yoff = int((self.geotransform[3] - ymax) / self.geotransform[1])
        xcount = int((xmax - xmin) / self.geotransform[1]) + 1
        ycount = int((ymax - ymin) / self.geotransform[1]) + 1
        target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount,
                                                       gdal.GDT_Byte)
        target_ds.SetGeoTransform((xmin, self.geotransform[1], 0, ymax, 0,
                                   self.geotransform[5]))

        # create for target raster the same projection as for the value raster
        raster_srs = osr.SpatialReference()
        raster_srs.ImportFromWkt(self.s_fh.GetProjectionRef())
        target_ds.SetProjection(raster_srs.ExportToWkt())
        # rasterize zone polygon to raster
        gdal.RasterizeLayer(target_ds, [1], laymask, burn_values=[1])
        import pdb; pdb.set_trace()
        bandmask = target_ds.GetRasterBand(1)
        datamask = bandmask.ReadAsArray(0, 0, xcount, ycount)

        # read raster as arrays
        for b in range(1, self.bands + 1):
            banddataraster = self.s_fh.GetRasterBand(b)
            dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount)

            outband = numpy.ma.masked_array(dataraster, datamask)
            outband_null = numpy.ma.filled(outband.astype(float), numpy.nan)
            outband_null = outband_null.astype(datatype, copy=False)
            pdb.set_trace()
            t_band = output.GetRasterBand(b)

            t_band.WriteArray(outband_null)

    def copy_into(self, t_fh, t_band=1, s_band=1, nodata_arg=None):
        """Copy this files image into target file.

        This method will compute the overlap area of the file_info objects
        file, and the target gdal.Dataset object, and copy the image data
        for the common window area.  It is assumed that the files are in
        a compatible projection. no checking or warping is done.  However,
        if the destination file is a different resolution, or different
        image pixel type, the appropriate resampling and conversions will
        be done (using normal GDAL promotion/demotion rules).

        :param t_fh: gdal.Dataset object for the file into which some or all
                     of this file may be copied.
        :param s_band: source band
        :param t_band: target band
        :param nodata_arg:

        :return: 1 on success (or if nothing needs to be copied), and zero one
                 failure.

        """
        t_geotransform = t_fh.GetGeoTransform()
        t_ulx = t_geotransform[0]
        t_uly = t_geotransform[3]
        t_lrx = t_geotransform[0] + t_fh.RasterXSize * t_geotransform[1]
        t_lry = t_geotransform[3] + t_fh.RasterYSize * t_geotransform[5]

        # figure out intersection region
        tgw_ulx = max(t_ulx, self.ulx)
        tgw_lrx = min(t_lrx, self.lrx)
        if t_geotransform[5] < 0:
            tgw_uly = min(t_uly, self.uly)
            tgw_lry = max(t_lry, self.lry)
        else:
            tgw_uly = max(t_uly, self.uly)
            tgw_lry = min(t_lry, self.lry)

        # do they even intersect?
        if tgw_ulx >= tgw_lrx:
            return 1
        if t_geotransform[5] < 0 and tgw_uly <= tgw_lry:
            return 1
        if t_geotransform[5] > 0 and tgw_uly >= tgw_lry:
            return 1

        # compute target window in pixel coordinates.
        tw_xoff = int((tgw_ulx - t_geotransform[0]) / t_geotransform[1] + 0.1)
        tw_yoff = int((tgw_uly - t_geotransform[3]) / t_geotransform[5] + 0.1)
        tw_xsize = int((tgw_lrx - t_geotransform[0]) / t_geotransform[1] + 0.5) - tw_xoff
        tw_ysize = int((tgw_lry - t_geotransform[3]) / t_geotransform[5] + 0.5) - tw_yoff

        if tw_xsize < 1 or tw_ysize < 1:
            return 1

        # Compute source window in pixel coordinates.
        sw_xoff = int((tgw_ulx - self.geotransform[0]) / self.geotransform[1])
        sw_yoff = int((tgw_uly - self.geotransform[3]) / self.geotransform[5])
        sw_xsize = int((tgw_lrx - self.geotransform[0])
                       / self.geotransform[1] + 0.5) - sw_xoff
        sw_ysize = int((tgw_lry - self.geotransform[3])
                       / self.geotransform[5] + 0.5) - sw_yoff

        if sw_xsize < 1 or sw_ysize < 1:
            return 1

        return \
            raster_copy(self.s_fh, sw_xoff, sw_yoff, sw_xsize, sw_ysize,
                        s_band, t_fh, tw_xoff, tw_yoff, tw_xsize, tw_ysize,
                        t_band, nodata_arg)
        self.s_fh = None


def get_parser():
    """Create the parser for running as script"""
    import argparse
    parser = argparse.ArgumentParser(description='Script for GDAL/OGR operations')
    parser.add_argument('inputs', metavar='input', type=str, nargs='+',
                        help='the path to the inputs GDAL files')
    parser.add_argument('output', metavar='output', type=str,
                        help='the path to the output GDAL file')
    parser.add_argument('-f', '--format', type=str,
                        help='the format to use in the output file, check'
                        ' the supported formats with `python {pr} '
                        '--formats`'.format(pr=parser.prog))
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
        gdalinfo_stem = file_info()
        gdalconvert_stem = convertGDAL()
        ogrinfo_stem = infoOGR()
        Pyro4.Daemon.serveSimple({gdalinfo_stem: "stem.gdalinfo",
                                  gdalconvert_stem: "stem.gdalconvert",
                                  ogrinfo_stem: "stem.ogrinfo"},
                                 host=PYROSERVER, port=GDAL_PORT, ns=True)
    else:
        cgdal = convertGDAL()
        cgdal.initialize(args.inputs, args.output, args.format)
        cgdal.write()

if __name__ == "__main__":
    gdal.AllRegister()
    argv = gdal.GeneralCmdLineProcessor(sys.argv)
    if argv is not None:
        main()
