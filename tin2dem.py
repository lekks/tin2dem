#!/usr/bin/env python

import argparse
import logging
import sys
import time

from tqdm import tqdm

from dem_file import GeoTiff
from dem_geo import DemInfo, split_dem
from render import Render
from tinn_read import Surface

log = logging.getLogger("tin to dem")

CHUNK_DEFAULT = 256
NO_DATA_VALUE = -32767


def tin2dem(tinn_file, tiff_file, pix_size, epsg, margins, chunk_width, chunk_height):
    start = time.time()
    if epsg is None:
        log.warn("NO EPSG GIVEN")
    print ("Reading tin file {} ...".format(tinn_file))
    surface = Surface()
    surface.read_tin(tinn_file)
    print ("Found {} points and {} faces".format(len(surface.vertices), len(surface.faces)))
    print ("Min corner is {}".format(surface.min_vertex))
    print ("Max corner is {}".format(surface.max_vertex))
    shift = surface.shift_origin()
    dem = DemInfo.from_envelope(*surface.get_envelope(), pix_size=pix_size, margins=margins)
    tiff = GeoTiff(tiff_file, dem, NO_DATA_VALUE, shift, epsg)

    print ("Preprocessing...")
    render = Render(surface, NO_DATA_VALUE)
    print ("Rendering...")
    chunks = list(split_dem(dem, chunk_width, chunk_height))
    for chunk in tqdm(chunks):
        filter_buf = render.filter_bounds(chunk)
        result, debug = render.render_dem(chunk, filter_buf)
        tiff.write_chunk(chunk, result)
    end = time.time()
    print ("Done in {0:.2f} seconds".format(end - start))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tin")
    parser.add_argument("tiff")
    parser.add_argument("--pixel", type=float, default=1.0)
    parser.add_argument("--epsg", type=int, default=None)
    parser.add_argument("--chunk", type=int, default=CHUNK_DEFAULT)
    parser.add_argument("--margins", type=float, default=None)
    args = parser.parse_args()
    tin2dem(args.tin, args.tiff, args.pixel, args.epsg, args.margins, args.chunk, args.chunk)


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN, stream=sys.stdout,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    main()
