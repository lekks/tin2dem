# tin2dem
Tool for fast rendering of TIN (Triangular Irregular Networks) surface in LandXML format into DEM (Digital Elevation Model) raster files in GeoTIFF format using OpenCL on CPU or GPU

# Installation

## Requirements
 - python 2 or 3
 - GDAL library with python bindings
 - OpenCL runtime
 
## Linux
### Install dependencies
```console
  sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
  sudo apt-get update
  sudo apt-get install python-pip gdal-bin python-gdal clinfo
  pip install pyopencl tqdm pytest
``` 
### Install OpenCL driver 
Here is the list of OpenCL implementations: https://www.iwocl.org/resources/opencl-implementations/  
Install runtime corresponding to your GPU

You can use universal runtime POCL and run render using CPU only:
```console
sudo apt install pocl-opencl-icd
```
Check if you have runtime installed
```console
clinfo -l
```
and run test
```console
python -m pytest
```
### Usage
```console
usage: tin2dem.py [-h] [--pixel PIXEL] [--epsg EPSG] [--chunk CHUNK]
                  [--margins MARGINS] [--surface SURFACE]
                  input_tin output_tiff

positional arguments:
  input_tin
  output_tiff

optional arguments:
  -h, --help         show this help message and exit
  --pixel PIXEL      Pixel size
  --epsg EPSG        EPSG code
  --chunk CHUNK      Processing chunk size, optimal value may depend of your
                     GPU memory.Default is 256
  --margins MARGINS  Output DEM margins
  --surface SURFACE  Surface to render if multiple surfaces is found
```
## Windows

