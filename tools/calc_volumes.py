#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import gdal

import numpy

METERS3_IN_YARDS3 = 0.764555
ELEVATION_LIMIT_M = 10000

def _get_dem_info(dem):
    info = gdal.Info(dem, format='json')
    pixel_width = info["geoTransform"][1]
    pixel_height = info["geoTransform"][5]
    size_x, size_y = info['size']
    upper_left = info["geoTransform"][0], info["geoTransform"][3]
    lower_right = info["geoTransform"][0]+size_x*pixel_width, info["geoTransform"][3]+size_y*pixel_height
    lat_sample = info["wgs84Extent"]["coordinates"][0][0][1]
    return (pixel_width, pixel_height), (size_x, size_y), upper_left, lower_right, lat_sample


def _resize_first_to_second(src_name, templ_dem):
    _, dimensions_pixels, upper_left, lower_right, _ = _get_dem_info(templ_dem)
    w, h = dimensions_pixels
    ulx, uly = upper_left
    lrx, lry = lower_right

    resized = gdal.Translate('', src_name, format='MEM', width=w, height=h, projWin=[ulx, uly, lrx, lry], resampleAlg="average")
    return resized


def _read_dem_data_n_nod(dem):
    """
    Reads and amends DEM's data and NoData value. Both should be in
    [-ELEVATION_LIMIT_M, ELEVATION_LIMIT_M] interval. All values off this interval
    replaced with NoData
    """
    nod = gdal.Info(dem, format='json')['bands'][0]['noDataValue']
    if not -ELEVATION_LIMIT_M < nod < ELEVATION_LIMIT_M:
        nod = ELEVATION_LIMIT_M

    data = dem.ReadAsArray()
    data[data > ELEVATION_LIMIT_M] = nod
    data[data < -ELEVATION_LIMIT_M] = nod

    return data, nod



def create_dem_from(template, data):
    """
    Creates a copy of template DEM with provided elevations data
    :param [osgeo.gdal.Dataset] template:  DEM to take metadata from
    :param [numpy.ndarray] data: elevations matrix
    :return: [osgeo.gdal.Dataset] new DEM
    """
    driver = gdal.GetDriverByName('MEM')
    driver.Register()
    cols = template.RasterXSize
    rows = template.RasterYSize
    bands = template.RasterCount
    band = template.GetRasterBand(1)
    gt = template.GetGeoTransform()
    proj = template.GetProjection()
    output = driver.Create('', cols, rows, bands, band.DataType)
    output.SetGeoTransform(gt)
    output.SetProjection(proj)
    outBand = output.GetRasterBand(1)
    ndv = band.GetNoDataValue()
    outBand.SetNoDataValue(ndv)
    outBand.WriteArray(data, 0, 0)
    return output


def _calc_volumes(A, B):

    def diff_vol(arr, pix_area):

        height = numpy.sum(arr)
        volume_m3 = pix_area * height
        return volume_m3

    def make_diff(A,B):
        arrA, nodA = _read_dem_data_n_nod(A)
        arrB, nodB = _read_dem_data_n_nod(B)
        return (arrA - arrB)* (arrA != nodA)*(arrB != nodB)

    diff = make_diff(A, B)
    info = gdal.Info(A, format='json')
    lat = info["wgs84Extent"]["coordinates"][0][0][1]
    gt = A.GetGeoTransform()
    pix_area = abs(gt[1] * gt[5]) * numpy.math.pow(numpy.cos(numpy.radians(lat)), 2)

    cut_vol = diff_vol(diff * (diff>=0), pix_area)
    filArr = (-diff) * (diff<=0)
    del diff
    fill_vol = diff_vol(filArr, pix_area)

    return cut_vol, fill_vol


def _get_diff_volumes(first_dem, second_dem, strategy="first"):
    # Resolving DEM pixel dimensions and choose direction of matching
    width_first = _get_dem_info(first_dem)[0][0]
    width_second = _get_dem_info(second_dem)[0][0]
    first_larger = width_first > width_second

    if strategy == "first":
        first_to_second = True
    elif strategy == "second":
        first_to_second = False
    elif strategy.startswith("large"):
        first_to_second = first_larger
    elif strategy.startswith("small"):
        first_to_second = not first_larger
    else:
        raise AttributeError("Unknown resize method")

    if first_to_second:
        print("Resizing first to second")
        A = _resize_first_to_second(first_dem, second_dem)
        B = second_dem
    else:
        print("Resizing second to first")
        A = first_dem
        B = _resize_first_to_second(second_dem, first_dem)

    cut, fill = _calc_volumes(A, B)
    return cut, fill


def get_res(file):
    gt = gdal.Open(file).GetGeoTransform()
    return gt[1], -gt[5]


def just_compare(first, second, resize):
    res1 = get_res(first)
    res2 = get_res(second)
    print("Resolutions are {} and {}".format(res1, res2))

    ref_cut, ref_fill = _get_diff_volumes(gdal.Open(first), gdal.Open(second), resize)
    print("Cut is {} m3, fill is {} m3".format(ref_cut, ref_fill))
    ref_cut /= METERS3_IN_YARDS3
    ref_fill /= METERS3_IN_YARDS3
    print("Cut is {} cy, fill is {} cy".format(ref_cut, ref_fill))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("first")
    parser.add_argument("second")
    parser.add_argument("--resize", help="Resize:first,second,largerst,smallest", default="first")
    args = parser.parse_args()
    just_compare(args.first, args.second, args.resize)
