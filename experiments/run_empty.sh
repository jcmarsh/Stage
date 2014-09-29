#!/bin/bash

# Make sure the benchmarker is set run the correct controller

for index in `seq 0 9`; do
	timeout 140s player baseline.cfg > $1_$index.txt &
	sleep 5
	timeout 130s ./controllers/c_cont/basic 127.0.0.1
	sleep 10
done
