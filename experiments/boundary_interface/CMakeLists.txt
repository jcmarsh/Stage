CMAKE_MINIMUM_REQUIRED (VERSION 2.4 FATAL_ERROR)
PROJECT (playerplugin_boundary)

# Include this CMake module to get most of the settings needed to build
SET (CMAKE_MODULE_PATH "@CMAKE_INSTALL_PREFIX@/share/cmake/Modules")
INCLUDE (UsePlayerPlugin)
INCLUDE (UsePlayerC)

INCLUDE_DIRECTORIES (${PROJECT_BINARY_DIR})
PLAYER_ADD_PLUGIN_INTERFACE (boundary 124_boundary.def SOURCES boundary_interf_client.c)
# Note the use of files generated during the PLAYER_ADD_PLUGIN_INTERFACE step
PLAYER_ADD_PLUGIN_DRIVER (boundary_driver SOURCES boundary_interf_driver.cc boundary_interface.h boundary_xdr.h)
PLAYER_ADD_PLAYERC_CLIENT (boundary_client SOURCES test_boundary_client.c boundary_interface.h)
PLAYER_ADD_PLAYERC_CLIENT (multi_client SOURCES test_multi.c boundary_interface.h)
TARGET_LINK_LIBRARIES (boundary_client boundary)
TARGET_LINK_LIBRARIES (multi_client boundary)

INSTALL(FILES ./build/libboundary_driver.so ./build/libboundary.so
  DESTINATION ./lib/)