#!/bin/bash

# Generated by script_gen.py

echo "0 Experiment: ############################"
python overlord.py ./experiments/convoy_simple_grid_baseline/conf_0.ini ./experiments/convoy_simple_grid_baseline/results.txt

echo "1 Experiment: ############################"
python overlord.py ./experiments/convoy_simple_grid_baseline/conf_1.ini ./experiments/convoy_simple_grid_baseline/results.txt

echo "2 Experiment: ############################"
python overlord.py ./experiments/convoy_simple_grid_baseline/conf_2.ini ./experiments/convoy_simple_grid_baseline/results.txt

echo "3 Experiment: ############################"
python overlord.py ./experiments/convoy_simple_grid_baseline/conf_3.ini ./experiments/convoy_simple_grid_baseline/results.txt

