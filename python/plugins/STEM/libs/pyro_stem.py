# -*- coding: utf-8 -*-
"""
Library for Pyro4, it set some variable for the Pyro4 server, like the IP of
the server and the ports for the different servers (one for each STEM library)

@author: Luca delucchi

Date: April 2015
"""

PYROSERVER = '172.31.17.14'
GRASS_PORT = 6000
GDAL_PORT = 6000
ML_PORT = 6000
LAS_PORT = 6000

# GDAL_PORT = 6001
# ML_PORT = 6002
# LAS_PORT = 6003
GRASSPYROOBJNAME = "grass_stem_pyro_production"
TREESTOOLSNAME = "trees_tools_pyro_production"
GDALINFOPYROOBJNAME = "gdalinfo_stem_pyro_production"
GDALCONVERTPYROOBJNAME = "gdalconvert_stem_pyro_production"
OGRINFOPYROOBJNAME = "ogrinfo_stem_pyro_production"
MLPYROOBJNAME = "ml_stem_pyro_production"
LASPYROOBJNAME = "las_stem_pyro_production"