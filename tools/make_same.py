#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import gdal


def resize_as(src_name, dst_name, templ_name, method="average"):
    data = gdal.Info(templ_name, format='json')
    w, h = data["size"]
    gt = data["geoTransform"]
    ulx, uly = gt[0], gt[3]
    lrx, lry = ulx + w * gt[1], uly + h * gt[5]
    co = ["COMPRESS=DEFLATE", "ZLEVEL=1", "TILED=YES", "BIGTIFF=YES"]
    gdal.Translate(dst_name, src_name, format='GTiff', width=w, height=h, projWin=[ulx, uly, lrx, lry],
                   resampleAlg=method, creationOptions=co)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("result")
    parser.add_argument("template")
    parser.add_argument('--method', default="average")
    args = parser.parse_args()

    resize_as(args.source, args.result, args.template, args.method)
