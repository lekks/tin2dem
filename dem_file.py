import os
from osgeo import gdal, osr


class GeoTiff:
    TIFF_DRIVER = gdal.GetDriverByName("GTiff")

    def __init__(self, dem_name, dem_info, nodata_value, shift=(0, 0), epsg=None):
        assert dem_info.offset_col == 0
        assert dem_info.offset_row == 0

        if os.path.exists(dem_name):
            os.remove(dem_name)

        co = ["COMPRESS=DEFLATE", "ZLEVEL=1", "TILED=YES", "BIGTIFF=YES"]
        self.dst_ds = self.TIFF_DRIVER.Create(dem_name, xsize=dem_info.width, ysize=dem_info.height, bands=1,
                                              eType=gdal.GDT_Float32, options=co)
        gt = list(dem_info.gt)
        gt[0] += shift[0]
        gt[3] += shift[1]
        self.dst_ds.SetGeoTransform(gt)
        self.dst_ds.GetRasterBand(1).SetNoDataValue(nodata_value)

        if epsg is not None:
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(int(epsg))
            self.dst_ds.SetProjection(srs.ExportToWkt())

    def write_chunk(self, chunk, data):
        self.dst_ds.GetRasterBand(1).WriteArray(data, chunk.offset_col, chunk.offset_row)
