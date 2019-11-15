#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import shutil
import subprocess
import uuid
from osgeo import gdal

MIN_VOL = 0.001
CREATION_OPTIONS = [
    "-co",
    "COMPRESS=DEFLATE",
    "-co",
    "ZLEVEL=1",
    "-co",
    "TILED=YES",
    "-co",
    "BIGTIFF=YES"
]
CREATION_OPTIONS2 = [
    "--overwrite",
    "--co",
    "COMPRESS=DEFLATE",
    "--co",
    "TILED=YES",
    "--co",
    "BIGTIFF=YES",
    "--co",
    "ZLEVEL=1"
]
SRSS_OPTIONS = [
    "-s_srs",
    "EPSG:3857"
]
TMP_PATH = '/tmp/compare/'
LOG_ENABLED = True


def log(log_line):
    if (LOG_ENABLED):
        print(log_line)

def cmd(args):
    log("$" + ' '.join(args))
    subprocess.check_call(args)


def call(args):
    log("$" + ' '.join(args))
    output = subprocess.check_output(args)
    return output


def resize_as(src_name, dst_name, templ_name, method="average"):
    data = gdal.Info(templ_name, format='json')
    w, h = data["size"]
    gt = data["geoTransform"]
    ulx, uly = gt[0], gt[3]
    lrx, lry = ulx + w * gt[1], uly + h * gt[5]
    co = ["COMPRESS=DEFLATE", "ZLEVEL=1", "TILED=YES", "BIGTIFF=YES"]
    gdal.Translate(dst_name, src_name, format='GTiff', width=w, height=h, projWin=[ulx, uly, lrx, lry],
                   resampleAlg=method, creationOptions=co)

def gdal_calc(A, B, dst_name, expression):
    opt = CREATION_OPTIONS2 + ['-A', A, '--NoDataValue=-32768']
    if B:
        opt += ['-B', B]
    opt += ['--calc', expression, '--outfile=' + dst_name]
    cmd(['gdal_calc.py']+opt)


def main(first,second,result, tmp_file = None):
    tmp_dir = os.path.join(TMP_PATH,"compare-tmp-"+str(uuid.uuid1())) #tmp_dir = TMP_PATH

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    try:
        if tmp_file is None:
            tmp_file = os.path.join(tmp_dir,"target_resize.tif")
        resize_as(
            second,
            tmp_file,
            first
        )
        #tmp_file = second
        gdal_calc(
            first,
            tmp_file,
            result,
            "(A-B)*(-10000<A)*(10000>A)*(-10000<B)*(10000>B)"
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("first")
    parser.add_argument("second")
    parser.add_argument("result")
    parser.add_argument("--temp", default=None)

    args = parser.parse_args()
    main(
        args.first,
        args.second,
        args.result,
        args.temp,
    )
