#!/bin/bash

# MAKE SURE THAT THE BENCHMARKER IS SET TO RUN EMPTY CONTROLLER

timeout 120s player baseline.cfg > vote_run0.txt &
sleep 3
timeout 125s ./controllers/c_cont/basic 127.0.0.1

timeout 120s player baseline.cfg > vote_run1.txt &
sleep 3
timeout 125s ./controllers/c_cont/basic 127.0.0.1

timeout 120s player baseline.cfg > vote_run2.txt &
sleep 3
timeout 125s ./controllers/c_cont/basic 127.0.0.1

timeout 120s player baseline.cfg > vote_run3.txt &
sleep 3
timeout 125s ./controllers/c_cont/basic 127.0.0.1

timeout 120s player baseline.cfg > vote_run4.txt &
sleep 3
timeout 125s ./controllers/c_cont/basic 127.0.0.1
