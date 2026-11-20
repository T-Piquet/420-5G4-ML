cmake_minimum_required(VERSION 3.21)
project(bibliotheque LANGUAGES CXX)

# Specifie qu'on veut la version C++17 du langage
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

# Coeur metier partage entre le CLI et le module Python
add_library(bibliotheque_core STATIC
    book.cpp
    user.cpp
    library.cpp
    filemanager.cpp
)
target_include_directories(bibliotheque_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)
set_target_properties(bibliotheque_core PROPERTIES POSITION_INDEPENDENT_CODE ON)

# CLI : uniquement main.cpp
add_executable(bibliotheque main.cpp)
target_link_libraries(bibliotheque PRIVATE bibliotheque_core)
target_compile_options(bibliotheque PRIVATE -Wall -Wextra -Wpedantic)

# Module pybind11 (desactive par defaut)
option(BUILD_PYTHON_BINDINGS "Construire le module Python pybind11" OFF)

if(BUILD_PYTHON_BINDINGS)
    find_package(Python COMPONENTS Interpreter Development REQUIRED)

    if(NOT DEFINED pybind11_DIR)
        execute_process(
            COMMAND ${Python_EXECUTABLE} -m pybind11 --cmakedir
            OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
        if(PYBIND11_CMAKE_DIR)
            set(pybind11_DIR "${PYBIND11_CMAKE_DIR}")
        endif()
    endif()

    find_package(pybind11 CONFIG REQUIRED)

    pybind11_add_module(bibliotheque_py bindings.cpp)
    target_link_libraries(bibliotheque_py PRIVATE bibliotheque_core)
    set_target_properties(bibliotheque_py PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/python
    )
endif()
