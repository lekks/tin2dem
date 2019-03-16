#!/usr/bin/env python

import argparse
import logging
import sys

from dem_file import GeoTiff
from dem_geo import DemInfo, split_dem
from render import Render
from tinn_read import Surface
from tqdm import tqdm

log = logging.getLogger("tinn to dem")

CHUNK_WIDTH = 256
CHUNK_HEIGHT = 256

NO_DATA_VALUE = -32767

def tin2dem(tinn_file, tiff_file, pix_size):
    log.info("Let`s read tinn {}".format(tinn_file))
    surface = Surface()
    surface.read_tin(tinn_file)
    log.info("{} points".format(len(surface.vertices)))
    log.info("{} faces".format(len(surface.faces)))
    log.info("Min corner is {}".format(surface.min_vertex))
    log.info("Max corner is {}".format(surface.max_vertex))
    shift = surface.shift_origin()
    render = Render(surface, NO_DATA_VALUE)
    dem = DemInfo.from_envelope(*surface.get_envelope(), pix_size=pix_size)
    print (dem.gt)
    print ("Shift {}".format(shift))
    tiff = GeoTiff(tiff_file, dem, NO_DATA_VALUE, shift)

    chunks = list(split_dem(dem, CHUNK_WIDTH, CHUNK_WIDTH))
    for chunk in tqdm(chunks):
        filter_buf = render.filter_bounds(chunk)
        result, debug = render.render_dem(chunk, filter_buf)
        tiff.write_chunk(chunk, result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tinn")
    parser.add_argument("tiff")
    parser.add_argument("--pixel", type=float, default=1.0)
    args = parser.parse_args()
    tin2dem(args.tinn, args.tiff, args.pixel)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    main()
