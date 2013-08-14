CMAKE_MINIMUM_REQUIRED (VERSION 2.4 FATAL_ERROR)
PROJECT (playerplugin_examples)

# Include this CMake module to get most of the settings needed to build
SET (CMAKE_MODULE_PATH "/usr/local/share/cmake/Modules")
INCLUDE (UsePlayerPlugin)
INCLUDE (UsePlayerC)

INCLUDE_DIRECTORIES (${PROJECT_BINARY_DIR})
PLAYER_ADD_PLUGIN_INTERFACE (smrtln 100_smrtln.def SOURCES smrtlninterf_client.c)
# Note the use of files generated during the PLAYER_ADD_PLUGIN_INTERFACE step
PLAYER_ADD_PLUGIN_DRIVER (smrtln_driver SOURCES smrtlninterf_driver.cc smrtln_interface.h smrtln_xdr.h)
PLAYER_ADD_PLAYERC_CLIENT (smrtln_client SOURCES smrtln_client.c smrtln_interface.h)
TARGET_LINK_LIBRARIES (smrtln_client smrtln)
