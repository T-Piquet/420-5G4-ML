cmake_minimum_required(VERSION 3.14)
project(bibliotheque_pybind11 VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find required packages
find_package(pybind11 REQUIRED)

# Include directories
include_directories(${pybind11_INCLUDE_DIR})

# Create Python extension module
pybind11_add_module(bibliotheque 
    python_bindings.cpp
    book.cpp
    library.cpp
    user.cpp
    filemanager.cpp
)

# Install target
install(TARGETS bibliotheque DESTINATION .)
