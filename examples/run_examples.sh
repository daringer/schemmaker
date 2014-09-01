#!/bin/bash 

echo "DO NOT WORK AT THE MOMENT - USE TESTS INSTEAD!!!!"
echo "DO NOT WORK AT THE MOMENT - USE TESTS INSTEAD!!!!"
echo "DO NOT WORK AT THE MOMENT - USE TESTS INSTEAD!!!!"
echo "DO NOT WORK AT THE MOMENT - USE TESTS INSTEAD!!!!"
echo "DO NOT WORK AT THE MOMENT - USE TESTS INSTEAD!!!!"

exit 1;

PY="python2"
export PYTHONPATH=$PYTHONPATH:../src/
for fn in *.vhdl
do
	$PY ../src/schemmaker.py ${fn} pdfs/${fn}.pdf
done
