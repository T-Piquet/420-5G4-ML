cmake_minimum_required(VERSION 3.21)
project(bibliotheque LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

# Bibliothèque partagée par la CLI et le module Python.
add_library(bibliotheque_lib STATIC
    book.cpp
    library.cpp
    user.cpp
    filemanager.cpp
)
target_include_directories(bibliotheque_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_options(bibliotheque_lib PRIVATE -Wall -Wextra -Wpedantic)
set_target_properties(bibliotheque_lib PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Exécutable en ligne de commande.
add_executable(bibliotheque main.cpp)
target_link_libraries(bibliotheque PRIVATE bibliotheque_lib)
target_compile_options(bibliotheque PRIVATE -Wall -Wextra -Wpedantic)

# Module pybind11 utilisé par la GUI Python.
option(BUILD_PYTHON_BINDINGS "Construire le module pybind11 de la GUI" OFF)

if(BUILD_PYTHON_BINDINGS)
    find_package(Python 3 COMPONENTS Interpreter Development REQUIRED)
    find_package(pybind11 CONFIG REQUIRED)

    pybind11_add_module(bibliotheque_core MODULE bindings.cpp)
    target_link_libraries(bibliotheque_core PRIVATE bibliotheque_lib)
    set_target_properties(bibliotheque_core PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/GUI"
    )
endif()
