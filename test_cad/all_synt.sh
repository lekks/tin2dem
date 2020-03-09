#!/bin/bash
set -e

export PYOPENCL_CTX='1'

function simple() {
	files=(\
		synt/2slopes1H.xml \
		synt/2slopes1V.xml \
		synt/2slopes2HV.xml \
	)

	for f in ${files[@]}; do
		bname=$(basename $f)
		name=${bname%.*}
		path=$(dirname "${f}")
		mkdir -p "$path/out"
		../tin2dem.py $f $path/out/$name-td-1ft.tif --pixels_shift 0.5 0.5
		../tin2dem.py $f $path/out/$name-td-1ft.tif --pixels_shift 0.15 0.15 --pixel=0.3
	done

		mkdir -p "$path/out"
}

function complex() {
	mkdir -p cplx_test/out
	../tin2dem.py cplx_test/cplx_test.xml cplx_test/out/cplx_test-td-0.01.tif --pixel=0.01 --pixels_shift 0.005 0.005
	../tin2dem.py cplx_test/cplx_test.xml cplx_test/out/cplx_test-td-0.02.tif --pixel=0.02 --pixels_shift 0.01 0.01
	../tin2dem.py cplx_test/cplx_test.xml cplx_test/out/cplx_test-td-0.005.tif --pixel=0.005 --pixels_shift 0.0025 0.0025
}

#simple
complex

