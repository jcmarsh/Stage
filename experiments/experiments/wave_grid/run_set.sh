#!/bin/bash

# TODO: This should really be a loop

echo "First Experiment: ###############################"
python overlord.py ./experiments/wave_grid/single_grid_90.ini
echo "Second Experiment: ###############################"
python overlord.py ./experiments/wave_grid/single_grid_72.ini
echo "Third Experiment: ###############################"
python overlord.py ./experiments/wave_grid/single_grid_54.ini
echo "Fourth Experiment: ###############################"
python overlord.py ./experiments/wave_grid/single_grid_36.ini
echo "Fifth Experiment: ################################"
python overlord.py ./experiments/wave_grid/single_grid_18.ini
