#!/bin/bash

# This script copies over the modified player files to the player source directory (9122)
# It assumes that stage and player are both located in the same directory (usually ~/research/)
# It also assumes that it is executed withing stage/experiments/to_player/

cp CMakeLists.txt ../../../player/libplayerinterface/
cp interfaces/* ../../../player/libplayerinterface/interfaces/
cp libplayerc/* ../../../player/client_libs/libplayerc/


