#!/bin/bash

# TODO: This should really be a loop

echo "First Experiment: ###############################"
python overlord.py ./experiments/a_star_grid/single_grid_90.ini results.txt
echo "Second Experiment: ###############################"
python overlord.py ./experiments/a_star_grid/single_grid_72.ini results.txt
echo "Third Experiment: ###############################"
python overlord.py ./experiments/a_star_grid/single_grid_54.ini results.txt
echo "Fourth Experiment: ###############################"
python overlord.py ./experiments/a_star_grid/single_grid_36.ini results.txt
echo "Fifth Experiment: ################################"
python overlord.py ./experiments/a_star_grid/single_grid_18.ini results.txt
