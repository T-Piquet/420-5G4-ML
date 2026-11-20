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

# flag pour tous les warnings possible (GCC/Clang ; MSVC ne les connait pas)
if(NOT MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Module Python (pybind11)
option(BUILD_PYTHON_BINDINGS "Construire le module Python bibliotheque_py" ON)
if(BUILD_PYTHON_BINDINGS)
    # pybind11 installe par pip n'est pas dans les chemins CMake par defaut
    find_package(Python3 COMPONENTS Interpreter Development.Module QUIET)
    if(Python3_Interpreter_FOUND)
        execute_process(
            COMMAND "${Python3_EXECUTABLE}" -m pybind11 --cmakedir
            OUTPUT_VARIABLE PYBIND11_PIP_CMAKE_DIR
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
        if(PYBIND11_PIP_CMAKE_DIR AND EXISTS "${PYBIND11_PIP_CMAKE_DIR}/pybind11Config.cmake")
            list(APPEND CMAKE_PREFIX_PATH "${PYBIND11_PIP_CMAKE_DIR}")
        endif()
    endif()

    find_package(pybind11 CONFIG QUIET)
    if(pybind11_FOUND)
        pybind11_add_module(bibliotheque_py python_bindings.cpp ${CORE_SOURCES})
        set_target_properties(bibliotheque_py PROPERTIES
            CXX_STANDARD 17
            CXX_STANDARD_REQUIRED YES
            CXX_EXTENSIONS NO
        )
        if(NOT MSVC)
            target_compile_options(bibliotheque_py PRIVATE -Wall -Wextra -Wpedantic)
        endif()
        # Le module est copie a cote de gui.py : plus besoin de PYTHONPATH
        add_custom_command(TARGET bibliotheque_py POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_SOURCE_DIR}/python"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "$<TARGET_FILE:bibliotheque_py>"
                    "${CMAKE_CURRENT_SOURCE_DIR}/python/"
            COMMENT "Copie de bibliotheque_py dans python/"
        )
    else()
        message(WARNING "pybind11 introuvable : le module Python bibliotheque_py ne sera pas construit.")
    endif()
endif()
