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

# --- Module Python (pybind11) ---
# Localise l'installation de pybind11 via le Python système, puis le package CMake.
execute_process(
    COMMAND python3 -m pybind11 --cmakedir
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE PYBIND11_CMAKE_RESULT
    ERROR_QUIET
)
if(PYBIND11_CMAKE_RESULT EQUAL 0 AND PYBIND11_CMAKE_DIR)
    list(APPEND CMAKE_PREFIX_PATH "${PYBIND11_CMAKE_DIR}")
endif()

find_package(pybind11 CONFIG REQUIRED)

# Le module réutilise le coeur C++ mais pas main.cpp (réservé au CLI).
set(CORE_SOURCES ${SOURCES})
list(REMOVE_ITEM CORE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/main.cpp")

pybind11_add_module(bibliotheque_core gui/binding/bindings.cpp ${CORE_SOURCES})

target_include_directories(bibliotheque_core PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

set_target_properties(bibliotheque_core PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)
