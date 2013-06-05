#!/bin/bash

# usage

echo "First Experiment: ###############################" > $1
python overlord.py ./experiments/set0/single_wave_u.ini &>> $1
echo "\n\nSecon Experiment: ###############################" >> $1
python overlord.py ./experiments/set0/single_wave_g0.ini &>> $1
echo "\n\nThird Experiment: ###############################" >> $1
python overlord.py ./experiments/set0/single_wave_g1.ini &>> $1