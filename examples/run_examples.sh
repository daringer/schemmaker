#!/bin/bash 

export PYTHONPATH=$PYTHONPATH:..
for fn in *.vhdl
do
	python ../schemmaker.py ${fn} pdfs/${fn}.pdf
done
