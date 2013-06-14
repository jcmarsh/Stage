#!/bin/bash

# usage

echo "First Experiment: ###############################"
python overlord.py ./experiments/set0/single_wave_u.ini
echo "\n\nSecon Experiment: ###############################"
python overlord.py ./experiments/set0/single_wave_g0.ini
echo "\n\nThird Experiment: ###############################"
python overlord.py ./experiments/set0/single_wave_g1.ini
