#!/bin/bash
set -e

export PYOPENCL_CTX='0'

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
		../tin2dem.py $f $path/out/$name-td-1ft.tif -a
		../tin2dem.py $f $path/out/$name-td-0.3ft.tif --pixel=0.3 -a
	done

		mkdir -p "$path/out"
}

function complex() {
	mkdir -p synt/out
	../tin2dem.py synt/cplx_test.xml synt/out/cplx_test-td-0.01.tif --pixel=0.01 -a
	../tin2dem.py synt/cplx_test.xml synt/out/cplx_test-td-0.02.tif --pixel=0.02 -a
	../tin2dem.py synt/cplx_test.xml synt/out/cplx_test-td-0.005.tif --pixel=0.005 -a
}

simple
complex

