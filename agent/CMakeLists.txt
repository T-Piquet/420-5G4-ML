cmake_minimum_required(VERSION 3.21)
project(bibliotheque LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

# Noyau partagé entre le CLI et le module Python
add_library(bibliotheque_core STATIC
    book.cpp
    user.cpp
    library.cpp
    filemanager.cpp
    session.cpp
)
target_include_directories(bibliotheque_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)
set_target_properties(bibliotheque_core PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Exécutable CLI d'origine
add_executable(bibliotheque main.cpp)
target_link_libraries(bibliotheque PRIVATE bibliotheque_core)

# Module Python (pybind11) : instructions dans fichiersMD/plan.md
set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG QUIET)
if(pybind11_FOUND)
    pybind11_add_module(bibliotheque_py bindings.cpp)
    target_link_libraries(bibliotheque_py PRIVATE bibliotheque_core)
    target_compile_options(bibliotheque_py PRIVATE -Wall -Wextra -Wpedantic)
else()
    message(STATUS "pybind11 introuvable : le module bibliotheque_py ne sera pas construit")
endif()
