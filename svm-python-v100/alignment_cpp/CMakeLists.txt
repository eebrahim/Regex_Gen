cmake_minimum_required (VERSION 2.6)
project (Align)

# Standard Build Type is "Release"
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release" CACHE STRING
      "Choose the type of build, options are: Debug Release RelWithDebInfo MinSizeRel."
      FORCE)
endif(NOT CMAKE_BUILD_TYPE)

# The version number.
set (Align_VERSION_MAJOR 0)
set (Align_VERSION_MINOR 1)

# configure a header file to pass some of the CMake settings
# to the source code
configure_file (
  "${PROJECT_SOURCE_DIR}/AlignConfig.h.in"
  "${PROJECT_BINARY_DIR}/AlignConfig.h"
  )

# add the binary tree to the search path for include files
# so that we will find TutorialConfig.h
include_directories("${PROJECT_BINARY_DIR}")

# add the executable
add_executable(Align Main.cpp 
                     Hirschberg.h Hirschberg.cpp 
                     Util.h Util.cpp 
                     SimilarityString.h SimilarityString.cpp
                     AlignedString.h AlignedString.cpp
                     )
