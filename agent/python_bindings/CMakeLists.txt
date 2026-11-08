cmake_minimum_required(VERSION 3.14)
project(bibliotheque_pybind11 VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(pybind11 REQUIRED)

# Les sources C++ de la bibliothèque se trouvent dans le répertoire parent.
set(LIBRARY_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/..)

pybind11_add_module(bibliotheque
    python_bindings.cpp
    ${LIBRARY_SOURCE_DIR}/book.cpp
    ${LIBRARY_SOURCE_DIR}/library.cpp
    ${LIBRARY_SOURCE_DIR}/user.cpp
    ${LIBRARY_SOURCE_DIR}/filemanager.cpp
)

target_include_directories(bibliotheque PRIVATE ${LIBRARY_SOURCE_DIR})
target_compile_options(bibliotheque PRIVATE -Wall -Wextra -Wpedantic)

install(TARGETS bibliotheque DESTINATION .)
