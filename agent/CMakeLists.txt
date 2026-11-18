cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

find_package(pybind11 REQUIRED)


file(GLOB SOURCES "*.cpp")
list(REMOVE_ITEM SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/binding.cpp")
add_executable(bibliotheque_cli ${SOURCES})

set_target_properties(bibliotheque_cli PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO)
target_compile_options(bibliotheque_cli PRIVATE
    -Wall -Wextra -Wpedantic)


file(GLOB LIB_SOURCES "*.cpp")
list(REMOVE_ITEM LIB_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/main.cpp")

pybind11_add_module(bibliotheque ${LIB_SOURCES})
set_target_properties(bibliotheque PROPERTIES
    CXX_STANDARD 17 CXX_STANDARD_REQUIRED YES CXX_EXTENSIONS NO)