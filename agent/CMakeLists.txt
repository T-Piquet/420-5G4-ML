cmake_minimum_required(VERSION 3.21)
project(bibliotheque LANGUAGES CXX)

# C++17, as in the original TUI project.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

set(BIBLIO_WARNINGS -Wall -Wextra -Wpedantic)

# Domain model shared by the TUI and the Python bindings.
add_library(biblio_domain STATIC
    book.cpp
    user.cpp
    library.cpp
    filemanager.cpp
)
target_include_directories(biblio_domain PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_options(biblio_domain PRIVATE ${BIBLIO_WARNINGS})
# The same objects feed a Python extension module.
set_target_properties(biblio_domain PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Original terminal application.
add_executable(bibliotheque main.cpp)
target_link_libraries(bibliotheque PRIVATE biblio_domain)
target_compile_options(bibliotheque PRIVATE ${BIBLIO_WARNINGS})

# pybind11 module used by the graphical (Python + web) application.
find_package(pybind11 CONFIG REQUIRED)
pybind11_add_module(biblio_core bindings/module.cpp)
target_link_libraries(biblio_core PRIVATE biblio_domain)
set_target_properties(biblio_core PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
