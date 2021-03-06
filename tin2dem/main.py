
import argparse
import logging
import time

from tqdm import tqdm

from tin2dem.dem_file import GeoTiff
from tin2dem.dem_geo import DemInfo, split_dem
from tin2dem.render import Render
from tin2dem.surface import Surface

log = logging.getLogger("tin2dem main")

CHUNK_DEFAULT = 256
NO_DATA_VALUE = -32767


def tin2dem(tinn_file, tiff_file, pix_size, epsg, margins, chunk_width, chunk_height, select_surface, cad_mode):
    start = time.time()
    if epsg is None:
        log.warn("NO EPSG GIVEN")
    print("Reading tin file {} ...".format(tinn_file))
    surface = Surface()
    surface.from_file(tinn_file, select_surface)
    print(
        "Found {} serfaces, {} points and {} faces".format(surface.surfaces, len(surface.vertices), len(surface.faces)))
    if len(surface.vertices) == 0 or len(surface.faces) == 0:
        print("Nothing to do")
        exit(1)
    if surface.surfaces > 1:
        if select_surface is None:
            print("You may want to select one of {} surfaces found".format(surface.surfaces))
            print(" rendering all of them, however")
        else:
            print("Surface {} is selected to render".format(select_surface))
    print("Min corner is {}".format(surface.min_vertex))
    print("Max corner is {}".format(surface.max_vertex))

    origin = surface.shift_origin()
    dem = DemInfo.from_envelope(*surface.get_envelope(), pix_size=pix_size, margins=margins)
    shift = (origin[0] + pix_size / 2, origin[1] + pix_size / 2) if cad_mode else origin
    tiff = GeoTiff(tiff_file, dem, NO_DATA_VALUE, shift, epsg)

    print("Preprocessing...")
    render = Render(surface, NO_DATA_VALUE)
    print("Rendering...")
    chunks = list(split_dem(dem, chunk_width, chunk_height))
    for chunk in tqdm(chunks):
        filter_buf = render.filter_bounds(chunk)
        result, debug = render.render_dem(chunk, filter_buf)
        tiff.write_chunk(chunk, result)
    end = time.time()
    print("Done in {0:.2f} seconds".format(end - start))


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_tin")
    parser.add_argument("output_tiff")
    parser.add_argument("--pixel", type=float, default=1.0, help="Pixel size")
    parser.add_argument("--epsg", type=int, default=None, help="EPSG code")
    parser.add_argument("--chunk", type=int, default=CHUNK_DEFAULT, help="Processing chunk size, "
                                                                         "optimal value may depend of your GPU memory."
                                                                         "Default is 256")
    parser.add_argument("--margins", type=float, default=None, help="Output DEM margins")
    parser.add_argument("--surface", type=int, default=None, help="Surface to render if multiple surfaces is found")
    parser.add_argument("-a", "--autocad", action='store_true',
                        help="Autocad compatible output (shift on 1/2 pixels)")
    args = parser.parse_args()
    tin2dem(args.input_tin, args.output_tiff, args.pixel, args.epsg, args.margins, args.chunk, args.chunk, args.surface,
            args.autocad)

