cmake_minimum_required(VERSION 3.21)
project(gui_test LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Le module Python pilote les sources C++ d'origine, compilées telles quelles.
pybind11_add_module(_cpp_backend
    cpp/backend.cpp
    ../book.cpp
    ../user.cpp
    ../library.cpp
    ../filemanager.cpp
)

target_include_directories(_cpp_backend PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/..")

set_target_properties(_cpp_backend PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

target_compile_options(_cpp_backend PRIVATE -Wall -Wextra -Wpedantic)
