CMAKE_MINIMUM_REQUIRED (VERSION 2.4 FATAL_ERROR)
PROJECT (actuation_noise_driver)

# Include this CMake module to get most of the settings needed to build
SET (CMAKE_MODULE_PATH "/usr/local/share/cmake/Modules")
INCLUDE (UsePlayerPlugin)

PLAYER_ADD_PLUGIN_DRIVER (actuation_noise_driver SOURCES actuation_noise_driver.cc)

INSTALL(FILES ./build/libactuation_noise_driver.so
  DESTINATION ./lib/)