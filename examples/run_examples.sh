#!/bin/bash 

PY="python2"
export PYTHONPATH=$PYTHONPATH:../src/
for fn in *.vhdl
do
	$PY ../src/schemmaker.py ${fn} pdfs/${fn}.pdf
done
