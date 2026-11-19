cmake_minimum_required(VERSION 3.15)
project(library_core)

set(CMAKE_CXX_STANDARD 17)

find_package(pybind11 REQUIRED)

pybind11_add_module(library_core
    bindings.cpp
    agent/library.cpp
    agent/filemanager.cpp
    agent/book.cpp
    agent/user.cpp
)

target_include_directories(library_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/src)