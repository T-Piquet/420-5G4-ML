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
# Compilé automatiquement dès que le fichier bindings.cpp est créé
find_package(pybind11 QUIET)
if(pybind11_FOUND AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/bindings.cpp")
    pybind11_add_module(bibliotheque_cpp ${LIB_SOURCES} bindings.cpp)
    target_compile_options(bibliotheque_cpp PRIVATE -Wall -Wextra -Wpedantic)
endif()
