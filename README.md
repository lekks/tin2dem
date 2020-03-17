# tin2dem
Tool for fast rendering of TIN (Triangular Irregular Networks) surface in LandXML format into DEM (Digital Elevation Model) raster files in GeoTIFF format using OpenCL on CPU or GPU

# Installation

## Requirements
 - python3
 - GDAL library with python bindings
 - OpenCL runtime
 
## Linux
### Install dependencies
```console
  sudo add-apt-repository ppa:ubuntugis/ppa
  sudo apt-get update
  sudo apt-get install python3-pip gdal-bin gdal-data python3-gdal clinfo
``` 


### Install OpenCL driver 
Here is the list of OpenCL implementations: https://www.iwocl.org/resources/opencl-implementations/  
Install runtime corresponding to your GPU

You can use universal runtime POCL and run render with CPU:
```console
sudo apt install pocl-opencl-icd
```
Check if you have runtime installed
```console
clinfo -l
```

install package using pip

```console
pip3 install git+ssh://git@github.com/lekks/tin2dem
```

or checkout from git and run test
```console
sudo apt-get install python3-pytest
py.test-3 tests
```
## Windows

# Usage
```
usage: tin2dem.py [-h] [--pixel PIXEL] [--epsg EPSG] [--chunk CHUNK]
                  [--margins MARGINS] [--surface SURFACE] [-a]
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
  -a, --autocad      Autocad compatible output (shift on 1/2 pixels)
```
set PYOPENCL_CTX environment variable if you don't want choose runtime every time,
for example:
``` 
PYOPENCL_CTX=0 tin2dem tin.xml dem.tif
```
## Examples
Render example files from landxml.org
```console
wget http://landxml.org/schema/LandXML-2.0/samples/Carlson%20Software/Olympus_Subdivision-2.0.xml
tin2dem Olympus_Subdivision-2.0.xml Olympus_Subdivision-2.0.tif
```
Multiple surfaces:
```console
wget http://landxml.org/schema/LandXML-1.1/samples/BLUERIDGE%20Analytics/siteops.xml
tin2dem siteops.xml siteops.tif --surface=4
```
