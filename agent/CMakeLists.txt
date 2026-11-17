cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

set(CORE_SOURCES
    book.cpp
    user.cpp
    library.cpp
    filemanager.cpp
)

add_executable(${PROJECT_NAME} main.cpp ${CORE_SOURCES})

# Specifie qu'on veut la version C++17 du langage
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

# flag pour tous les warnings possible
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

# Module Python pybind11
find_package(Python3 COMPONENTS Interpreter Development QUIET)
find_package(pybind11 CONFIG QUIET)

if(pybind11_FOUND)
    pybind11_add_module(bibliotheque_cpp bindings/bindings.cpp ${CORE_SOURCES})
    target_include_directories(bibliotheque_cpp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
    set_target_properties(bibliotheque_cpp PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/gui"
    )
endif()
