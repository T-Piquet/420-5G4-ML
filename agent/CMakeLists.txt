cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

# Sources du coeur de la bibliothèque (hors main)
set(LIB_SOURCES
    book.cpp
    user.cpp
    library.cpp
    filemanager.cpp
)

# Exécutable en ligne de commande (CLI) original
add_executable(${PROJECT_NAME} main.cpp ${LIB_SOURCES})
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

# Module d'extension Python via pybind11 (Phase 2 du TP)
# Fait échouer CMake explicitement si bindings.cpp existe mais que pybind11 est manquant
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/bindings.cpp")
    # Use FindPython so -DPython_EXECUTABLE selects the interpreter that will
    # actually import the module (important when the GUI runs in a venv).
    set(PYBIND11_FINDPYTHON ON)
    find_package(Python COMPONENTS Interpreter Development REQUIRED)
    find_package(pybind11 REQUIRED)
    pybind11_add_module(bibliotheque_cpp ${LIB_SOURCES} bindings.cpp)
    target_compile_options(bibliotheque_cpp PRIVATE -Wall -Wextra -Wpedantic)
endif()
