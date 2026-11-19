cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

file(GLOB SOURCES "*.cpp")
add_executable(${PROJECT_NAME} ${SOURCES})

# Specifie qu'on veut la version C++17 du langage
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

# flag pour tous les warnings possible
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

# Module Python optionnel : expose le cœur C++ à l'interface customtkinter.
option(BUILD_PYTHON_BINDINGS "Construire le module Python pybind11" OFF)

if(BUILD_PYTHON_BINDINGS)
    find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
    find_package(pybind11 CONFIG REQUIRED)

    pybind11_add_module(bibliotheque_core
        bindings/library_bindings.cpp
        book.cpp
        user.cpp
        library.cpp
        filemanager.cpp
    )

    target_include_directories(bibliotheque_core
        PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
    )
    target_compile_options(bibliotheque_core
        PRIVATE -Wall -Wextra -Wpedantic
    )
    set_target_properties(bibliotheque_core PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/UI/app"
    )
endif()
