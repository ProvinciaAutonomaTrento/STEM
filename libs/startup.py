from pyro_stem import PYROSERVER
from pyro_stem import GRASSPYROOBJNAME
from pyro_stem import GDALINFOPYROOBJNAME
from pyro_stem import GDALCONVERTPYROOBJNAME
from pyro_stem import OGRINFOPYROOBJNAME
from pyro_stem import MLPYROOBJNAME
from pyro_stem import LASPYROOBJNAME
from las_stem import stemLAS
from machine_learning import MLToolBox
from gdal_stem import file_info, convertGDAL, infoOGR
from grass_stem import stemGRASS
import Pyro4
import os
        
GLOBAL_SERVER_PORT = 6000

def main():
    Pyro4.config.SERVERTYPE = "multiplex"
    os.environ["PYRO_LOGFILE"] = "/root/pyrodebug.log"
    os.environ["PYRO_LOGLEVEL"] = "DEBUG"
    daemon = Pyro4.Daemon(host = PYROSERVER, port = GLOBAL_SERVER_PORT)
        
    uri_las = daemon.register(stemLAS, objectId = LASPYROOBJNAME, force = True)
    uri_machine = daemon.register(MLToolBox, objectId = MLPYROOBJNAME, force = True)
    uri_gdal_info = daemon.register(file_info, objectId = GDALINFOPYROOBJNAME, force = True)
    uri_gdal_convert = daemon.register(convertGDAL, objectId = GDALCONVERTPYROOBJNAME, force = True)
    uri_ogr = daemon.register(infoOGR, objectId = OGRINFOPYROOBJNAME, force = True)
    uri_grass = daemon.register(stemGRASS, objectId = GRASSPYROOBJNAME, force = True)
    
    ns = Pyro4.locateNS()
    
    ns.register("PyroLasStem", uri_las)
    ns.register("PyroMachineStem", uri_machine)
    ns.register("PyroGdalInfoStem", uri_gdal_info)
    ns.register("PyroGdalConvertStem", uri_gdal_convert)
    ns.register("PyroOgrStem", uri_ogr)
    ns.register("PyroGrassStem", uri_grass)
    
    daemon.requestLoop()

if __name__ == "__main__":
    main()