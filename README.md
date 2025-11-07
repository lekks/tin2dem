# tin2dem
Tool for fast rendering of TIN (Triangular Irregular Networks) surface in LandXML format into DEM (Digital Elevation Model) raster files in GeoTIFF format using OpenCL on CPU or GPU


# Running in Docker

Two Docker images are available: CPU (with POCL) and GPU (vendor-agnostic, requires host GPU runtime).

### Using Pre-built Images

You can use pre-built images from Docker Hub without building them locally.

#### CPU Image

```console
docker run --rm -v "$(pwd)":/data lekkks/tin2dem:latest-cpu /data/input.xml /data/output.tif
```

#### GPU Image

To use GPU acceleration, you need to configure Docker to access GPU devices. For setup instructions, see:

- [NVIDIA GPUs](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- [AMD GPUs](https://docs.docker.com/engine/reference/commandline/dockerd/#gpu-options)

```console
# For NVIDIA GPUs
docker run --rm --gpus all -v /etc/OpenCL/vendors:/host-ocl-vendors:ro -e OCL_ICD_VENDORS=/host-ocl-vendors -v "$(pwd)":/data lekkks/tin2dem:latest-gpu /data/input.xml /data/output.tif
```

For AMD GPUs, you'll need to manually run with appropriate device access (NOT TESTED):

```console
docker run --rm --device=/dev/kfd --device=/dev/dri --group-add video -v /opt/rocm:/opt/rocm:ro -v /etc/OpenCL/vendors:/host-ocl-vendors:ro -e OCL_ICD_VENDORS=/host-ocl-vendors -v "$(pwd)":/data lekkks/tin2dem:latest-gpu /data/input.xml /data/output.tif
```
### Diagnostics

Both images include `clinfo` for OpenCL diagnostics. To check available platforms:
```console
docker run --rm -it --entrypoint clinfo lekkks/tin2dem:latest-cpu
docker run --rm -it --gpus all \
  -v /etc/OpenCL/vendors:/host-ocl-vendors:ro \
  -e OCL_ICD_VENDORS=/host-ocl-vendors \
  --entrypoint clinfo lekkks/tin2dem:latest-gpu
```

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

## Windows

Install Python 3, GDAL (e.g., via conda: `conda install -c conda-forge gdal`), and OpenCL runtime (GPU drivers or POCL).

## Install package using pip

```console
pip install git+ssh://git@github.com/lekks/tin2dem
```

or checkout from git and run test
```console
pip install pytest
pytest tests
```

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
                     GPU memory. Default is 256
  --margins MARGINS  Output DEM margins
  --surface SURFACE  Surface to render if multiple surfaces is found
  -a, --autocad      Autocad compatible output (shift on 1/2 pixels)
```
set PYOPENCL_CTX environment variable if you don't want to choose runtime every time,
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

