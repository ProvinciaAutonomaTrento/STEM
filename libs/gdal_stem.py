# -*- coding: utf-8 -*-

"""
***************************************************************************
    gdal_stem.py
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


class infoOGR:
    """A class to work with vector data"""
    def __init__(self, iname):
        self.inp = ogr.Open(iname)
        self.lay0 = self.inp.GetLayer(0)

    def getType(self):
        return self.lay0.GetGeomType()


class convertGDAL:
    """A class to convert modis data from hdf to GDAL formats using GDAL

       :param str inname: name of input data
       :param str output: prefix for output data
       :param str outformat: the name of output format according with gdal
                             format names
    """
    def __init__(self, innames, output, outformat='GTIFF'):
        """Function for the initialize the object"""
        # Open source dataset
        self.in_names = innames
        self.file_infos = []
        self.driver = gdal.GetDriverByName(outformat)
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
        self._names_to_fileinfos()
        self.xsize = self.file_infos[0].xsize
        self.ysize = self.file_infos[0].ysize
        self.proj = self.file_infos[0].projection
        self.geotrasf = self.file_infos[0].geotransform
        self.bandtype = self.file_infos[0].band_type

    def _checkOutputBands(self):
        output = 0
        for fi in self.file_infos:
            output += fi.bands
        return output

    def write(self):
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

       Class copied from gdal_merge.py

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
        self.band_type = self.s_fh.GetRasterBand(1).DataType
        self.block_size = self.s_fh.GetRasterBand(1).GetBlockSize()
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
