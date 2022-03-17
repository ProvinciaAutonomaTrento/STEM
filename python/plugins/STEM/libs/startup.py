from __future__ import absolute_import
from .pyro_stem import PYROSERVER
from .pyro_stem import GRASSPYROOBJNAME
from .pyro_stem import GDALINFOPYROOBJNAME
from .pyro_stem import GDALCONVERTPYROOBJNAME
from .pyro_stem import OGRINFOPYROOBJNAME
from .pyro_stem import MLPYROOBJNAME
from .pyro_stem import LASPYROOBJNAME
from .pyro_stem import TREESTOOLSNAME
from .las_stem import stemLAS
from .machine_learning import MLToolBox
from .gdal_stem import file_info, convertGDAL, infoOGR, TreesTools
from .grass_stem import stemGRASS
import gdal
import os
        
GLOBAL_SERVER_PORT = 6000

def main():
    gdal.AllRegister()

    #os.environ["PYRO_LOGFILE"] = "/opt/pyrodebug.log"
    #os.environ["PYRO_LOGLEVEL"] = "DEBUG"

if __name__ == "__main__":
    main()