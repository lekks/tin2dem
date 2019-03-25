#!/bin/bash

test_vol() {
	NAME=$1
	TIN_FILE=$2
	SCAN_FILE=$3
	CAD_FILE=$4
	EPSG=$5
	PIX=$6

	CAD_3857=data/${NAME}-cad-3857.tif
	CAD_3857M=data/${NAME}-cad-3857m.tif

	TIN2DEM_FILE=data/${NAME}-tin2dem2.tif
	TIN2DEM3857=data/${NAME}-tin2dem2-3857.tif
	TIN2DEM3857M=data/${NAME}-tin2dem2-3857m.tif

	PYOPENCL_CTX=0 /usr/bin/time --verbose ./tin2dem.py $TIN_FILE $TIN2DEM_FILE --epsg=$EPSG --pixel=$PIX

	gdalwarp $TIN2DEM_FILE $TIN2DEM3857 -t_srs EPSG:3857 -r average
	gdal_calc.py -A $TIN2DEM3857 --outfile=$TIN2DEM3857M --calc="A*0.3048"

	gdal_edit.py $CAD_FILE -a_srs EPSG:${EPSG}
	gdalwarp $CAD_FILE $CAD_3857 -t_srs EPSG:3857 -r average
	gdal_calc.py -A $CAD_3857 --outfile=$CAD_3857M --calc="A*0.3048"

	echo  $TIN2DEM3857M $CAD_3857M $SCAN_FILE
	./calc_volumes.py $TIN2DEM3857M $CAD_3857M 
	./calc_volumes.py $TIN2DEM3857M $SCAN_FILE
	./calc_volumes.py $CAD_3857M $SCAN_FILE
}

#buffalo
test_vol buffalo data/1510766440189-BUFFALO_RIDGE_SUB_GRADE.xml data/buffalo.float.tif data/buffalo-autocad.tif 2276 0.3
#faria
#test_vol faria data/Faria-dtm-14.xml data/faria.float.tif data/faria-cad.tif 2227 0.3
