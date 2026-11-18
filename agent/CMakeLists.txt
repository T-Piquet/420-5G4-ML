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

# Module Python optionnel (les sources Python vivent dans python/ pour ne pas
# être captées par le GLOB "*.cpp" du programme console).
option(BUILD_PYTHON_MODULE "Construire le module Python bibliotheque_py" ON)

if(BUILD_PYTHON_MODULE)
    set(PYBIND11_FINDPYTHON ON)
    find_package(Python COMPONENTS Interpreter Development.Module QUIET)
    find_package(pybind11 CONFIG QUIET)

    if(Python_FOUND AND pybind11_FOUND)
        pybind11_add_module(bibliotheque_py
            python/bindings.cpp
            book.cpp
            user.cpp
            library.cpp
            filemanager.cpp
        )

        target_include_directories(bibliotheque_py PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
        set_target_properties(bibliotheque_py PROPERTIES
            CXX_STANDARD 17
            CXX_STANDARD_REQUIRED YES
            CXX_EXTENSIONS NO
        )
        target_compile_options(bibliotheque_py PRIVATE -Wall -Wextra -Wpedantic)
    else()
        message(WARNING "Python ou pybind11 introuvable : module bibliotheque_py non construit.")
    endif()
endif()
