#!/bin/bash 

export PYTHONPATH=$PYTHONPATH:..
for fn in *.vhdl
do
	python ../schemmaker.py ${fn} ${fn}.pdf &
done

echo "[i] waiting for all processes to end!"
wait
