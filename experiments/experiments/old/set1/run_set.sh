#!/bin/bash

# usage

echo "First Experiment: ###############################"
python overlord.py ./experiments/set1/single_a_star_u.ini
echo "\n\nSecon Experiment: ###############################"
python overlord.py ./experiments/set1/single_a_star_g0.ini
echo "\n\nThird Experiment: ###############################"
python overlord.py ./experiments/set1/single_a_star_g1.ini
