cmake_minimum_required(VERSION 3.21)
project(bibliotheque LANGUAGES CXX)

option(BUILD_PYTHON_BINDINGS "Construire le module Python pybind11" ON)

# Coeur de la bibliotheque partage entre le CLI et les bindings Python
add_library(bibliotheque_core STATIC
    book.cpp
    user.cpp
    library.cpp
    filemanager.cpp
)

target_include_directories(bibliotheque_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

set_target_properties(bibliotheque_core PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
    POSITION_INDEPENDENT_CODE ON
)

target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)

# CLI interactif
add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE bibliotheque_core)

set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

# Module Python (pybind11)
if(BUILD_PYTHON_BINDINGS)
    set(PYBIND11_FINDPYTHON ON)
    find_package(pybind11 CONFIG REQUIRED)

    pybind11_add_module(bibliotheque_py python/bindings.cpp)
    target_link_libraries(bibliotheque_py PRIVATE bibliotheque_core)

    set_target_properties(bibliotheque_py PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO
    )
endif()
