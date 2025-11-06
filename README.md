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

## Docker

Two Docker images are available: CPU (with POCL) and GPU (vendor-agnostic, requires host GPU runtime).

### Building Images

**CPU Image (POCL - works everywhere):**
```console
make docker-build-cpu
```

**GPU Image (requires NVIDIA/AMD runtime on host):**
```console
make docker-build-gpu
```

### Running with Docker

**CPU Image:**
```console
black-box-test/indocker.sh tin2dem-cpu input.xml output.tif
```

**GPU Image (NVIDIA):**
Requires NVIDIA Container Toolkit installed on host. The image expects vendor OpenCL ICDs to be provided by the host runtime:
```console
black-box-test/indocker.sh --gpu --mount-vendors tin2dem-gpu input.xml output.tif
```

The `--gpu` flag adds `--gpus all` for NVIDIA GPU access, and `--mount-vendors` mounts the host's `/etc/OpenCL/vendors` directory so the container can discover GPU platforms.

**GPU Image (AMD ROCm):**
For AMD GPUs, you'll need to manually run with appropriate device access:
```console
docker run -it --rm \
  --device=/dev/kfd --device=/dev/dri --group-add video \
  -v /opt/rocm:/opt/rocm:ro \
  -v /etc/OpenCL/vendors:/host-ocl-vendors:ro \
  -e OCL_ICD_VENDORS=/host-ocl-vendors \
  -v "$(realpath input.xml)":/var/input.xml \
  -v "$(pwd)":/var/output/ \
  tin2dem-gpu \
  /var/input.xml /var/output/output.tif
```

### Testing

Run black-box tests:
```console
make docker-test-cpu    # Test CPU image
make docker-test-gpu    # Test GPU image (requires GPU runtime)
```

### Diagnostics

Both images include `clinfo` for OpenCL diagnostics. To check available platforms:
```console
docker run --rm -it tin2dem-cpu clinfo
docker run --rm -it --gpus all \
  -v /etc/OpenCL/vendors:/host-ocl-vendors:ro \
  -e OCL_ICD_VENDORS=/host-ocl-vendors \
  tin2dem-gpu clinfo
```
