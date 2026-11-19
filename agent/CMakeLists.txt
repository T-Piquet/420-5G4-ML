cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

file(GLOB SOURCES "*.cpp")
list(FILTER SOURCES EXCLUDE REGEX "bibliotheque_bindings\\.cpp$")
add_executable(${PROJECT_NAME} ${SOURCES})

# Specifie qu'on veut la version C++17 du langage
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

# flag pour tous les warnings possible
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

# Bindings Python optionnels
find_package(pybind11 CONFIG QUIET)

# Repli pour une installation de pybind11 via pip
if(NOT pybind11_FOUND)
    find_program(PYBIND11_PYTHON_EXECUTABLE NAMES python3 python)
    if(PYBIND11_PYTHON_EXECUTABLE)
        execute_process(
            COMMAND ${PYBIND11_PYTHON_EXECUTABLE} -m pybind11 --cmakedir
            OUTPUT_VARIABLE PYBIND11_PIP_CMAKE_DIR
            OUTPUT_STRIP_TRAILING_WHITESPACE
            RESULT_VARIABLE PYBIND11_PIP_RESULT
            ERROR_QUIET
        )
        if(PYBIND11_PIP_RESULT EQUAL 0)
            find_package(pybind11 CONFIG QUIET
                PATHS "${PYBIND11_PIP_CMAKE_DIR}"
                NO_DEFAULT_PATH
            )
        endif()
    endif()
endif()

if(pybind11_FOUND)
    pybind11_add_module(bibliotheque_python
        bibliotheque_bindings.cpp
        book.cpp
        user.cpp
        library.cpp
        filemanager.cpp
    )

    set_target_properties(bibliotheque_python PROPERTIES
        OUTPUT_NAME bibliotheque
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO
    )

    target_compile_options(bibliotheque_python PRIVATE -Wall -Wextra -Wpedantic)
else()
    message(STATUS "pybind11 introuvable : cible Python bibliotheque ignorée")
endif()
