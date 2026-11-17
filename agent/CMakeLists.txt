cmake_minimum_required(VERSION 3.21)
project(bibliotheque LANGUAGES CXX)

# Sources du coeur de l'application, partagées par l'exécutable et les bindings Python.
set(CORE_SOURCES
    book.cpp
    filemanager.cpp
    library.cpp
    user.cpp
)

add_library(bibliotheque_core STATIC ${CORE_SOURCES})
target_include_directories(bibliotheque_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Specifie qu'on veut la version C++17 du langage
set_target_properties(bibliotheque_core PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
    POSITION_INDEPENDENT_CODE ON
)

# flag pour tous les warnings possible
target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE bibliotheque_core)
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

# Module Python (pybind11) utilisé par l'interface graphique.
option(BUILD_PYTHON_BINDINGS "Compile le module Python bibliotheque_py" ON)

if(BUILD_PYTHON_BINDINGS)
    find_package(Python3 COMPONENTS Interpreter Development.Module REQUIRED)
    find_package(pybind11 CONFIG QUIET)

    # pybind11 installé via pip n'est pas toujours trouvé automatiquement par CMake.
    if(NOT pybind11_FOUND)
        execute_process(
            COMMAND ${Python3_EXECUTABLE} -m pybind11 --cmakedir
            OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )

        if(PYBIND11_CMAKE_DIR)
            list(APPEND CMAKE_PREFIX_PATH "${PYBIND11_CMAKE_DIR}")
        endif()

        find_package(pybind11 CONFIG REQUIRED)
    endif()

    pybind11_add_module(bibliotheque_py bindings.cpp)
    target_link_libraries(bibliotheque_py PRIVATE bibliotheque_core)
endif()
